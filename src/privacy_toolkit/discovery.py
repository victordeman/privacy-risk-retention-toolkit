"""Automated data discovery: rule-based detection of POSSIBLE personal information."""
from __future__ import annotations

import re
from pathlib import Path

from .common import DataFileError, load_json, mask_value, read_csv, log

FINDING_FIELDS = ["finding_id", "file", "column", "category", "rule_matched", "matched_records", "non_empty_records",
                  "total_records", "match_rate", "column_name_hint", "negative_hint", "confidence",
                  "masked_examples", "review_status"]


def load_rules(path) -> dict:
    rules = load_json(path)
    for name, cat in rules["categories"].items():
        cat["_hint"] = re.compile(cat["column_hints"], re.I) if cat.get("column_hints") else None
        cat["_neg"] = re.compile(cat["negative_column_hints"], re.I) if cat.get("negative_column_hints") else None
        for p in cat["patterns"]:
            p["_re"] = re.compile(p["regex"])
    rules["_placeholders"] = {p.lower() for p in rules.get("placeholder_values", [])}
    return rules


def _confidence(hint: bool, neg: bool, rate: float, min_rate: float) -> str:
    if neg or (rate < min_rate and not hint):
        return "low"
    if hint and rate >= min_rate:
        return "high"
    return "medium"


def scan_file(path, rules) -> dict:
    """Scan one CSV. Returns findings, per-category record hits and warnings. Never stores raw values."""
    data = read_csv(path)
    min_rate = rules["min_match_rate"]
    findings, hits = [], {}
    for col in data.fieldnames:
        values = [(i, (r.get(col) or "").strip()) for i, r in enumerate(data.rows)]
        values = [(i, v) for i, v in values if v.lower() not in rules["_placeholders"]]
        if not values:
            continue
        for cname, cat in rules["categories"].items():
            hint = bool(cat["_hint"] and cat["_hint"].search(col))
            neg = bool(cat["_neg"] and cat["_neg"].search(col))
            matched, rule_names, example = [], set(), None
            for i, v in values:
                for p in cat["patterns"]:
                    if p["requires_column_hint"] and not hint:
                        continue
                    if p["_re"].match(v):
                        matched.append(i)
                        rule_names.add(p["name"])
                        example = example or v
                        break
            if not matched:
                continue
            rate = len(matched) / len(values)
            if rate < min_rate and not hint:
                continue
            findings.append({
                "file": Path(path).name, "column": col, "category": cname,
                "rule_matched": "|".join(sorted(rule_names)),
                "matched_records": len(matched), "non_empty_records": len(values),
                "total_records": len(data.rows), "match_rate": round(rate, 3),
                "column_name_hint": "Y" if hint else "N", "negative_hint": "Y" if neg else "N",
                "confidence": _confidence(hint, neg, rate, min_rate),
                "masked_examples": " ; ".join(mask_value(cname, v) for _, v in
                                              [x for x in values if x[0] in set(matched[:2])][:2]),
                "review_status": "pending_review",
            })
            hits[(col, cname)] = set(matched)
    return {"file": Path(path).name, "total_records": len(data.rows), "findings": findings,
            "hits": hits, "warnings": data.warnings}


def scan_folder(folder, rules) -> dict:
    """Scan every CSV in a folder. Unreadable files are skipped and reported, not fatal."""
    folder = Path(folder)
    if not folder.is_dir():
        raise DataFileError(f"scan folder not found: {folder}")
    excluded = set(rules.get("scan_exclude", []))
    findings, skipped, warnings, per_file = [], [], [], {}
    for path in sorted(folder.glob("*.csv")):
        if path.name in excluded:
            continue
        try:
            res = scan_file(path, rules)
        except DataFileError as exc:
            log.warning("skipped %s", exc)
            skipped.append({"file": path.name, "reason": str(exc)})
            continue
        warnings += [f"{path.name}: {w}" for w in res["warnings"]]
        findings += res["findings"]
        # records with at least one non-low finding (the "affected records" figure)
        affected = set()
        for f in res["findings"]:
            if f["confidence"] != "low":
                affected |= res["hits"][(f["column"], f["category"])]
        per_file[path.name] = {"total_records": res["total_records"], "affected_records": len(affected)}
    findings.sort(key=lambda f: (f["file"], f["column"], f["category"]))
    for n, f in enumerate(findings, 1):
        f["finding_id"] = f"F-{n:03d}"
    return {"findings": findings, "per_file": per_file, "skipped_files": skipped, "warnings": warnings}


def summarise(scan: dict) -> dict:
    """Roll findings up by category and by file (counts only)."""
    by_cat, by_file = {}, {}
    for f in scan["findings"]:
        if f["confidence"] == "low":
            continue
        c = by_cat.setdefault(f["category"], {"fields": 0, "files": set(), "field_record_matches": 0})
        c["fields"] += 1
        c["files"].add(f["file"])
        c["field_record_matches"] += f["matched_records"]
        by_file.setdefault(f["file"], []).append(f["column"])
    for c in by_cat.values():
        c["files"] = sorted(c["files"])
    return {"by_category": by_cat, "by_file": by_file, "per_file": scan["per_file"],
            "skipped_files": scan["skipped_files"], "warnings": scan["warnings"],
            "total_findings": len(scan["findings"]),
            "actionable_findings": sum(1 for f in scan["findings"] if f["confidence"] != "low"),
            "notice": "Pattern matches indicate possible personal information, not a confirmed classification."}
