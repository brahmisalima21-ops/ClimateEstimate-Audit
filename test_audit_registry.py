import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from audit_registry import classify_directness, validate, load_rows


def make_row(**fields):
    """A registry row with 'No' for both accounting flags unless overridden."""
    row = {
        "recognized_accounting_amount_measured": "No",
        "accounting_framework_confirmed": "No",
    }
    row.update(fields)
    return row


def make_valid_row(**fields):
    row = {
        "study_id": "X",
        "title": "T",
        "doi_or_url": "link",
        "source_verification_status": "checked",
        "source_verified_date": "2026-01-01",
        "recognized_accounting_amount_measured": "No",
        "accounting_framework_confirmed": "No",
        "directness_level": "D3",
        "variable_type": "PD",
    }
    row.update(fields)
    return row


class RegistryTests(unittest.TestCase):
    def test_registry_loads_and_validates(self):
        rows = load_rows()
        self.assertGreaterEqual(len(rows), 15)
        self.assertEqual(validate(rows)[0], [])

    def test_pd_is_not_ecl(self):
        row = make_row(variable_type="PD", accounting_standard="IFRS 9")
        self.assertEqual(classify_directness(row), "D3")

    def test_llp_is_not_ecl(self):
        row = make_row(variable_type="LLP", accounting_standard="IFRS 9 not confirmed")
        self.assertEqual(classify_directness(row), "D3")

    def test_naming_a_standard_does_not_upgrade_a_proxy(self):
        row = make_row(
            variable_type="LLP",
            accounting_standard="IFRS 9 not established",
            accounting_outcome="Loan loss provisions (LLP)",
        )
        self.assertEqual(classify_directness(row), "D3")

    def test_illustrative_mapping_is_context(self):
        row = make_row(
            variable_type="Qualitative mapping",
            accounting_standard="IAS 36 and IFRS 9 discussed",
            accounting_outcome="Illustrative mapping, not recognized outcome",
        )
        self.assertEqual(classify_directness(row), "D4")

    def test_impairment_test_discussion_is_d2(self):
        row = make_row(
            variable_type="Accounting measurement",
            accounting_standard="IAS 36",
            accounting_outcome="Impairment test discussed",
        )
        self.assertEqual(classify_directness(row), "D2")

    def test_d1_needs_amount_and_framework(self):
        row = make_valid_row(
            recognized_accounting_amount_measured="Yes",
            accounting_framework_confirmed="Yes",
            directness_level="D1",
        )
        self.assertEqual(validate([row])[0], [])
        row["accounting_framework_confirmed"] = "No"
        self.assertTrue(validate([row])[0])

    def test_terms_match_whole_words_only(self):
        # 'pd' sits inside 'updated' and 'ead' inside 'spread'; neither should count
        updated = make_row(variable_type="Updated scenario", accounting_outcome="Illustrative")
        spread = make_row(variable_type="Spread of ratings", accounting_outcome="Impairment test discussed")
        self.assertEqual(classify_directness(updated), "D4")
        self.assertEqual(classify_directness(spread), "D2")

    def test_stored_label_must_match_classifier(self):
        row = make_valid_row(directness_level="D2", variable_type="PD")
        self.assertTrue(validate([row])[0])


if __name__ == "__main__":
    unittest.main()
