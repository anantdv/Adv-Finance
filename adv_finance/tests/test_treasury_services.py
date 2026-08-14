import sys
import types
import unittest
from datetime import date, timedelta
from decimal import Decimal

frappe = sys.modules.get("frappe") or types.ModuleType("frappe")
frappe.throw = lambda message: (_ for _ in ()).throw(Exception(message))
frappe.session = types.SimpleNamespace(user="treasury@example.com")
frappe.has_role = lambda role: False
frappe._dict = lambda value=None, **kwargs: Row(**(value or {}), **kwargs)
sys.modules.setdefault("frappe", frappe)

utils = sys.modules.get("frappe.utils") or types.ModuleType("frappe.utils")
def getdate(value=None):
    if value is None:
        return date(2026, 8, 15)
    if isinstance(value, date):
        return value
    return date.fromisoformat(str(value))
utils.getdate = getdate
utils.add_days = lambda value, days: getdate(value) + timedelta(days=int(days))
utils.date_diff = lambda left, right: (getdate(left) - getdate(right)).days
utils.now_datetime = lambda: "2026-08-15 00:00:00"
utils.today = lambda: "2026-08-15"
sys.modules.setdefault("frappe.utils", utils)

from adv_finance.services.treasury.cash_forecast_service import aggregate_weekly, build_forecast_lines, generate_cash_forecast
from adv_finance.services.treasury.cash_position_service import get_cash_position
from adv_finance.services.treasury.forecast_accuracy_service import get_forecast_accuracy
from adv_finance.services.treasury.liquidity_service import liquidity_status
from adv_finance.services.treasury.settings import get_receipt_probability
from adv_finance.services.treasury.close_readiness_service import get_treasury_close_readiness


class Row(types.SimpleNamespace):
    def copy(self):
        return self.__dict__.copy()
    def as_dict(self):
        return self.__dict__.copy()


class Forecast(Row):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.lines = kw.get("lines", [])
        self.saved = False
    def set(self, field, value):
        setattr(self, field, value)
    def append(self, field, value):
        getattr(self, field).append(Row(**value))
    def save(self):
        self.saved = True


class FakeDB:
    def __init__(self):
        self.values = {("Company", "Company A", "default_currency"): "PGK"}
        self.counts = {}
    def get_value(self, doctype, name=None, fieldname=None, as_dict=False, **kwargs):
        if isinstance(fieldname, list):
            return Row(account_name="BSP Operating", account_currency="PGK", company="Company A")
        return self.values.get((doctype, name, fieldname)) or self.values.get((doctype, name))
    def count(self, doctype, filters=None):
        return self.counts.get(doctype, 0)


class TestTreasuryServices(unittest.TestCase):
    def setUp(self):
        frappe.db = FakeDB()
        frappe.get_all = lambda *a, **k: []
        self.new_docs = []
        def new_doc(doctype):
            doc = Row(doctype=doctype, name=f"{doctype}-1")
            doc.update = lambda values: doc.__dict__.update(values)
            doc.insert = lambda *a, **k: self.new_docs.append(doc)
            return doc
        frappe.new_doc = new_doc

    def patch_forecast_sources(self, svc, **sources):
        originals = {}
        for name, value in sources.items():
            originals[name] = getattr(svc, name)
            setattr(svc, name, value)
        return originals

    def restore(self, svc, originals):
        for name, value in originals.items():
            setattr(svc, name, value)

    def test_treasury_account_cash_position_matches_gl_and_restricted_excluded(self):
        import adv_finance.services.treasury.cash_position_service as svc
        originals = self.patch_forecast_sources(
            svc,
            get_treasury_accounts=lambda company, treasury_group=None: [Row(name="TA-1", account="Bank - A", bank_account="BSP", treasury_account_type="Operating Bank", treasury_group="Operating", account_currency="PGK", restricted_amount=Decimal("500"), minimum_balance=Decimal("1000"), include_in_available_liquidity=1)],
            get_cash_account_balance=lambda company, account, as_of_date: {"balance": Decimal("10000"), "currency": "PGK"},
            get_liquidity_threshold=lambda company, as_of_date: {"minimum_operating_cash": Decimal("3000"), "warning_threshold": Decimal("2000"), "critical_threshold": Decimal("1000")},
        )
        try:
            result = get_cash_position("Company A", "2026-08-15")
        finally:
            self.restore(svc, originals)
        self.assertEqual(result["actual_cash"], Decimal("10000"))
        self.assertEqual(result["restricted_cash"], Decimal("500"))
        self.assertEqual(result["available_liquidity"], Decimal("9500"))
        self.assertEqual(result["liquidity_headroom"], Decimal("6500"))

    def test_multi_currency_cash_position_converts_without_overwriting_native(self):
        import adv_finance.services.treasury.cash_position_service as svc
        originals = self.patch_forecast_sources(
            svc,
            get_treasury_accounts=lambda company, treasury_group=None: [Row(name="TA-USD", account="USD Bank", bank_account="USD", treasury_account_type="Operating Bank", treasury_group="FX", account_currency="USD", restricted_amount=0, minimum_balance=0, include_in_available_liquidity=1)],
            get_cash_account_balance=lambda company, account, as_of_date: {"balance": Decimal("200"), "currency": "USD"},
            convert_amount=lambda amount, src, dst, d: (Decimal(str(amount)) * Decimal("3.5"), Decimal("3.5")),
            get_liquidity_threshold=lambda company, as_of_date: {"minimum_operating_cash": Decimal("0"), "warning_threshold": Decimal("0"), "critical_threshold": Decimal("0")},
        )
        try:
            account = get_cash_position("Company A", "2026-08-15")["accounts"][0]
        finally:
            self.restore(svc, originals)
        self.assertEqual(account["native_balance"], Decimal("200"))
        self.assertEqual(account["company_currency_balance"], Decimal("700.0"))

    def test_receipt_source_precedence_promise_over_invoice(self):
        import adv_finance.services.treasury.cash_forecast_service as svc
        originals = self.patch_forecast_sources(
            svc,
            get_active_promises_for_forecast=lambda *a: [Row(name="PTP-1", customer="CUST", customer_name="C", promised_payment_date="2026-08-20", currency="PGK", remaining_promised_amount=Decimal("80"), invoice_promised_amount=Decimal("80"), status="Active", sales_invoice="SINV-1")],
            get_open_sales_invoices_for_forecast=lambda *a: [Row(name="SINV-1", customer="CUST", posting_date="2026-08-01", due_date="2026-08-18", currency="PGK", outstanding_amount=Decimal("100"))],
            get_active_disputed_amounts=lambda *a: {}, get_payment_behaviour=lambda *a: {"average_days_late": 0},
            get_payment_runs_for_forecast=lambda *a: [], get_payment_proposals_for_forecast=lambda *a: [], get_open_purchase_invoices_for_forecast=lambda *a: [], get_manual_treasury_items_for_forecast=lambda *a: [], get_active_hold=lambda *a: None, convert_amount=lambda amount, src, dst, d: (Decimal(str(amount)), Decimal("1")),
        )
        try:
            lines = build_forecast_lines("Company A", "2026-08-15", "2026-11-15", None, "PGK")
        finally:
            self.restore(svc, originals)
        self.assertEqual(sum(l["native_amount"] for l in lines if l["direction"] == "Inflow"), Decimal("100"))
        self.assertEqual([l["source_type"] for l in lines if l["direction"] == "Inflow"], ["Sales Invoice", "Promise to Pay"])

    def test_payment_source_precedence_run_over_proposal_over_invoice_and_hold_excluded(self):
        import adv_finance.services.treasury.cash_forecast_service as svc
        originals = self.patch_forecast_sources(
            svc,
            get_active_promises_for_forecast=lambda *a: [], get_open_sales_invoices_for_forecast=lambda *a: [], get_active_disputed_amounts=lambda *a: {},
            get_payment_runs_for_forecast=lambda *a: [Row(name="RUN-1", payment_date="2026-08-19", currency="PGK", supplier="SUP", purchase_invoice="PINV-1", selected_amount=Decimal("100"))],
            get_payment_proposals_for_forecast=lambda *a: [Row(name="PROP-1", posting_date="2026-08-20", currency="PGK", supplier="SUP", purchase_invoice="PINV-1", selected_amount=Decimal("100"))],
            get_open_purchase_invoices_for_forecast=lambda *a: [Row(name="PINV-1", supplier="SUP", posting_date="2026-08-01", due_date="2026-08-22", currency="PGK", outstanding_amount=Decimal("100")), Row(name="PINV-HELD", supplier="SUP", posting_date="2026-08-01", due_date="2026-08-22", currency="PGK", outstanding_amount=Decimal("50"))],
            get_manual_treasury_items_for_forecast=lambda *a: [], get_active_hold=lambda company, supplier, invoice: invoice == "PINV-HELD", convert_amount=lambda amount, src, dst, d: (Decimal(str(amount)), Decimal("1")),
        )
        try:
            lines = build_forecast_lines("Company A", "2026-08-15", "2026-11-15", None, "PGK")
        finally:
            self.restore(svc, originals)
        self.assertEqual(len([l for l in lines if l["direction"] == "Outflow"]), 1)
        self.assertEqual(lines[0]["source_type"], "Payment Run")

    def test_manual_recurring_item_and_scenario(self):
        import adv_finance.services.treasury.cash_forecast_service as svc
        scenario = Row(receipt_probability_multiplier=Decimal("0.8"), payment_probability_multiplier=Decimal("1"), receipt_delay_days=10, payment_acceleration_days=0)
        originals = self.patch_forecast_sources(
            svc,
            frappe=frappe, get_active_promises_for_forecast=lambda *a: [], get_open_sales_invoices_for_forecast=lambda *a: [], get_active_disputed_amounts=lambda *a: {}, get_payment_runs_for_forecast=lambda *a: [], get_payment_proposals_for_forecast=lambda *a: [], get_open_purchase_invoices_for_forecast=lambda *a: [], get_active_hold=lambda *a: None,
            get_manual_treasury_items_for_forecast=lambda *a: [Row(name="ITEM-1", direction="Inflow", category="Customer Deposit", description="Deposit", party_type="Customer", party="CUST", expected_date="2026-08-15", currency="PGK", amount=Decimal("100"), probability_percent=Decimal("100"), recurrence="Monthly")],
            convert_amount=lambda amount, src, dst, d: (Decimal(str(amount)), Decimal("1")), _get_scenario=lambda s: scenario,
        )
        try:
            lines = build_forecast_lines("Company A", "2026-08-15", "2026-11-15", "Stress", "PGK")
        finally:
            self.restore(svc, originals)
        self.assertGreaterEqual(len(lines), 3)
        self.assertEqual(lines[0]["probability_percent"], Decimal("80.0"))

    def test_liquidity_shortfall_and_13_week_aggregation(self):
        lines = [{"week_number": 1, "direction": "Outflow", "probability_weighted_amount": Decimal("5000"), "source_type": "Manual Forecast Item"}]
        frappe.db.counts = {}
        import adv_finance.services.treasury.cash_forecast_service as svc
        original = svc.get_liquidity_threshold
        svc.get_liquidity_threshold = lambda company, d: {"minimum_operating_cash": Decimal("3000"), "warning_threshold": Decimal("2000"), "critical_threshold": Decimal("1000")}
        try:
            weekly = aggregate_weekly(lines, Decimal("1000"), "Company A", "2026-08-15")
        finally:
            svc.get_liquidity_threshold = original
        self.assertEqual(weekly[0]["status"], "Shortfall")
        self.assertEqual(weekly[0]["liquidity_shortfall"], Decimal("7000"))

    def test_generate_forecast_is_frozen_when_approved(self):
        frappe.get_doc = lambda doctype, name: Forecast(name=name, status="Approved")
        with self.assertRaises(Exception):
            generate_cash_forecast("FCST-1", force=True)

    def test_forecast_accuracy(self):
        import adv_finance.services.treasury.forecast_accuracy_service as svc
        forecast = Forecast(name="FCST", company="Company A", forecast_from="2026-08-01", forecast_to="2026-08-31", lines=[Row(direction="Inflow", probability_weighted_amount=Decimal("100")), Row(direction="Outflow", probability_weighted_amount=Decimal("60"))])
        frappe.get_doc = lambda doctype, name: forecast
        original = svc.get_actual_cash_movements
        svc.get_actual_cash_movements = lambda *a: [Row(payment_type="Receive", received_amount=Decimal("110"), paid_amount=0), Row(payment_type="Pay", paid_amount=Decimal("50"), received_amount=0)]
        try:
            result = get_forecast_accuracy("FCST")
        finally:
            svc.get_actual_cash_movements = original
        self.assertEqual(result["actual_net_flow"], Decimal("60"))
        self.assertEqual(result["variance"], Decimal("20"))

    def test_treasury_close_readiness(self):
        frappe.db.counts = {"Treasury Forecast Exception": 0, "Cash Forecast": 1, "Treasury Account": 2}
        self.assertTrue(get_treasury_close_readiness("Company A", "2026-08-31")["ready"])

    def test_probability_weighted_amount(self):
        self.assertEqual(get_receipt_probability("31-60"), Decimal("65"))
        self.assertEqual(liquidity_status(Decimal("2500"), {"minimum_operating_cash": Decimal("3000"), "warning_threshold": Decimal("2800"), "critical_threshold": Decimal("1000")})["status"], "Shortfall")


if __name__ == "__main__":
    unittest.main()
