from __future__ import annotations

from decimal import Decimal

import frappe


def recalculate_settlement(settlement) -> None:
    expected = sum(Decimal(str(row.amount or 0)) for row in settlement.items)
    settled = sum(Decimal(str(row.settled_amount or 0)) for row in settlement.items)
    settlement.expected_settlement_amount = expected
    settlement.actual_settlement_amount = Decimal(str(settlement.actual_settlement_amount or 0)) or settled
    settlement.outstanding_amount = expected - Decimal(str(settlement.actual_settlement_amount or 0))
    if settlement.status == "Cancelled":
        return
    if settlement.outstanding_amount == 0 and expected:
        settlement.status = "Settled"
    elif settlement.actual_settlement_amount and settlement.outstanding_amount > 0:
        settlement.status = "Partially Settled"
    elif settlement.outstanding_amount < 0:
        settlement.status = "Overpayment"
    else:
        settlement.status = settlement.status or "Expected"


def mark_settlement_complete(name: str, payment_entry: str | None = None) -> dict:
    doc = frappe.get_doc("Intercompany Settlement", name)
    recalculate_settlement(doc)
    if payment_entry:
        doc.payment_entry = payment_entry
    doc.status = "Settled" if Decimal(str(doc.outstanding_amount or 0)) == 0 else "Partially Settled"
    doc.save()
    for row in doc.items:
        if row.transaction:
            frappe.db.set_value("Intercompany Transaction", row.transaction, {"settlement": doc.name, "settlement_status": doc.status})
    return {"status": doc.status, "outstanding_amount": doc.outstanding_amount}
