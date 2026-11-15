"""Processing activity register with owner review and a full change history."""
from __future__ import annotations

from pathlib import Path

from .common import read_csv, write_csv

BASE = ["activity_id", "name", "owner", "purpose", "data_categories", "legal_basis", "retention_period",
        "recipients", "systems", "status"]
EXTRA = ["version", "last_reviewed", "reviewed_by"]
HIST = ["activity_id", "version", "changed_at", "changed_by", "field", "old_value", "new_value", "reason"]
EDITABLE = {"name", "owner", "purpose", "data_categories", "legal_basis", "retention_period", "recipients", "systems", "status"}


def init_register(source_csv, working_csv, history_csv):
    """Create the working register (extra review columns) from the supplied register. Never touches the source."""
    if Path(working_csv).exists():
        return
    rows = read_csv(source_csv).rows
    for r in rows:
        r.update({"version": "1", "last_reviewed": "", "reviewed_by": ""})
    write_csv(working_csv, BASE + EXTRA, rows)
    write_csv(history_csv, HIST, [])


def load(working_csv):
    return read_csv(working_csv).rows


def review_activity(working_csv, history_csv, activity_id, reviewer, review_date, reason, changes=None):
    """Owner review. Any field change is logged with old/new value; the review itself is always logged."""
    if not reviewer.strip():
        raise ValueError("reviewer name is required")
    rows = load(working_csv)
    hist = read_csv(history_csv).rows
    row = next((r for r in rows if r["activity_id"] == activity_id), None)
    if row is None:
        raise KeyError(f"unknown activity {activity_id}")
    new_version = int(row["version"]) + 1
    for field, new in (changes or {}).items():
        if field not in EDITABLE:
            raise ValueError(f"field '{field}' cannot be edited")
        if row[field] != new:
            hist.append({"activity_id": activity_id, "version": new_version, "changed_at": review_date,
                         "changed_by": reviewer, "field": field, "old_value": row[field], "new_value": new, "reason": reason})
            row[field] = new
    hist.append({"activity_id": activity_id, "version": new_version, "changed_at": review_date, "changed_by": reviewer,
                 "field": "(review)", "old_value": "", "new_value": "reviewed", "reason": reason})
    row.update({"version": str(new_version), "last_reviewed": review_date, "reviewed_by": reviewer})
    write_csv(working_csv, BASE + EXTRA, rows)
    write_csv(history_csv, HIST, hist)
    return row


def unreviewed(rows):
    return [r for r in rows if not r.get("last_reviewed")]
