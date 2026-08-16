from __future__ import annotations

from decimal import Decimal

import frappe
from frappe.utils import date_diff, getdate, today

from adv_finance.compatibility.erpnext_v16 import get_ap_ageing_rows, get_ar_ageing_rows


def _first(rows):
    return rows[0] if rows else None


def _remark(remark, remark_type, date, source_doctype, source_name, **extra):
    return {"remark": remark or "", "remark_type": remark_type or "Other", "date": date, "source_doctype": source_doctype, "source_name": source_name, **extra}


def get_ar_ageing_remark(company, customer, sales_invoice):
    dispute = _first(frappe.get_all("Customer Dispute", filters={"company": company, "customer": customer, "sales_invoice": sales_invoice, "status": ["not in", ["Resolved", "Rejected", "Closed"]]}, fields=["name", "dispute_date", "status", "description"], order_by="dispute_date desc, modified desc", limit=1))
    if dispute:
        return _remark(dispute.description or f"Open dispute: {dispute.status}", "Dispute", dispute.dispute_date, "Customer Dispute", dispute.name, dispute_status=dispute.status)
    promise = _first(frappe.get_all("Promise to Pay", filters={"company": company, "customer": customer, "status": ["in", ["Active", "Partially Kept", "Broken"]]}, fields=["name", "promise_date", "promised_payment_date", "status", "remaining_promised_amount"], order_by="promised_payment_date asc, modified desc", limit=1))
    if promise:
        return _remark(f"Promise {promise.status}: payment expected on {promise.promised_payment_date}.", "Promise", promise.promise_date, "Promise to Pay", promise.name, promise_status=promise.status)
    activity = _first(frappe.get_all("Collection Activity", filters={"company": company, "customer": customer}, fields=["name", "activity_date", "activity_type", "notes", "created_by"], order_by="activity_date desc", limit=1))
    if activity:
        return _remark(activity.notes or activity.activity_type, "Collection", activity.activity_date, "Collection Activity", activity.name, collector=activity.created_by)
    return get_finance_ageing_remark(company, "Customer", customer, "Sales Invoice", sales_invoice)


def get_ap_ageing_remark(company, supplier, purchase_invoice):
    hold = _first(frappe.get_all("Payment Hold", filters={"company": company, "supplier": supplier, "active": 1, "purchase_invoice": ["in", [purchase_invoice, None, ""]]}, fields=["name", "hold_from", "reason"], order_by="modified desc", limit=1))
    if hold:
        return _remark(hold.reason, "Payment Hold", hold.hold_from, "Payment Hold", hold.name, payment_hold=hold.name)
    rec = _first(frappe.get_all("Supplier Reconciliation Exception", filters={"purchase_invoice": purchase_invoice}, fields=["name", "status", "resolution_notes", "modified"], order_by="modified desc", limit=1))
    if rec:
        return _remark(rec.resolution_notes or rec.status, "Supplier Query", rec.modified, "Supplier Reconciliation Exception", rec.name, reconciliation_status=rec.status)
    return get_finance_ageing_remark(company, "Supplier", supplier, "Purchase Invoice", purchase_invoice)


def get_finance_ageing_remark(company, party_type, party, voucher_type, voucher_no):
    rows = frappe.get_all("Finance Ageing Remark", filters={"company": company, "party_type": party_type, "party": party, "voucher_type": voucher_type, "voucher_no": voucher_no, "active": 1}, fields=["name", "remark", "remark_type", "remark_date", "entered_by"], order_by="remark_date desc, modified desc", limit=1)
    row = _first(rows)
    if not row:
        return _remark("", "", None, "", "")
    return _remark(row.remark, row.remark_type, row.remark_date, "Finance Ageing Remark", row.name, collector=row.entered_by)


def ageing_bucket(age):
    age = int(age or 0)
    if age <= 30: return "0-30"
    if age <= 60: return "31-60"
    if age <= 90: return "61-90"
    if age <= 120: return "91-120"
    return "120+"


def ar_ageing_with_remarks(filters=None):
    filters = filters or {}
    as_of = filters.get("as_of_date") or today()
    rows=[]
    for inv in get_ar_ageing_rows(**filters):
        age = date_diff(getdate(as_of), getdate(inv.due_date or inv.posting_date))
        remark = get_ar_ageing_remark(inv.company, inv.customer, inv.name)
        rows.append({**getattr(inv, "__dict__", inv), "age": age, "ageing_bucket": ageing_bucket(age), **remark})
    return rows


def ap_ageing_with_remarks(filters=None):
    filters = filters or {}
    as_of = filters.get("as_of_date") or today()
    rows=[]
    for inv in get_ap_ageing_rows(**filters):
        age = date_diff(getdate(as_of), getdate(inv.due_date or inv.posting_date))
        remark = get_ap_ageing_remark(inv.company, inv.supplier, inv.name)
        rows.append({**getattr(inv, "__dict__", inv), "age": age, "ageing_bucket": ageing_bucket(age), **remark})
    return rows
