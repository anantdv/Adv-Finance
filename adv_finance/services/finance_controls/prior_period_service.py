from __future__ import annotations

import frappe
from frappe.utils import getdate, now_datetime, today


def approve_prior_period_request(name, valid_from=None, valid_until=None):
    doc = frappe.get_doc("Prior Period Posting Request", name)
    if doc.requested_by == frappe.session.user and not frappe.has_role("System Manager"):
        frappe.throw("Requester cannot approve the same prior-period posting request.")
    doc.status = "Approved"; doc.approved_by = frappe.session.user; doc.approved_on = now_datetime(); doc.valid_from = valid_from or today(); doc.valid_until = valid_until or getattr(doc, "valid_until", None) or today(); doc.save()
    return {"status": doc.status}


def find_valid_prior_period_request(doc):
    rows = frappe.get_all("Prior Period Posting Request", filters={"company": doc.company, "requested_by": getattr(doc, "owner", frappe.session.user), "posting_date": doc.posting_date, "transaction_doctype": doc.doctype, "status": "Approved", "valid_from": ["<=", today()], "valid_until": [">=", today()]}, fields=["name", "single_use", "proposed_amount", "transaction_name"], order_by="modified desc")
    for row in rows:
        if row.transaction_name and row.transaction_name != getattr(doc, "name", None):
            continue
        if row.proposed_amount and getattr(doc, "grand_total", 0) and abs(float(getattr(doc, "grand_total", 0))) > float(row.proposed_amount):
            continue
        return row
    return None


def is_prior_period_restricted(company, posting_date):
    period = frappe.db.exists("Accounting Period", {"company": company, "start_date": ["<=", posting_date], "end_date": [">=", posting_date], "closed": 1})
    return bool(period)


def validate_prior_period_posting(doc, method=None):
    if not getattr(doc, "company", None) or not getattr(doc, "posting_date", None):
        return
    if not is_prior_period_restricted(doc.company, doc.posting_date):
        return
    approval = find_valid_prior_period_request(doc)
    if not approval:
        frappe.throw("Prior-period posting requires an approved ADV Finance Prior Period Posting Request.")
    if approval.single_use:
        mark_prior_period_request_used(approval.name, doc.doctype, doc.name)


def mark_prior_period_request_used(name, doctype, docname):
    doc = frappe.get_doc("Prior Period Posting Request", name)
    doc.status = "Used"; doc.usage_document = docname; doc.used_on = now_datetime(); doc.save(ignore_permissions=True)
    return {"status": doc.status}


def prior_period_posting_register(filters=None):
    filters = filters or {}
    query={}
    for key in ("company", "status", "transaction_doctype"):
        if filters.get(key): query[key]=filters[key]
    return frappe.get_all("Prior Period Posting Request", filters=query, fields=["name", "company", "requested_by", "posting_date", "transaction_doctype", "transaction_name", "reason", "approved_by", "approved_on", "usage_document", "used_on", "status"], order_by="posting_date desc, modified desc")
