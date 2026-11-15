import json
import re

import pytest
from conftest import write
from privacy_toolkit import disposal as D
from privacy_toolkit import retention as R
from privacy_toolkit.common import DataFileError, hash_tree, read_csv, write_csv


@pytest.fixture()
def staged(project):
    cfg = R.load_config(project / "config" / "retention_schedule_config.json")
    recs = R.run_review(project / "data" / "source", cfg)["records"]
    out = project / "output"
    prop = out / "prop.csv"
    rows = D.build_proposal(recs, prop, "DP-T")
    idc = {r["dataset"]: r["id_column"] for r in cfg["rules"]}
    return dict(project=project, cfg=cfg, recs=recs, prop=prop, rows=rows, appr=out / "appr.json", log=out / "log.csv",
                work=out / "sim", idc=idc, src=project / "data" / "source")


def run(s, **kw):
    return D.execute(s["src"], s["work"], s["prop"], s["appr"], s["log"], "RUN-T", id_columns=s["idc"], **kw)


def test_proposal_only_contains_eligible_non_held(staged):
    held = {(r["dataset"], r["record_id"]) for r in staged["recs"] if r["on_hold"] == "Y"}
    eligible = {(r["dataset"], r["record_id"]) for r in staged["recs"] if r["category"] == R.ELIGIBLE}
    prop = {(r["dataset"], r["record_id"]) for r in staged["rows"]}
    assert prop == eligible and not (prop & held) and len(prop) == 104
    assert all(r["on_hold"] == "N" for r in staged["rows"])


def test_no_disposal_without_approval(staged):
    with pytest.raises(DataFileError, match="no approval"):
        run(staged)


def test_rejected_or_unnamed_reviewer_cannot_dispose(staged):
    with pytest.raises(ValueError):
        D.approve(staged["prop"], staged["appr"], " ", "2026-11-14")
    D.approve(staged["prop"], staged["appr"], "Rev", "2026-11-14", decision="REJECTED")
    with pytest.raises(DataFileError, match="not approved"):
        run(staged)


def test_proposal_tampering_after_approval_is_detected(staged):
    D.approve(staged["prop"], staged["appr"], "Rev", "2026-11-14")
    with open(staged["prop"], "a") as fh:
        fh.write("DP-T,employees.csv,EMP1001,,,Y,PROPOSED\n")
    with pytest.raises(DataFileError, match="checksum"):
        run(staged)


def test_simulation_inside_source_folder_refused(staged):
    D.approve(staged["prop"], staged["appr"], "Rev", "2026-11-14")
    staged["work"] = staged["src"] / "sim"
    with pytest.raises(DataFileError, match="separate"):
        run(staged)


def test_execution_only_touches_the_copy(staged):
    before = hash_tree(staged["src"])
    D.approve(staged["prop"], staged["appr"], "Rev", "2026-11-14")
    res = run(staged)
    assert hash_tree(staged["src"]) == before and res["source_unchanged"]
    assert res["counts"]["DELETED_IN_COPY"] == 104
    for ds, n in {"employees.csv": 2, "customers.csv": 5, "suppliers.csv": 1, "support_tickets.csv": 22,
                  "marketing_contacts.csv": 29, "access_logs.csv": 45}.items():
        orig = len(read_csv(staged["src"] / ds).rows)
        assert len(read_csv(staged["work"] / "working_copy" / ds).rows) == orig - n


def test_held_records_survive_simulation(staged):
    D.approve(staged["prop"], staged["appr"], "Rev", "2026-11-14")
    run(staged)
    for r in staged["recs"]:
        if r["category"] == R.ON_HOLD:
            ids = {x[staged["idc"][r["dataset"]]] for x in read_csv(staged["work"] / "working_copy" / r["dataset"]).rows}
            assert r["record_id"] in ids


def test_defence_in_depth_blocks_held_record_even_if_proposed(staged):
    held = next(r for r in staged["recs"] if r["category"] == R.ON_HOLD)
    rows = read_csv(staged["prop"]).rows + [{"proposal_id": "DP-T", "dataset": held["dataset"], "record_id": held["record_id"],
                                              "review_due_date": "", "days_past_due": "", "on_hold": "N", "proposal_status": "PROPOSED"}]
    write_csv(staged["prop"], D.PROPOSAL_FIELDS, rows)
    D.approve(staged["prop"], staged["appr"], "Rev", "2026-11-14")
    res = run(staged)
    assert res["counts"]["BLOCKED_ON_HOLD"] == 1
    log = read_csv(staged["log"]).rows
    assert any(r["record_id"] == held["record_id"] and r["execution_result"] == "BLOCKED_ON_HOLD" for r in log)


def test_rejected_record_ids_are_not_deleted(staged):
    first = staged["rows"][0]
    D.approve(staged["prop"], staged["appr"], "Rev", "2026-11-14", rejected_ids=[first["record_id"]])
    res = run(staged)
    assert res["counts"]["DELETED_IN_COPY"] == 103
    ids = {x[staged["idc"][first["dataset"]]] for x in read_csv(staged["work"] / "working_copy" / first["dataset"]).rows}
    assert first["record_id"] in ids


def test_log_has_decision_reviewer_date_result_and_no_personal_data(staged):
    D.approve(staged["prop"], staged["appr"], "Rev One", "2026-11-14")
    run(staged)
    text = staged["log"].read_text()
    log = read_csv(staged["log"]).rows
    rec = [r for r in log if r["event"] == "RECORD"]
    assert rec and all(r["decision"] == "APPROVED" and r["reviewer"] == "Rev One" and r["decision_date"] == "2026-11-14"
                       and r["execution_result"] for r in rec)
    assert any(r["event"] == "SOURCE_INTEGRITY_CHECK" and r["execution_result"] == "SOURCE_UNCHANGED" for r in log)
    assert not re.search(r"[\w.]+@[\w.]+\.\w+", text)


def test_recovery_restores_identical_copy(staged):
    D.approve(staged["prop"], staged["appr"], "Rev", "2026-11-14")
    run(staged)
    rec = D.recover(staged["src"], staged["work"], staged["work"] / "restored")
    assert rec["identical_to_source"] and rec["files_checked"] == 6 and not rec["mismatched_files"]


def test_recovery_detects_damage(staged):
    D.approve(staged["prop"], staged["appr"], "Rev", "2026-11-14")
    run(staged)
    (staged["work"] / "recovery_copy" / "employees.csv").write_text("employee_id\nEMP1\n")
    assert not D.recover(staged["src"], staged["work"], staged["work"] / "restored")["identical_to_source"]


def test_recover_without_copy_fails(staged):
    with pytest.raises(DataFileError):
        D.recover(staged["src"], staged["work"], staged["work"] / "restored")


def test_proposal_filter_blocks_holds_independently_of_retention_engine(tmp_path):
    """Even if an upstream bug labelled a held record ELIGIBLE, the proposal must still exclude it."""
    recs = [{"dataset": "d.csv", "record_id": "A", "category": R.ELIGIBLE, "on_hold": "Y", "review_due_date": "", "days_past_due": ""},
            {"dataset": "d.csv", "record_id": "B", "category": R.ELIGIBLE, "on_hold": "N", "review_due_date": "", "days_past_due": ""},
            {"dataset": "d.csv", "record_id": "C", "category": R.INSUFFICIENT, "on_hold": "N", "review_due_date": "", "days_past_due": ""}]
    rows = D.build_proposal(recs, tmp_path / "p.csv", "DP-X")
    assert [r["record_id"] for r in rows] == ["B"]
