"""Controlled disposal simulation: proposal -> approval -> execution on a COPY -> recovery.
The source dataset is never modified. Records on hold are excluded at proposal AND re-checked at execution."""
from __future__ import annotations

import json
import shutil
from datetime import datetime
from pathlib import Path

from .common import DataFileError, hash_tree, read_csv, sha256_file, write_csv, write_json
from .retention import ELIGIBLE

PROPOSAL_FIELDS = ["proposal_id", "dataset", "record_id", "review_due_date", "days_past_due", "on_hold", "proposal_status"]
LOG_FIELDS = ["timestamp", "run_id", "event", "dataset", "record_id", "decision", "reviewer", "decision_date", "execution_result"]


def build_proposal(records, path, proposal_id: str) -> list:
    """Only ELIGIBLE_FOR_REVIEW records with on_hold != Y. Holds, unknown and not-due records can never appear."""
    rows = [{"proposal_id": proposal_id, "dataset": r["dataset"], "record_id": r["record_id"],
             "review_due_date": r["review_due_date"], "days_past_due": r["days_past_due"], "on_hold": r["on_hold"],
             "proposal_status": "PROPOSED"} for r in records if r["category"] == ELIGIBLE and r["on_hold"] != "Y"]
    write_csv(path, PROPOSAL_FIELDS, rows)
    return rows


def approve(proposal_path, approval_path, reviewer, decision_date, decision="APPROVED", rejected_ids=(), comment=""):
    if not reviewer or not reviewer.strip():
        raise ValueError("a named reviewer is required")
    if decision not in ("APPROVED", "REJECTED"):
        raise ValueError("decision must be APPROVED or REJECTED")
    rows = read_csv(proposal_path).rows
    rej = set(rejected_ids)
    rec = {"proposal_id": rows[0]["proposal_id"] if rows else "", "proposal_sha256": sha256_file(proposal_path),
           "decision": decision, "reviewer": reviewer, "decision_date": decision_date, "comment": comment,
           "proposed_count": len(rows), "rejected_record_ids": sorted(rej),
           "approved_count": 0 if decision == "REJECTED" else len([r for r in rows if r["record_id"] not in rej])}
    write_json(approval_path, rec)
    return rec


def _log(rows, run_id, event, **kw):
    rows.append({"timestamp": datetime.now().isoformat(timespec="seconds"), "run_id": run_id, "event": event,
                 "dataset": kw.get("dataset", ""), "record_id": kw.get("record_id", ""), "decision": kw.get("decision", ""),
                 "reviewer": kw.get("reviewer", ""), "decision_date": kw.get("decision_date", ""),
                 "execution_result": kw.get("result", "")})


def execute(source_dir, work_dir, proposal_path, approval_path, log_path, run_id, *, hold_column="on_hold", hold_value="Y",
            id_columns: dict) -> dict:
    """Run the simulated disposal on a fresh copy. Refuses to run without a valid approval."""
    source_dir, work_dir = Path(source_dir).resolve(), Path(work_dir).resolve()
    if work_dir == source_dir or source_dir in work_dir.parents or work_dir in source_dir.parents:
        raise DataFileError("simulation folder must be separate from the source folder")
    if not Path(approval_path).exists():
        raise DataFileError("no approval record: disposal not permitted")
    appr = json.loads(Path(approval_path).read_text(encoding="utf-8"))
    if appr.get("decision") != "APPROVED" or not appr.get("reviewer"):
        raise DataFileError("proposal is not approved by a named reviewer: disposal not permitted")
    if appr["proposal_sha256"] != sha256_file(proposal_path):
        raise DataFileError("proposal changed after approval (checksum mismatch): disposal not permitted")

    before = hash_tree(source_dir)
    copy_dir, recovery_dir = work_dir / "working_copy", work_dir / "recovery_copy"
    for d in (copy_dir, recovery_dir):
        if d.exists():
            shutil.rmtree(d)
    shutil.copytree(source_dir, copy_dir)
    shutil.copytree(source_dir, recovery_dir)          # recovery copy taken BEFORE any deletion
    for p in list(copy_dir.glob("*.csv")) + list(recovery_dir.glob("*.csv")):
        p.chmod(0o644)

    log = []
    _log(log, run_id, "RUN_START", reviewer=appr["reviewer"], decision=appr["decision"], decision_date=appr["decision_date"])
    approved = {(r["dataset"], r["record_id"]) for r in read_csv(proposal_path).rows
                if r["record_id"] not in set(appr["rejected_record_ids"])}
    counts = {"DELETED_IN_COPY": 0, "BLOCKED_ON_HOLD": 0, "NOT_FOUND": 0}
    by_ds = {}
    for ds, rid in sorted(approved):
        by_ds.setdefault(ds, set()).add(rid)
    for ds, ids in by_ds.items():
        data = read_csv(copy_dir / ds)
        idc = id_columns[ds]
        keep, seen = [], set()
        for row in data.rows:
            rid = row[idc]
            if rid in ids:
                seen.add(rid)
                if (row.get(hold_column) or "").strip().upper() == hold_value.upper():   # defence in depth
                    keep.append(row)
                    res = "BLOCKED_ON_HOLD"
                else:
                    res = "DELETED_IN_COPY"
                counts[res] += 1
                _log(log, run_id, "RECORD", dataset=ds, record_id=rid, decision=appr["decision"],
                     reviewer=appr["reviewer"], decision_date=appr["decision_date"], result=res)
            else:
                keep.append(row)
        for rid in sorted(ids - seen):
            counts["NOT_FOUND"] += 1
            _log(log, run_id, "RECORD", dataset=ds, record_id=rid, decision=appr["decision"], reviewer=appr["reviewer"],
                 decision_date=appr["decision_date"], result="NOT_FOUND")
        write_csv(copy_dir / ds, data.fieldnames, keep)
    after = hash_tree(source_dir)
    intact = before == after
    _log(log, run_id, "SOURCE_INTEGRITY_CHECK", result="SOURCE_UNCHANGED" if intact else "SOURCE_MODIFIED")
    _log(log, run_id, "RUN_END", reviewer=appr["reviewer"], result="COMPLETED" if intact else "FAILED")
    write_csv(log_path, LOG_FIELDS, log)
    if not intact:
        raise DataFileError("source dataset hash changed during simulation")
    return {"run_id": run_id, "counts": counts, "source_unchanged": intact, "working_copy": str(copy_dir),
            "recovery_copy": str(recovery_dir)}


def recover(source_dir, work_dir, restore_dir) -> dict:
    """Restore from the recovery copy and prove the result is identical to the original source."""
    recovery_dir = Path(work_dir) / "recovery_copy"
    if not recovery_dir.is_dir():
        raise DataFileError("no recovery copy found")
    restore_dir = Path(restore_dir)
    if restore_dir.exists():
        shutil.rmtree(restore_dir)
    shutil.copytree(recovery_dir, restore_dir)
    src, rec = hash_tree(source_dir), hash_tree(restore_dir)
    rows = {p.name: len(read_csv(p).rows) for p in sorted(restore_dir.glob("*.csv"))}
    return {"identical_to_source": src == rec, "files_checked": len(src), "restored_row_counts": rows,
            "mismatched_files": sorted(k for k in src if src[k] != rec.get(k))}
