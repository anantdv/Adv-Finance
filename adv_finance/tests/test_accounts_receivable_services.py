import sys
import types
import unittest
from decimal import Decimal


frappe = sys.modules.get("frappe") or types.ModuleType("frappe")
frappe.throw = lambda message: (_ for _ in ()).throw(Exception(message))
frappe.session = types.SimpleNamespace(user="collector@example.com")
frappe.has_role = lambda role: True
sys.modules.setdefault("frappe", frappe)

utils = sys.modules.get("frappe.utils") or types.ModuleType("frappe.utils")
utils.today = lambda: "2026-08-15"
utils.date_diff = lambda left, right: {
    ("2026-08-15", "2026-08-10"): 5,
    ("2026-08-15", "2026-07-01"): 45,
}.get((left, right), 0)
utils.add_days = lambda value, days: f"{value}+{days}"
utils.getdate = lambda value=None: value or "2026-08-15"
utils.now_datetime = lambda: "2026-08-15 00:00:00"
sys.modules.setdefault("frappe.utils", utils)

from adv_finance.services.accounts_receivable.ar_balance_service import ageing_bucket, get_customer_ar_summary
from adv_finance.services.accounts_receivable.collection_priority_service import score_collection_case
from adv_finance.services.accounts_receivable.credit_hold_service import validate_customer_credit_status
from adv_finance.services.accounts_receivable.promise_service import validate_promise


class Row(types.SimpleNamespace):
    pass


class FakeDB:
    def __init__(self):
        self.values = {}
        self.exists_result = None

    def get_value(self, doctype, name, fields=None, as_dict=False):
        return self.values.get((doctype, name))

    def exists(self, *args, **kwargs):
        return self.exists_result


class TestAccountsReceivableServices(unittest.TestCase):
    def setUp(self):
        frappe.db = FakeDB()

    def test_ageing_bucket(self):
        self.assertEqual(ageing_bucket(0), "Current")
        self.assertEqual(ageing_bucket(30), "1-30")
        self.assertEqual(ageing_bucket(90), "61-90")
        self.assertEqual(ageing_bucket(121), "120+")

    def test_ar_summary_uses_open_sales_invoices(self):
        import adv_finance.services.accounts_receivable.ar_balance_service as balance_service

        original = balance_service.get_customer_open_sales_invoices
        balance_service.get_customer_open_sales_invoices = lambda company, customer, as_of_date: [
            Row(name="SINV-1", posting_date="2026-07-01", due_date="2026-07-01", grand_total=100, outstanding_amount=Decimal("100"), currency="PGK"),
            Row(name="SINV-2", posting_date="2026-08-10", due_date="2026-08-10", grand_total=50, outstanding_amount=Decimal("50"), currency="PGK"),
        ]
        try:
            summary = get_customer_ar_summary("Company A", "Customer A", "2026-08-15")
        finally:
            balance_service.get_customer_open_sales_invoices = original

        self.assertEqual(summary["total_outstanding"], Decimal("150"))
        self.assertEqual(summary["overdue_amount"], Decimal("150"))
        self.assertEqual(summary["open_invoice_count"], 2)
        self.assertEqual(summary["invoices"][0]["ageing_bucket"], "31-60")

    def test_collection_priority_is_explainable(self):
        case = Row(overdue_amount=Decimal("120000"), oldest_overdue_days=95, broken_promise_count=1, open_dispute_count=1)
        result = score_collection_case(case, {"available_credit": Decimal("-1")})
        self.assertEqual(result["priority"], "Critical")
        self.assertGreaterEqual(result["score"], 70)
        self.assertTrue(result["factors"])

    def test_credit_hold_blocks_customer(self):
        import adv_finance.services.accounts_receivable.credit_hold_service as hold_service

        original = hold_service.get_active_credit_hold
        hold_service.get_active_credit_hold = lambda company, customer, transaction_type=None: Row(name="HOLD-1", hold_reason="Overdue exposure")
        try:
            result = validate_customer_credit_status("Company A", "Customer A", "Sales Order", 100)
        finally:
            hold_service.get_active_credit_hold = original

        self.assertFalse(result["allowed"])
        self.assertEqual(result["credit_hold"], "HOLD-1")

    def test_promise_allocation_cannot_exceed_invoice(self):
        frappe.db.values[("Sales Invoice", "SINV-1")] = Row(company="Company A", customer="Customer A", currency="PGK", outstanding_amount=Decimal("100"))
        promise = Row(
            company="Company A",
            customer="Customer A",
            promised_amount=Decimal("150"),
            notes="Customer committed extra remittance.",
            invoices=[Row(sales_invoice="SINV-1", promised_amount=Decimal("101"), invoice_outstanding=0)],
        )

        with self.assertRaises(Exception):
            validate_promise(promise)


if __name__ == "__main__":
    unittest.main()
