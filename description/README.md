# Project description (for non-technical readers)

**Privacy Risk Assessment and Data Retention Automation Toolkit** · ICDFA Group 4 capstone project

This page explains the project in plain language: the problem it addresses, what the toolkit does, and what every file in this repository is for. You do not need to know how to program to follow it.

> **All data in this project is fictional (synthetic).** The retention periods are **test policies**, not legal requirements. The toolkit is not connected to any real company system.

---

## 1. The problem

Organisations hold personal information about customers, employees and suppliers. It is usually spread across spreadsheets, shared folders and business systems. Three things often go wrong:

1. **Nobody has a complete list** of what personal data exists, where it is, who owns it, or why it is kept.
2. **Data is kept longer than necessary.** Records stay long after they should have been reviewed, and it is unclear which ones may be removed and which must be kept (for example because of a legal case).
3. **There is no proof** of how privacy risks were judged and handled.

Policies and blank templates do not solve this, because nothing connects the **data**, the **purpose**, the **risk** and the **retention decision**.

## 2. The solution in one sentence

A working toolkit that **finds personal data, records why it is held, assesses the risk, decides what is due for review, and simulates safe disposal, with every decision written down as evidence.**

### An everyday comparison
Think of an office archive room.
- **Discovery** is walking through the room and noting which boxes contain personal files.
- **Review** is a person checking that list, because a label can look right and be wrong.
- **Register and inventory** are the catalogue: what each box is, who owns it, why we keep it.
- **Risk assessment** is deciding how harmful it would be if a box was lost or exposed.
- **Retention review** is checking each file's "keep until" date.
- **Disposal** is the shredding plan: only approved files, never files on hold, and a practice run on photocopies first.
- **Report** is the summary for management.

## 3. How the toolkit works (eight stages)

| # | Stage | What happens | Why it matters |
|---|---|---|---|
| 1 | **Discover** | Scans the data files and flags columns that look like personal data (emails, phone numbers, names, ID numbers, IP addresses). | You cannot protect what you do not know you hold. |
| 2 | **Review** | A person confirms or rejects each finding. Mistakes are logged. | A pattern match is only a *possible* match. A human confirms it. |
| 3 | **Check accuracy** | Compares the results with an answer sheet prepared in advance. | Shows how well the rules work (found 28 of 28, none missed). |
| 4 | **Register** | Records each data-processing activity: purpose, owner, recipients, retention period. Every change keeps its history. | Accountability: who decided what, and when. |
| 5 | **Assess risk** | Scores risk as *likelihood x severity*, then again after safeguards. Records an owner and a deadline. | Shows how risks were judged and treated. |
| 6 | **Inventory** | One table linking each dataset or system to its activity, owner, risk assessment and retention rule. | Connects everything in one place. |
| 7 | **Retention review** | Works out each record's review date and sorts it into: *eligible*, *on hold*, *needs investigation*, *active*, *not yet due*. | Finds records kept too long without endangering protected ones. |
| 8 | **Disposal (simulated)** | Proposes removals, needs a named approver, runs on a copy only, and can be fully undone. | Safe, evidenced deletion with nothing real destroyed. |
| | **Report** | Produces a management report showing counts and masked examples only. | Managers see the position without seeing personal data. |

### Built-in safety rules
- **A missing date is never permission to delete.** Such records are flagged for investigation.
- **Records on hold are never proposed for disposal** and are blocked a second time when disposal runs.
- **The original data files are never changed.** The toolkit checks they are identical before and after every run.
- **Reports and logs never show full personal data.** Values are masked (for example `j***@example.com`).
- **Rules live in settings files, not in the program.** An analyst can change a retention period without rewriting anything.

## 4. Headline results (on the demonstration data)

| Measure | Result |
|---|---|
| Records scanned | 410 across 6 datasets |
| Personal-data columns found | 28 of 28, none missed |
| False alarms before review / after review | 2 / 0 |
| Retention outcomes matching the answer sheet | 30 of 30 |
| Records eligible for review / on hold / needing investigation | 104 / 12 / 10 |
| Disposal simulation | 104 removed in a copy only, 0 blocked, source unchanged, fully recovered |
| Automated checks passing | 88 of 88 |

## 5. What each file is for

### Top level
| File | What it is | How it helps |
|---|---|---|
| `README.md` | The short technical introduction to the repository. | First page developers see. |
| `description/README.md` | **This page.** | Explains the project to everyone else. |
| `run.sh` | A small launcher. | Lets anyone start the toolkit or the checks with one short command instead of long ones. |
| `pyproject.toml` | The project's technical identity card (name, version, requirements). | Tells computers how to treat the project. Needs no attention from non-developers. |
| `.gitignore` | A list of things not to store in the repository. | Keeps generated results out of the saved project, because they are recreated on every run. |

### `data/`: the information the toolkit works on
| File | What it is | How it helps |
|---|---|---|
| `data/source/employees.csv` | 70 fictional employee records. | One of six datasets to scan. |
| `data/source/customers.csv` | 90 fictional customer records. | Includes records past their retention period. |
| `data/source/suppliers.csv` | 40 fictional supplier records. | Contains business names and categories that *look* like personal names, which tests the false-alarm handling. |
| `data/source/support_tickets.csv` | 80 fictional support tickets. | A dataset with many records due for review. |
| `data/source/marketing_contacts.csv` | 60 fictional marketing contacts. | Contains missing and invalid dates, which test the "flag, never delete" rule. |
| `data/source/access_logs.csv` | 70 fictional system access logs. | Contains IP addresses and records on legal or security hold. |
| `data/registers/processing_activities_register.csv` | The 12 data-processing activities (for example "Employee HR Administration"). | Starting point for the register: purpose, owner, recipients, retention. |
| `data/registers/privacy_risk_assessments.csv` | The six risk assessments already completed. | Starting point for risk assessment. The demo adds a seventh. |
| `data/README_synthetic_data.md` | Describes the fictional data. | Confirms it is safe to use and explains each file. |

### `config/`: the settings (changed without programming)
| File | What it controls |
|---|---|
| `discovery_rules.json` | What counts as an email, phone number, name, ID number or IP address, and what lowers confidence. |
| `retention_schedule_config.json` | How many years each dataset is kept, which date starts the clock, which column marks a hold, and the "as of" date (14 November 2026). |
| `retention_schedule_config.original.json` | A backup copy of the retention settings as first supplied. Use it to restore the original if you experiment. |
| `risk_scoring.json` | The 1 to 5 scales and the Low, Medium, High and Critical bands for risk. |

### `answer_sheet/`: the marking scheme
| File | What it is | How it helps |
|---|---|---|
| `expected_discoveries.csv` | The list of columns that really are personal data, and those that are not. | Used to measure discovery accuracy. |
| `expected_retention_outcomes.json` | The correct retention outcome counts, in a form a computer can read. | Lets the toolkit check its own results automatically. |
| `LABELED_ANSWER_SHEET_ORIGINAL.md` | The answer sheet as first supplied. | Kept for the record. Its totals did not add up to the 410 records. |
| `LABELED_ANSWER_SHEET_CORRECTED.md` | The corrected version prepared by the team. | The one the toolkit is checked against (30 of 30 match). |

### `src/privacy_toolkit/`: the program itself
Each file does one job, matching the stages above.

| File | Job |
|---|---|
| `discovery.py` | **Stage 1.** Scans files and flags possible personal data, with masked examples. |
| `review.py` | **Stage 2.** Records a person's confirm or reject decisions, missed items and suggested rule changes. |
| `evaluate.py` | **Stage 3.** Measures accuracy and compares retention results with the answer sheet. |
| `register.py` | **Stage 4.** Keeps the register of activities and its change history. |
| `risk.py` | **Stage 5.** Calculates and checks risk scores, owners and deadlines. |
| `inventory.py` | **Stage 6.** Builds the linked inventory of datasets and systems. |
| `retention.py` | **Stage 7.** Works out review dates and sorts every record into an outcome. |
| `disposal.py` | **Stage 8.** Proposal, approval, run on a copy, and recovery. |
| `report.py` | Produces the management report (counts and masked examples only). |
| `cli.py` | The command centre. It reads what the user types (such as `discover` or `report`) and runs the right stage. |
| `common.py` | Shared helpers: safe file reading, masking of values, date handling and file fingerprints (to prove files did not change). |
| `__main__.py` and `__init__.py` | Small technical files that let the toolkit start as a program. |

### `tests/`: the automatic quality checks (88 in total)
| File | What it checks |
|---|---|
| `test_discovery.py` | Detection rules, phone formats, masking, confidence levels, the analyst review step, accuracy against the answer sheet, and unreadable or damaged files. |
| `test_retention.py` | Date calculations, leap years, holds, missing and invalid dates. |
| `test_risk_register_inventory.py` | Risk scoring, register history and inventory links. |
| `test_disposal.py` | Approval rules, tampered proposals, blocked held records and recovery. |
| `test_end_to_end.py` | The whole process from start to finish works, no raw personal data appears in any report or log, and errors are shown cleanly. |
| `conftest.py` | Shared set-up: gives every test a throwaway copy of the project, so the tests never touch the real data. |

### `docs/`: the written documentation
| File | What it explains |
|---|---|
| `USER_GUIDE.md` | The steps and commands, one by one. |
| `METHOD_AND_RULES.md` | The exact rules for discovery, risk scoring and retention, and the assumptions made. |
| `LIMITATIONS.md` | What the toolkit cannot do and where a human must decide. |
| `TEST_RESULTS.md` | The results of the automatic checks. |
| `CONTRIBUTION_RECORD.md` | A table for each member to record who did what. |

### `notebooks/`: the guided demonstration
| File | What it is |
|---|---|
| `privacy_toolkit_demo.ipynb` | A step-by-step demonstration that runs the whole process in Google Colab. Every step has a note on **why it matters, what it does and the result to expect**. Best starting point for presenting. |

### `output/`: results (created when you run it)
This folder does not exist in the repository. Every run creates it, holding findings, decisions, the inventory, the retention review, the disposal proposal, approval and log, and the report. It is left out on purpose so each run starts clean and produces evidence live.

## 6. How the files fit together

```
  data/ (the information)  +  config/ (the rules)
              |                       |
              v                       v
        src/ (the program: discover > review > evaluate > register
                            > assess > inventory > retention > dispose > report)
              |
              v
        output/ (the evidence)  <---- checked against ---- answer_sheet/ (the marking scheme)
              ^
              |
        tests/ (88 automatic quality checks)

  docs/ and notebooks/ explain and demonstrate all of the above.
```

## 7. How to see it working (no coding needed)

1. Open `notebooks/privacy_toolkit_demo.ipynb` in Google Colab.
2. Upload `privacy_toolkit.zip` as the first cell says.
3. Run the cells in order, one at a time, and read the notes above each one.
4. At the end, open the generated management report.

## 8. Plain-language glossary

| Term | Meaning |
|---|---|
| **Personal data** | Information that identifies a person: name, email, phone, ID number, IP address. |
| **Synthetic data** | Invented data that looks real but belongs to no real person. |
| **Discovery** | Automatically searching for personal data. |
| **False positive** | A false alarm: something flagged as personal data that is not. |
| **Processing activity** | A task that uses personal data, such as running payroll. |
| **Register** | The official list of processing activities, with purpose and owner. |
| **Inventory** | The list of datasets and systems and how they link to the register. |
| **Risk (likelihood x severity)** | How likely harm is, multiplied by how bad it would be. |
| **Residual risk** | The risk left after safeguards are in place. |
| **Retention period** | How long a record may be kept before it must be reviewed. |
| **Trigger date** | The date the retention clock starts, such as the day an account closed. |
| **Hold** | A reason a record must not be removed, such as a legal case. |
| **Masking** | Hiding part of a value so it cannot be read in full (`j***@example.com`). |
| **Simulation** | A practice run on a copy that changes nothing real. |

## 9. Limits to keep in mind

- A pattern match is **not** proof of personal data. People must review findings.
- The toolkit does not read free text such as the content of notes or tickets.
- It knows only the data formats in this demonstration. Other countries' ID formats would need new rules.
- Retention periods are test values. Real use needs legal advice and approval.
- The reviewer and analyst in the demonstration are simulated. A real run needs named people.
- Disposal is simulated only. There is no connection to any real deletion service.
