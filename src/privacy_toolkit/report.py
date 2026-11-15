"""Management privacy report (HTML). Counts and masked samples only - no full personal data, no free-text values."""
from __future__ import annotations

from collections import Counter
from html import escape as h

from .common import mask_value
from .retention import ACTIVE, CATEGORIES, ELIGIBLE, INSUFFICIENT, NOT_DUE, ON_HOLD

CSS = """body{font-family:Arial,Helvetica,sans-serif;margin:32px auto;max-width:1050px;color:#1b2a3a;line-height:1.45}
h1{color:#14365d}h2{color:#14365d;border-bottom:2px solid #d7e1ec;padding-bottom:4px;margin-top:34px}
table{border-collapse:collapse;width:100%;margin:10px 0;font-size:13px}th{background:#14365d;color:#fff;text-align:left;padding:6px}
td{border-bottom:1px solid #d7e1ec;padding:5px 6px;vertical-align:top}.k{display:flex;gap:12px;flex-wrap:wrap}
.kpi{background:#f2f6fa;border:1px solid #d7e1ec;border-radius:6px;padding:10px 16px;min-width:150px}.kpi b{font-size:22px;display:block}
.note{background:#fff8e1;border-left:4px solid #e0a800;padding:8px 12px;margin:10px 0;font-size:13px}
.ok{color:#1a7f37;font-weight:bold}.bad{color:#b42318;font-weight:bold}small{color:#566}"""


def _table(headers, rows):
    t = "<table><tr>" + "".join(f"<th>{h(str(x))}</th>" for x in headers) + "</tr>"
    for r in rows:
        t += "<tr>" + "".join(f"<td>{c if isinstance(c, _Raw) else h(str(c))}</td>" for c in r) + "</tr>"
    return t + "</table>"


class _Raw(str):
    pass


def build_report(ctx: dict) -> str:
    disc, acc, inv, reg, risk = ctx["discovery_summary"], ctx["accuracy"], ctx["inventory"], ctx["register"], ctx["risk"]
    ret, cmp_, records = ctx["retention_summary"], ctx["retention_comparison"], ctx["retention_records"]
    tot = {c: sum(d[c] for d in ret.values()) for c in CATEGORIES}
    unrev = [r for r in reg if not r.get("last_reviewed")]
    assessed = {r["activity_id"] for r in risk["items"]}
    o = []
    o.append(f"<!doctype html><html><head><meta charset='utf-8'><title>Privacy report</title><style>{CSS}</style></head><body>")
    o.append(f"<h1>Privacy and Data Retention Report</h1><p>As of <b>{h(ctx['as_of'])}</b>. Synthetic demonstration data. "
             "Retention periods are <b>TEST POLICIES</b>, not legal requirements.</p>")
    o.append("<div class='note'>This report is masked: it contains counts, rule names and partially masked samples only. "
             "Record identifiers appear only in the analyst working files (proposal, log), not here.</div>")
    o.append("<div class='k'>" + "".join(f"<div class='kpi'><b>{v}</b>{h(l)}</div>" for l, v in [
        ("datasets scanned", len(disc["per_file"])), ("records scanned", sum(x["total_records"] for x in disc["per_file"].values())),
        ("confirmed PI fields", ctx["confirmed_fields"]), ("unreviewed activities", len(unrev)),
        ("records awaiting disposal decision", tot[ELIGIBLE]), ("records on hold (expired)", tot[ON_HOLD]),
        ("records needing date investigation", tot[INSUFFICIENT])]) + "</div>")

    o.append("<h2>1. Discovered data categories</h2><p>Fields confirmed by an analyst, by category (pending findings of medium/high confidence if no review has been recorded). "
             "<b>Pattern matches indicate possible personal information, not a confirmed classification.</b></p>")
    o.append(_table(["Category", "Fields", "Files", "Field-level record matches"],
                    [(c, v["fields"], ", ".join(v["files"]), v["field_record_matches"]) for c, v in sorted(disc["by_category"].items())]))
    o.append("<p><small>Field-level record matches = sum over fields of records matching, so one person can be counted several times.</small></p>")
    o.append(_table(["File", "Records", "Records with at least one match", "Fields flagged"],
                    [(f, v["total_records"], v["affected_records"], len(disc["by_file"].get(f, []))) for f, v in sorted(disc["per_file"].items())]))
    if disc["skipped_files"]:
        o.append("<p class='bad'>Skipped files: " + h("; ".join(s["reason"] for s in disc["skipped_files"])) + "</p>")

    o.append("<h2>2. Discovery accuracy against the labelled answer sheet</h2>")
    rows = []
    for k, label in [("raw_rules", "Raw rules (all findings)"), ("actionable_confidence_medium_or_high", "Actionable (confidence medium/high)"),
                     ("after_analyst_review", "After analyst review")]:
        if k in acc:
            m = acc[k]
            rows.append((label, m["true_positives"], m["false_positives"], m["missed_detections"], m["precision"], m["recall"], m["f1"]))
    o.append(_table(["View", "Correct detections", "False positives", "Missed", "Precision", "Recall", "F1"], rows))
    o.append("<p><small>Unit = (file, column, category). Precision = correct / (correct + false positives). Recall = correct / (correct + missed). "
             f"Labelled personal-data columns: {acc['labelled_positive_columns']}.</small></p>")
    fps = acc["actionable_confidence_medium_or_high"]["false_positive_detail"]
    if fps:
        o.append("<p>False positives still flagged at medium/high confidence (need analyst rejection): " +
                 h(", ".join(f"{a}:{b}" for a, b, _ in fps)) + "</p>")

    o.append("<h2>3. Data inventory linked to processing activities</h2>")
    o.append(_table(["ID", "Type", "Name", "Records", "Activity", "Owner", "Sensitivity", "Retention rule", "Assessments"],
                    [(r["inventory_id"], r["type"], r["name"], r["record_count"], r["activity_id"], r["responsible_owner"],
                      r["sensitivity"], r["retention_rule_id"], r["assessment_ids"]) for r in inv]))

    o.append("<h2>4. Processing activities awaiting owner review</h2>")
    o.append(f"<p>{len(reg)} activities in the register; <b>{len(unrev)}</b> not yet reviewed; "
             f"<b>{len([r for r in reg if r['activity_id'] not in assessed])}</b> have no completed privacy risk assessment.</p>")
    o.append(_table(["Activity", "Name", "Owner", "Last reviewed", "Risk assessed"],
                    [(r["activity_id"], r["name"], r["owner"], r.get("last_reviewed") or "NOT REVIEWED",
                      "yes" if r["activity_id"] in assessed else "NO") for r in reg]))

    o.append("<h2>5. Privacy risks</h2><p>Method: Likelihood (1-5) x Severity (1-5) = Inherent risk; residual risk uses the likelihood and "
             "severity after controls. Bands: 1-4 Low, 5-9 Medium, 10-15 High, 16-25 Critical.</p>")
    o.append(_table(["ID", "Activity", "Calculation", "Inherent", "Residual", "Owner", "Deadline", "Days left"],
                    [(i["assessment_id"], i["activity_name"], i["calc"], f"{i['inherent']} {i['inherent_band']}",
                      f"{i['residual']} {i['residual_band']}", i["owner"], i["deadline"], i["days_to_deadline"]) for i in risk["items"]]))
    hi = risk["high_or_critical_inherent"]
    o.append(f"<p>High or Critical inherent risks: <b>{len(hi)}</b>. High or Critical residual risks: <b>{len(risk['high_or_critical_residual'])}</b>. "
             f"Overdue treatment actions: <b>{len(risk['overdue_actions'])}</b>. Due within the next {ctx['due_soon_days']} days: <b>{len(risk['due_soon'])}</b>.</p>")

    o.append("<h2>6. Retention review (test policies)</h2>")
    o.append(_table(["Dataset", "Eligible for review", "On hold (expired)", "Insufficient info", "Active, no trigger", "Not yet due"],
                    [(d, v[ELIGIBLE], v[ON_HOLD], v[INSUFFICIENT], v[ACTIVE], v[NOT_DUE]) for d, v in ret.items()] +
                    [("TOTAL", tot[ELIGIBLE], tot[ON_HOLD], tot[INSUFFICIENT], tot[ACTIVE], tot[NOT_DUE])]))
    o.append("<p>Calculation: review due date = trigger date + retention years (29 Feb rolls to 28 Feb). A record is eligible when due date "
             f"&lt;= {h(ctx['as_of'])} and it is not on hold. Blank or invalid trigger dates are flagged for investigation, never treated as permission to delete.</p>")
    o.append("<p>Comparison with the corrected answer sheet: " +
             ("<span class='ok'>all %d cells match</span>" % len(cmp_["rows"]) if cmp_["all_match"] else "<span class='bad'>MISMATCH - see retention_comparison.csv</span>") + "</p>")
    overdue = sorted([int(r["days_past_due"]) for r in records if r["category"] == ELIGIBLE])
    if overdue:
        o.append(f"<p><b>Overdue actions:</b> {len(overdue)} records are past their review date; oldest is {max(overdue)} days overdue, median {overdue[len(overdue)//2]} days.</p>")
    hold_reasons = Counter(r["hold_reason"] or "(no reason recorded)" for r in records if r["category"] == ON_HOLD)
    o.append("<p>Holds blocking disposal: " + h(", ".join(f"{k} x{v}" for k, v in hold_reasons.most_common())) + "</p>")
    flags = [r for r in records if r["data_quality_flag"]]
    o.append(f"<p>Data-quality flags (informational): {len(flags)} records have a placeholder or inconsistent trigger on an open record.</p>")

    o.append("<h2>7. Records awaiting retention decisions</h2>")
    p = ctx["proposal"]
    o.append(f"<p>Disposal proposal: <b>{p['proposed']}</b> records proposed (holds and unknown dates excluded). "
             f"Approval: <b>{h(p['approval_status'])}</b>.</p>")
    if ctx.get("disposal"):
        d = ctx["disposal"]
        o.append(f"<p>Simulation on a separate copy: {d['counts']['DELETED_IN_COPY']} deleted in copy, {d['counts']['BLOCKED_ON_HOLD']} blocked on hold. "
                 f"Source unchanged: <b>{d['source_unchanged']}</b>. Recovery identical to source: <b>{ctx['recovery']['identical_to_source']}</b>.</p>")

    o.append("<h2>8. Limitations and human review</h2><ul>"
             "<li>Rules detect possible personal information by pattern and column name; they cannot confirm that a value identifies a person.</li>"
             "<li>Free text inside a field (for example ticket content) is not inspected; unusual formats can be missed.</li>"
             "<li>Business categories with two capitalised words (for example supplier categories) can look like names and need analyst rejection.</li>"
             "<li>Sensitivity for systems without sample data is a heuristic and needs the owner's confirmation.</li>"
             "<li>Retention rules are test policies. Real deployments need legal review and approval before any real disposal.</li></ul>")
    o.append("</body></html>")
    return "".join(o)
