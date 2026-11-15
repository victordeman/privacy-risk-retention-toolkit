# Method, rules and assumptions

All data is fictional. Retention periods are **TEST POLICIES**, not legal requirements. Nothing here connects to a production system.

## 1. Discovery rules (`config/discovery_rules.json`)
Pattern matches indicate **possible** personal information. They never confirm a classification; an analyst does (section 3).

| Category | Value patterns | Column-name hint | Negative hint (lowers confidence) |
|---|---|---|---|
| email | `local@domain.tld` | `e_?mail` | - |
| phone | NA formats `+1-448-685-9537`, `(247) 201-8529`, `607-426-5775`; international spaced `+44 9499 685098`; 10-15 plain digits | `phone`, `mobile`, `tel` | - |
| name | two or more capitalised words; a single capitalised word **only** when the column name says it is a name | `first/last/full/customer/contact ... name`, `_name` | `company, org, business, department, job, title, location, campaign` |
| identification_number | `EMP`, `CUST`, `SUP` + digits; `NID`, `TX`, `VAT` + 8 or more alphanumerics | `national_id, tax_id, tax_registration, employee/customer/supplier_id, user_id` | `session, log_id, ticket, agent` |
| ip_address | IPv4, octets 0-255 | `ip` | - |

- Blank values and placeholders (`N/A`, `unknown`, `TBD`, `invalid`, ...) are ignored.
- A column is reported when matches >= 50% of its non-empty values, or when its name hints at the category.
- **Confidence:** *low* = negative hint hit, or rate below 50% without a hint; *high* = hint and rate >= 50%; *medium* = rate >= 50% without a hint.
- Findings are per (file, column, category). The summary counts only medium/high findings; low ones stay in the findings file for review.
- Logs and reports show masked examples only (`j***@example.com`, `41.*.*.*`, `NID*********`).

## 2. Accuracy measurement
Unit = (file, column, category) against `answer_sheet/expected_discoveries.csv` (28 labelled personal-data columns, 8 explicit non-matches).
Correct detections = TP; false positives = findings not labelled personal; missed = labelled columns not found.
Precision = TP / (TP + FP); recall = TP / (TP + missed); F1 is their harmonic mean. Three views are reported: raw rules, medium/high only, and after analyst review.

## 3. Review and validation
`review_decisions.csv` holds one confirm/reject per finding with analyst, date and note. Missed detections go to `missed_detections.csv`; rejected findings generate rule-change suggestions in `rule_improvements.csv`.
`./run.sh review --interactive --analyst "Name"` for a human reviewer. `--simulate` stands in for an analyst using the answer sheet and is **demo only**.

## 4. Retention triggers and date calculation (`config/retention_schedule_config.json`)
Review due date = trigger date + retention years. A 29 Feb trigger rolls to 28 Feb in a non-leap due year. A record is due when due date <= as-of date (2026-11-14; override with `--as-of`).

Order of checks for each record:
1. Trigger blank/placeholder/unparseable: open record -> **Active, no trigger**; any other record -> **Insufficient info** (investigate). Never eligible.
2. Due date after as-of date -> **Not yet due**.
3. Due and `on_hold = Y` -> **On hold (expired)**; excluded from disposal.
4. Due and not on hold -> **Eligible for review**.

"Open" is decided per dataset by `status_column` / `closed_statuses` in the config (an extension to the supplied config). Datasets without a status column (marketing, access logs) always expect a trigger.
Placeholders on an open record (for example `TBD` in `termination_date` on an Active employee) are listed as data-quality flags.

## 5. Risk scoring (`config/risk_scoring.json`)
Likelihood (1-5) x Severity (1-5) = inherent risk; residual risk uses residual likelihood and severity after controls. Bands: 1-4 Low, 5-9 Medium, 10-15 High, 16-25 Critical.
Validation checks: scores equal the product, residual does not exceed inherent, activity exists in the register, owner and valid deadline present, at least five assessments.
Overdue = treatment deadline before the as-of date; "due soon" = within 60 days.

## 6. Sensitivity classification (inventory)
High = identification numbers discovered; Medium = direct identifiers (name, email, phone, IP); Low = none. Systems without a sample use a keyword heuristic on documented categories and need owner confirmation.

## 7. Disposal simulation controls
Proposal contains only eligible, not-on-hold records. Approval needs a named reviewer and records the proposal checksum; a changed proposal is refused. Execution works on a copy in a folder separate from the source, takes a recovery copy first, re-checks holds, writes a log (decision, reviewer, date, result - IDs only), and verifies source hashes before and after. `dispose recover` restores the recovery copy and proves it matches the source.
