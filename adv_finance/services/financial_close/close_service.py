from __future__ import annotations

from decimal import Decimal

import frappe
from frappe.utils import getdate, now_datetime, today

COMPLETED_STATUSES = ("Completed", "Waived")
ACTIVE_STATUSES = ("Draft", "Open", "In Progress", "Ready for Review", "Review", "Approved for Close", "Closing", "Reopened")


def recalculate_close_period(close_period, save: bool = True) -> dict:
    if isinstance(close_period, str):
        close_period = frappe.get_doc("Financial Close Period", close_period)
    tasks = frappe.get_all(
        "Financial Close Task",
        filters={"financial_close_period": close_period.name},
        fields=["status", "risk_level", "required", "blocking", "due_date"],
    )
    total = len(tasks)
    completed = sum(1 for row in tasks if row.status in COMPLETED_STATUSES)
    in_progress = sum(1 for row in tasks if row.status in ("In Progress", "Waiting", "Ready for Review"))
    blocked = sum(1 for row in tasks if row.status == "Blocked")
    not_started = sum(1 for row in tasks if row.status == "Not Started")
    overdue = sum(1 for row in tasks if row.due_date and getdate(row.due_date) < getdate(today()) and row.status not in COMPLETED_STATUSES)
    critical_open = sum(1 for row in tasks if row.risk_level == "Critical" and row.status not in COMPLETED_STATUSES)
    completion = (Decimal(completed) / Decimal(total) * Decimal(100)) if total else Decimal(0)
    close_period.total_tasks = total
    close_period.completed_tasks = completed
    close_period.in_progress_tasks = in_progress
    close_period.blocked_tasks = blocked
    close_period.overdue_tasks = overdue
    close_period.not_started_tasks = not_started
    close_period.critical_open_tasks = critical_open
    close_period.overall_completion_percent = completion
    close_period.close_readiness = "Ready" if total and completed == total and not blocked and not critical_open else "Not Ready"
    if save:
        close_period.save()
    return {
        "ready": close_period.close_readiness == "Ready",
        "completion_percent": completion,
        "critical_open": critical_open,
        "blocked": blocked,
        "overdue": overdue,
        "unmet_requirements": [],
    }


def get_financial_close_readiness(close_period: str) -> dict:
    period = frappe.get_doc("Financial Close Period", close_period)
    result = recalculate_close_period(period, save=True)
    unmet = []
    if period.blocked_tasks:
        unmet.append(f"{period.blocked_tasks} blocked task(s)")
    if period.overdue_tasks:
        unmet.append(f"{period.overdue_tasks} overdue task(s)")
    if period.critical_open_tasks:
        unmet.append(f"{period.critical_open_tasks} open critical task(s)")
    result["unmet_requirements"] = unmet
    result["ready"] = not unmet and period.total_tasks == period.completed_tasks and period.total_tasks > 0
    return result


def submit_for_review(close_period: str) -> dict:
    period = frappe.get_doc("Financial Close Period", close_period)
    readiness = get_financial_close_readiness(period.name)
    if not readiness["ready"]:
        frappe.throw("Close period is not ready for review: " + "; ".join(readiness["unmet_requirements"]))
    period.status = "Ready for Review"
    period.reviewed_by = None
    period.reviewed_on = None
    period.save()
    return {"status": period.status}


def start_review(close_period: str) -> dict:
    period = frappe.get_doc("Financial Close Period", close_period)
    if period.status != "Ready for Review":
        frappe.throw("Financial Close Period must be Ready for Review first.")
    period.status = "Review"
    period.reviewed_by = frappe.session.user
    period.reviewed_on = now_datetime()
    period.save()
    return {"status": period.status}


def approve_for_close(close_period: str) -> dict:
    period = frappe.get_doc("Financial Close Period", close_period)
    if period.status not in ("Ready for Review", "Review"):
        frappe.throw("Financial Close Period must be under review before approval.")
    if period.close_manager and period.close_manager == frappe.session.user:
        frappe.throw("Close Manager cannot be the final approver.")
    period.status = "Approved for Close"
    period.approved_by = frappe.session.user
    period.approved_on = now_datetime()
    period.save()
    return {"status": period.status}


def certify_close(close_period: str, statement: str | None = None) -> dict:
    period = frappe.get_doc("Financial Close Period", close_period)
    period.certification_statement = statement or period.certification_statement
    if not period.certification_statement:
        frappe.throw("Certification statement is required.")
    period.certified_by = frappe.session.user
    period.certified_on = now_datetime()
    period.save()
    return {"certified": True}


def close_period(close_period: str) -> dict:
    period = frappe.get_doc("Financial Close Period", close_period)
    if period.status != "Approved for Close":
        frappe.throw("Financial Close Period must be Approved for Close before closing.")
    readiness = get_financial_close_readiness(period.name)
    if not readiness["ready"]:
        frappe.throw("Close period is not complete: " + "; ".join(readiness["unmet_requirements"]))
    if period.require_close_certification and not period.certified_by:
        frappe.throw("Close certification is required before final close.")
    period.status = "Closed"
    period.actual_close_date = today()
    period.closed_by = frappe.session.user
    period.closed_on = now_datetime()
    period.save()
    return {"closed": True}


def reopen_close(close_period: str, reason: str) -> dict:
    if not (frappe.has_role("System Manager") or frappe.has_role("Financial Close Manager") or frappe.has_role("Supplier Reconciliation Manager")):
        frappe.throw("Only an authorized manager can reopen a financial close period.")
    if not reason:
        frappe.throw("Reopen reason is required.")
    period = frappe.get_doc("Financial Close Period", close_period)
    period.status = "Reopened"
    period.reopen_reason = reason
    period.reopened_by = frappe.session.user
    period.reopened_on = now_datetime()
    period.save()
    return {"reopened": True}
