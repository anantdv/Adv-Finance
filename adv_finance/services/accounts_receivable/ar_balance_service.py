from __future__ import annotations

from decimal import Decimal

from frappe.utils import date_diff, today

from adv_finance.compatibility.erpnext_v16 import get_customer_open_sales_invoices


def ageing_bucket(days: int) -> str:
    if days <= 0:
        return "Current"
    if days <= 30:
        return "1-30"
    if days <= 60:
        return "31-60"
    if days <= 90:
        return "61-90"
    if days <= 120:
        return "91-120"
    return "120+"


def get_customer_ar_summary(company: str, customer: str, as_of_date=None) -> dict:
    as_of_date = as_of_date or today()
    invoices = get_customer_open_sales_invoices(company, customer, as_of_date)
    total = Decimal("0")
    overdue = Decimal("0")
    current = Decimal("0")
    oldest_date = None
    oldest_days = 0
    rows = []
    for inv in invoices:
        amount = Decimal(str(inv.outstanding_amount or 0))
        due = inv.due_date or inv.posting_date
        days = max(date_diff(as_of_date, due), 0) if due else 0
        total += amount
        if days > 0:
            overdue += amount
        else:
            current += amount
        if amount and (oldest_date is None or (due and due < oldest_date)):
            oldest_date = due
            oldest_days = days
        rows.append({"sales_invoice": inv.name, "posting_date": inv.posting_date, "due_date": inv.due_date, "grand_total": inv.grand_total, "snapshot_outstanding_amount": inv.outstanding_amount, "current_outstanding_amount": inv.outstanding_amount, "overdue_days": days, "ageing_bucket": ageing_bucket(days), "currency": inv.currency, "collection_status": "Open", "selected": 1})
    return {"total_outstanding": total, "overdue_amount": overdue, "current_amount": current, "oldest_invoice_date": oldest_date, "oldest_overdue_days": oldest_days, "open_invoice_count": len(rows), "overdue_invoice_count": sum(1 for row in rows if row["overdue_days"] > 0), "currency": invoices[0].currency if invoices else None, "invoices": rows}
