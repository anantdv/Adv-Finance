from __future__ import annotations

import frappe

from adv_finance.compatibility.erpnext_v16 import create_draft_period_closing_voucher, get_period_closing_voucher_docstatus


def create_period_closing_voucher(close_period: str) -> dict:
    period = frappe.get_doc("Financial Close Period", close_period)
    if period.status != "Approved for Close":
        frappe.throw("Financial Close Period must be Approved for Close before creating Period Closing Voucher.")
    if period.period_closing_voucher:
        return {"period_closing_voucher": period.period_closing_voucher, "created": False}
    voucher = create_draft_period_closing_voucher(period)
    period.period_closing_voucher = voucher.name
    period.period_closing_voucher_status = "Draft Created"
    period.save()
    return {"period_closing_voucher": voucher.name, "created": True}


def refresh_period_closing_voucher_status(close_period: str) -> dict:
    period = frappe.get_doc("Financial Close Period", close_period)
    status = get_period_closing_voucher_docstatus(period.period_closing_voucher)
    if status == 1:
        period.period_closing_voucher_status = "Submitted"
    elif status == 2:
        period.period_closing_voucher_status = "Cancelled"
    elif period.period_closing_voucher:
        period.period_closing_voucher_status = "Draft Created"
    else:
        period.period_closing_voucher_status = "Not Created"
    period.save()
    return {"status": period.period_closing_voucher_status}
