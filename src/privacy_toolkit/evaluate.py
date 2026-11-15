"""Measure discovery accuracy and retention outcomes against the labelled answer sheet."""
from __future__ import annotations

import csv
from pathlib import Path

from .common import load_json


def load_truth(path) -> dict:
    pos, neg = set(), set()
    with open(path, newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            key = (r["file"], r["column"], r["category"])
            (pos if r["label"] == "positive" else neg).add(key)
    return {"positive": pos, "negative": neg}


def _metrics(predicted: set, truth: dict) -> dict:
    tp = predicted & truth["positive"]
    fp = predicted - truth["positive"]
    fn = truth["positive"] - predicted
    p = len(tp) / (len(tp) + len(fp)) if predicted else 0.0
    r = len(tp) / len(truth["positive"]) if truth["positive"] else 0.0
    f1 = 2 * p * r / (p + r) if (p + r) else 0.0
    return {"true_positives": len(tp), "false_positives": len(fp), "missed_detections": len(fn),
            "precision": round(p, 3), "recall": round(r, 3), "f1": round(f1, 3),
            "false_positive_detail": sorted(fp), "missed_detail": sorted(fn)}


def discovery_accuracy(findings: list, truth: dict, decisions: dict | None = None) -> dict:
    """Column-level accuracy for three views: raw rules, actionable (non-low), and after analyst review."""
    key = lambda f: (f["file"], f["column"], f["category"])
    out = {"labelled_positive_columns": len(truth["positive"]),
           "raw_rules": _metrics({key(f) for f in findings}, truth),
           "actionable_confidence_medium_or_high": _metrics({key(f) for f in findings if f["confidence"] != "low"}, truth)}
    if decisions:
        confirmed = {key(f) for f in findings if decisions.get(f["finding_id"], {}).get("decision") == "confirmed"}
        out["after_analyst_review"] = _metrics(confirmed, truth)
    explicit = [k for k in truth["negative"]]
    flagged_neg = {key(f): f["confidence"] for f in findings if key(f) in truth["negative"]}
    out["explicit_negatives"] = {"checked": len(explicit),
                                 "flagged_at_all": {f"{k[0]}:{k[1]}": v for k, v in flagged_neg.items()},
                                 "flagged_as_actionable": [f"{k[0]}:{k[1]}" for k, v in flagged_neg.items() if v != "low"]}
    return out


def retention_comparison(actual: dict, expected_path) -> dict:
    """actual: {dataset: {category: n}} from retention.summarise. Compares with the corrected answer sheet."""
    exp = load_json(expected_path)["datasets"]
    rows, ok = [], True
    for ds, e in exp.items():
        a = actual.get(ds, {})
        for cat, n in e.items():
            m = a.get(cat, 0) == n
            ok &= m
            rows.append({"dataset": ds, "category": cat, "expected": n, "actual": a.get(cat, 0), "match": m})
    return {"all_match": ok, "rows": rows}
