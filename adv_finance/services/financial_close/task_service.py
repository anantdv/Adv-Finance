from __future__ import annotations

import frappe
from frappe.utils import now_datetime

from adv_finance.services.financial_close.close_service import recalculate_close_period
from adv_finance.services.financial_close.dependency_service import get_unmet_dependencies


def start_task(name: str) -> dict:
    task = frappe.get_doc("Financial Close Task", name)
    if get_unmet_dependencies(task):
        task.status = "Blocked"
        task.blocked_reason = "Blocked by unmet dependencies."
    else:
        task.status = "In Progress"
    task.save()
    recalculate_close_period(task.financial_close_period)
    return {"status": task.status}


def complete_task(name: str, notes: str | None = None) -> dict:
    task = frappe.get_doc("Financial Close Task", name)
    unmet = get_unmet_dependencies(task)
    if unmet:
        task.status = "Blocked"
        task.blocked_reason = "Blocked by: " + ", ".join(row.task_name for row in unmet)
        task.save()
        frappe.throw(task.blocked_reason)
    task.completion_notes = notes or task.completion_notes
    if task.evidence_required and not (task.evidence_reference or task.source_document or task.linked_reconciliation or task.linked_accrual or task.linked_journal_entry):
        if not frappe.get_all("File", filters={"attached_to_doctype": task.doctype, "attached_to_name": task.name}, limit=1):
            frappe.throw("Evidence is required before completing this task.")
    task.status = "Completed"
    task.completed_by = frappe.session.user
    task.completed_on = now_datetime()
    task.save()
    recalculate_close_period(task.financial_close_period)
    return {"status": task.status}


def submit_task_for_review(name: str, notes: str | None = None) -> dict:
    task = frappe.get_doc("Financial Close Task", name)
    if get_unmet_dependencies(task):
        frappe.throw("Task has unmet dependencies.")
    task.completion_notes = notes or task.completion_notes
    task.completed_by = frappe.session.user
    task.completed_on = now_datetime()
    task.status = "Ready for Review"
    task.save()
    recalculate_close_period(task.financial_close_period)
    return {"status": task.status}


def review_task(name: str, approve: bool = True, notes: str | None = None) -> dict:
    task = frappe.get_doc("Financial Close Task", name)
    if task.completed_by and task.completed_by == frappe.session.user:
        frappe.throw("Task preparer cannot review their own task.")
    task.review_notes = notes
    task.reviewed_by = frappe.session.user
    task.reviewed_on = now_datetime()
    task.status = "Completed" if approve else "Rejected"
    task.save()
    recalculate_close_period(task.financial_close_period)
    return {"status": task.status}


def waive_task(name: str, reason: str) -> dict:
    if not reason:
        frappe.throw("Waiver reason is required.")
    task = frappe.get_doc("Financial Close Task", name)
    task.status = "Waived"
    task.completion_notes = reason
    task.completed_by = frappe.session.user
    task.completed_on = now_datetime()
    task.save()
    recalculate_close_period(task.financial_close_period)
    return {"status": task.status}
