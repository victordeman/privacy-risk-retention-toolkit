"""Retention review automation driven entirely by config/retention_schedule_config.json."""
from __future__ import annotations

from datetime import date
from pathlib import Path

from .common import DataFileError, add_years, load_json, parse_date, read_csv, write_csv

ELIGIBLE = "ELIGIBLE_FOR_REVIEW"
ON_HOLD = "ON_HOLD_EXPIRED"
INSUFFICIENT = "INSUFFICIENT_INFO"
ACTIVE = "ACTIVE_NO_TRIGGER"
NOT_DUE = "NOT_YET_DUE"
CATEGORIES = [ELIGIBLE, ON_HOLD, INSUFFICIENT, ACTIVE, NOT_DUE]
OUT_FIELDS = ["dataset", "record_id", "trigger_column", "trigger_value", "trigger_state", "retention_years", "review_due_date",
              "days_past_due", "on_hold", "hold_reason", "category", "reason", "data_quality_flag"]


def load_config(path) -> dict:
    cfg = load_json(path)
    cfg["_invalid"] = {v.strip().lower() for v in cfg["invalid_date_values"]}
    cfg["_as_of"] = parse_date(cfg["as_of_date"])
    if cfg["_as_of"] is None:
        raise DataFileError("as_of_date in retention config is not a valid date")
    return cfg


def classify(row: dict, rule: dict, cfg: dict, as_of: date) -> dict:
    """Classify one record. The order of the checks is the policy:
    1 invalid/missing trigger -> ACTIVE_NO_TRIGGER (open record) or INSUFFICIENT_INFO (investigate)
    2 trigger + retention not yet expired -> NOT_YET_DUE
    3 expired and on hold -> ON_HOLD_EXPIRED (never in a disposal proposal)
    4 expired and not on hold -> ELIGIBLE_FOR_REVIEW
    A missing date is never read as permission to delete."""
    raw = (row.get(rule["trigger_column"]) or "").strip()
    hold = (row.get(cfg["hold_column"]) or "").strip().upper() == cfg["hold_value"].upper()
    hold_reason = (row.get(cfg.get("hold_reason_column", "")) or "").strip() if hold else ""
    d = None if raw.lower() in cfg["_invalid"] else parse_date(raw)
    base = {"dataset": rule["dataset"], "record_id": row.get(rule["id_column"], "?"), "trigger_column": rule["trigger_column"],
            "trigger_value": raw if d else (raw or "(blank)"), "retention_years": rule["retention_years"],
            "on_hold": "Y" if hold else "N", "hold_reason": hold_reason, "review_due_date": "", "days_past_due": "",
            "data_quality_flag": ""}
    if d is None:
        status_col = rule.get("status_column")
        status = (row.get(status_col) or "").strip() if status_col else None
        base["trigger_state"] = "missing" if not raw else "invalid"
        if status_col and status not in rule.get("closed_statuses", []):
            base["category"] = ACTIVE
            base["reason"] = f"Record is open (status '{status}'): no trigger date yet, so not eligible"
            if raw:
                base["data_quality_flag"] = f"placeholder '{raw}' in {rule['trigger_column']} on an open record"
        else:
            base["category"] = INSUFFICIENT
            base["reason"] = "Trigger date missing or invalid on a record that should have one: investigate, do NOT dispose"
        return base
    due = add_years(d, rule["retention_years"])
    base.update({"trigger_state": "valid", "review_due_date": due.isoformat(), "days_past_due": (as_of - due).days})
    status_col = rule.get("status_column")
    if status_col and (row.get(status_col) or "").strip() not in rule.get("closed_statuses", []):
        base["data_quality_flag"] = f"open status with trigger date in {rule['trigger_column']}"
    if due > as_of:
        base["category"] = NOT_DUE
        base["reason"] = f"{d.isoformat()} + {rule['retention_years']}y = {due.isoformat()} is after {as_of.isoformat()}"
    elif hold:
        base["category"] = ON_HOLD
        base["reason"] = f"Retention expired {due.isoformat()} but record is on hold ({hold_reason or 'no reason recorded'}): excluded from disposal"
    else:
        base["category"] = ELIGIBLE
        base["reason"] = f"{d.isoformat()} + {rule['retention_years']}y = {due.isoformat()} is on/before {as_of.isoformat()}"
    return base


def run_review(source_dir, cfg, as_of: date | None = None) -> dict:
    as_of = as_of or cfg["_as_of"]
    results, errors = [], []
    for rule in cfg["rules"]:
        try:
            data = read_csv(Path(source_dir) / rule["dataset"])
            for col in (rule["trigger_column"], rule["id_column"], cfg["hold_column"]):
                if col not in data.fieldnames:
                    raise DataFileError(f"{rule['dataset']}: required column '{col}' missing")
        except DataFileError as exc:
            errors.append(str(exc))
            continue
        results += [classify(r, rule, cfg, as_of) for r in data.rows]
    return {"as_of": as_of.isoformat(), "records": results, "errors": errors}


def summarise(records) -> dict:
    out = {}
    for r in records:
        ds = out.setdefault(r["dataset"].replace(".csv", ""), {c: 0 for c in CATEGORIES})
        ds[r["category"]] += 1
    return out


def write_review(path, records):
    write_csv(path, OUT_FIELDS, records)
