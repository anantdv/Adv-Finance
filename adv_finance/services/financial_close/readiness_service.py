from __future__ import annotations

import frappe
from frappe.utils import now_datetime

from adv_finance.services.financial_close.close_service import recalculate_close_period
from adv_finance.services.financial_close.exception_service import replace_task_exceptions
from adv_finance.services.financial_close.provider_registry import get_provider


def refresh_task_readiness(task_name: str) -> dict:
    task = frappe.get_doc("Financial Close Task", task_name)
    period = frappe.get_doc("Financial Close Period", task.financial_close_period)
    provider = get_provider(task.readiness_provider)
    try:
        result = provider.check(task, period)
    except Exception as exc:
        result = {"ready": False, "status": "Failed", "message": f"Unable to verify readiness: {exc}", "exceptions": [], "details": {}}
    task.automated_check = 1
    task.automated_status = "Ready" if result.get("ready") else ("Failed" if result.get("status") == "Failed" else "Not Ready")
    task.automated_message = result.get("message")
    task.last_checked_on = now_datetime()
    if result.get("ready") and task.status in ("Not Started", "In Progress", "Waiting", "Blocked"):
        task.status = "Completed" if task.auto_complete_when_ready else "Ready for Review"
    elif not result.get("ready") and task.status not in ("Completed", "Waived", "Rejected"):
        task.status = "Blocked" if task.blocking else "Waiting"
        task.blocked_reason = result.get("message")
    task.exception_count = len(result.get("exceptions") or [])
    task.save()
    replace_task_exceptions(task, result.get("exceptions") or [])
    recalculate_close_period(period.name)
    return result


def refresh_close_readiness(close_period: str) -> dict:
    names = frappe.get_all("Financial Close Task", filters={"financial_close_period": close_period, "automated_check": 1}, pluck="name")
    results = []
    for name in names:
        results.append(refresh_task_readiness(name))
    recalculate_close_period(close_period)
    return {"checked": len(results)}
