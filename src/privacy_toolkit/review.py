"""Detection review and validation: an analyst confirms or rejects findings, logs missed detections and rule changes."""
from __future__ import annotations

import csv
from pathlib import Path

from .common import read_csv, write_csv

DECISION_FIELDS = ["finding_id", "file", "column", "category", "decision", "analyst", "review_date", "note"]
MISSED_FIELDS = ["file", "column", "category", "analyst", "review_date", "note"]
IMPROVE_FIELDS = ["date", "analyst", "trigger", "rule_change", "status"]
NOTICE = ("Pattern matches indicate POSSIBLE personal information. A finding is not a confirmed "
          "classification until an analyst has reviewed it.")


def load_decisions(path) -> dict:
    p = Path(path)
    if not p.exists():
        return {}
    return {r["finding_id"]: r for r in read_csv(p).rows}


def record_decision(path, finding, decision, analyst, review_date, note=""):
    if decision not in ("confirmed", "rejected"):
        raise ValueError("decision must be 'confirmed' or 'rejected'")
    if not analyst.strip():
        raise ValueError("analyst name is required")
    existing = load_decisions(path)
    existing[finding["finding_id"]] = {"finding_id": finding["finding_id"], "file": finding["file"],
        "column": finding["column"], "category": finding["category"], "decision": decision,
        "analyst": analyst, "review_date": review_date, "note": note}
    write_csv(path, DECISION_FIELDS, list(existing.values()))
    return existing[finding["finding_id"]]


def simulate_analyst(findings, truth, analyst, review_date):
    """DEMO ONLY: stands in for a human analyst by using the labelled ground truth. Output is labelled as simulated."""
    out = {}
    for f in findings:
        k = (f["file"], f["column"], f["category"])
        ok = k in truth["positive"]
        if ok:
            note = "Confirmed: column holds personal information"
        elif k in truth["negative"]:
            note = "Rejected (false positive): listed as an expected non-match in the answer sheet"
        else:
            note = "Rejected (false positive): values are business categories, not personal data"
        out[f["finding_id"]] = {"finding_id": f["finding_id"], "file": f["file"], "column": f["column"],
            "category": f["category"], "decision": "confirmed" if ok else "rejected",
            "analyst": analyst, "review_date": review_date, "note": note}
    return out


def save_decisions(path, decisions: dict):
    write_csv(path, DECISION_FIELDS, list(decisions.values()))


def find_missed(findings, truth):
    found = {(f["file"], f["column"], f["category"]) for f in findings}
    return sorted(truth["positive"] - found)


def log_improvement(path, date, analyst, trigger, rule_change, status="proposed"):
    p = Path(path)
    rows = read_csv(p).rows if p.exists() else []
    rows.append({"date": date, "analyst": analyst, "trigger": trigger, "rule_change": rule_change, "status": status})
    write_csv(p, IMPROVE_FIELDS, rows)


def suggest_improvements(decisions: dict) -> list:
    """Turn rejected findings into rule-change suggestions for the analyst to accept or ignore."""
    out = []
    for d in decisions.values():
        if d["decision"] == "rejected":
            out.append((f"False positive {d['file']}:{d['column']} ({d['category']})",
                        f"Add '{d['column']}' (or a matching word) to negative_column_hints for category '{d['category']}'"))
    return out
