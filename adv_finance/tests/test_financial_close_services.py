import sys
import types
import unittest
from decimal import Decimal


frappe = sys.modules.get("frappe") or types.ModuleType("frappe")
frappe.throw = lambda message: (_ for _ in ()).throw(Exception(message))
frappe.session = types.SimpleNamespace(user="closer@example.com")
frappe.has_role = lambda role: True
sys.modules.setdefault("frappe", frappe)

utils = sys.modules.get("frappe.utils") or types.ModuleType("frappe.utils")
utils.getdate = lambda value=None: value if value is not None else "2026-08-15"
utils.today = lambda: "2026-08-15"
utils.now_datetime = lambda: "2026-08-15 00:00:00"
utils.add_days = lambda value, days: f"{value}+{days}"
utils.date_diff = lambda left, right: 3
sys.modules.setdefault("frappe.utils", utils)

from adv_finance.services.financial_close.close_service import recalculate_close_period
from adv_finance.services.financial_close.dependency_service import get_unmet_dependencies
from adv_finance.services.financial_close.provider_registry import get_provider
from adv_finance.services.financial_close.providers.accrual import AccrualProvider


class Row(types.SimpleNamespace):
    pass


class FakeDB:
    def __init__(self):
        self.status_by_name = {}

    def get_value(self, doctype, name, fieldname=None, as_dict=False):
        if doctype == "Financial Close Task" and fieldname == "status":
            return self.status_by_name.get(name)
        return None


class TestFinancialCloseServices(unittest.TestCase):
    def setUp(self):
        frappe.db = FakeDB()

    def test_recalculate_close_period_counts(self):
        tasks = [
            Row(status="Completed", risk_level="Critical", required=1, blocking=1, due_date="2026-08-10"),
            Row(status="Blocked", risk_level="Critical", required=1, blocking=1, due_date="2026-08-10"),
            Row(status="Not Started", risk_level="Medium", required=1, blocking=1, due_date="2026-08-20"),
            Row(status="Ready for Review", risk_level="High", required=1, blocking=1, due_date="2026-08-14"),
        ]
        frappe.get_all = lambda *args, **kwargs: tasks
        period = Row(name="FIN-CLOSE-1")

        result = recalculate_close_period(period, save=False)

        self.assertEqual(period.total_tasks, 4)
        self.assertEqual(period.completed_tasks, 1)
        self.assertEqual(period.blocked_tasks, 1)
        self.assertEqual(period.critical_open_tasks, 1)
        self.assertEqual(period.overall_completion_percent, Decimal("25.00"))
        self.assertFalse(result["ready"])

    def test_dependency_detects_unmet_task(self):
        frappe.db.status_by_name = {"TASK-A": "In Progress"}
        frappe.get_doc = lambda doctype, name: Row(name=name, task_name="Task A", status="In Progress")
        task = Row(
            financial_close_period="FIN-CLOSE-1",
            dependencies=[Row(depends_on_task="TASK-A", depends_on_task_code="TASK_A", blocking=1)],
        )

        unmet = get_unmet_dependencies(task)

        self.assertEqual(len(unmet), 1)
        self.assertEqual(task.dependencies[0].dependency_status, "Unmet")

    def test_dependency_treats_completed_task_as_met(self):
        frappe.db.status_by_name = {"TASK-A": "Completed"}
        task = Row(
            financial_close_period="FIN-CLOSE-1",
            dependencies=[Row(depends_on_task="TASK-A", depends_on_task_code="TASK_A", blocking=1)],
        )

        self.assertEqual(get_unmet_dependencies(task), [])
        self.assertEqual(task.dependencies[0].dependency_status, "Met")

    def test_provider_registry_defaults_to_manual(self):
        provider = get_provider("missing-provider")
        self.assertEqual(provider.provider_name, "manual")

    def test_accrual_provider_maps_readiness_result(self):
        import adv_finance.services.financial_close.providers.accrual as accrual_provider

        original = accrual_provider.get_accrual_close_readiness
        accrual_provider.get_accrual_close_readiness = lambda company, period_end: {
            "ready": False,
            "unapproved": 1,
            "unposted": 2,
            "missing_reversals": 0,
            "material_variances": 3,
        }
        try:
            result = AccrualProvider().check(Row(), Row(company="Company A", period_end="2026-07-31"))
        finally:
            accrual_provider.get_accrual_close_readiness = original

        self.assertFalse(result["ready"])
        self.assertEqual(len(result["exceptions"]), 3)
        self.assertEqual(result["details"]["unposted"], 2)


if __name__ == "__main__":
    unittest.main()
