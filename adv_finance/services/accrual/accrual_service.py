from __future__ import annotations

from decimal import Decimal

import frappe
from frappe.utils import now_datetime

from adv_finance.compatibility.erpnext_v16 import get_journal_entry_docstatus
from adv_finance.services.accrual.accrual_ageing_service import age_bucket, days_open
from adv_finance.services.accrual.accrual_variance_service import classify_variance


def recalculate_accrual(accrual) -> None:
    accepted_matches = [row for row in accrual.matches if row.status in ("Accepted", "Posted", "Closed")]
    accrual.consumed_amount = sum(Decimal(str(row.matched_amount or 0)) for row in accepted_matches)
    accrual.actual_amount = sum(Decimal(str(row.invoice_amount or 0)) for row in accepted_matches)
    accrual.remaining_amount = Decimal(str(accrual.accrual_amount or 0)) - Decimal(str(accrual.consumed_amount or 0))
    accrual.variance_amount = Decimal(str(accrual.actual_amount or 0)) - Decimal(str(accrual.consumed_amount or 0))
    accrual.variance_status = classify_variance(
        accrual.variance_amount,
        Decimal(str(accrual.variance_tolerance_amount or 0)),
        accrual.variance_tolerance_percentage,
        accrual.accrual_amount,
    )
    days = days_open(accrual.accrual_date)
    accrual.days_open = days
    accrual.age_bucket = age_bucket(days)
    if accrual.consumed_amount and accrual.remaining_amount:
        accrual.matching_status = "Partially Matched"
    elif accrual.consumed_amount and not accrual.remaining_amount:
        accrual.matching_status = "Fully Matched"
    elif accrual.variance_status in ("Under Accrued", "Over Accrued"):
        accrual.matching_status = "Variance Review"
    else:
        accrual.matching_status = accrual.matching_status or "Unmatched"


def submit_for_review(name: str) -> dict:
    accrual = frappe.get_doc("Accrual", name)
    accrual.prepared_by = frappe.session.user
    accrual.prepared_on = now_datetime()
    accrual.workflow_status = "Under Review"
    accrual.status = "Under Review"
    accrual.save()
    return {"status": accrual.workflow_status}


def approve_accrual(name: str) -> dict:
    accrual = frappe.get_doc("Accrual", name)
    if accrual.enforce_segregation_of_duties and accrual.prepared_by == frappe.session.user:
        frappe.throw("Preparer cannot approve their own accrual.")
    if accrual.require_supporting_attachment and not accrual.supporting_attachment:
        frappe.throw("Supporting attachment is required before approval.")
    _check_duplicate_accrual(accrual)
    accrual.reviewed_by = frappe.session.user
    accrual.reviewed_on = now_datetime()
    accrual.approved_by = frappe.session.user
    accrual.approved_on = now_datetime()
    accrual.workflow_status = "Approved"
    accrual.status = "Approved"
    accrual.save()
    return {"approved": True}


def refresh_accrual_status(name: str) -> dict:
    accrual = frappe.get_doc("Accrual", name)
    je_status = get_journal_entry_docstatus(accrual.accrual_journal_entry)
    if je_status == 1:
        accrual.posting_status = "Posted"
        if accrual.status in ("Journal Draft Created", "Approved"):
            accrual.status = "Posted"
    elif accrual.accrual_journal_entry:
        accrual.posting_status = "Draft Journal Created"
    reversal_status = get_journal_entry_docstatus(accrual.reversal_journal_entry)
    if reversal_status == 1:
        accrual.reversal_status = "Reversed"
    elif accrual.reversal_journal_entry:
        accrual.reversal_status = "Draft Created"
    recalculate_accrual(accrual)
    accrual.save()
    return {"posting_status": accrual.posting_status, "reversal_status": accrual.reversal_status}


def carry_forward_accrual(name: str, to_period: str, reason: str) -> dict:
    accrual = frappe.get_doc("Accrual", name)
    if not reason:
        frappe.throw("Carry-forward reason is required.")
    accrual.carried_forward = 1
    accrual.carried_forward_from_period = accrual.accounting_period
    accrual.carried_forward_to_period = to_period
    accrual.carry_forward_reason = reason
    accrual.carried_forward_by = frappe.session.user
    accrual.carried_forward_on = now_datetime()
    accrual.save()
    return {"carried_forward": True}


def close_accrual(name: str) -> dict:
    accrual = frappe.get_doc("Accrual", name)
    open_critical = [row for row in accrual.exceptions if row.status == "Open" and row.severity == "Critical"]
    if open_critical:
        frappe.throw("Critical open exceptions must be resolved before closing.")
    if accrual.reversal_required and accrual.reversal_status in ("Pending", "Draft Created") and not accrual.closing_notes:
        frappe.throw("Closing notes are required when reversal is not complete.")
    if accrual.matching_status != "Fully Matched" and not accrual.closing_notes:
        frappe.throw("Closing notes are required for unmatched or partially matched accruals.")
    accrual.workflow_status = "Closed"
    accrual.status = "Closed"
    accrual.closed_by = frappe.session.user
    accrual.closed_on = now_datetime()
    accrual.save()
    return {"closed": True}


def reopen_accrual(name: str, reason: str) -> dict:
    if not (frappe.has_role("System Manager") or frappe.has_role("Supplier Reconciliation Manager")):
        frappe.throw("Only an authorized manager can reopen accruals.")
    if not reason:
        frappe.throw("Reopen reason is required.")
    accrual = frappe.get_doc("Accrual", name)
    accrual.reopen_reason = reason
    accrual.reopened_by = frappe.session.user
    accrual.reopened_on = now_datetime()
    accrual.workflow_status = "Approved"
    accrual.status = "Approved"
    accrual.save()
    return {"reopened": True}


def _check_duplicate_accrual(accrual) -> None:
    filters = {
        "company": accrual.company,
        "accounting_period": accrual.accounting_period,
        "expense_account": accrual.expense_account,
        "cost_center": accrual.cost_center,
        "accrual_amount": accrual.accrual_amount,
    }
    if accrual.supplier:
        filters["supplier"] = accrual.supplier
    duplicate = frappe.db.exists("Accrual", {**filters, "name": ["!=", accrual.name], "workflow_status": ["!=", "Closed"]})
    if duplicate:
        frappe.throw(f"Potential duplicate accrual exists: {duplicate}")
