from __future__ import annotations

from decimal import Decimal

import frappe
from frappe.utils import now_datetime


def validate_supplement(doc) -> None:
    if Decimal(str(doc.amount or 0)) <= 0:
        frappe.throw("Supplement amount must be greater than zero.")
    if not doc.requested_by:
        doc.requested_by = frappe.session.user


def approve_supplement(name: str) -> dict:
    doc = frappe.get_doc("Budget Supplement", name)
    if doc.requested_by == frappe.session.user and not frappe.has_role("System Manager"):
        frappe.throw("Supplement requester cannot approve the same supplement.")
    doc.status = "Approved"
    doc.approved_by = frappe.session.user
    doc.approved_on = now_datetime()
    doc.save()
    return {"status": doc.status}
