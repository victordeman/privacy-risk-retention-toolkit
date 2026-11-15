"""Data inventory: one record per dataset/file/system, linked to processing activity, assessments and retention rule."""
from __future__ import annotations

from pathlib import Path

from .common import read_csv, write_csv

FIELDS = ["inventory_id", "type", "name", "storage_location", "record_count", "activity_id", "business_purpose",
          "responsible_owner", "documented_data_categories", "discovered_categories", "recipients",
          "sensitivity", "sensitivity_basis", "retention_rule_id", "retention_policy", "assessment_ids", "scan_status"]
RANK = {"Low": 0, "Medium": 1, "High": 2}


def _heuristic_sensitivity(text: str) -> str:
    t = text.lower()
    if any(k in t for k in ("national id", "tax", "bank", "salary", "beneficial")):
        return "High"
    return "Medium"


def build_inventory(source_dir, register_rows, assessments, retention_rules, summary, rules) -> list:
    source_dir = Path(source_dir)
    cat_sens = {k: v["sensitivity"] for k, v in rules["categories"].items()}
    rule_by_file = {r["dataset"]: r for r in retention_rules}
    by_activity = {}
    for a in assessments:
        by_activity.setdefault(a["activity_id"], []).append(a["assessment_id"])
    rows, n = [], 0
    file_systems = set()
    for fp in sorted(source_dir.glob("*.csv")):
        n += 1
        act = next((a for a in register_rows if fp.name in a["systems"]), None)
        cats = sorted({c for c, v in summary["by_category"].items() if fp.name in v["files"]})
        sens = max((cat_sens[c] for c in cats), key=lambda s: RANK[s], default="Low")
        rr = rule_by_file.get(fp.name, {})
        info = summary["per_file"].get(fp.name, {})
        for s in (act["systems"].split(", ") if act else []):
            file_systems.add(s.strip())
        rows.append({"inventory_id": f"DS-{n:03d}", "type": "file", "name": fp.name, "storage_location": str(source_dir),
            "record_count": info.get("total_records", ""), "activity_id": act["activity_id"] if act else "",
            "business_purpose": act["purpose"] if act else "", "responsible_owner": act["owner"] if act else "",
            "documented_data_categories": act["data_categories"] if act else "",
            "discovered_categories": ", ".join(cats), "recipients": act["recipients"] if act else "",
            "sensitivity": sens, "sensitivity_basis": "discovered: High if identification numbers, else Medium if direct identifiers",
            "retention_rule_id": rr.get("rule_id", ""), "retention_policy": act["retention_period"] if act else "",
            "assessment_ids": ", ".join(by_activity.get(act["activity_id"], [])) if act else "",
            "scan_status": "scanned" if fp.name in summary["per_file"] else "not scanned"})
    s = 0
    seen = set()
    for act in register_rows:
        for sysname in [x.strip() for x in act["systems"].split(",")]:
            if sysname.endswith(".csv") or sysname in seen:
                continue
            seen.add(sysname)
            s += 1
            sens = _heuristic_sensitivity(act["data_categories"])
            rows.append({"inventory_id": f"SYS-{s:03d}", "type": "system", "name": sysname,
                "storage_location": "system of record (no sample provided)", "record_count": "",
                "activity_id": act["activity_id"], "business_purpose": act["purpose"], "responsible_owner": act["owner"],
                "documented_data_categories": act["data_categories"], "discovered_categories": "",
                "recipients": act["recipients"], "sensitivity": sens,
                "sensitivity_basis": "heuristic from documented categories - owner to confirm",
                "retention_rule_id": "", "retention_policy": act["retention_period"],
                "assessment_ids": ", ".join(by_activity.get(act["activity_id"], [])), "scan_status": "not scanned"})
    return rows


def write_inventory(path, rows):
    write_csv(path, FIELDS, rows)
