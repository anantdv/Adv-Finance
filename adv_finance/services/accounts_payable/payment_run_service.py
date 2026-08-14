from __future__ import annotations

from collections import defaultdict
from decimal import Decimal

import frappe
from frappe.utils import now, now_datetime

from adv_finance.compatibility.erpnext_v16 import (
    create_draft_supplier_payment_entry,
    get_purchase_invoice_payment_state,
)
from adv_finance.services.accounts_payable.payment_hold_service import get_active_hold
from adv_finance.services.accounts_payable.payment_validation_service import duplicate_invoice_context


def create_payment_run_from_proposal(proposal_name: str) -> dict:
    proposal = frappe.get_doc("Payment Proposal", proposal_name)
    if proposal.status != "Approved":
        frappe.throw("Payment Proposal must be Approved before creating a Payment Run.")

    payment_run = frappe.new_doc("Payment Run")
    payment_run.update(
        {
            "company": proposal.company,
            "payment_date": proposal.posting_date or proposal.proposal_date,
            "payment_proposal": proposal.name,
            "bank_account": proposal.bank_account,
            "mode_of_payment": proposal.mode_of_payment,
            "currency": proposal.currency,
            "payable_account": proposal.payable_account,
            "status": "Draft",
            "prepared_by": frappe.session.user,
            "prepared_on": now_datetime(),
        }
    )

    selected_items = [row for row in proposal.items if row.selected and Decimal(str(row.selected_amount or 0)) > 0]
    grouped = defaultdict(list)
    for row in selected_items:
        duplicate = duplicate_invoice_context(row.purchase_invoice, proposal=proposal.name)
        if duplicate:
            payment_run.append(
                "exceptions",
                _exception(row, "Invoice Already Selected", f"Invoice is already included in {duplicate}."),
            )
            continue
        key = (row.supplier, row.currency, proposal.payable_account, proposal.bank_account, proposal.mode_of_payment)
        grouped[key].append(row)
        payment_run.append(
            "invoices",
            {
                "supplier": row.supplier,
                "purchase_invoice": row.purchase_invoice,
                "currency": row.currency,
                "proposal_outstanding_amount": row.outstanding_amount,
                "execution_outstanding_amount": row.outstanding_amount,
                "selected_amount": row.selected_amount,
                "payment_status": "Pending",
            },
        )

    for (supplier, currency, payable_account, bank_account, mode_of_payment), rows in grouped.items():
        payment_run.append(
            "items",
            {
                "supplier": supplier,
                "currency": currency,
                "gross_amount": sum(Decimal(str(row.selected_amount or 0)) for row in rows),
                "credit_amount": 0,
                "net_amount": sum(Decimal(str(row.selected_amount or 0)) for row in rows),
                "payment_status": "Pending",
            },
        )

    recalculate_payment_run(payment_run)
    payment_run.status = "Prepared" if not payment_run.exceptions else "Failed"
    payment_run.insert()
    proposal.db_set("status", "Converted to Payment Run")
    return {"payment_run": payment_run.name}


def recalculate_payment_run(payment_run) -> None:
    payment_run.supplier_count = len({row.supplier for row in payment_run.invoices})
    payment_run.invoice_count = len(payment_run.invoices)
    payment_run.gross_payment_amount = sum(Decimal(str(row.selected_amount or 0)) for row in payment_run.invoices)
    payment_run.credit_adjustments = sum(Decimal(str(row.credit_amount or 0)) for row in payment_run.items)
    payment_run.net_payment_amount = Decimal(str(payment_run.gross_payment_amount or 0)) - Decimal(
        str(payment_run.credit_adjustments or 0)
    )


def revalidate_payment_run(name: str) -> dict:
    payment_run = frappe.get_doc("Payment Run", name)
    payment_run.set("exceptions", [])
    for invoice in payment_run.invoices:
        state = get_purchase_invoice_payment_state(invoice.purchase_invoice)
        if not state:
            payment_run.append("exceptions", _exception(invoice, "Document Cancelled", "Purchase Invoice was not found."))
            continue
        invoice.execution_outstanding_amount = state.outstanding_amount
        if state.docstatus != 1:
            payment_run.append("exceptions", _exception(invoice, "Document Cancelled", "Purchase Invoice is not submitted."))
        elif Decimal(str(state.outstanding_amount or 0)) < Decimal(str(invoice.selected_amount or 0)):
            payment_run.append(
                "exceptions",
                _exception(
                    invoice,
                    "Outstanding Amount Changed",
                    f"Expected {invoice.selected_amount}; current outstanding is {state.outstanding_amount}.",
                ),
            )
        elif get_active_hold(payment_run.company, invoice.supplier, invoice.purchase_invoice):
            payment_run.append("exceptions", _exception(invoice, "Invoice On Hold", "A payment hold is now active."))

    payment_run.status = "Failed" if payment_run.exceptions else "Approved"
    payment_run.save()
    return {"exceptions": len(payment_run.exceptions)}


def create_draft_payment_entries(name: str) -> dict:
    payment_run = frappe.get_doc("Payment Run", name)
    revalidate_payment_run(name)
    payment_run.reload()
    if payment_run.exceptions:
        frappe.throw("Resolve Payment Run exceptions before creating Payment Entries.")

    payment_run.status = "Processing"
    payment_run.processing_started_on = now()
    created = []
    by_supplier = defaultdict(list)
    for invoice in payment_run.invoices:
        by_supplier[invoice.supplier].append(invoice)

    for supplier, invoices in by_supplier.items():
        try:
            payment_entry = create_draft_supplier_payment_entry(payment_run, supplier, invoices)
            created.append(payment_entry.name)
            for invoice in invoices:
                invoice.payment_entry = payment_entry.name
                invoice.payment_status = "Payment Entry Created"
        except Exception as exc:
            payment_run.append(
                "exceptions",
                {
                    "supplier": supplier,
                    "exception_type": "Payment Entry Creation Failure",
                    "description": str(exc),
                    "status": "Open",
                },
            )

    payment_run.status = "Payment Entries Created" if not payment_run.exceptions else "Failed"
    if not payment_run.exceptions:
        payment_run.completed_on = now()
    payment_run.save()
    return {"payment_entries": created}


def _exception(row, exception_type: str, description: str) -> dict:
    return {
        "supplier": row.supplier,
        "purchase_invoice": getattr(row, "purchase_invoice", None),
        "exception_type": exception_type,
        "description": description,
        "amount": getattr(row, "selected_amount", 0),
        "status": "Open",
    }
