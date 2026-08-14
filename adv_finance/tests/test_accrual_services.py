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
utils.date_diff = lambda left, right: 45
utils.nowdate = lambda: "2026-08-14"
utils.now_datetime = lambda: "2026-08-14 00:00:00"
sys.modules.setdefault("frappe.utils", utils)

from adv_finance.services.accrual.accrual_ageing_service import age_bucket
from adv_finance.services.accrual.accrual_service import recalculate_accrual
from adv_finance.services.accrual.accrual_variance_service import classify_variance, variance_percentage


class Child(types.SimpleNamespace):
    pass


class Accrual(types.SimpleNamespace):
    pass


class TestAccrualServices(unittest.TestCase):
    def test_variance_classification(self):
        self.assertEqual(classify_variance(Decimal("0"), Decimal("0")), "Within Tolerance")
        self.assertEqual(classify_variance(Decimal("5"), Decimal("10")), "Within Tolerance")
        self.assertEqual(classify_variance(Decimal("11"), Decimal("10")), "Under Accrued")
        self.assertEqual(classify_variance(Decimal("-11"), Decimal("10")), "Over Accrued")
        self.assertEqual(classify_variance(Decimal("12"), Decimal("0"), Decimal("10"), Decimal("100")), "Under Accrued")

    def test_variance_percentage_handles_zero_base(self):
        self.assertEqual(variance_percentage(Decimal("10"), Decimal("0")), Decimal("0"))
        self.assertEqual(variance_percentage(Decimal("10"), Decimal("200")), Decimal("5.00"))

    def test_age_bucket(self):
        self.assertEqual(age_bucket(0), "Current")
        self.assertEqual(age_bucket(30), "1-30 Days")
        self.assertEqual(age_bucket(90), "61-90 Days")
        self.assertEqual(age_bucket(181), "180+ Days")

    def test_recalculate_accrual_amounts(self):
        accrual = Accrual(
            accrual_amount=Decimal("1000"),
            variance_tolerance_amount=Decimal("5"),
            variance_tolerance_percentage=None,
            accrual_date="2026-07-01",
            matching_status="Unmatched",
            matches=[
                Child(status="Accepted", matched_amount=Decimal("600"), invoice_amount=Decimal("610")),
                Child(status="Suggested", matched_amount=Decimal("400"), invoice_amount=Decimal("400")),
            ],
        )

        recalculate_accrual(accrual)

        self.assertEqual(accrual.consumed_amount, Decimal("600"))
        self.assertEqual(accrual.actual_amount, Decimal("610"))
        self.assertEqual(accrual.remaining_amount, Decimal("400"))
        self.assertEqual(accrual.variance_amount, Decimal("10"))
        self.assertEqual(accrual.variance_status, "Under Accrued")
        self.assertEqual(accrual.matching_status, "Partially Matched")
        self.assertEqual(accrual.days_open, 45)
        self.assertEqual(accrual.age_bucket, "31-60 Days")


if __name__ == "__main__":
    unittest.main()
