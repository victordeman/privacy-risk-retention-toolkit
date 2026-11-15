# Privacy Risk Assessment and Data Retention Automation Toolkit

Python 3.10+ , standard library only (pytest for the tests). Synthetic data only. Retention periods are **test policies**.

```
./run.sh demo      # full pipeline: discovery -> review -> accuracy -> register -> risk -> inventory -> retention -> disposal -> report
./run.sh test      # 88 tests
```

| Folder | Contents |
|---|---|
| `config/` | discovery rules, retention schedule, risk scoring - edit these, not the code |
| `data/source/` | six synthetic CSVs (read-only; hash-checked on every run) |
| `data/registers/` | supplied processing register and risk assessments |
| `answer_sheet/` | original sheet, **corrected** sheet, machine-readable expected results |
| `src/privacy_toolkit/` | discovery, review, inventory, register, risk, retention, disposal, report, evaluate, cli |
| `tests/` | pytest suite |
| `output/` | results of the last demo run (findings, decisions, inventory, retention review, proposal, approval, simulation log, report) |
| `docs/` | method and rules, limitations, user guide, test results, contribution record |

Start with `docs/USER_GUIDE.md`.
