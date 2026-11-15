from datetime import date

import pytest
from conftest import ROOT, write
from privacy_toolkit import retention as R
from privacy_toolkit.common import add_years, parse_date

CFG = R.load_config(ROOT / "config" / "retention_schedule_config.json")
RULE = {"dataset": "t.csv", "trigger_column": "closed", "retention_years": 3, "id_column": "id",
        "status_column": "status", "closed_statuses": ["Closed"]}
ASOF = date(2026, 11, 14)


def cl(closed, status="Closed", hold="N", rule=RULE):
    return R.classify({"id": "X1", "closed": closed, "status": status, "on_hold": hold, "hold_reason": "Legal hold" if hold == "Y" else ""}, rule, CFG, ASOF)


def test_date_parsing():
    assert parse_date("2024-02-29") == date(2024, 2, 29)
    assert parse_date("2024-11-26 00:00:00") == date(2024, 11, 26)
    for bad in ["", "invalid", "2023-13-45", "2023-02-30", "26/11/2024", "0000-00-00", "2024-1-1"]:
        assert parse_date(bad) is None


def test_leap_day_rolls_to_28_feb():
    assert add_years(date(2024, 2, 29), 1) == date(2025, 2, 28)
    assert add_years(date(2024, 2, 29), 4) == date(2028, 2, 29)


def test_boundary_exactly_expired_is_eligible():
    assert cl("2023-11-14")["category"] == R.ELIGIBLE          # due == today
    assert cl("2023-11-15")["category"] == R.NOT_DUE           # due tomorrow
    assert cl("2023-11-13")["category"] == R.ELIGIBLE


def test_review_due_date_is_explained():
    r = cl("2022-05-20")
    assert r["review_due_date"] == "2025-05-20" and "2022-05-20 + 3y = 2025-05-20" in r["reason"]


def test_hold_excludes_even_when_expired():
    r = cl("2020-01-01", hold="Y")
    assert r["category"] == R.ON_HOLD and r["on_hold"] == "Y"


def test_hold_flag_case_insensitive_and_blank_means_not_held():
    assert cl("2020-01-01", hold="y")["category"] == R.ON_HOLD
    assert cl("2020-01-01", hold="")["category"] == R.ELIGIBLE


@pytest.mark.parametrize("token", CFG["invalid_date_values"] + ["2023-13-45", "garbage"])
def test_invalid_trigger_on_closed_record_is_investigate_not_delete(token):
    r = cl(token, status="Closed")
    assert r["category"] == R.INSUFFICIENT and r["trigger_state"] in ("missing", "invalid")


@pytest.mark.parametrize("token", ["", "N/A", "TBD", "unknown", "pending"])
def test_invalid_trigger_on_open_record_is_not_eligible(token):
    assert cl(token, status="Active")["category"] == R.ACTIVE


def test_placeholder_on_open_record_gets_quality_flag_blank_does_not():
    assert cl("TBD", status="Active")["data_quality_flag"]
    assert cl("", status="Active")["data_quality_flag"] == ""


def test_dataset_without_status_column_always_expects_trigger():
    rule = {k: v for k, v in RULE.items() if k not in ("status_column", "closed_statuses")}
    assert cl("", rule=rule)["category"] == R.INSUFFICIENT


def test_held_record_with_missing_date_is_still_not_eligible():
    assert cl("", hold="Y")["category"] == R.INSUFFICIENT


def test_real_data_matches_corrected_answer_sheet():
    from privacy_toolkit.evaluate import retention_comparison
    res = R.run_review(ROOT / "data" / "source", CFG)
    assert not res["errors"]
    cmp_ = retention_comparison(R.summarise(res["records"]), ROOT / "answer_sheet" / "expected_retention_outcomes.json")
    assert cmp_["all_match"], [r for r in cmp_["rows"] if not r["match"]]
    assert len(res["records"]) == 410


def test_every_record_in_exactly_one_category_and_totals():
    res = R.run_review(ROOT / "data" / "source", CFG)
    tot = {c: sum(1 for r in res["records"] if r["category"] == c) for c in R.CATEGORIES}
    assert tot == {R.ELIGIBLE: 104, R.ON_HOLD: 12, R.INSUFFICIENT: 10, R.ACTIVE: 143, R.NOT_DUE: 141}


def test_no_closed_record_is_silently_active():
    """Open-status exemption must only ever apply to open records."""
    res = R.run_review(ROOT / "data" / "source", CFG)
    assert all(r["category"] != R.ACTIVE or r["dataset"] not in ("marketing_contacts.csv", "access_logs.csv") for r in res["records"])


def test_as_of_override_changes_outcome():
    a = R.summarise(R.run_review(ROOT / "data" / "source", CFG)["records"])
    b = R.summarise(R.run_review(ROOT / "data" / "source", CFG, date(2030, 1, 1))["records"])
    assert b["access_logs"][R.ELIGIBLE] + b["access_logs"][R.ON_HOLD] > a["access_logs"][R.ELIGIBLE] + a["access_logs"][R.ON_HOLD]


def test_missing_required_column_reported_not_crash(project):
    write(project / "data" / "source" / "customers.csv", "customer_id,status\nCUST1,Active\n")
    res = R.run_review(project / "data" / "source", R.load_config(project / "config" / "retention_schedule_config.json"))
    assert any("customers.csv" in e and "account_closed_date" in e for e in res["errors"])
    assert any(r["dataset"] == "employees.csv" for r in res["records"])


def test_config_is_separate_from_logic(project):
    """Changing retention years in the config alone changes the result - no code edits."""
    import json
    p = project / "config" / "retention_schedule_config.json"
    c = json.loads(p.read_text())
    for r in c["rules"]:
        if r["dataset"] == "access_logs.csv":
            r["retention_years"] = 10
    p.write_text(json.dumps(c))
    s = R.summarise(R.run_review(project / "data" / "source", R.load_config(p))["records"])
    assert s["access_logs"][R.ELIGIBLE] == 0
