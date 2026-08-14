from __future__ import annotations

from decimal import Decimal

import frappe


def validate_reservation(doc) -> None:
    amount = Decimal(str(doc.amount or 0))
    consumed = Decimal(str(doc.consumed_amount or 0))
    if amount <= 0:
        frappe.throw("Reservation amount must be greater than zero.")
    if consumed > amount:
        frappe.throw("Consumed amount cannot exceed reservation amount.")
    doc.remaining_amount = amount - consumed
    if doc.remaining_amount <= 0 and doc.status not in ("Cancelled", "Released"):
        doc.status = "Consumed"
