"""Command line interface. Run: python -m privacy_toolkit <command> [options]  (see docs/USER_GUIDE.md)."""
from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import date
from pathlib import Path

from . import discovery, disposal, evaluate, inventory, register, report, retention, review, risk
from .common import DataFileError, Paths, load_json, parse_date, read_csv, write_csv, write_json, hash_tree

SIM_ANALYST = "Demo Analyst (simulated)"
SIM_REVIEWER = "Demo Reviewer (simulated)"


def _ctx(root):
    P = Paths(root)
    return P, retention.load_config(P.config / "retention_schedule_config.json")


def _out(P, name):
    return P.output / name


def _load_findings(P):
    return read_csv(_out(P, "discovery_findings.csv")).rows


def cmd_discover(P, cfg, a):
    rules = discovery.load_rules(P.config / "discovery_rules.json")
    scan = discovery.scan_folder(a.folder or P.source, rules)
    summ = discovery.summarise(scan)
    write_csv(_out(P, "discovery_findings.csv"), discovery.FINDING_FIELDS, scan["findings"])
    write_json(_out(P, "discovery_summary.json"), summ)
    print(f"Scanned {len(scan['per_file'])} files, {summ['total_findings']} findings "
          f"({summ['actionable_findings']} medium/high). Skipped: {len(scan['skipped_files'])}.")
    print(review.NOTICE)
    return scan


def cmd_review(P, cfg, a):
    findings = _load_findings(P)
    truth = evaluate.load_truth(P.answer / "expected_discoveries.csv")
    dpath = _out(P, "review_decisions.csv")
    when = cfg["as_of_date"]
    if a.simulate:
        dec = review.simulate_analyst(findings, truth, SIM_ANALYST, when)
        review.save_decisions(dpath, dec)
        print(f"Simulated analyst reviewed {len(dec)} findings (DEMO ONLY - stands in for a human).")
    elif a.interactive:
        for f in findings:
            if f["confidence"] == "low" or True:
                print(f"{f['finding_id']} {f['file']}:{f['column']} [{f['category']}] conf={f['confidence']} "
                      f"rate={f['match_rate']} examples={f['masked_examples']}")
                ans = input("  (c)onfirm / (r)eject / (s)kip: ").strip().lower()
                if ans in ("c", "r"):
                    note = input("  note: ")
                    review.record_decision(dpath, f, "confirmed" if ans == "c" else "rejected", a.analyst, when, note)
    else:
        print("Use --simulate (demo) or --interactive.")
        return
    dec = review.load_decisions(dpath)
    missed = review.find_missed(findings, truth)
    write_csv(_out(P, "missed_detections.csv"), review.MISSED_FIELDS,
              [{"file": f, "column": c, "category": k, "analyst": SIM_ANALYST, "review_date": when,
                "note": "expected by answer sheet but not detected"} for f, c, k in missed])
    for trig, change in review.suggest_improvements(dec):
        review.log_improvement(_out(P, "rule_improvements.csv"), when, SIM_ANALYST, trig, change, "proposed")
    print(f"Missed detections: {len(missed)}; rejected (false positives): "
          f"{sum(1 for d in dec.values() if d['decision'] == 'rejected')}")


def cmd_evaluate(P, cfg, a):
    findings = _load_findings(P)
    truth = evaluate.load_truth(P.answer / "expected_discoveries.csv")
    dec = review.load_decisions(_out(P, "review_decisions.csv"))
    acc = evaluate.discovery_accuracy(findings, truth, dec)
    write_json(_out(P, "discovery_accuracy.json"), acc)
    for k in ("raw_rules", "actionable_confidence_medium_or_high", "after_analyst_review"):
        if k in acc:
            m = acc[k]
            print(f"{k:42s} TP={m['true_positives']} FP={m['false_positives']} missed={m['missed_detections']} "
                  f"P={m['precision']} R={m['recall']} F1={m['f1']}")
    return acc


def cmd_register(P, cfg, a):
    work, hist = _out(P, "processing_register.csv"), _out(P, "processing_register_history.csv")
    register.init_register(P.registers / "processing_activities_register.csv", work, hist)
    if a.activity:
        changes = dict(x.split("=", 1) for x in (a.change or []))
        row = register.review_activity(work, hist, a.activity, a.reviewer, a.date or cfg["as_of_date"], a.reason or "Owner review", changes)
        print(f"{a.activity} reviewed by {a.reviewer}; now version {row['version']}")
    else:
        rows = register.load(work)
        print(f"{len(rows)} activities, {len(register.unreviewed(rows))} unreviewed")


def _assess_file(P):
    w = _out(P, "privacy_risk_assessments.csv")
    if not w.exists():
        write_csv(w, risk.FIELDS, read_csv(P.registers / "privacy_risk_assessments.csv").rows)
    return w


def cmd_assess(P, cfg, a):
    scoring = load_json(P.config / "risk_scoring.json")
    w = _assess_file(P)
    rows = read_csv(w).rows
    reg_rows = read_csv(P.registers / "processing_activities_register.csv").rows
    if a.activity:
        act = next(r for r in reg_rows if r["activity_id"] == a.activity)
        rec = risk.new_assessment(rows, scoring, activity_id=a.activity, activity_name=act["name"], assessor=a.assessor,
            assessment_date=cfg["as_of_date"], harm=a.harm, likelihood=a.likelihood, severity=a.severity,
            safeguards=a.safeguards, measures=a.measures, residual_likelihood=a.residual_likelihood,
            residual_severity=a.residual_severity, owner=a.owner or act["owner"], deadline=a.deadline)
        rows.append(rec)
        write_csv(w, risk.FIELDS, rows)
        print(f"Recorded {rec['assessment_id']}: inherent {rec['inherent_risk_score']} "
              f"({risk.band(rec['inherent_risk_score'], scoring)}), residual {rec['residual_risk_score']} "
              f"({risk.band(rec['residual_risk_score'], scoring)})")
    problems = risk.validate(rows, {r["activity_id"] for r in reg_rows}, scoring)
    print("Assessment validation:", "OK" if not problems else problems)


def cmd_inventory(P, cfg, a):
    rules = discovery.load_rules(P.config / "discovery_rules.json")
    summ = load_json(_out(P, "discovery_summary.json"))
    reg_rows = read_csv(P.registers / "processing_activities_register.csv").rows
    asm = read_csv(_assess_file(P)).rows
    rows = inventory.build_inventory(P.source, reg_rows, asm, cfg["rules"], summ, rules)
    inventory.write_inventory(_out(P, "data_inventory.csv"), rows)
    print(f"Inventory: {len(rows)} entries ({sum(r['type']=='file' for r in rows)} files, {sum(r['type']=='system' for r in rows)} systems)")


def cmd_retention(P, cfg, a):
    as_of = parse_date(a.as_of) if a.as_of else None
    res = retention.run_review(P.source, cfg, as_of)
    retention.write_review(_out(P, "retention_review.csv"), res["records"])
    summ = retention.summarise(res["records"])
    write_json(_out(P, "retention_summary.json"), {"as_of": res["as_of"], "errors": res["errors"], "datasets": summ})
    for e in res["errors"]:
        print("ERROR:", e)
    cmp_ = evaluate.retention_comparison(summ, P.answer / "expected_retention_outcomes.json")
    write_csv(_out(P, "retention_comparison.csv"), ["dataset", "category", "expected", "actual", "match"], cmp_["rows"])
    print("Retention vs corrected answer sheet:", "ALL MATCH" if cmp_["all_match"] else "MISMATCH")
    return cmp_


def cmd_dispose(P, cfg, a):
    work = P.output / "disposal_simulation"
    prop, appr = _out(P, "disposal_proposal.csv"), _out(P, "disposal_approval.json")
    idc = {r["dataset"]: r["id_column"] for r in cfg["rules"]}
    recs = read_csv(_out(P, "retention_review.csv")).rows
    if a.step == "propose":
        rows = disposal.build_proposal(recs, prop, a.proposal_id or "DP-2026-001")
        print(f"Proposal {rows[0]['proposal_id'] if rows else ''}: {len(rows)} records; holds excluded.")
    elif a.step == "approve":
        r = disposal.approve(prop, appr, a.reviewer, a.date or cfg["as_of_date"], a.decision, a.reject or [], a.comment or "")
        print(f"{r['decision']} by {r['reviewer']} on {r['decision_date']}: {r['approved_count']} records")
    elif a.step == "run":
        r = disposal.execute(P.source, work, prop, appr, _out(P, "simulation_log.csv"), a.run_id or "RUN-001",
                             hold_column=cfg["hold_column"], hold_value=cfg["hold_value"], id_columns=idc)
        write_json(_out(P, "disposal_result.json"), r)
        print(r)
    elif a.step == "recover":
        r = disposal.recover(P.source, work, work / "restored")
        write_json(_out(P, "recovery_result.json"), r)
        print(r)


def cmd_report(P, cfg, a):
    scoring = load_json(P.config / "risk_scoring.json")
    asm = read_csv(_assess_file(P)).rows
    as_of = cfg["_as_of"]
    dec = review.load_decisions(_out(P, "review_decisions.csv"))
    findings = _load_findings(P)
    rsum = load_json(_out(P, "retention_summary.json"))["datasets"]
    cmp_ = evaluate.retention_comparison(rsum, P.answer / "expected_retention_outcomes.json")
    p = read_csv(_out(P, "disposal_proposal.csv")).rows if _out(P, "disposal_proposal.csv").exists() else []
    ap = _out(P, "disposal_approval.json")
    dsum = load_json(_out(P, "discovery_summary.json"))
    if dec:   # after analyst review, report CONFIRMED fields only
        conf = [f for f in findings if dec.get(f["finding_id"], {}).get("decision") == "confirmed"]
        by_cat, by_file = {}, {}
        for f in conf:
            c = by_cat.setdefault(f["category"], {"fields": 0, "files": set(), "field_record_matches": 0})
            c["fields"] += 1
            c["files"].add(f["file"])
            c["field_record_matches"] += int(f["matched_records"])
            by_file.setdefault(f["file"], []).append(f["column"])
        for c in by_cat.values():
            c["files"] = sorted(c["files"])
        dsum.update({"by_category": by_cat, "by_file": by_file})
    ctx = {"as_of": cfg["as_of_date"], "discovery_summary": dsum,
           "accuracy": load_json(_out(P, "discovery_accuracy.json")),
           "inventory": read_csv(_out(P, "data_inventory.csv")).rows,
           "register": register.load(_out(P, "processing_register.csv")),
           "risk": risk.summarise(asm, scoring, as_of), "due_soon_days": scoring["due_soon_days"],
           "retention_summary": rsum, "retention_comparison": cmp_,
           "retention_records": read_csv(_out(P, "retention_review.csv")).rows,
           "confirmed_fields": sum(1 for d in dec.values() if d["decision"] == "confirmed"),
           "proposal": {"proposed": len(p), "approval_status": load_json(ap)["decision"] if ap.exists() else "PENDING REVIEWER APPROVAL"},
           "disposal": load_json(_out(P, "disposal_result.json")) if _out(P, "disposal_result.json").exists() else None,
           "recovery": load_json(_out(P, "recovery_result.json")) if _out(P, "recovery_result.json").exists() else None}
    html = report.build_report(ctx)
    _out(P, "management_report.html").write_text(html, encoding="utf-8")
    print("Report written:", _out(P, "management_report.html"))


def cmd_demo(P, cfg, a):
    """Full end-to-end run. Reviewer/analyst actions are SIMULATED and labelled as such."""
    src_before = hash_tree(P.source)
    when = cfg["as_of_date"]
    ns = argparse.Namespace
    print("== 1 Discovery"); cmd_discover(P, cfg, ns(folder=None))
    print("== 2 Analyst review (simulated)"); cmd_review(P, cfg, ns(simulate=True, interactive=False, analyst=SIM_ANALYST))
    print("== 3 Accuracy vs answer sheet"); cmd_evaluate(P, cfg, ns())
    print("== 4 Processing register owner reviews (simulated)")
    work, hist = _out(P, "processing_register.csv"), _out(P, "processing_register_history.csv")
    for f in (work, hist):
        f.unlink(missing_ok=True)
    cmd_register(P, cfg, ns(activity="PA-001", reviewer="HR Director (simulated)", date=when, reason="Annual owner review: no change", change=None))
    cmd_register(P, cfg, ns(activity="PA-002", reviewer="Head of Customer Success (simulated)", date=when,
                            reason="Owner review: support platform added as recipient",
                            change=["recipients=CRM, billing system, support platform"]))
    cmd_register(P, cfg, ns(activity=None))
    print("== 5 Privacy risk assessment (new, simulated assessor)")
    _out(P, "privacy_risk_assessments.csv").unlink(missing_ok=True)
    cmd_assess(P, cfg, ns(activity="PA-003", assessor="Privacy Analyst (simulated)",
        harm="Supplier contact details and tax registrations disclosed to unauthorised parties could enable phishing or business-identity fraud",
        likelihood=3, severity=3, safeguards="Access limited to Finance and Legal, ERP role-based access",
        measures="Mask contact details in exports; quarterly access review; purge contacts at contract end + 7 years",
        residual_likelihood=2, residual_severity=2, owner=None, deadline="2027-03-31"))
    print("== 6 Inventory"); cmd_inventory(P, cfg, ns())
    print("== 7 Retention review"); cmd_retention(P, cfg, ns(as_of=None))
    print("== 8 Disposal: propose / approve / run / recover")
    cmd_dispose(P, cfg, ns(step="propose", proposal_id="DP-2026-001"))
    cmd_dispose(P, cfg, ns(step="approve", reviewer=SIM_REVIEWER, date=when, decision="APPROVED", reject=[], comment="Simulation approval for demonstration"))
    cmd_dispose(P, cfg, ns(step="run", run_id="RUN-001"))
    cmd_dispose(P, cfg, ns(step="recover"))
    print("== 9 Report"); cmd_report(P, cfg, ns())
    unchanged = hash_tree(P.source) == src_before
    print("Source CSVs unchanged:", unchanged)
    if not unchanged:
        sys.exit(2)


def main(argv=None):
    ap = argparse.ArgumentParser(prog="privacy_toolkit", description=__doc__)
    ap.add_argument("--root", default=".", help="project root (default: current folder)")
    ap.add_argument("-v", "--verbose", action="store_true")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("discover"); s.add_argument("--folder"); s.set_defaults(f=cmd_discover)
    s = sub.add_parser("review"); s.add_argument("--simulate", action="store_true"); s.add_argument("--interactive", action="store_true")
    s.add_argument("--analyst", default="analyst"); s.set_defaults(f=cmd_review)
    sub.add_parser("evaluate").set_defaults(f=cmd_evaluate)
    s = sub.add_parser("register"); s.add_argument("--activity"); s.add_argument("--reviewer", default="")
    s.add_argument("--date"); s.add_argument("--reason"); s.add_argument("--change", action="append", help="field=new value"); s.set_defaults(f=cmd_register)
    s = sub.add_parser("assess"); s.add_argument("--activity"); s.add_argument("--assessor", default="")
    s.add_argument("--harm", default=""); s.add_argument("--likelihood", type=int); s.add_argument("--severity", type=int)
    s.add_argument("--safeguards", default=""); s.add_argument("--measures", default="")
    s.add_argument("--residual-likelihood", type=int, dest="residual_likelihood"); s.add_argument("--residual-severity", type=int, dest="residual_severity")
    s.add_argument("--owner"); s.add_argument("--deadline"); s.set_defaults(f=cmd_assess)
    sub.add_parser("inventory").set_defaults(f=cmd_inventory)
    s = sub.add_parser("retention"); s.add_argument("--as-of", dest="as_of"); s.set_defaults(f=cmd_retention)
    s = sub.add_parser("dispose"); s.add_argument("step", choices=["propose", "approve", "run", "recover"])
    s.add_argument("--proposal-id"); s.add_argument("--reviewer", default=""); s.add_argument("--date")
    s.add_argument("--decision", default="APPROVED"); s.add_argument("--reject", nargs="*"); s.add_argument("--comment")
    s.add_argument("--run-id"); s.set_defaults(f=cmd_dispose)
    sub.add_parser("report").set_defaults(f=cmd_report)
    sub.add_parser("demo").set_defaults(f=cmd_demo)
    a = ap.parse_args(argv)
    logging.basicConfig(level=logging.INFO if a.verbose else logging.WARNING, format="%(levelname)s %(message)s")
    try:
        P, cfg = _ctx(a.root)
        a.f(P, cfg, a)
    except (DataFileError, ValueError, KeyError, FileNotFoundError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
