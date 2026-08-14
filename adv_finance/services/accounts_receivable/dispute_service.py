from __future__ import annotations

from decimal import Decimal

import frappe

from adv_finance.compatibility.erpnext_v16 import create_draft_customer_credit_note


def validate_dispute(dispute) -> None:
    if Decimal(str(dispute.disputed_amount or 0)) <= 0:
        frappe.throw("Disputed amount must be greater than zero.")
    for row in dispute.invoices:
        inv = frappe.db.get_value("Sales Invoice", row.sales_invoice, ["company", "customer", "grand_total", "outstanding_amount"], as_dict=True)
        if not inv:
            frappe.throw(f"Sales Invoice {row.sales_invoice} was not found.")
        if inv.company != dispute.company or inv.customer != dispute.customer:
            frappe.throw(f"Sales Invoice {row.sales_invoice} does not match dispute company/customer.")
        row.invoice_amount = inv.grand_total
        row.outstanding_amount = inv.outstanding_amount
        if Decimal(str(row.disputed_amount or 0)) > Decimal(str(inv.outstanding_amount or 0)):
            frappe.throw(f"Disputed amount exceeds outstanding amount for {row.sales_invoice}.")


def create_credit_note(name: str) -> dict:
    dispute = frappe.get_doc("Customer Dispute", name)
    if dispute.credit_note:
        return {"credit_note": dispute.credit_note, "created": False}
    note = create_draft_customer_credit_note(dispute)
    dispute.credit_note = note.name
    dispute.status = "Credit Note Proposed"
    dispute.save()
    return {"credit_note": note.name, "created": True}
