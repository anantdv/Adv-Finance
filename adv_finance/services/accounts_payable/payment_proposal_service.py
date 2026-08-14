from __future__ import annotations

from decimal import Decimal

import frappe
from frappe.utils import date_diff, getdate, nowdate

from adv_finance.compatibility.erpnext_v16 import (
    get_outstanding_purchase_invoices,
    get_supplier_bank_account,
)
from adv_finance.services.accounts_payable.payment_hold_service import get_active_hold
from adv_finance.services.accounts_payable.payment_validation_service import (
    duplicate_invoice_context,
    validate_selected_amount,
)


def generate_payment_proposal(name: str) -> dict:
    proposal = frappe.get_doc("Payment Proposal", name)
    if proposal.status not in ("Draft", "Generated"):
        frappe.throw("Payment Proposal can only be generated from Draft or Generated status.")

    invoices = get_outstanding_purchase_invoices(
        company=proposal.company,
        payable_account=proposal.payable_account,
        supplier=proposal.supplier,
        supplier_group=proposal.supplier_group,
        currency=proposal.currency,
        due_date_from=proposal.due_date_from,
        due_date_to=proposal.due_date_to,
        include_overdue=proposal.include_overdue,
        include_due_today=proposal.include_due_today,
        include_future_due=proposal.include_future_due,
        minimum_amount=proposal.minimum_amount,
        maximum_amount=proposal.maximum_amount,
    )

    available = Decimal(str(proposal.available_payment_amount or 0))
    remaining = available
    has_cash_limit = available > 0
    proposal.set("items", [])

    for invoice in invoices:
        item = _invoice_to_item(proposal, invoice)
        if item["exception"]:
            item["selected"] = 0
            item["selected_amount"] = 0
        elif has_cash_limit and Decimal(str(item["proposed_amount"])) > remaining:
            item["selected"] = 0
            item["selected_amount"] = 0
            item["exclusion_reason"] = "Available cash limit exceeded"
        else:
            item["selected"] = 1
            item["selected_amount"] = item["proposed_amount"]
            if has_cash_limit:
                remaining -= Decimal(str(item["selected_amount"]))
        proposal.append("items", item)

    proposal.status = "Generated"
    recalculate_payment_proposal(proposal)
    proposal.save()
    return {"proposal": proposal.name, "items": len(proposal.items)}


def recalculate_payment_proposal(proposal) -> None:
    suppliers = {row.supplier for row in proposal.items}
    invoices = [row for row in proposal.items if row.purchase_invoice]
    proposal.suppliers_count = len(suppliers)
    proposal.invoices_count = len(invoices)
    proposal.total_outstanding = sum(Decimal(str(row.outstanding_amount or 0)) for row in proposal.items)
    proposal.proposed_payment_total = sum(Decimal(str(row.proposed_amount or 0)) for row in proposal.items)
    proposal.selected_payment_total = sum(Decimal(str(row.selected_amount or 0)) for row in proposal.items if row.selected)
    proposal.total_selected = proposal.selected_payment_total
    proposal.total_on_hold = sum(Decimal(str(row.outstanding_amount or 0)) for row in proposal.items if row.payment_hold)
    proposal.total_excluded = sum(Decimal(str(row.outstanding_amount or 0)) for row in proposal.items if not row.selected)
    proposal.total_credit_adjustment = sum(Decimal(str(row.available_credit or 0)) for row in proposal.items)
    proposal.remaining_available_amount = Decimal(str(proposal.available_payment_amount or 0)) - Decimal(
        str(proposal.selected_payment_total or 0)
    )


def approve_payment_proposal(name: str) -> dict:
    if not (frappe.has_role("Supplier Reconciliation Manager") or frappe.has_role("System Manager")):
        frappe.throw("Only an authorized manager can approve Payment Proposals.")
    proposal = frappe.get_doc("Payment Proposal", name)
    if proposal.status not in ("Generated", "Under Review"):
        frappe.throw("Only generated proposals can be approved.")
    _validate_items(proposal)
    proposal.status = "Approved"
    proposal.save()
    return {"approved": True}


def _validate_items(proposal) -> None:
    for row in proposal.items:
        validate_selected_amount(row.selected_amount, row.outstanding_amount)
        if row.selected:
            duplicate = duplicate_invoice_context(row.purchase_invoice, proposal=proposal.name)
            if duplicate:
                frappe.throw(f"Invoice {row.purchase_invoice} is already included in {duplicate}.")


def _invoice_to_item(proposal, invoice) -> dict:
    outstanding = Decimal(str(invoice.outstanding_amount or 0))
    hold = get_active_hold(proposal.company, invoice.supplier, invoice.name)
    duplicate = duplicate_invoice_context(invoice.name, proposal=proposal.name)
    bank_account = get_supplier_bank_account(invoice.supplier)
    exception = ""
    exception_reason = ""
    if hold:
        exception = "Supplier On Hold" if hold.hold_scope == "Supplier" else "Invoice On Hold"
        exception_reason = hold.reason
    elif duplicate:
        exception = "Invoice Already Selected"
        exception_reason = duplicate
    elif proposal.bank_account and not bank_account:
        exception = "Missing Supplier Bank Account"
        exception_reason = "Supplier has no active bank account."

    return {
        "supplier": invoice.supplier,
        "supplier_name": invoice.supplier_name,
        "purchase_invoice": invoice.name,
        "supplier_invoice_number": invoice.bill_no,
        "posting_date": invoice.posting_date,
        "due_date": invoice.due_date,
        "currency": invoice.currency,
        "invoice_amount": invoice.grand_total,
        "outstanding_amount": outstanding,
        "available_credit": 0,
        "proposed_amount": outstanding,
        "selected_amount": outstanding,
        "days_overdue": max(date_diff(nowdate(), invoice.due_date), 0) if invoice.due_date else 0,
        "selected": 0,
        "payment_priority": calculate_payment_priority(invoice.due_date),
        "payment_hold": 1 if hold else 0,
        "hold_reason": hold.reason if hold else "",
        "exclusion_reason": exception_reason,
        "exception": exception,
        "exception_reason": exception_reason,
        "supplier_bank_account": bank_account,
        "bank_account_verified": 1 if bank_account else 0,
    }


def calculate_payment_priority(due_date) -> str:
    if not due_date:
        return "Normal"
    overdue_days = date_diff(nowdate(), getdate(due_date))
    days_until_due = date_diff(getdate(due_date), nowdate())
    if overdue_days > 60:
        return "Critical"
    if overdue_days > 30:
        return "High"
    if days_until_due <= 7:
        return "Normal"
    return "Low"
