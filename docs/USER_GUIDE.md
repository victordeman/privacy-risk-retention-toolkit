# User guide

Run everything from the project folder. `./run.sh <command>` (or `PYTHONPATH=src python3 -m privacy_toolkit --root . <command>`).

## One-shot demonstration
`./run.sh demo` runs all steps and writes to `output/`. Analyst and reviewer actions in the demo are **simulated** and labelled as such. Run the individual commands below for a real review.

## Step by step
| Step | Command | Result |
|---|---|---|
| 1 Scan | `discover [--folder PATH]` | `discovery_findings.csv`, `discovery_summary.json` (masked) |
| 2 Review | `review --interactive --analyst "Your Name"` | `review_decisions.csv` (confirm/reject + note), `missed_detections.csv`, `rule_improvements.csv` |
| 3 Accuracy | `evaluate` | correct / false positive / missed, precision, recall (`discovery_accuracy.json`) |
| 4 Register | `register --activity PA-002 --reviewer "Owner" --reason "..." --change "recipients=..."` | `processing_register.csv` + `processing_register_history.csv` (old/new values) |
| 5 Risk | `assess --activity PA-003 --assessor "Name" --harm "..." --likelihood 3 --severity 3 --safeguards "..." --measures "..." --residual-likelihood 2 --residual-severity 2 --deadline 2027-03-31` | new assessment with calculated scores; all assessments validated |
| 6 Inventory | `inventory` | `data_inventory.csv` linking dataset - activity - owner - assessment - retention rule |
| 7 Retention | `retention [--as-of YYYY-MM-DD]` | `retention_review.csv`, `retention_summary.json`, `retention_comparison.csv` (vs corrected answer sheet) |
| 8a Propose | `dispose propose` | `disposal_proposal.csv` (eligible, not on hold only) |
| 8b Approve | `dispose approve --reviewer "Name" [--reject ID ...]` | `disposal_approval.json` (reviewer, date, proposal checksum) |
| 8c Run | `dispose run` | simulation on a **copy** in `output/disposal_simulation/`, `simulation_log.csv`, source hash check |
| 8d Recover | `dispose recover` | restores the recovery copy and proves it equals the source |
| 9 Report | `report` | `management_report.html` (masked) |

## Changing the rules
- Retention years, trigger columns, hold column, invalid-date tokens, as-of date: `config/retention_schedule_config.json`.
- Patterns, hints, minimum match rate: `config/discovery_rules.json`.
- Risk bands and scales: `config/risk_scoring.json`.
No code change is needed (there is a test for this).

## Safety rules built in
- Source CSVs are never written to; every run verifies their SHA-256 hashes.
- Disposal refuses to run without an approval record from a named reviewer, or if the proposal changed after approval, or if the simulation folder is inside the source folder.
- Records with `on_hold = Y` are excluded from the proposal and blocked again at execution.
- Missing or invalid trigger dates are flagged for investigation; they are never treated as permission to delete.
- Unreadable files (empty, binary, wrong encoding, duplicate headers) are skipped and reported; ragged rows are skipped with a warning.
- Logs and reports contain masked examples and counts, not full personal data.
