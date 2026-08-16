import sys
import types
import unittest
from decimal import Decimal
from pathlib import Path

frappe = sys.modules.get("frappe") or types.ModuleType("frappe")
frappe.throw = lambda message: (_ for _ in ()).throw(Exception(message))
frappe.session = types.SimpleNamespace(user="group@example.com")
frappe.has_role = lambda role: False
sys.modules.setdefault("frappe", frappe)

utils = sys.modules.get("frappe.utils") or types.ModuleType("frappe.utils")
utils.now_datetime = lambda: "2026-08-16 00:00:00"
sys.modules.setdefault("frappe.utils", utils)

from adv_finance.services.consolidation.close_service import advance_period_status, get_consolidation_close_readiness
from adv_finance.services.consolidation.group_service import validate_group
from adv_finance.services.consolidation.ownership_service import apply_ownership
from adv_finance.services.consolidation.ratio_service import group_ratios
from adv_finance.services.consolidation.report_service import balance_sheet, cash_flow, consolidated_trial_balance, profit_loss
from adv_finance.services.consolidation.snapshot_service import collect_trial_balance_snapshot
from adv_finance.services.consolidation.translation_service import get_translation_rate_type, translate_trial_balance_row


class Row(types.SimpleNamespace):
    def get(self, key, default=None):
        return getattr(self, key, default)


class Doc(Row):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.companies = kw.get("companies", [])
        self.saved = False

    def update(self, values):
        self.__dict__.update(values)

    def append(self, field, value):
        getattr(self, field).append(Row(**value))

    def insert(self, *args, **kwargs):
        self.name = getattr(self, "name", None) or f"{self.doctype}-1"
        return self

    def save(self, *args, **kwargs):
        self.saved = True
        return self


class FakeDB:
    def __init__(self):
        self.counts = {}
        self.exists_calls = []

    def count(self, doctype, filters=None):
        return self.counts.get(doctype, 0)

    def exists(self, doctype, filters=None):
        self.exists_calls.append((doctype, filters))
        return False

    def get_value(self, *args, **kwargs):
        return None


class TestConsolidationServices(unittest.TestCase):
    def setUp(self):
        frappe.db = FakeDB()
        frappe.session = types.SimpleNamespace(user="group@example.com")
        self.new_docs = []
        self.docs = {}
        frappe.delete_doc = lambda *a, **k: None
        frappe.get_doc = lambda doctype, name=None: self.docs.get((doctype, name), self.docs.get(doctype))
        frappe.get_all = lambda *a, **k: []

        def new_doc(doctype):
            doc = Doc(doctype=doctype, name=f"{doctype}-{len(self.new_docs) + 1}")
            original_insert = doc.insert

            def insert(*args, **kwargs):
                original_insert(*args, **kwargs)
                self.new_docs.append(doc)
                return doc

            doc.insert = insert
            return doc

        frappe.new_doc = new_doc

    def patch(self, module, **values):
        originals = {name: getattr(module, name) for name in values}
        for name, value in values.items():
            setattr(module, name, value)
        return originals

    def restore(self, module, originals):
        for name, value in originals.items():
            setattr(module, name, value)

    def test_group_creation_validation_defaults_currency(self):
        group = Doc(reporting_currency="PGK", companies=[Row(company="A", ownership_percent=100, reporting_currency=None)])
        validate_group(group)
        self.assertEqual(group.companies[0].reporting_currency, "PGK")
        with self.assertRaises(Exception):
            validate_group(Doc(reporting_currency="PGK", companies=[Row(company="A", ownership_percent=100), Row(company="A", ownership_percent=50)]))

    def test_currency_translation_rules_and_difference(self):
        import adv_finance.services.consolidation.translation_service as svc

        originals = self.patch(svc, convert_amount=lambda amount, src, dst, d: (Decimal(str(amount)) * Decimal("3.5"), Decimal("3.5")))
        try:
            result = translate_trial_balance_row(Row(balance=100, currency="USD", root_type="Asset"), "PGK", "2026-08-31")
        finally:
            self.restore(svc, originals)
        self.assertEqual(result["translated_amount"], Decimal("350.0"))
        self.assertEqual(result["translation_difference"], Decimal("250.0"))

    def test_average_closing_historical_rate_mapping(self):
        self.assertEqual(get_translation_rate_type("Asset"), "Closing Rate")
        self.assertEqual(get_translation_rate_type("Liability"), "Closing Rate")
        self.assertEqual(get_translation_rate_type("Income"), "Average Rate")
        self.assertEqual(get_translation_rate_type("Expense"), "Average Rate")
        self.assertEqual(get_translation_rate_type("Equity"), "Historical Rate")

    def test_ownership_methods_and_minority_interest(self):
        self.assertEqual(apply_ownership(100, 100, "Full Consolidation")["owned_amount"], Decimal("100"))
        self.assertEqual(apply_ownership(100, 60, "Full Consolidation")["minority_interest_amount"], Decimal("40"))
        self.assertEqual(apply_ownership(100, 60, "Proportionate")["owned_amount"], Decimal("60"))
        self.assertEqual(apply_ownership(100, 35, "Equity Method")["owned_amount"], Decimal("35"))

    def test_trial_balance_snapshot_collection(self):
        import adv_finance.services.consolidation.snapshot_service as svc

        period = Doc(name="PER-1", consolidation_group="GRP", start_date="2026-08-01", end_date="2026-08-31", status="Open")
        group = Doc(name="GRP", reporting_currency="PGK")
        self.docs = {("Consolidation Period", "PER-1"): period, ("Consolidation Group", "GRP"): group}
        originals = self.patch(
            svc,
            get_group_companies=lambda name: [Row(company="Company A", active=1, consolidation_method="Full Consolidation", functional_currency="USD", reporting_currency="PGK")],
            get_company_trial_balance_rows=lambda *a: [Row(account="Cash - A", account_name="Cash", root_type="Asset", balance=Decimal("100"), currency="USD")],
            translate_trial_balance_row=lambda row, cur, end: {"exchange_rate": Decimal("3"), "translated_amount": Decimal("300"), "translation_difference": Decimal("200")},
        )
        try:
            result = collect_trial_balance_snapshot("PER-1")
        finally:
            self.restore(svc, originals)
        self.assertEqual(result["snapshots"], 1)
        self.assertEqual(self.new_docs[0].doctype, "Trial Balance Snapshot")
        self.assertEqual(self.new_docs[0].translated_amount, Decimal("300"))
        self.assertEqual(period.translation_status, "Translated")

    def test_elimination_generation(self):
        import adv_finance.services.consolidation.elimination_service as svc

        period = Doc(name="PER-1")
        self.docs = {("Consolidation Period", "PER-1"): period}
        frappe.get_all = lambda doctype, **kwargs: [Row(name="CAN-1", origin_company="A", destination_company="B", amount=Decimal("10"), currency="PGK", intercompany_match="M1", intercompany_transaction="T1")] if doctype == "Intercompany Elimination Candidate" else []
        result = svc.generate_elimination_journals("PER-1")
        self.assertEqual(result["elimination_journals"], 1)
        self.assertEqual(self.new_docs[0].doctype, "Elimination Journal")
        self.assertEqual(period.elimination_status, "Generated")

    def test_consolidated_trial_balance_adjustment_and_elimination(self):
        import adv_finance.services.consolidation.consolidation_service as svc

        period = Doc(name="PER-1", consolidation_group="GRP", status="Open")
        self.docs = {("Consolidation Period", "PER-1"): period}
        snapshots = [Row(company="A", account="Cash", account_name="Cash", root_type="Asset", translated_amount=Decimal("100"), translation_difference=Decimal("0"), currency="PGK")]
        def get_all(doctype, filters=None, fields=None, order_by=None):
            if doctype == "Consolidated Trial Balance Line":
                return []
            if doctype == "Trial Balance Snapshot":
                return snapshots
            if doctype == "Elimination Journal":
                return [Row(debit_account="Cash", credit_account=None, amount=Decimal("10"))]
            if doctype == "Consolidation Adjustment":
                return [Row(account="Cash", amount=Decimal("5"))]
            return []
        frappe.get_all = get_all
        originals = self.patch(svc, get_group_companies=lambda group: [Row(company="A", ownership_percent=80, consolidation_method="Full Consolidation")])
        try:
            result = svc.generate_consolidated_trial_balance("PER-1")
        finally:
            self.restore(svc, originals)
        self.assertEqual(result["lines"], 1)
        self.assertEqual(self.new_docs[0].final_amount, Decimal("95"))
        self.assertEqual(self.new_docs[0].minority_interest_amount, Decimal("20"))

    def test_consolidated_reports(self):
        rows = [
            Row(company="A", account="Cash", account_name="Cash", root_type="Asset", company_total=100, translation_amount=0, elimination_amount=0, adjustment_amount=0, minority_interest_amount=10, final_amount=100, currency="PGK"),
            Row(company="A", account="Payable", account_name="Payable", root_type="Liability", company_total=-40, translation_amount=0, elimination_amount=0, adjustment_amount=0, minority_interest_amount=0, final_amount=-40, currency="PGK"),
            Row(company="A", account="Revenue", account_name="Revenue", root_type="Income", company_total=80, translation_amount=0, elimination_amount=0, adjustment_amount=0, minority_interest_amount=0, final_amount=80, currency="PGK"),
            Row(company="A", account="Expense", account_name="Expense", root_type="Expense", company_total=25, translation_amount=0, elimination_amount=0, adjustment_amount=0, minority_interest_amount=0, final_amount=25, currency="PGK"),
        ]
        frappe.get_all = lambda *a, **k: rows
        self.assertEqual(len(consolidated_trial_balance("PER-1")), 4)
        self.assertEqual(balance_sheet("PER-1")["Asset"], Decimal("100"))
        self.assertEqual(profit_loss("PER-1")["Net Profit"], Decimal("55"))
        self.assertEqual(cash_flow("PER-1")["Closing Cash"], Decimal("100"))

    def test_group_ratios(self):
        rows = [
            Row(root_type="Asset", final_amount=Decimal("200"), minority_interest_amount=0, account_name="Cash"),
            Row(root_type="Liability", final_amount=Decimal("-50"), minority_interest_amount=0, account_name="Debt"),
            Row(root_type="Equity", final_amount=Decimal("-100"), minority_interest_amount=0, account_name="Equity"),
            Row(root_type="Income", final_amount=Decimal("100"), minority_interest_amount=0, account_name="Sales"),
            Row(root_type="Expense", final_amount=Decimal("40"), minority_interest_amount=0, account_name="Expense"),
        ]
        frappe.get_all = lambda *a, **k: rows
        self.assertEqual(group_ratios("PER-1")["Net Margin"], Decimal("0.6"))

    def test_close_workflow(self):
        period = Doc(name="PER-1", status="Review")
        self.docs = {("Consolidation Period", "PER-1"): period}
        self.assertEqual(advance_period_status("PER-1", "Closed")["status"], "Closed")
        self.assertEqual(period.closed_by, "group@example.com")
        frappe.db.counts = {"Trial Balance Snapshot": 1, "Consolidated Trial Balance Line": 1, "Consolidation Adjustment": 0, "Intercompany Elimination Candidate": 0}
        self.assertTrue(get_consolidation_close_readiness("PER-1")["ready"])

    def test_no_gl_changes(self):
        service_dir = Path("adv_finance/services/consolidation")
        source = "\\n".join(path.read_text() for path in service_dir.glob("*.py"))
        self.assertNotIn('new_doc("GL Entry"', source)
        self.assertNotIn('delete_doc("GL Entry"', source)
        self.assertNotIn('set_value("GL Entry"', source)
        self.assertNotIn('new_doc("Payment Ledger Entry"', source)


if __name__ == "__main__":
    unittest.main()
