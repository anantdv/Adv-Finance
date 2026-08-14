from __future__ import annotations

from frappe.utils import getdate, nowdate

import frappe


def get_active_hold(company: str, supplier: str, purchase_invoice: str | None = None):
    today = getdate(nowdate())
    filters = {
        "company": company,
        "supplier": supplier,
        "active": 1,
    }
    holds = frappe.get_all(
        "Payment Hold",
        filters=filters,
        fields=["name", "hold_scope", "purchase_invoice", "hold_from", "hold_until", "reason"],
        order_by="hold_scope desc, modified desc",
    )
    for hold in holds:
        if hold.hold_from and getdate(hold.hold_from) > today:
            continue
        if hold.hold_until and getdate(hold.hold_until) < today:
            continue
        if hold.hold_scope == "Supplier":
            return hold
        if hold.hold_scope == "Invoice" and hold.purchase_invoice == purchase_invoice:
            return hold
    return None
