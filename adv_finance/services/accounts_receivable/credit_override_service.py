from __future__ import annotations

import frappe
from frappe.utils import add_days, now_datetime, today

from adv_finance.services.accounts_receivable.credit_exposure_service import get_credit_exposure


def refresh_override_exposure(doc, save: bool = True) -> dict:
    exposure = get_credit_exposure(doc.company, doc.customer)
    doc.current_exposure = exposure["total_exposure"]
    doc.credit_limit = exposure["credit_limit"]
    doc.exposure_after_transaction = exposure["total_exposure"] + (doc.requested_amount or 0)
    if save:
        doc.save()
    return exposure


def approve_override(name: str, valid_days: int = 7, notes: str | None = None) -> dict:
    doc = frappe.get_doc("Credit Override Request", name)
    if doc.requested_by == frappe.session.user and not frappe.has_role("System Manager"):
        frappe.throw("Requester cannot approve their own override.")
    doc.status = "Approved"
    doc.approved_by = frappe.session.user
    doc.approved_on = now_datetime()
    doc.valid_until = add_days(today(), valid_days)
    doc.approval_notes = notes
    doc.save()
    return {"status": doc.status}


def mark_override_used(name: str) -> dict:
    doc = frappe.get_doc("Credit Override Request", name)
    if doc.status != "Approved":
        frappe.throw("Only approved overrides can be used.")
    doc.status = "Used"
    doc.save()
    return {"status": doc.status}
