# Labelled Answer Sheet
## Privacy Risk Assessment and Data Retention Automation Toolkit
### Synthetic Demonstration Data – Expected Outcomes

**Generated:** November 2026  
**Purpose:** Evaluation reference for the toolkit. All data is fictional.  
**Retention periods below are TEST POLICIES for demonstration only – not legal requirements.**

---

## 1. Dataset Inventory

| File | Records | Primary PII Fields | Retention Trigger Column | Test Retention Period |
|------|---------|-------------------|--------------------------|-----------------------|
| employees.csv | 70 | full_name, email, phone, national_id | termination_date | 7 years after termination |
| customers.csv | 90 | first_name, last_name, email, phone, tax_id | account_closed_date | 5 years after closure |
| suppliers.csv | 40 | contact_first_name, contact_last_name, contact_email, contact_phone, tax_registration | contract_end_date | 7 years after contract end |
| support_tickets.csv | 80 | customer_name, customer_email, customer_phone | closed_date | 3 years after ticket close |
| marketing_contacts.csv | 60 | first_name, last_name, email, phone | retention_trigger_date | 2 years after trigger |
| access_logs.csv | 70 | user_id (when employee), ip_address | access_timestamp | 1 year after access |
| **Total** | **410** | | | |

Supporting files:
- processing_activities_register.csv (12 activities)
- privacy_risk_assessments.csv (6 completed assessments)

---

## 2. Discovery Rules – Expected Matches & Non-Matches

### Rules the toolkit should implement (documented patterns)

| Category | Pattern / Rule | Expected True Positives | Expected False Positives / Non-Matches |
|----------|----------------|-------------------------|----------------------------------------|
| **Email** | Contains `@` and a domain (e.g. `.com`, `.org`, `.net`, `.io`) | Almost all `email`, `contact_email`, `customer_email` fields | Rare; some systems may flag product codes if overly broad |
| **Phone** | Digits with separators, country codes, or 10+ consecutive digits | `phone`, `contact_phone`, `customer_phone` fields | Bare numeric fields that are not phones (e.g. some `session_id` fragments, pure IDs) |
| **Name** | Two or more capitalised words, or first + last name columns | `full_name`, `first_name`+`last_name`, `customer_name`, `contact_*_name` | Company names in `company_name` (suppliers), department names, job titles |
| **Identification number** | Alphanumeric codes with prefixes (EMP, NID, TX, VAT, CUST, etc.) or long digit strings | `employee_id`, `national_id`, `customer_id`, `tax_id`, `tax_registration`, `supplier_id` | `session_id`, `log_id`, `ticket_id`, `agent_id` (operational IDs, not personal) |
| **IP Address** | Dotted decimal (IPv4) | `ip_address` in access_logs | None expected if pattern is specific |

### Explicit test cases to evaluate

**Should match (true positives):**
- Any row containing a realistic email address
- Any row containing a formatted phone number
- `national_id`, `tax_id`, `tax_registration` columns
- Combined first + last name fields

**Should NOT match (or should be treated as lower confidence):**
- `company_name` values (e.g. “Apex Solutions Ltd”) – business entity, not individual
- Pure operational IDs (`LOG6000`, `TKT4000`, `SESS…`) when not linked to a person
- Department names, job titles, status values (“Active”, “Terminated”)
- Empty or placeholder strings (“”, “N/A”, “unknown”, “TBD”, “invalid”)

**Notes for analysts:**
- Pattern matches indicate *possible* personal information only.
- Confirmation requires human review (Detection Review and Validation step).
- Some fields intentionally contain mixed or partial data to test false-positive handling.

---

## 3. Retention Review Rules (TEST POLICIES)

| Dataset | Trigger Field | Retention Period | Review Due When | Special Rules |
|---------|---------------|------------------|-----------------|---------------|
| employees | termination_date | 7 years | termination_date + 7 years ≤ TODAY (2026-11-14) | Active employees (blank termination) = not eligible |
| customers | account_closed_date | 5 years | account_closed_date + 5 years ≤ TODAY | Active customers = not eligible |
| suppliers | contract_end_date | 7 years | contract_end_date + 7 years ≤ TODAY | Active contracts = not eligible |
| support_tickets | closed_date | 3 years | closed_date + 3 years ≤ TODAY | Open tickets = not eligible |
| marketing_contacts | retention_trigger_date | 2 years | retention_trigger_date + 2 years ≤ TODAY | |
| access_logs | access_timestamp | 1 year | access_timestamp + 1 year ≤ TODAY | |

**TODAY for calculations:** 2026-11-14

### Categories the toolkit must separate

1. **Eligible for review / disposal proposal**
   - Trigger date present and valid
   - Retention period has expired
   - `on_hold` = “N” (or blank)

2. **On hold (must be excluded from disposal)**
   - `on_hold` = “Y”
   - Even if retention period has expired
   - Hold reasons include: Litigation hold, Regulatory inquiry, Internal investigation, Dispute open, Contract dispute, etc.

3. **Insufficient information (flag for investigation – do NOT treat as permission to delete)**
   - Trigger date blank, “invalid”, “N/A”, “unknown”, “TBD”, “pending”, “NULL”, “0000-00-00”, “malformed”, etc.
   - Or trigger date unparseable

---

## 4. Expected Retention Outcomes (as of 2026-11-14)

These counts were calculated against the generated CSVs using the test policies above.  
Your toolkit should produce the same (or very similar) categorisation.

| Dataset | Eligible for review (expired + not on hold) | On hold AND expired (must exclude) | Invalid / missing trigger | Still active / not yet eligible |
|---------|---------------------------------------------|------------------------------------|---------------------------|---------------------------------|
| employees | 2 | 2 | 0* | 47 |
| customers | 5 | 1 | 0* | 70 |
| suppliers | 1 | 0 | 0* | 3 |
| support_tickets | 22 | 2 | 0* | 23 |
| marketing_contacts | 29 | 4 | 4 | 40 |
| access_logs | 45 | 3 | 1 | — |
| **Totals** | **104** | **12** | **5** | **183** |

\* For employees, customers, suppliers and support tickets, blank trigger dates almost always correspond to still-active / open records. These must **not** be treated as eligible for disposal. The toolkit should distinguish “active – no trigger yet” from “trigger date missing or invalid on a closed/terminated record”.

**Key demonstration points:**
- At least some records are past their retention date **and** marked `on_hold = Y` — these must appear in the review report but be **excluded** from any disposal proposal.
- Missing or invalid dates are flagged for investigation rather than treated as permission to delete.
- Disposal simulation must only be run against a **copy** of the data; the original CSVs remain unchanged.

---

## 5. Processing Activities & Risk Assessments

- **12 processing activities** are defined in `processing_activities_register.csv`
- **6 completed privacy risk assessments** are in `privacy_risk_assessments.csv`
- Scoring method used (documented in each assessment):  
  **Likelihood (1–5) × Severity (1–5) = Inherent Risk**  
  Residual risk recalculated after controls.  
  Thresholds: 1–4 Low | 5–9 Medium | 10–15 High | 16–25 Critical

---

## 6. Controlled Disposal Simulation Notes

- Always work on a **copy** of the source CSVs.
- Proposed disposal list must **exclude** any record where `on_hold = "Y"`.
- After simulated disposal, a recovery copy of the original must still be available.
- Log must record: decision, reviewer, date, and execution result.

---

## 7. Quick Reference – File Locations

All files are in the `synthetic_data/` folder:
- employees.csv
- customers.csv
- suppliers.csv
- support_tickets.csv
- marketing_contacts.csv
- access_logs.csv
- processing_activities_register.csv
- privacy_risk_assessments.csv
- LABELED_ANSWER_SHEET.md (this document)

**Source datasets must remain unchanged.** Perform all analysis and disposal simulation on copies.
