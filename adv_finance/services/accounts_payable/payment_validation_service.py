from __future__ import annotations

from decimal import Decimal

import frappe


OPEN_PROPOSAL_STATUSES = ("Generated", "Under Review", "Approved")
OPEN_RUN_STATUSES = ("Draft", "Prepared", "Under Approval", "Approved", "Processing")


def validate_selected_amount(selected_amount, outstanding_amount):
    selected = Decimal(str(selected_amount or 0))
    outstanding = Decimal(str(outstanding_amount or 0))
    if selected < 0:
        frappe.throw("Selected amount cannot be negative.")
    if selected > outstanding:
        frappe.throw("Selected amount cannot exceed current outstanding amount.")


def duplicate_invoice_context(purchase_invoice: str, proposal: str | None = None, payment_run: str | None = None) -> str | None:
    proposal_filters = {
        "purchase_invoice": purchase_invoice,
        "selected": 1,
        "parenttype": "Payment Proposal",
    }
    if proposal:
        proposal_filters["parent"] = ["!=", proposal]

    proposal_item = frappe.db.get_value(
        "Payment Proposal Item",
        proposal_filters,
        ["parent"],
        as_dict=True,
    )
    if proposal_item:
        status = frappe.db.get_value("Payment Proposal", proposal_item.parent, "status")
        if status in OPEN_PROPOSAL_STATUSES:
            return f"Payment Proposal {proposal_item.parent}"

    run_filters = {
        "purchase_invoice": purchase_invoice,
        "parenttype": "Payment Run",
    }
    if payment_run:
        run_filters["parent"] = ["!=", payment_run]
    run_invoice = frappe.db.get_value("Payment Run Invoice", run_filters, ["parent"], as_dict=True)
    if run_invoice:
        status = frappe.db.get_value("Payment Run", run_invoice.parent, "status")
        if status in OPEN_RUN_STATUSES:
            return f"Payment Run {run_invoice.parent}"

    submitted_payment = frappe.db.sql(
        """
        select ref.parent
        from `tabPayment Entry Reference` ref
        inner join `tabPayment Entry` pe on pe.name = ref.parent
        where ref.reference_doctype = 'Purchase Invoice'
          and ref.reference_name = %(purchase_invoice)s
          and pe.docstatus = 1
        limit 1
        """,
        {"purchase_invoice": purchase_invoice},
        as_dict=True,
    )
    if submitted_payment:
        return f"submitted Payment Entry {submitted_payment[0].parent}"

    return None
