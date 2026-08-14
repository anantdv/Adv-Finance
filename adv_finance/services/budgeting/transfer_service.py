from __future__ import annotations

from decimal import Decimal

import frappe
from frappe.utils import now_datetime

from adv_finance.services.budgeting.available_budget_service import get_available_budget


def validate_transfer(doc) -> None:
    amount = Decimal(str(doc.amount or 0))
    if amount <= 0:
        frappe.throw("Transfer amount must be greater than zero.")
    if doc.from_account == doc.to_account and doc.from_cost_center == doc.to_cost_center and doc.from_project == doc.to_project:
        frappe.throw("Transfer source and destination cannot be identical.")
    available = get_available_budget(doc.company, doc.from_account, doc.from_cost_center, doc.from_project, as_of_date=doc.transfer_date)
    if doc.status in ("Submitted for Approval", "Approved", "Applied") and amount > Decimal(str(available["available_budget"] or 0)):
        frappe.throw("Source budget does not have sufficient available budget for this transfer.")
    if not doc.requested_by:
        doc.requested_by = frappe.session.user


def approve_transfer(name: str) -> dict:
    doc = frappe.get_doc("Budget Transfer", name)
    if doc.requested_by == frappe.session.user and not frappe.has_role("System Manager"):
        frappe.throw("Transfer requester cannot approve the same transfer.")
    doc.status = "Approved"
    doc.approved_by = frappe.session.user
    doc.approved_on = now_datetime()
    doc.save()
    return {"status": doc.status}
