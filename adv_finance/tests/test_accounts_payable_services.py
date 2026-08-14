import sys
import types
import unittest
from datetime import date
from decimal import Decimal


frappe = sys.modules.get("frappe") or types.ModuleType("frappe")
frappe.throw = lambda message: (_ for _ in ()).throw(Exception(message))
sys.modules.setdefault("frappe", frappe)

utils = sys.modules.get("frappe.utils") or types.ModuleType("frappe.utils")
utils.getdate = lambda value: value if isinstance(value, date) else date.fromisoformat(value)
utils.nowdate = lambda: "2026-08-14"
utils.date_diff = lambda left, right: (utils.getdate(left) - utils.getdate(right)).days
sys.modules.setdefault("frappe.utils", utils)

from adv_finance.services.accounts_payable.payment_proposal_service import calculate_payment_priority
from adv_finance.services.accounts_payable.payment_validation_service import validate_selected_amount


class TestAccountsPayableServices(unittest.TestCase):
    def test_priority_calculation(self):
        self.assertEqual(calculate_payment_priority("2026-06-01"), "Critical")
        self.assertEqual(calculate_payment_priority("2026-07-01"), "High")
        self.assertEqual(calculate_payment_priority("2026-08-20"), "Normal")
        self.assertEqual(calculate_payment_priority("2026-09-30"), "Low")

    def test_selected_amount_cannot_exceed_outstanding(self):
        validate_selected_amount(Decimal("99.00"), Decimal("100.00"))
        with self.assertRaises(Exception):
            validate_selected_amount(Decimal("101.00"), Decimal("100.00"))


if __name__ == "__main__":
    unittest.main()
