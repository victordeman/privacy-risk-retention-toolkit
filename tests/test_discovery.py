import pytest
from conftest import ROOT, write
from privacy_toolkit import discovery, evaluate, review
from privacy_toolkit.common import DataFileError, mask_value, read_csv

RULES = discovery.load_rules(ROOT / "config" / "discovery_rules.json")
TRUTH = evaluate.load_truth(ROOT / "answer_sheet" / "expected_discoveries.csv")


def scan_text(tmp_path, text):
    p = write(tmp_path / "t.csv", text)
    return discovery.scan_file(p, RULES)["findings"]


def cats(findings):
    return {(f["column"], f["category"]) for f in findings}


def test_detects_email_phone_ip_name_id(tmp_path):
    f = scan_text(tmp_path, "email,phone,ip_address,first_name,tax_id\n"
                            "a.b@example.com,+1-448-685-9537,10.1.2.3,Anna,TXAB12CD34\n"
                            "c@test.org,(247) 201-8529,41.152.186.248,Bob,TXZZ99YY88\n")
    assert {("email", "email"), ("phone", "phone"), ("ip_address", "ip_address"),
            ("first_name", "name"), ("tax_id", "identification_number")} <= cats(f)


@pytest.mark.parametrize("phone", ["+1-448-685-9537", "607-426-5775", "8265834251", "+44 9499 685098", "(247) 201-8529"])
def test_phone_formats(tmp_path, phone):
    assert ("phone", "phone") in cats(scan_text(tmp_path, f"phone\n{phone}\n{phone}\n"))


def test_placeholders_and_blanks_do_not_match(tmp_path):
    f = scan_text(tmp_path, "email,phone\nN/A,unknown\nTBD,invalid\n,\n")
    assert f == []


def test_operational_ids_not_flagged(tmp_path):
    f = scan_text(tmp_path, "log_id,ticket_id,session_id,agent_id\nLOG6000,TKT4000,SESSFY0AYISNGKPI,AGT147\n")
    assert f == []


def test_company_name_is_low_confidence(tmp_path):
    f = scan_text(tmp_path, "company_name\nApex Solutions Ltd\nGlobal Tech Pte Ltd\n")
    assert [x["confidence"] for x in f] == ["low"]


def test_single_word_needs_name_column(tmp_path):
    assert scan_text(tmp_path, "department\nLegal\nFinance\n") == []
    assert ("first_name", "name") in cats(scan_text(tmp_path, "first_name\nAnna\nBob\n"))


def test_examples_are_masked(tmp_path):
    f = scan_text(tmp_path, "email\njane.doe@example.com\njohn@example.org\n")
    assert "jane.doe" not in f[0]["masked_examples"] and "j***@example.com" in f[0]["masked_examples"]


def test_mask_value_all_categories():
    assert mask_value("phone", "+1-448-685-9537") .endswith("37") and "448" not in mask_value("phone", "+1-448-685-9537")
    assert mask_value("name", "Jane Doe") == "J*** D***"
    assert mask_value("identification_number", "NID123456789") == "NID*********"
    assert mask_value("ip_address", "41.152.186.248") == "41.*.*.*"


def test_real_data_accuracy_against_answer_sheet():
    scan = discovery.scan_folder(ROOT / "data" / "source", RULES)
    acc = evaluate.discovery_accuracy(scan["findings"], TRUTH)
    assert acc["raw_rules"]["missed_detections"] == 0 and acc["raw_rules"]["recall"] == 1.0
    assert acc["raw_rules"]["true_positives"] == 28
    # the false positives we expect, and no others
    assert {(a, b) for a, b, _ in acc["raw_rules"]["false_positive_detail"]} == {("suppliers.csv", "company_name"), ("suppliers.csv", "category")}
    assert acc["explicit_negatives"]["flagged_as_actionable"] == []      # company_name only at low confidence


def test_review_resolves_false_positives():
    scan = discovery.scan_folder(ROOT / "data" / "source", RULES)
    dec = review.simulate_analyst(scan["findings"], TRUTH, "sim", "2026-11-14")
    acc = evaluate.discovery_accuracy(scan["findings"], TRUTH, dec)
    assert acc["after_analyst_review"]["false_positives"] == 0
    assert review.suggest_improvements(dec)


def test_record_decision_validation(tmp_path):
    f = {"finding_id": "F-001", "file": "a.csv", "column": "x", "category": "email"}
    with pytest.raises(ValueError):
        review.record_decision(tmp_path / "d.csv", f, "maybe", "me", "2026-01-01")
    with pytest.raises(ValueError):
        review.record_decision(tmp_path / "d.csv", f, "confirmed", " ", "2026-01-01")
    review.record_decision(tmp_path / "d.csv", f, "rejected", "me", "2026-01-01", "n")
    assert review.load_decisions(tmp_path / "d.csv")["F-001"]["decision"] == "rejected"


# ------------------------------------------------ invalid / unreadable inputs
def test_unreadable_files_are_skipped_not_fatal(tmp_path):
    write(tmp_path / "good.csv", "email\na@b.com\nc@d.org\n")
    (tmp_path / "binary.csv").write_bytes(b"\x00\x01\x02binary\x00")
    (tmp_path / "empty.csv").write_bytes(b"")
    (tmp_path / "latin.csv").write_bytes("email\nj\xe9@x.com\n".encode("latin-1"))
    write(tmp_path / "dupehdr.csv", "a,a\n1,2\n")
    res = discovery.scan_folder(tmp_path, RULES)
    assert [f["file"] for f in res["findings"]] == ["good.csv"]
    assert {s["file"] for s in res["skipped_files"]} == {"binary.csv", "empty.csv", "latin.csv", "dupehdr.csv"}


def test_ragged_rows_warned_and_skipped(tmp_path):
    write(tmp_path / "r.csv", "email,x\na@b.com,1\nbroken\nc@d.org,2\n")
    res = discovery.scan_folder(tmp_path, RULES)
    assert res["warnings"] and res["per_file"]["r.csv"]["total_records"] == 2


def test_missing_folder_raises(tmp_path):
    with pytest.raises(DataFileError):
        discovery.scan_folder(tmp_path / "nope", RULES)


def test_read_csv_missing_file(tmp_path):
    with pytest.raises(DataFileError):
        read_csv(tmp_path / "missing.csv")
