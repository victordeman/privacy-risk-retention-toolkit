import re
import subprocess
import sys

from conftest import ROOT
from privacy_toolkit.common import hash_tree, read_csv


def test_demo_pipeline_and_report_masking(project):
    before = hash_tree(project / "data" / "source")
    r = subprocess.run([sys.executable, "-m", "privacy_toolkit", "--root", str(project), "demo"],
                       capture_output=True, text=True, env={"PYTHONPATH": str(ROOT / "src"), "PATH": ""})
    assert r.returncode == 0, r.stderr + r.stdout
    assert "ALL MATCH" in r.stdout and "Source CSVs unchanged: True" in r.stdout
    assert hash_tree(project / "data" / "source") == before
    out = project / "output"
    for f in ("discovery_findings.csv", "review_decisions.csv", "data_inventory.csv", "retention_review.csv", "disposal_proposal.csv",
              "disposal_approval.json", "simulation_log.csv", "management_report.html", "processing_register_history.csv",
              "privacy_risk_assessments.csv", "retention_comparison.csv", "discovery_accuracy.json"):
        assert (out / f).exists(), f
    # the held records must not be in the proposal
    held = {r["record_id"] for r in read_csv(out / "retention_review.csv").rows if r["on_hold"] == "Y"}
    assert not held & {r["record_id"] for r in read_csv(out / "disposal_proposal.csv").rows}


def test_no_raw_personal_data_in_reports_or_logs(project):
    subprocess.run([sys.executable, "-m", "privacy_toolkit", "--root", str(project), "demo"], capture_output=True,
                   env={"PYTHONPATH": str(ROOT / "src"), "PATH": ""}, check=True)
    sensitive = set()
    for name, cols in {"employees": ["email", "phone", "national_id", "full_name"], "customers": ["email", "phone", "tax_id"],
                       "suppliers": ["contact_email", "contact_phone", "tax_registration"],
                       "support_tickets": ["customer_email", "customer_name"], "marketing_contacts": ["email"],
                       "access_logs": ["ip_address"]}.items():
        for row in read_csv(project / "data" / "source" / f"{name}.csv").rows:
            sensitive |= {row[c] for c in cols if len(row[c]) > 6}
    checked = 0
    for p in (project / "output").rglob("*"):
        if p.is_file() and "disposal_simulation" not in p.parts and p.suffix in (".csv", ".json", ".html"):
            text = p.read_text(encoding="utf-8")
            checked += 1
            leaked = [v for v in sensitive if v in text]
            assert not leaked, f"{p.name} leaks {len(leaked)} raw values"
    assert checked >= 10


def test_cli_reports_errors_cleanly(project, capsys):
    from privacy_toolkit.cli import main
    assert main(["--root", str(project), "dispose", "run"]) == 1        # no retention review / approval yet
    assert "ERROR" in capsys.readouterr().err
