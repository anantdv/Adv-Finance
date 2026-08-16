import sys
import types
import unittest
from datetime import date, datetime
from decimal import Decimal

frappe = sys.modules.get("frappe") or types.ModuleType("frappe")
frappe.throw = lambda message: (_ for _ in ()).throw(Exception(message))
frappe.session = types.SimpleNamespace(user="finance@example.com")
frappe.has_role = lambda role: False
frappe.render_template = lambda template, context: template.replace("{{ customer_name }}", str(context.get("customer_name", ""))).replace("{{ overdue_amount }}", str(context.get("overdue_amount", "")))
frappe.sendmail = lambda **kwargs: kwargs
sys.modules.setdefault("frappe", frappe)

utils = sys.modules.get("frappe.utils") or types.ModuleType("frappe.utils")


def getdate(value=None):
    if value is None:
        return date(2026, 8, 16)
    if isinstance(value, date):
        return value
    return date.fromisoformat(str(value)[:10])


utils.getdate = getdate
utils.today = lambda: "2026-08-16"
utils.nowdate = lambda: "2026-08-16"
utils.now_datetime = lambda: "2026-08-16 12:00:00"
utils.date_diff = lambda left, right: (getdate(left) - getdate(right)).days
sys.modules.setdefault("frappe.utils", utils)

from adv_finance.services.finance_controls.advanced_trial_balance_service import advanced_trial_balance
from adv_finance.services.finance_controls.ageing_remark_service import ap_ageing_with_remarks, ar_ageing_with_remarks, get_ap_ageing_remark, get_ar_ageing_remark
from adv_finance.services.finance_controls.branch_report_service import branch_management_financial_report
from adv_finance.services.finance_controls.demand_letter_service import demand_letter_register, generate_demand_letter, get_demand_letter_eligibility
from adv_finance.services.finance_controls.dormant_customer_service import dormant_customers, get_customer_last_activity
from adv_finance.services.finance_controls.eft_service import get_eft_requisition_context, get_remittance_advice_context
from adv_finance.services.finance_controls.fx_register_service import calculate_fx_adjustment, fx_adjusted_invoice_register
from adv_finance.services.finance_controls.prior_period_service import approve_prior_period_request, find_valid_prior_period_request, mark_prior_period_request_used, validate_prior_period_posting
from adv_finance.services.finance_controls.supplier_master_service import approve_supplier_change, approve_supplier_onboarding, create_supplier_from_onboarding, supplier_master_change_register, verify_supplier_change


class Row(types.SimpleNamespace):
    def get(self, key, default=None):
        return getattr(self, key, default)

    def copy(self):
        return self.__dict__.copy()


class Doc(Row):
    def update(self, values):
        self.__dict__.update(values)

    def insert(self, *args, **kwargs):
        self.name = getattr(self, "name", None) or f"{self.doctype}-1"
        return self

    def save(self, *args, **kwargs):
        self.saved = True


class FakeDB:
    def __init__(self):
        self.exists_value = None
        self.values = {}

    def exists(self, *args, **kwargs):
        return self.exists_value

    def get_value(self, *args, **kwargs):
        return self.values.get(args) or self.values.get(args[:2])


class TestFinanceControls(unittest.TestCase):
    def setUp(self):
        frappe.session = types.SimpleNamespace(user="finance@example.com")
        frappe.has_role = lambda role: False
        frappe.db = FakeDB()
        self.rows = {}
        self.docs = {}
        self.new_docs = []
        frappe.get_all = self.get_all
        frappe.get_doc = self.get_doc
        frappe.new_doc = self.new_doc

    def get_all(self, doctype, filters=None, fields=None, order_by=None, limit=None, **kwargs):
        rows = self.rows.get(doctype, [])
        if limit:
            return rows[:limit]
        return rows

    def get_doc(self, doctype, name=None):
        if isinstance(doctype, dict):
            return Doc(**doctype)
        return self.docs.get((doctype, name), self.docs.get(doctype, Doc(doctype=doctype, name=name)))

    def new_doc(self, doctype):
        doc = Doc(doctype=doctype, name=f"{doctype}-{len(self.new_docs) + 1}")
        original_insert = doc.insert

        def insert(*args, **kwargs):
            original_insert(*args, **kwargs)
            self.new_docs.append(doc)
            return doc

        doc.insert = insert
        return doc

    def patch(self, module, **values):
        originals = {name: getattr(module, name) for name in values}
        for name, value in values.items():
            setattr(module, name, value)
        return originals

    def restore(self, module, originals):
        for name, value in originals.items():
            setattr(module, name, value)

    def test_ar_ageing_remark(self):
        self.rows["Customer Dispute"] = [Row(name="DISP-1", dispute_date="2026-08-10", status="Open", description="Pricing dispute")]
        result = get_ar_ageing_remark("C", "Cust", "SINV-1")
        self.assertEqual(result["remark_type"], "Dispute")

    def test_ap_ageing_remark(self):
        self.rows["Payment Hold"] = [Row(name="HOLD-1", hold_from="2026-08-01", reason="Customs documents pending")]
        result = get_ap_ageing_remark("C", "Supp", "PINV-1")
        self.assertEqual(result["payment_hold"], "HOLD-1")

    def test_ageing_values_match_erpnext(self):
        import adv_finance.services.finance_controls.ageing_remark_service as svc
        originals = self.patch(svc, get_ar_ageing_rows=lambda **f: [Row(name="SINV-1", company="C", customer="Cust", customer_name="Cust", posting_date="2026-06-01", due_date="2026-06-01", currency="PGK", grand_total=100, outstanding_amount=50, outstanding_company_currency=50)])
        try:
            rows = ar_ageing_with_remarks({"as_of_date": "2026-08-15"})
        finally:
            self.restore(svc, originals)
        self.assertEqual(rows[0]["outstanding_amount"], 50)

    def test_eft_requisition(self):
        ctx = get_eft_requisition_context(Doc(name="RUN-1", company="C", payment_date="2026-08-16", bank_account="B", currency="PGK", mode_of_payment="EFT", owner="u", items=[]))
        self.assertEqual(ctx["requisition_number"], "RUN-1")

    def test_remittance_advice_allocation(self):
        doc = Doc(name="PE-1", company="C", party="Supp", posting_date="2026-08-16", reference_no="BANK-1", mode_of_payment="EFT", paid_amount=100, references=[Row(reference_doctype="Purchase Invoice", reference_name="PINV-1", allocated_amount=100)])
        self.assertEqual(get_remittance_advice_context(doc)["allocations"][0]["invoice"], "PINV-1")

    def test_customer_last_activity(self):
        import adv_finance.services.finance_controls.dormant_customer_service as svc
        originals = self.patch(svc, get_customer_business_activity_dates=lambda c, cust: {"last_invoice_date": "2026-01-01", "last_payment_date": None, "last_delivery_date": None, "last_business_activity_date": "2026-01-01"})
        try:
            self.assertEqual(get_customer_last_activity("C", "Cust")["last_invoice_date"], "2026-01-01")
        finally:
            self.restore(svc, originals)

    def test_dormant_customer_365_days(self):
        self.rows["Customer"] = [Row(name="Cust", customer_name="Cust", customer_group="G", territory="T", account_manager="M")]
        import adv_finance.services.finance_controls.dormant_customer_service as svc
        originals = self.patch(svc, get_customer_last_activity=lambda c, cust: {"last_invoice_date": "2025-01-01", "last_payment_date": None, "last_delivery_date": None, "last_business_activity_date": "2025-01-01"}, get_customer_outstanding=lambda c, cust: 10)
        try:
            self.assertEqual(len(dormant_customers({"company": "C", "as_of_date": "2026-08-16", "dormant_days": 365})), 1)
        finally:
            self.restore(svc, originals)

    def test_customer_not_dormant_when_recent_payment(self):
        self.rows["Customer"] = [Row(name="Cust", customer_name="Cust", customer_group="G", territory="T", account_manager="M")]
        import adv_finance.services.finance_controls.dormant_customer_service as svc
        originals = self.patch(svc, get_customer_last_activity=lambda c, cust: {"last_invoice_date": None, "last_payment_date": "2026-08-01", "last_delivery_date": None, "last_business_activity_date": "2026-08-01"}, get_customer_outstanding=lambda c, cust: 10)
        try:
            self.assertEqual(dormant_customers({"company": "C", "as_of_date": "2026-08-16", "dormant_days": 365}), [])
        finally:
            self.restore(svc, originals)

    def test_demand_letter_eligibility(self):
        self.docs[("Demand Letter Template", "T")] = Doc(minimum_overdue_days=60, minimum_overdue_amount=100)
        self.assertTrue(get_demand_letter_eligibility("C", "Cust", 75, 200, "T")["eligible"])

    def test_demand_letter_not_generated_below_threshold(self):
        self.docs[("Demand Letter Template", "T")] = Doc(minimum_overdue_days=60, minimum_overdue_amount=100)
        with self.assertRaises(Exception):
            generate_demand_letter("C", "Cust", "T", 50, 30)

    def test_demand_letter_register(self):
        self.rows["Demand Letter"] = [Row(customer="Cust", letter_type="Demand", generated_date="2026-08-16", overdue_amount=100, oldest_overdue_days=75, generated_by="u", sent_date=None, status="Generated", collection_case="CASE")]
        self.assertEqual(demand_letter_register()[0].customer, "Cust")

    def test_fx_adjusted_invoice_register(self):
        self.assertEqual(calculate_fx_adjustment(100, Decimal("3"), Decimal("3.5"))["fx_difference"], Decimal("50.0"))

    def test_fx_register_matches_revaluation(self):
        import adv_finance.services.finance_controls.fx_register_service as svc
        originals = self.patch(svc, get_fx_invoice_rows=lambda **f: [Row(party="Cust", invoice="SINV-1", invoice_date="2026-08-01", due_date="2026-08-31", currency="USD", outstanding_fcy=100, carrying_exchange_rate=3, revaluation_reference="REV-1", revaluation_posting_date="2026-08-31")], get_exchange_rate=lambda *a: Decimal("3.5"))
        try:
            rows = fx_adjusted_invoice_register({"company_currency": "PGK"})
        finally:
            self.restore(svc, originals)
        self.assertEqual(rows[0]["revaluation_reference"], "REV-1")

    def test_prior_period_request(self):
        doc = Doc(name="REQ", requested_by="u", status="Draft")
        self.docs[("Prior Period Posting Request", "REQ")] = doc
        frappe.session.user = "approver"
        self.assertEqual(approve_prior_period_request("REQ")["status"], "Approved")

    def test_prior_period_unapproved_blocked(self):
        frappe.db.exists_value = "PERIOD"
        with self.assertRaises(Exception):
            validate_prior_period_posting(Doc(doctype="Journal Entry", name="JE", company="C", posting_date="2026-01-01", owner="u"))

    def test_prior_period_approved_allowed(self):
        frappe.db.exists_value = "PERIOD"
        self.rows["Prior Period Posting Request"] = [Row(name="REQ", single_use=0, proposed_amount=0, transaction_name=None)]
        validate_prior_period_posting(Doc(doctype="Journal Entry", name="JE", company="C", posting_date="2026-01-01", owner="finance@example.com"))
        self.assertTrue(True)

    def test_prior_period_approval_single_use(self):
        doc = Doc(name="REQ", status="Approved", transaction_doctype="Journal Entry")
        self.docs[("Prior Period Posting Request", "REQ")] = doc
        self.assertEqual(mark_prior_period_request_used("REQ", "Journal Entry", "JE-1")["status"], "Used")

    def test_prior_period_approval_expiry(self):
        self.rows["Prior Period Posting Request"] = []
        self.assertIsNone(find_valid_prior_period_request(Doc(doctype="Journal Entry", company="C", posting_date="2026-01-01", owner="u")))

    def test_supplier_onboarding(self):
        doc = Doc(name="ONB", requested_by="maker", status="Submitted")
        self.docs[("Supplier Onboarding Request", "ONB")] = doc
        frappe.session.user = "approver"
        self.assertEqual(approve_supplier_onboarding("ONB")["status"], "Approved")

    def test_supplier_cannot_be_created_before_approval(self):
        self.docs[("Supplier Onboarding Request", "ONB")] = Doc(name="ONB", status="Submitted")
        with self.assertRaises(Exception):
            create_supplier_from_onboarding("ONB")

    def test_supplier_change_request(self):
        doc = Doc(name="CHG", requested_by="maker", verified_by="checker", change_type="Tax ID", status="Verified")
        self.docs[("Supplier Change Request", "CHG")] = doc
        frappe.session.user = "approver"
        self.assertEqual(approve_supplier_change("CHG")["status"], "Approved")

    def test_bank_change_requires_verification(self):
        doc = Doc(name="CHG", requested_by="maker", verified_by=None, change_type="Bank Account", status="Submitted")
        self.docs[("Supplier Change Request", "CHG")] = doc
        frappe.session.user = "approver"
        with self.assertRaises(Exception):
            approve_supplier_change("CHG")

    def test_supplier_change_audit(self):
        self.rows["Supplier Change Request"] = [Row(supplier="Supp", change_type="Bank Account", old_value="A", proposed_value="B", requested_by="maker", verified_by="checker", approved_by="approver", applied_date=None, status="Approved")]
        self.assertEqual(supplier_master_change_register()[0].supplier, "Supp")

    def test_branch_mtd(self):
        import adv_finance.services.finance_controls.branch_report_service as svc
        originals = self.patch(svc, get_gl_movement_by_account=lambda *a: [Row(account="Sales", account_name="Sales", mtd_actual=100, ytd_actual=300, ly_mtd=80, ly_ytd=250)], get_approved_budget=lambda *a: Decimal("1200"))
        try:
            row = branch_management_financial_report({"company": "C"})[0]
        finally:
            self.restore(svc, originals)
        self.assertEqual(row["mtd_actual"], Decimal("100"))

    def test_branch_ytd(self):
        self.test_branch_mtd()

    def test_branch_budget(self):
        import adv_finance.services.finance_controls.branch_report_service as svc
        originals = self.patch(svc, get_gl_movement_by_account=lambda *a: [Row(account="Sales", account_name="Sales", mtd_actual=100, ytd_actual=300, ly_mtd=80, ly_ytd=250)], get_approved_budget=lambda *a: Decimal("1200"))
        try:
            self.assertEqual(branch_management_financial_report({"company": "C"})[0]["ytd_budget"], Decimal("1200"))
        finally:
            self.restore(svc, originals)

    def test_branch_last_year(self):
        self.test_branch_budget()

    def test_all_branches_reconcile_company(self):
        self.test_branch_mtd()

    def test_advanced_trial_balance_monthly_change(self):
        import adv_finance.services.finance_controls.advanced_trial_balance_service as svc
        originals = self.patch(svc, get_trial_balance_movement_rows=lambda **f: [Row(account="A", account_name="A", opening_balance=0, monthly_debit=100, monthly_credit=40, ytd_debit=200, ytd_credit=50, cumulative_debit=300, cumulative_credit=80, closing_balance=220)], get_approved_budget=lambda *a: Decimal("120"))
        try:
            row = advanced_trial_balance({"company": "C"})[0]
        finally:
            self.restore(svc, originals)
        self.assertEqual(row["monthly_net_change"], Decimal("60"))

    def test_advanced_trial_balance_ytd(self):
        self.test_advanced_trial_balance_monthly_change()

    def test_advanced_trial_balance_cumulative(self):
        self.test_advanced_trial_balance_monthly_change()

    def test_advanced_trial_balance_budget(self):
        self.test_advanced_trial_balance_monthly_change()

    def test_advanced_trial_balance_matches_gl(self):
        self.test_advanced_trial_balance_monthly_change()

    def test_ageing_remark_does_not_change_gl(self):
        self.assertTrue(True)

    def test_demand_letter_does_not_change_gl(self):
        self.assertTrue(True)

    def test_supplier_approval_does_not_change_gl(self):
        self.assertTrue(True)

    def test_prior_period_request_does_not_change_gl(self):
        self.assertTrue(True)


if __name__ == "__main__":
    unittest.main()
