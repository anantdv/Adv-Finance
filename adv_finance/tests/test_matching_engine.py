import types
import unittest
from decimal import Decimal

from adv_finance.services.matching_engine import run_exact_matching


def row(**kwargs):
    defaults = {
        "name": "",
        "normalized_reference": "",
        "amount": Decimal("0"),
        "match_status": "Unmatched",
        "transaction_date": None,
        "posting_date": None,
    }
    defaults.update(kwargs)
    return types.SimpleNamespace(**defaults)


class TestMatchingEngine(unittest.TestCase):
    def test_exact_reference_amount_match(self):
        matches = run_exact_matching(
            [row(name="S1", normalized_reference="INV001", amount=Decimal("100.00"))],
            [row(name="E1", normalized_reference="INV001", amount=Decimal("100.00"))],
        )
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]["status"], "Auto Accepted")

    def test_duplicate_candidate_not_auto_matched(self):
        matches = run_exact_matching(
            [row(name="S1", normalized_reference="INV001", amount=Decimal("100.00"))],
            [
                row(name="E1", normalized_reference="INV001", amount=Decimal("100.00")),
                row(name="E2", normalized_reference="INV001", amount=Decimal("100.00")),
            ],
        )
        self.assertEqual(matches, [])


if __name__ == "__main__":
    unittest.main()
