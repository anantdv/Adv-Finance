import sys
import types
import unittest
from decimal import Decimal


frappe = sys.modules.get("frappe") or types.ModuleType("frappe")
frappe.throw = lambda message: (_ for _ in ()).throw(Exception(message))
frappe.session = types.SimpleNamespace(user="reviewer@example.com")
frappe.has_role = lambda role: True
sys.modules.setdefault("frappe", frappe)

utils = sys.modules.get("frappe.utils") or types.ModuleType("frappe.utils")
utils.getdate = getattr(utils, "getdate", lambda value: value)
utils.date_diff = lambda left, right: 45
utils.now = lambda: "2026-08-14 00:00:00"
utils.now_datetime = lambda: "2026-08-14 00:00:00"
sys.modules.setdefault("frappe.utils", utils)
file_manager = types.ModuleType("frappe.utils.file_manager")
file_manager.get_file_path = lambda value: value
sys.modules.setdefault("frappe.utils.file_manager", file_manager)

from adv_finance.services.account_reconciliation.providers.manual import ManualSupportingBalanceProvider
from adv_finance.services.account_reconciliation.reconciliation_service import age_bucket, recalculate


class Child(types.SimpleNamespace):
    pass


class Reconciliation(types.SimpleNamespace):
    pass


class TestAccountReconciliationServices(unittest.TestCase):
    def test_difference_calculation(self):
        rec = Reconciliation(
            gl_closing_balance=Decimal("10000"),
            supporting_balance=Decimal("9000"),
            tolerance_amount=Decimal("0"),
            period_end="2026-07-31",
            items=[Child(item_type="Reconciling Item", amount=Decimal("1000"), status="Confirmed", transaction_date=None)],
        )
        recalculate(rec)
        self.assertEqual(rec.gross_difference, Decimal("1000"))
        self.assertEqual(rec.explained_difference, Decimal("1000"))
        self.assertEqual(rec.unexplained_difference, Decimal("0"))

    def test_tolerance(self):
        rec = Reconciliation(
            gl_closing_balance=Decimal("100.05"),
            supporting_balance=Decimal("100.00"),
            tolerance_amount=Decimal("0.10"),
            period_end="2026-07-31",
            items=[],
        )
        recalculate(rec)
        self.assertTrue(rec.difference_within_tolerance)

    def test_age_bucket(self):
        self.assertEqual(age_bucket(0), "Current")
        self.assertEqual(age_bucket(30), "1-30")
        self.assertEqual(age_bucket(90), "61-90")
        self.assertEqual(age_bucket(181), "180+")

    def test_manual_provider(self):
        rec = Reconciliation(supporting_balance=Decimal("123.45"))
        self.assertEqual(ManualSupportingBalanceProvider().get_supporting_balance(rec), Decimal("123.45"))


if __name__ == "__main__":
    unittest.main()
