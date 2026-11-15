# Labelled Answer Sheet - CORRECTED (retention outcomes)

Corrects Section 4 of `LABELED_ANSWER_SHEET_ORIGINAL.md`. Sections 1-3, 5-7 of the original are unchanged and still apply.
Machine-readable version: `expected_retention_outcomes.json`. Discovery ground truth: `expected_discoveries.csv`.

**As-of date:** 2026-11-14. All retention periods are TEST POLICIES, not legal requirements.

## What was wrong in the original Section 4

The original columns did not add up to the record counts (for example employees: 2 + 2 + 0 + 47 = 51, but the file has 70 records).

1. Its "Still active / not yet eligible" column was really the number of **blank or placeholder trigger dates on open records**. Records with a valid trigger date whose retention period has not yet expired were left out of every column.
2. Marketing was wrong: it listed 4 invalid and 40 active. The file has **9** blank or invalid trigger dates (7 blank, 1 `invalid`, 1 `unknown`) and **18** records that are not yet due.
3. Access logs had no "not yet due" figure (21).

The eligible (104) and on-hold (12) totals in the original were correct and are unchanged.

## Corrected outcomes (every row sums to the dataset record count)

| Dataset | Eligible for review (expired, not on hold) | On hold AND expired (exclude) | Insufficient info (investigate) | Active, no trigger yet (not eligible) | Not yet due | Total |
|---|---|---|---|---|---|---|
| employees | 2 | 2 | 0 | 47 | 19 | 70 |
| customers | 5 | 1 | 0 | 70 | 14 | 90 |
| suppliers | 1 | 0 | 0 | 3 | 36 | 40 |
| support_tickets | 22 | 2 | 0 | 23 | 33 | 80 |
| marketing_contacts | 29 | 4 | 9 | 0 | 18 | 60 |
| access_logs | 45 | 3 | 1 | 0 | 21 | 70 |
| **Totals** | **104** | **12** | **10** | **143** | **141** | **410** |

## Category definitions

- **Eligible for review**: valid trigger date, trigger + retention years <= 2026-11-14, `on_hold` is not `Y`.
- **On hold AND expired**: retention expired but `on_hold = Y`. Shown in the review report, never in a disposal proposal.
- **Insufficient information**: the trigger date is blank or a placeholder (`invalid`, `N/A`, `unknown`, `TBD`, `pending`, `NULL`, `0000-00-00`, `malformed`, `ongoing`, `TBC`, `open`, `invalid-date`) on a record that should have one: a terminated/closed/ended record, any marketing contact, or any access log. Flag for investigation; never treat as permission to delete.
- **Active, no trigger yet**: blank or placeholder trigger on an *open* record (Active employee, customer or supplier; Open ticket). Not eligible. Placeholder text on an open record (for example `N/A`, `TBD`, `unknown`, `pending`, `TBC`) is reported as a data-quality flag.
- **Not yet due**: valid trigger date but the retention period has not yet expired.

Note: 4 datasets have 0 insufficient-information records because every blank or invalid trigger belongs to an open record.
