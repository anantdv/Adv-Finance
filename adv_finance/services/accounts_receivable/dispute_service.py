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


def get_active_disputed_amount(company: str, customer: str, sales_invoice: str | None = None) -> Decimal:
    conditions = [
        "disp.company = %(company)s",
        "disp.customer = %(customer)s",
        "disp.status not in ('Resolved', 'Rejected', 'Closed')",
    ]
    values = {"company": company, "customer": customer}
    if sales_invoice:
        conditions.append("item.sales_invoice = %(sales_invoice)s")
        values["sales_invoice"] = sales_invoice
    rows = frappe.db.sql(
        f"""
        select coalesce(sum(item.disputed_amount), 0) as amount
        from `tabCustomer Dispute` disp
        inner join `tabCustomer Dispute Invoice` item on item.parent = disp.name
        where {" and ".join(conditions)}
        """,
        values,
        as_dict=True,
    )
    return Decimal(str(rows[0].amount if rows else 0))


def get_active_disputed_amounts(company: str, sales_invoices: list[str] | tuple[str, ...]) -> dict[str, Decimal]:
    if not sales_invoices:
        return {}
    rows = frappe.db.sql(
        """
        select item.sales_invoice, coalesce(sum(item.disputed_amount), 0) as amount
        from `tabCustomer Dispute` disp
        inner join `tabCustomer Dispute Invoice` item on item.parent = disp.name
        where disp.company = %(company)s
          and disp.status not in ('Resolved', 'Rejected', 'Closed')
          and item.sales_invoice in %(sales_invoices)s
        group by item.sales_invoice
        """,
        {"company": company, "sales_invoices": tuple(sales_invoices)},
        as_dict=True,
    )
    return {row.sales_invoice: Decimal(str(row.amount or 0)) for row in rows}
