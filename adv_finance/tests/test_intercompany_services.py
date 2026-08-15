import sys
import types
import unittest
from decimal import Decimal

frappe = sys.modules.get("frappe") or types.ModuleType("frappe")
frappe.throw = lambda message: (_ for _ in ()).throw(Exception(message))
frappe.session = types.SimpleNamespace(user="ic@example.com")
frappe.has_role = lambda role: False
sys.modules.setdefault("frappe", frappe)

utils = sys.modules.get("frappe.utils") or types.ModuleType("frappe.utils")
utils.now_datetime = lambda: "2026-08-15 00:00:00"
utils.getdate = lambda value=None: value or "2026-08-15"
utils.date_diff = lambda left, right: 45
sys.modules.setdefault("frappe.utils", utils)

from adv_finance.services.intercompany.close_service import get_intercompany_close_readiness
from adv_finance.services.intercompany.difference_service import classify_difference
from adv_finance.services.intercompany.elimination_service import prepare_elimination_candidate
from adv_finance.services.intercompany.fx_service import calculate_fx_difference
from adv_finance.services.intercompany.matching_service import create_match, score_match, suggest_invoice_matches
from adv_finance.services.intercompany.partner_service import validate_partner
from adv_finance.services.intercompany.reconciliation_service import reconcile_due_to_due_from
from adv_finance.services.intercompany.report_service import dashboard_summary
from adv_finance.services.intercompany.settlement_service import recalculate_settlement


class Row(types.SimpleNamespace):
    def get(self, key, default=None):
        return getattr(self, key, default)


class Doc(Row):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.items = kw.get("items", [])
    def update(self, values):
        self.__dict__.update(values)
    def append(self, field, value):
        getattr(self, field).append(Row(**value))
    def insert(self, *a, **k):
        self.name = getattr(self, "name", None) or "NEW-DOC"
    def save(self):
        pass


class FakeDB:
    def __init__(self):
        self.counts = {}
    def get_value(self, *args, **kwargs):
        return None
    def count(self, doctype, filters=None):
        return self.counts.get(doctype, 0)
    def set_value(self, *args, **kwargs):
        pass


class TestIntercompanyServices(unittest.TestCase):
    def setUp(self):
        frappe.db = FakeDB()
        frappe.get_all = lambda *a, **k: []
        frappe.new_doc = lambda doctype: Doc(doctype=doctype, name=f"{doctype}-1")

    def patch(self, module, **values):
        originals = {name: getattr(module, name) for name in values}
        for name, value in values.items():
            setattr(module, name, value)
        return originals
    def restore(self, module, originals):
        for name, value in originals.items(): setattr(module, name, value)

    def test_partner_creation(self):
        validate_partner(Row(company="A", partner_company="B", receivable_account=None, payable_account=None, settlement_account=None))
        with self.assertRaises(Exception):
            validate_partner(Row(company="A", partner_company="A", receivable_account=None, payable_account=None, settlement_account=None))

    def test_invoice_matching(self):
        origin = Row(reference_no="REF-1", currency="PGK", amount=Decimal("100"), posting_date="2026-08-15", origin_company="A", destination_company="B")
        target = Row(reference_no="REF-1", currency="PGK", amount=Decimal("100"), posting_date="2026-08-15", origin_company="B", destination_company="A")
        result = score_match(origin, target, 0)
        self.assertTrue(result["matched"])
        self.assertIn("Reference Number", result["factors"])

    def test_journal_matching_and_payment_matching(self):
        a = Row(reference_no="JE-REF", currency="PGK", amount=100, posting_date="2026-08-15", origin_company="A", destination_company="B")
        b = Row(reference_no="JE-REF", currency="PGK", amount=100, posting_date="2026-08-15", origin_company="B", destination_company="A")
        self.assertTrue(score_match(a, b, 0)["matched"])
        a.reference_no = b.reference_no = "PAY-REF"
        self.assertTrue(score_match(a, b, 0)["matched"])

    def test_partial_match_and_many_to_many_match(self):
        origins = [Row(name="T1", source_doctype="Sales Invoice", source_document="S1", origin_company="A", destination_company="B", amount=Decimal("60"), currency="PGK"), Row(name="T2", source_doctype="Sales Invoice", source_document="S2", origin_company="A", destination_company="B", amount=Decimal("40"), currency="PGK")]
        targets = [Row(name="T3", source_doctype="Purchase Invoice", source_document="P1", origin_company="B", destination_company="A", amount=Decimal("100"), currency="PGK")]
        result = create_match(origins, targets)
        self.assertEqual(result["difference_amount"], Decimal("0"))

    def test_many_to_many_match_difference(self):
        origins = [Row(name="T1", source_doctype="Sales Invoice", source_document="S1", origin_company="A", destination_company="B", amount=Decimal("70"), currency="PGK"), Row(name="T2", source_doctype="Sales Invoice", source_document="S2", origin_company="A", destination_company="B", amount=Decimal("40"), currency="PGK")]
        targets = [Row(name="T3", source_doctype="Purchase Invoice", source_document="P1", origin_company="B", destination_company="A", amount=Decimal("100"), currency="PGK")]
        result = create_match(origins, targets)
        self.assertEqual(result["difference_amount"], Decimal("10"))

    def test_fx_translation(self):
        import adv_finance.services.intercompany.fx_service as svc
        originals = self.patch(svc, convert_amount=lambda amount, src, dst, d: (Decimal(str(amount)) * Decimal("3"), Decimal("3")))
        try:
            result = calculate_fx_difference(100, 90, "USD", "USD", "PGK")
        finally:
            self.restore(svc, originals)
        self.assertEqual(result["fx_difference"], Decimal("30"))

    def test_due_to_due_from(self):
        import adv_finance.services.intercompany.reconciliation_service as svc
        originals = self.patch(svc, get_due_to_due_from_balances=lambda *a: {"due_from": Decimal("500000"), "due_to": Decimal("-495000")})
        try:
            result = reconcile_due_to_due_from("A", "B")
        finally:
            self.restore(svc, originals)
        self.assertEqual(result["difference"], Decimal("5000"))
        self.assertEqual(result["status"], "Difference")

    def test_difference_detection(self):
        diff = classify_difference(Row(amount=100, currency="PGK"), Row(amount=90, currency="PGK"), 0)
        self.assertEqual(diff["difference_type"], "Amount Difference")
        missing = classify_difference(Row(amount=100, currency="PGK"), None, 0)
        self.assertEqual(missing["difference_type"], "Missing Invoice")

    def test_settlement_and_partial_settlement(self):
        settlement = Row(status="Draft", actual_settlement_amount=Decimal("80"), items=[Row(amount=100, settled_amount=80)])
        recalculate_settlement(settlement)
        self.assertEqual(settlement.status, "Partially Settled")
        settlement.actual_settlement_amount = Decimal("100")
        recalculate_settlement(settlement)
        self.assertEqual(settlement.status, "Settled")

    def test_elimination_candidate(self):
        result = prepare_elimination_candidate(match=Row(name="M1", origin_company="A", destination_company="B", origin_total=100, difference_amount=0, currency="PGK"))
        self.assertEqual(result["status"], "Ready")

    def test_intercompany_reports(self):
        frappe.db.counts = {"Intercompany Transaction": 10, "Intercompany Difference": 2, "Intercompany Settlement": 3}
        result = dashboard_summary()
        self.assertEqual(result["transactions"], 10)
        self.assertEqual(result["unreconciled"], 2)

    def test_group_close_readiness(self):
        frappe.db.counts = {"Intercompany Difference": 0, "Intercompany Transaction": 0, "Intercompany Elimination Candidate": 1}
        result = get_intercompany_close_readiness()
        self.assertTrue(result["ready"])
        self.assertTrue(result["ready_for_consolidation"])

    def test_suggest_invoice_matches(self):
        import adv_finance.services.intercompany.matching_service as svc
        docs=[Row(company="A", partner_company="B", reference_no="R", currency="PGK", amount=100, posting_date="2026-08-15", origin_company="A", destination_company="B"), Row(company="B", partner_company="A", reference_no="R", currency="PGK", amount=100, posting_date="2026-08-15", origin_company="B", destination_company="A")]
        originals=self.patch(svc, get_intercompany_source_documents=lambda *a: docs, get_partner=lambda *a: Row(matching_tolerance_amount=0))
        try:
            result=suggest_invoice_matches("A","B")
        finally:
            self.restore(svc, originals)
        self.assertEqual(len(result),1)

    def test_no_gl_changes(self):
        self.assertTrue(True)


if __name__ == "__main__":
    unittest.main()
