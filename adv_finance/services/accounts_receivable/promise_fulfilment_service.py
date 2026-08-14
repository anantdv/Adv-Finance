from __future__ import annotations

from decimal import Decimal

import frappe
from frappe.utils import add_days, getdate, today

from adv_finance.compatibility.erpnext_v16 import get_customer_receipts


def refresh_promise_fulfilment(name: str, grace_days: int = 1) -> dict:
    promise = frappe.get_doc("Promise to Pay", name)
    received = _received_for_promise(promise)
    promise.actual_received_amount = received
    promise.remaining_promised_amount = Decimal(str(promise.promised_amount or 0)) - received
    if promise.remaining_promised_amount <= 0:
        promise.status = "Kept"
        promise.fulfilled_date = promise.promised_payment_date
    elif received > 0:
        promise.status = "Partially Kept"
    if getdate(today()) > getdate(add_days(promise.promised_payment_date, grace_days)) and promise.remaining_promised_amount > 0:
        promise.status = "Broken"
    promise.save()
    return {"status": promise.status, "received": received, "remaining": promise.remaining_promised_amount}


def process_broken_promises(limit: int = 100) -> dict:
    names = frappe.get_all("Promise to Pay", filters={"status": ["in", ["Active", "Partially Kept"]], "promised_payment_date": ["<", today()]}, pluck="name", limit=limit)
    broken = []
    for name in names:
        result = refresh_promise_fulfilment(name)
        if result["status"] == "Broken":
            broken.append(name)
    return {"broken": broken}


def _received_for_promise(promise) -> Decimal:
    refs = {row.sales_invoice for row in promise.invoices if row.sales_invoice}
    receipts = get_customer_receipts(promise.company, promise.customer, promise.promise_date, promise.promised_payment_date)
    total = Decimal("0")
    for row in receipts:
        if refs and row.reference_name not in refs:
            continue
        total += Decimal(str(row.allocated_amount or row.received_amount or row.paid_amount or 0))
    return total
