from __future__ import annotations

from decimal import Decimal

import frappe
from frappe.utils import now_datetime


def validate_adjustment(doc) -> None:
    if Decimal(str(doc.amount or 0)) == 0:
        frappe.throw("Adjustment amount cannot be zero.")
    if not doc.prepared_by:
        doc.prepared_by = frappe.session.user


def approve_adjustment(name: str) -> dict:
    doc = frappe.get_doc("Consolidation Adjustment", name)
    if doc.prepared_by == frappe.session.user and not frappe.has_role("System Manager"):
        frappe.throw("Adjustment preparer cannot approve the same adjustment.")
    doc.status = "Approved"
    doc.approved_by = frappe.session.user
    doc.approved_on = now_datetime()
    doc.save()
    return {"status": doc.status}
