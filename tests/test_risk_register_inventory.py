import json
from datetime import date

import pytest
from conftest import ROOT
from privacy_toolkit import inventory, register, risk
from privacy_toolkit.common import load_json, read_csv

SC = load_json(ROOT / "config" / "risk_scoring.json")
ASM = read_csv(ROOT / "data" / "registers" / "privacy_risk_assessments.csv").rows
REG = read_csv(ROOT / "data" / "registers" / "processing_activities_register.csv").rows


@pytest.mark.parametrize("v,b", [(1, "Low"), (4, "Low"), (5, "Medium"), (9, "Medium"), (10, "High"), (15, "High"), (16, "Critical"), (25, "Critical")])
def test_band_boundaries(v, b):
    assert risk.band(v, SC) == b


def test_score_validation():
    assert risk.score(3, 4) == 12
    for bad in [(0, 3), (6, 1), (2.5, 2)]:
        with pytest.raises(ValueError):
            risk.score(*bad)


def test_supplied_assessments_are_consistent():
    assert len(ASM) >= 5
    assert risk.validate(ASM, {r["activity_id"] for r in REG}, SC) == []


def test_validation_catches_errors():
    bad = [dict(ASM[0])]
    bad[0]["inherent_risk_score"] = "20"
    bad[0]["residual_risk_score"] = "99"
    bad[0]["activity_id"] = "PA-999"
    bad[0]["treatment_deadline"] = "soon"
    problems = " | ".join(risk.validate(bad, {r["activity_id"] for r in REG}, SC))
    assert "inherent score" in problems and "residual score" in problems and "not in register" in problems
    assert "invalid treatment deadline" in problems and "at least 5" in problems


def kw(**o):
    d = dict(activity_id="PA-003", activity_name="n", assessor="a", assessment_date="2026-11-14", harm="h", likelihood=3,
             severity=3, safeguards="s", measures="Mask exports", residual_likelihood=2, residual_severity=2, owner="o", deadline="2027-01-01")
    d.update(o)
    return d


def test_new_assessment_scores_and_requires_mitigation():
    r = risk.new_assessment(ASM, SC, **kw())
    assert r["assessment_id"] == "PRA-007" and r["inherent_risk_score"] == 9 and r["residual_risk_score"] == 4
    with pytest.raises(ValueError, match="mitigation"):
        risk.new_assessment(ASM, SC, **kw(measures=" "))
    with pytest.raises(ValueError, match="residual"):
        risk.new_assessment(ASM, SC, **kw(residual_likelihood=5, residual_severity=5))
    with pytest.raises(ValueError, match="deadline"):
        risk.new_assessment(ASM, SC, **kw(deadline="tomorrow"))


def test_summary_overdue_and_due_soon():
    s = risk.summarise(ASM, SC, date(2027, 2, 1))
    ids = {i["assessment_id"] for i in s["overdue_actions"]}
    assert {"PRA-001"} .isdisjoint(ids) and "PRA-004" in ids          # PRA-004 deadline 2026-12-31
    assert risk.summarise(ASM, SC, date(2026, 11, 14))["overdue_actions"] == []
    assert s["high_or_critical_inherent"] == []


# ---------------------------------------------------------------- register
def test_register_review_keeps_history(tmp_path):
    w, h = tmp_path / "w.csv", tmp_path / "h.csv"
    register.init_register(ROOT / "data" / "registers" / "processing_activities_register.csv", w, h)
    assert len(register.unreviewed(register.load(w))) == 12
    register.review_activity(w, h, "PA-002", "Owner", "2026-11-14", "update", {"recipients": "CRM, billing system, X"})
    register.review_activity(w, h, "PA-002", "Owner", "2026-11-15", "again", {"recipients": "CRM"})
    rows = {r["activity_id"]: r for r in register.load(w)}
    assert rows["PA-002"]["version"] == "3" and rows["PA-002"]["reviewed_by"] == "Owner"
    hist = [x for x in read_csv(h).rows if x["field"] == "recipients"]
    assert [x["new_value"] for x in hist] == ["CRM, billing system, X", "CRM"]
    assert hist[1]["old_value"] == "CRM, billing system, X"
    assert len(register.unreviewed(register.load(w))) == 11


def test_register_rejects_bad_edits(tmp_path):
    w, h = tmp_path / "w.csv", tmp_path / "h.csv"
    register.init_register(ROOT / "data" / "registers" / "processing_activities_register.csv", w, h)
    with pytest.raises(ValueError):
        register.review_activity(w, h, "PA-001", "o", "2026-11-14", "r", {"activity_id": "PA-X"})
    with pytest.raises(ValueError):
        register.review_activity(w, h, "PA-001", "", "2026-11-14", "r")
    with pytest.raises(KeyError):
        register.review_activity(w, h, "PA-404", "o", "2026-11-14", "r")


def test_register_source_file_never_modified(tmp_path):
    src = ROOT / "data" / "registers" / "processing_activities_register.csv"
    before = src.read_bytes()
    register.init_register(src, tmp_path / "w.csv", tmp_path / "h.csv")
    assert src.read_bytes() == before


# --------------------------------------------------------------- inventory
def test_inventory_links_files_to_activity_owner_rule_and_assessments():
    from privacy_toolkit import discovery
    rules = discovery.load_rules(ROOT / "config" / "discovery_rules.json")
    scan = discovery.scan_folder(ROOT / "data" / "source", rules)
    cfg = load_json(ROOT / "config" / "retention_schedule_config.json")
    rows = inventory.build_inventory(ROOT / "data" / "source", REG, ASM, cfg["rules"], discovery.summarise(scan), rules)
    ids = [r["inventory_id"] for r in rows]
    assert len(ids) == len(set(ids))
    files = [r for r in rows if r["type"] == "file"]
    assert len(files) == 6 and all(r["activity_id"] and r["responsible_owner"] and r["retention_rule_id"] for r in files)
    emp = next(r for r in files if r["name"] == "employees.csv")
    assert emp["activity_id"] == "PA-001" and emp["sensitivity"] == "High" and emp["assessment_ids"] == "PRA-001"
    sup = next(r for r in files if r["name"] == "suppliers.csv")
    assert sup["activity_id"] == "PA-003" and sup["assessment_ids"] == ""
    assert {r["activity_id"] for r in rows} == {r["activity_id"] for r in REG}     # every activity appears
