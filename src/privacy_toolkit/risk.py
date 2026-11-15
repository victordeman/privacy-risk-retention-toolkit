"""Privacy risk assessment: scoring, validation, recording and summary."""
from __future__ import annotations

from datetime import date

from .common import parse_date, read_csv, write_csv

FIELDS = ["assessment_id", "activity_id", "activity_name", "assessor", "assessment_date", "harm_description",
          "likelihood", "severity", "inherent_risk_score", "existing_safeguards", "additional_measures",
          "residual_likelihood", "residual_severity", "residual_risk_score", "risk_owner", "treatment_deadline",
          "status", "scoring_method"]


def score(likelihood: int, severity: int) -> int:
    for v in (likelihood, severity):
        if not isinstance(v, int) or not 1 <= v <= 5:
            raise ValueError("likelihood and severity must be integers 1-5")
    return likelihood * severity


def band(value: int, scoring: dict) -> str:
    for b in scoring["bands"]:
        if b["min"] <= value <= b["max"]:
            return b["name"]
    raise ValueError(f"score {value} outside defined bands")


def validate(rows, register_ids, scoring) -> list:
    """Return a list of problems (empty = consistent)."""
    problems = []
    for r in rows:
        aid = r["assessment_id"]
        try:
            li, sv, rl, rs = (int(r[k]) for k in ("likelihood", "severity", "residual_likelihood", "residual_severity"))
            if score(li, sv) != int(r["inherent_risk_score"]):
                problems.append(f"{aid}: inherent score {r['inherent_risk_score']} != {li}x{sv}")
            if score(rl, rs) != int(r["residual_risk_score"]):
                problems.append(f"{aid}: residual score {r['residual_risk_score']} != {rl}x{rs}")
            if int(r["residual_risk_score"]) > int(r["inherent_risk_score"]):
                problems.append(f"{aid}: residual risk exceeds inherent risk")
        except (ValueError, KeyError) as exc:
            problems.append(f"{aid}: invalid score fields ({exc})")
        if r["activity_id"] not in register_ids:
            problems.append(f"{aid}: activity {r['activity_id']} not in register")
        if not r.get("risk_owner"):
            problems.append(f"{aid}: no risk owner")
        if parse_date(r.get("treatment_deadline", "")) is None:
            problems.append(f"{aid}: invalid treatment deadline")
    if len(rows) < scoring["min_assessments"]:
        problems.append(f"only {len(rows)} assessments; at least {scoring['min_assessments']} required")
    return problems


def next_id(rows) -> str:
    n = max((int(r["assessment_id"].split("-")[1]) for r in rows), default=0) + 1
    return f"PRA-{n:03d}"


def new_assessment(rows, scoring, *, activity_id, activity_name, assessor, assessment_date, harm, likelihood, severity,
                   safeguards, measures, residual_likelihood, residual_severity, owner, deadline) -> dict:
    inh, res = score(likelihood, severity), score(residual_likelihood, residual_severity)
    if res > inh:
        raise ValueError("residual risk cannot exceed inherent risk")
    if not measures.strip():
        raise ValueError("a mitigation (additional measure) must be recorded")
    if parse_date(deadline) is None:
        raise ValueError("treatment deadline must be YYYY-MM-DD")
    return {"assessment_id": next_id(rows), "activity_id": activity_id, "activity_name": activity_name,
            "assessor": assessor, "assessment_date": assessment_date, "harm_description": harm,
            "likelihood": likelihood, "severity": severity, "inherent_risk_score": inh,
            "existing_safeguards": safeguards, "additional_measures": measures,
            "residual_likelihood": residual_likelihood, "residual_severity": residual_severity,
            "residual_risk_score": res, "risk_owner": owner, "treatment_deadline": deadline,
            "status": "Completed", "scoring_method": scoring["method"] + " Thresholds: " +
            ", ".join(f"{b['min']}-{b['max']} {b['name']}" for b in scoring["bands"])}


def summarise(rows, scoring, as_of: date) -> dict:
    items = []
    for r in rows:
        inh, res = int(r["inherent_risk_score"]), int(r["residual_risk_score"])
        dl = parse_date(r["treatment_deadline"])
        items.append({"assessment_id": r["assessment_id"], "activity_id": r["activity_id"], "activity_name": r["activity_name"],
                      "inherent": inh, "inherent_band": band(inh, scoring), "residual": res, "residual_band": band(res, scoring),
                      "owner": r["risk_owner"], "deadline": r["treatment_deadline"],
                      "days_to_deadline": (dl - as_of).days if dl else None, "status": r["status"],
                      "calc": f"{r['likelihood']} x {r['severity']} = {inh} ; residual {r['residual_likelihood']} x {r['residual_severity']} = {res}"})
    return {"items": items,
            "high_or_critical_inherent": [i for i in items if i["inherent_band"] in ("High", "Critical")],
            "high_or_critical_residual": [i for i in items if i["residual_band"] in ("High", "Critical")],
            "overdue_actions": [i for i in items if i["days_to_deadline"] is not None and i["days_to_deadline"] < 0],
            "due_soon": [i for i in items if i["days_to_deadline"] is not None and 0 <= i["days_to_deadline"] <= scoring["due_soon_days"]]}
