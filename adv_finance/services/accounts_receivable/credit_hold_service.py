from __future__ import annotations

import frappe
from frappe.utils import getdate, today, now_datetime


def get_active_credit_hold(company: str, customer: str, transaction_type: str | None = None):
    rows = frappe.get_all("Credit Hold", filters={"company": company, "customer": customer, "active": 1}, fields=["name", "hold_type", "effective_from", "effective_until", "hold_reason"], order_by="creation desc")
    for row in rows:
        if row.effective_from and getdate(row.effective_from) > getdate(today()):
            continue
        if row.effective_until and getdate(row.effective_until) < getdate(today()):
            continue
        if row.hold_type == "Full Credit Hold" or not transaction_type or transaction_type in row.hold_type:
            return row
    return None


def validate_customer_credit_status(company: str, customer: str, transaction_type: str, amount=0) -> dict:
    hold = get_active_credit_hold(company, customer, transaction_type)
    if hold:
        return {"allowed": False, "reason": hold.hold_reason, "credit_hold": hold.name, "override_allowed": True}
    return {"allowed": True}


def release_credit_hold(name: str, reason: str) -> dict:
    if not reason:
        frappe.throw("Release reason is required.")
    doc = frappe.get_doc("Credit Hold", name)
    if doc.created_by == frappe.session.user and not frappe.has_role("System Manager"):
        frappe.throw("Creator cannot release their own credit hold.")
    doc.active = 0
    doc.release_reason = reason
    doc.released_by = frappe.session.user
    doc.released_on = now_datetime()
    doc.save()
    return {"released": True}
