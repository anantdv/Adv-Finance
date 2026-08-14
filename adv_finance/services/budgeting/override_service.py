from __future__ import annotations

from decimal import Decimal

import frappe
from frappe.utils import getdate, now_datetime, today

from adv_finance.services.budgeting.available_budget_service import get_available_budget


def prepare_override_request(doc) -> None:
    result = get_available_budget(doc.company, doc.account, doc.cost_center, doc.project, as_of_date=getattr(doc, "valid_until", None) or today())
    doc.available_budget = result["available_budget"]
    doc.shortfall = max(Decimal(str(doc.requested_amount or 0)) - Decimal(str(doc.available_budget or 0)), Decimal("0"))
    if not doc.requested_by:
        doc.requested_by = frappe.session.user


def approve_override(name: str, notes: str | None = None) -> dict:
    doc = frappe.get_doc("Budget Override Request", name)
    if doc.requested_by == frappe.session.user and not frappe.has_role("System Manager"):
        frappe.throw("Override requester cannot approve the same request.")
    doc.status = "Approved"
    doc.approved_by = frappe.session.user
    doc.approved_on = now_datetime()
    doc.approval_notes = notes
    doc.save()
    return {"status": doc.status}


def find_valid_override(company: str, source_doctype: str, source_document: str, account: str, amount) -> object | None:
    rows = frappe.get_all("Budget Override Request", filters={"company": company, "source_doctype": source_doctype, "source_document": source_document, "account": account, "status": "Approved"}, fields=["name", "requested_amount", "valid_until"])
    requested = Decimal(str(amount or 0))
    for row in rows:
        if row.valid_until and getdate(row.valid_until) < getdate(today()):
            continue
        if Decimal(str(row.requested_amount or 0)) >= requested:
            return row
    return None


def mark_override_used(name: str) -> dict:
    doc = frappe.get_doc("Budget Override Request", name)
    if doc.status != "Approved":
        frappe.throw("Only Approved overrides can be marked Used.")
    doc.status = "Used"
    doc.used_on = now_datetime()
    doc.save()
    return {"status": doc.status}
