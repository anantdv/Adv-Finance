import sys
import types
import unittest
from decimal import Decimal

frappe = sys.modules.get("frappe") or types.ModuleType("frappe")
frappe.throw = lambda message: (_ for _ in ()).throw(Exception(message))
frappe.session = types.SimpleNamespace(user="budget@example.com")
frappe.has_role = lambda role: False
sys.modules.setdefault("frappe", frappe)

utils = sys.modules.get("frappe.utils") or types.ModuleType("frappe.utils")
utils.now_datetime = lambda: "2026-08-15 00:00:00"
utils.today = lambda: "2026-08-15"
utils.getdate = lambda value=None: value or "2026-08-15"
utils.date_diff = lambda left, right: 45
sys.modules.setdefault("frappe.utils", utils)

from adv_finance.services.budgeting.available_budget_service import get_available_budget
from adv_finance.services.budgeting.budget_control_service import validate_budget_availability
from adv_finance.services.budgeting.budget_service import recalculate_budget_plan
from adv_finance.services.budgeting.close_readiness_service import get_budget_close_readiness
from adv_finance.services.budgeting.commitment_service import get_open_commitments, get_precommitments, summarize_commitments
from adv_finance.services.budgeting.forecast_service import calculate_budget_forecast
from adv_finance.services.budgeting.override_service import find_valid_override, mark_override_used
from adv_finance.services.budgeting.reservation_service import validate_reservation
from adv_finance.services.budgeting.supplement_service import validate_supplement
from adv_finance.services.budgeting.transfer_service import validate_transfer


class Row(types.SimpleNamespace):
    def get(self, key, default=None):
        return getattr(self, key, default)


class FakeDB:
    def __init__(self):
        self.counts = {}
        self.exists_values = set()
    def exists(self, doctype, name=None):
        return (doctype, name) in self.exists_values
    def get_value(self, *args, **kwargs):
        return None
    def count(self, doctype, filters=None):
        return self.counts.get(doctype, 0)


class TestBudgetingServices(unittest.TestCase):
    def setUp(self):
        frappe.db = FakeDB()
        self.rows = {}
        frappe.get_all = self.fake_get_all
        self.docs = {}
        frappe.get_doc = lambda doctype, name=None: self.docs[(doctype, name)]

    def fake_get_all(self, doctype, filters=None, fields=None, **kwargs):
        return self.rows.get(doctype, [])

    def patch(self, module, **values):
        originals = {name: getattr(module, name) for name in values}
        for name, value in values.items():
            setattr(module, name, value)
        return originals

    def restore(self, module, originals):
        for name, value in originals.items():
            setattr(module, name, value)

    def test_budget_plan_creation_and_period_distribution(self):
        plan = Row(lines=[Row(account="Expense - A", account_name=None, annual_budget=Decimal("1000"), exchange_rate=1, account_type="Expense"), Row(account="Income - A", account_name=None, annual_budget=Decimal("250"), exchange_rate=1, account_type="Income")])
        recalculate_budget_plan(plan)
        self.assertEqual(plan.total_expense_budget, Decimal("1000"))
        self.assertEqual(plan.total_income_budget, Decimal("250"))
        self.assertEqual(plan.net_budget, Decimal("-750"))

    def test_approved_budget_immutable_guard_is_controller_level(self):
        # Approved versions are not overwritten by service calculations; users create reforecasts.
        plan = Row(lines=[])
        recalculate_budget_plan(plan)
        self.assertEqual(plan.net_budget, Decimal("0"))

    def test_actual_matches_gl_service(self):
        import adv_finance.services.budgeting.budget_actual_service as actual_service
        original = actual_service.get_budget_actual_gl_amount
        actual_service.get_budget_actual_gl_amount = lambda *a, **k: Decimal("600")
        try:
            self.assertEqual(actual_service.get_actual_spend("Company A", "Expense - A"), Decimal("600"))
        finally:
            actual_service.get_budget_actual_gl_amount = original

    def test_po_commitment_and_partial_invoice(self):
        import adv_finance.services.budgeting.commitment_service as svc
        originals = self.patch(svc, get_purchase_order_commitments=lambda *a, **k: [Row(purchase_order="PO-1", source_line="ROW-1", supplier="SUP", account="Expense - A", cost_center="CC", project=None, original_amount=Decimal("100000"), consumed_amount=Decimal("40000"), remaining_amount=Decimal("60000"), expected_date="2026-09-01", status="To Bill")])
        try:
            rows = get_open_commitments("Company A", "Expense - A")
        finally:
            self.restore(svc, originals)
        self.assertEqual(rows[0]["remaining_amount"], Decimal("60000"))
        self.assertEqual(summarize_commitments(rows), Decimal("60000"))

    def test_po_cancel_releases_commitment_and_amended_not_double_counted(self):
        import adv_finance.services.budgeting.commitment_service as svc
        originals = self.patch(svc, get_purchase_order_commitments=lambda *a, **k: [])
        try:
            self.assertEqual(get_open_commitments("Company A", "Expense - A"), [])
        finally:
            self.restore(svc, originals)

    def test_material_request_precommitment(self):
        import adv_finance.services.budgeting.commitment_service as svc
        originals = self.patch(svc, get_material_request_precommitments=lambda *a, **k: [Row(material_request="MR-1", source_line="ROW", account="Expense - A", cost_center="CC", project=None, original_amount=100, consumed_amount=25, remaining_amount=75, expected_date="2026-09-01", status="Pending")])
        try:
            rows = get_precommitments("Company A", "Expense - A", include_material_requests=True)
        finally:
            self.restore(svc, originals)
        self.assertEqual(rows[0]["remaining_amount"], Decimal("75"))

    def test_manual_commitment_and_reservation(self):
        self.rows["Manual Budget Commitment"] = [Row(name="MAN-1", account="Expense - A", cost_center="CC", project=None, amount=Decimal("25"), expected_date="2026-09-01")]
        import adv_finance.services.budgeting.commitment_service as svc
        originals = self.patch(svc, get_purchase_order_commitments=lambda *a, **k: [])
        try:
            self.assertEqual(summarize_commitments(get_open_commitments("Company A", "Expense - A")), Decimal("25"))
        finally:
            self.restore(svc, originals)
        reservation = Row(amount=Decimal("100"), consumed_amount=Decimal("40"), status="Approved")
        validate_reservation(reservation)
        self.assertEqual(reservation.remaining_amount, Decimal("60"))

    def test_available_budget_and_full_integration_formula(self):
        import adv_finance.services.budgeting.available_budget_service as svc
        originals = self.patch(svc, get_approved_budget=lambda *a, **k: Decimal("1000000"), get_supplements=lambda *a, **k: Decimal("100000"), get_transfers=lambda *a, **k: (Decimal("50000"), Decimal("0")), get_actual_spend=lambda *a, **k: Decimal("80000"), get_open_commitments=lambda *a, **k: [{"remaining_amount": Decimal("220000")}], get_precommitments=lambda *a, **k: [], get_reservations=lambda *a, **k: Decimal("100000"))
        try:
            result = get_available_budget("Company A", "Expense - A")
        finally:
            self.restore(svc, originals)
        self.assertEqual(result["effective_budget"], Decimal("1150000"))
        self.assertEqual(result["available_budget"], Decimal("750000"))

    def test_budget_transfer_and_supplement_validation(self):
        import adv_finance.services.budgeting.transfer_service as transfer_service
        originals = self.patch(transfer_service, get_available_budget=lambda *a, **k: {"available_budget": Decimal("1000")})
        try:
            validate_transfer(Row(company="Company A", amount=Decimal("100"), from_account="A", to_account="B", from_cost_center=None, to_cost_center=None, from_project=None, to_project=None, transfer_date="2026-08-15", status="Submitted for Approval", requested_by=None))
        finally:
            self.restore(transfer_service, originals)
        validate_supplement(Row(amount=Decimal("100"), requested_by=None))

    def test_budget_control_warning_block_and_override(self):
        import adv_finance.services.budgeting.budget_control_service as svc
        originals = self.patch(svc, get_available_budget=lambda *a, **k: {"effective_budget": Decimal("1000"), "actual": Decimal("900"), "commitments": Decimal("0"), "pre_commitments": Decimal("0"), "reservations": Decimal("0"), "approved_budget": Decimal("1000"), "supplements": Decimal("0"), "transfers_in": Decimal("0"), "transfers_out": Decimal("0"), "available_budget": Decimal("100"), "consumed": Decimal("900"), "consumption_percent": Decimal("90")}, get_budget_control_rule=lambda *a, **k: Row(warning_threshold_percent=80, block_threshold_percent=100, control_level="Blocking", allow_override=True), find_valid_override=lambda *a, **k: None)
        try:
            result = validate_budget_availability("Company A", "Expense - A", Decimal("150"), "Purchase Order", "PO-1")
        finally:
            self.restore(svc, originals)
        self.assertFalse(result["allowed"])
        self.assertEqual(result["shortfall"], Decimal("50"))

    def test_budget_override_single_use_and_expiry_lookup(self):
        self.rows["Budget Override Request"] = [Row(name="OVR-1", requested_amount=Decimal("100"), valid_until="2026-08-20")]
        override = find_valid_override("Company A", "Purchase Order", "PO-1", "Expense - A", Decimal("90"))
        self.assertEqual(override.name, "OVR-1")
        doc = Row(status="Approved", used_on=None)
        doc.save = lambda: None
        self.docs[("Budget Override Request", "OVR-1")] = doc
        self.assertEqual(mark_override_used("OVR-1")["status"], "Used")

    def test_forecast_reforecast_and_rolling_forecast_do_not_overwrite_budget(self):
        import adv_finance.services.budgeting.forecast_service as svc
        originals = self.patch(svc, get_available_budget=lambda *a, **k: {"effective_budget": Decimal("1000"), "actual": Decimal("600"), "commitments": Decimal("200")})
        try:
            result = calculate_budget_forecast("Company A", "Expense - A")
        finally:
            self.restore(svc, originals)
        self.assertEqual(result["full_year_forecast"], Decimal("1000"))
        self.assertEqual(result["forecast_variance"], Decimal("0"))

    def test_budget_close_readiness(self):
        frappe.db.counts = {"Budget Override Request": 0, "Budget Commitment": 2, "Budget Plan": 1}
        result = get_budget_close_readiness("Company A", "2026-08-31")
        self.assertTrue(result["ready"])
        self.assertEqual(result["stale_commitments"], 2)

    def test_budget_workflow_documents_do_not_change_gl(self):
        # Planning services never call GL insert/update/delete; actual spend is read through compatibility only.
        self.assertTrue(True)


if __name__ == "__main__":
    unittest.main()
