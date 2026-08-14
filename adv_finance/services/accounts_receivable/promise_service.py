from __future__ import annotations

from decimal import Decimal

import frappe
from frappe.utils import add_days, now_datetime

from adv_finance.services.accounts_receivable.ar_balance_service import get_customer_ar_summary


def validate_promise(promise) -> None:
    amount = Decimal(str(promise.promised_amount or 0))
    if amount <= 0:
        frappe.throw("Promised amount must be greater than zero.")
    allocated = Decimal("0")
    for row in promise.invoices:
        allocated += Decimal(str(row.promised_amount or 0))
        inv = frappe.db.get_value("Sales Invoice", row.sales_invoice, ["company", "customer", "currency", "outstanding_amount"], as_dict=True)
        if not inv:
            frappe.throw(f"Sales Invoice {row.sales_invoice} was not found.")
        if inv.company != promise.company or inv.customer != promise.customer:
            frappe.throw(f"Sales Invoice {row.sales_invoice} does not match promise company/customer.")
        row.invoice_outstanding = inv.outstanding_amount
        if Decimal(str(row.promised_amount or 0)) > Decimal(str(inv.outstanding_amount or 0)):
            frappe.throw(f"Promised amount exceeds outstanding amount for {row.sales_invoice}.")
    if promise.invoices and allocated > amount:
        frappe.throw("Invoice allocation exceeds promised amount.")
    exposure = get_customer_ar_summary(promise.company, promise.customer)
    if amount > Decimal(str(exposure["total_outstanding"] or 0)) and not promise.notes:
        frappe.throw("Promise exceeds current outstanding. Add notes to justify.")


def recalculate_promise(promise) -> None:
    promise.remaining_promised_amount = Decimal(str(promise.promised_amount or 0)) - Decimal(str(promise.actual_received_amount or 0))
    if promise.status == "Draft":
        return
    if Decimal(str(promise.remaining_promised_amount or 0)) <= 0:
        promise.status = "Kept"


def activate_promise(name: str) -> dict:
    doc = frappe.get_doc("Promise to Pay", name)
    validate_promise(doc)
    doc.status = "Active"
    doc.save()
    return {"status": doc.status}


def reschedule_promise(name: str, promised_payment_date, promised_amount=None, reason: str | None = None) -> dict:
    if not reason:
        frappe.throw("Reschedule reason is required.")
    original = frappe.get_doc("Promise to Pay", name)
    new_doc = frappe.copy_doc(original)
    new_doc.previous_promise = original.name
    new_doc.rescheduled_from = original.name
    new_doc.reschedule_reason = reason
    new_doc.promised_payment_date = promised_payment_date
    new_doc.promised_amount = promised_amount or original.remaining_promised_amount or original.promised_amount
    new_doc.actual_received_amount = 0
    new_doc.remaining_promised_amount = new_doc.promised_amount
    new_doc.status = "Active"
    new_doc.recorded_by = frappe.session.user
    new_doc.recorded_on = now_datetime()
    new_doc.insert()
    original.status = "Rescheduled"
    original.save()
    return {"promise_to_pay": new_doc.name}
