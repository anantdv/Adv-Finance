from __future__ import annotations

from decimal import Decimal
from typing import Any

import frappe


def validate_erpnext_installed() -> None:
    if not frappe.db.exists("Module Def", "ERPNext"):
        frappe.throw("ERPNext must be installed before using ADV Finance accounting features.")


def get_supplier_account(company: str, supplier: str, payable_account: str | None = None) -> str | None:
    if payable_account:
        return payable_account

    account = frappe.db.get_value(
        "Party Account",
        {"parenttype": "Supplier", "parent": supplier, "company": company},
        "account",
    )
    if account:
        return account

    return frappe.db.get_value("Company", company, "default_payable_account")


def get_supplier_ledger_entries(company: str, supplier: str, payable_account: str | None, from_date, to_date) -> list[dict[str, Any]]:
    """Read supplier ledger-affecting GL entries through a parameterized query.

    ERPNext does not expose a compact public function that returns the exact line
    shape required by this reconciliation module. This query is isolated here so
    v16 compatibility can be verified and upgraded without spreading GL details.
    It is read-only and never mutates accounting tables.
    """

    account = get_supplier_account(company, supplier, payable_account)
    filters: dict[str, Any] = {
        "company": company,
        "supplier": supplier,
        "from_date": from_date,
        "to_date": to_date,
    }
    account_clause = ""
    if account:
        filters["account"] = account
        account_clause = "and account = %(account)s"

    return frappe.db.sql(
        f"""
        select
            posting_date, voucher_type, voucher_no, against_voucher_type,
            against_voucher, remarks, debit, credit, account,
            account_currency as currency, party_type, party
        from `tabGL Entry`
        where company = %(company)s
          and party_type = 'Supplier'
          and party = %(supplier)s
          and posting_date between %(from_date)s and %(to_date)s
          and is_cancelled = 0
          {account_clause}
        order by posting_date, creation, name
        """,
        filters,
        as_dict=True,
    )


def get_supplier_opening_balance(company: str, supplier: str, payable_account: str | None, from_date) -> Decimal:
    account = get_supplier_account(company, supplier, payable_account)
    filters: dict[str, Any] = {"company": company, "supplier": supplier, "from_date": from_date}
    account_clause = ""
    if account:
        filters["account"] = account
        account_clause = "and account = %(account)s"

    result = frappe.db.sql(
        f"""
        select coalesce(sum(credit - debit), 0) as balance
        from `tabGL Entry`
        where company = %(company)s
          and party_type = 'Supplier'
          and party = %(supplier)s
          and posting_date < %(from_date)s
          and is_cancelled = 0
          {account_clause}
        """,
        filters,
        as_dict=True,
    )
    return Decimal(str(result[0].balance if result else 0))


def get_supplier_invoice_reference(voucher_type: str, voucher_no: str) -> str | None:
    if voucher_type == "Purchase Invoice":
        return frappe.db.get_value("Purchase Invoice", voucher_no, "bill_no")
    return None


def get_payment_reference(voucher_type: str, voucher_no: str) -> str | None:
    if voucher_type == "Payment Entry":
        return frappe.db.get_value("Payment Entry", voucher_no, "reference_no")
    return None


def get_outstanding_purchase_invoices(
    company: str,
    payable_account: str | None = None,
    supplier: str | None = None,
    supplier_group: str | None = None,
    currency: str | None = None,
    due_date_from=None,
    due_date_to=None,
    include_overdue: bool = True,
    include_due_today: bool = True,
    include_future_due: bool = False,
    minimum_amount=None,
    maximum_amount=None,
) -> list[dict[str, Any]]:
    validate_erpnext_installed()
    conditions = [
        "pi.company = %(company)s",
        "pi.docstatus = 1",
        "pi.outstanding_amount > 0",
    ]
    values: dict[str, Any] = {"company": company}
    if payable_account:
        conditions.append("pi.credit_to = %(payable_account)s")
        values["payable_account"] = payable_account
    if supplier:
        conditions.append("pi.supplier = %(supplier)s")
        values["supplier"] = supplier
    if supplier_group:
        conditions.append("sup.supplier_group = %(supplier_group)s")
        values["supplier_group"] = supplier_group
    if currency:
        conditions.append("pi.currency = %(currency)s")
        values["currency"] = currency
    if due_date_from:
        conditions.append("pi.due_date >= %(due_date_from)s")
        values["due_date_from"] = due_date_from
    if due_date_to:
        conditions.append("pi.due_date <= %(due_date_to)s")
        values["due_date_to"] = due_date_to
    if minimum_amount:
        conditions.append("pi.outstanding_amount >= %(minimum_amount)s")
        values["minimum_amount"] = minimum_amount
    if maximum_amount:
        conditions.append("pi.outstanding_amount <= %(maximum_amount)s")
        values["maximum_amount"] = maximum_amount
    if not include_future_due:
        conditions.append("pi.due_date <= curdate()")
    if not include_overdue:
        conditions.append("pi.due_date >= curdate()")
    if not include_due_today:
        conditions.append("pi.due_date != curdate()")

    return frappe.db.sql(
        f"""
        select
            pi.name, pi.supplier, pi.supplier_name, pi.bill_no, pi.posting_date,
            pi.due_date, pi.currency, pi.grand_total, pi.outstanding_amount,
            pi.credit_to as payable_account
        from `tabPurchase Invoice` pi
        left join `tabSupplier` sup on sup.name = pi.supplier
        where {" and ".join(conditions)}
        order by pi.due_date asc, pi.supplier asc, pi.name asc
        """,
        values,
        as_dict=True,
    )


def get_purchase_invoice_payment_state(purchase_invoice: str):
    return frappe.db.get_value(
        "Purchase Invoice",
        purchase_invoice,
        [
            "name",
            "company",
            "supplier",
            "docstatus",
            "currency",
            "credit_to",
            "outstanding_amount",
            "modified",
        ],
        as_dict=True,
    )


def get_supplier_bank_account(supplier: str) -> str | None:
    return frappe.db.get_value(
        "Bank Account",
        {"party_type": "Supplier", "party": supplier, "is_default": 1},
        "name",
    ) or frappe.db.get_value(
        "Bank Account",
        {"party_type": "Supplier", "party": supplier},
        "name",
    )


def get_bank_gl_account(bank_account: str | None) -> str | None:
    if not bank_account:
        return None
    return frappe.db.get_value("Bank Account", bank_account, "account") or bank_account


def create_draft_supplier_payment_entry(payment_run, supplier: str, invoices) -> Any:
    bank_gl_account = get_bank_gl_account(payment_run.bank_account)
    if not bank_gl_account:
        frappe.throw("Payment Run requires a bank account with a linked ledger account.")
    if not payment_run.payable_account:
        frappe.throw("Payment Run requires a payable account.")

    payment_entry = frappe.new_doc("Payment Entry")
    payment_entry.update(
        {
            "payment_type": "Pay",
            "company": payment_run.company,
            "posting_date": payment_run.payment_date,
            "mode_of_payment": payment_run.mode_of_payment,
            "party_type": "Supplier",
            "party": supplier,
            "paid_from": bank_gl_account,
            "paid_to": payment_run.payable_account,
            "paid_amount": sum(Decimal(str(row.selected_amount or 0)) for row in invoices),
            "received_amount": sum(Decimal(str(row.selected_amount or 0)) for row in invoices),
            "reference_no": payment_run.name,
            "reference_date": payment_run.payment_date,
        }
    )
    for row in invoices:
        payment_entry.append(
            "references",
            {
                "reference_doctype": "Purchase Invoice",
                "reference_name": row.purchase_invoice,
                "allocated_amount": row.selected_amount,
            },
        )
    payment_entry.insert()
    return payment_entry


def get_gl_account_balance(company: str, account: str, from_date, to_date) -> dict[str, Any]:
    """Return GL movement using the same sign convention as GL Entry.

    Debit balances are positive and credit balances are negative. The query is
    read-only, parameterized, and isolated here for validation against ERPNext v16
    General Ledger and Trial Balance reports in the deployment bench.
    """

    opening = frappe.db.sql(
        """
        select coalesce(sum(debit - credit), 0) as balance
        from `tabGL Entry`
        where company = %(company)s
          and account = %(account)s
          and posting_date < %(from_date)s
          and is_cancelled = 0
        """,
        {"company": company, "account": account, "from_date": from_date},
        as_dict=True,
    )
    movement = frappe.db.sql(
        """
        select coalesce(sum(debit), 0) as debit, coalesce(sum(credit), 0) as credit
        from `tabGL Entry`
        where company = %(company)s
          and account = %(account)s
          and posting_date between %(from_date)s and %(to_date)s
          and is_cancelled = 0
        """,
        {"company": company, "account": account, "from_date": from_date, "to_date": to_date},
        as_dict=True,
    )
    opening_balance = Decimal(str(opening[0].balance if opening else 0))
    period_debit = Decimal(str(movement[0].debit if movement else 0))
    period_credit = Decimal(str(movement[0].credit if movement else 0))
    return {
        "opening_balance": opening_balance,
        "period_debit": period_debit,
        "period_credit": period_credit,
        "closing_balance": opening_balance + period_debit - period_credit,
        "currency": frappe.db.get_value("Account", account, "account_currency"),
    }


def get_party_subledger_balance(company: str, account: str, party_type: str, to_date) -> Decimal:
    result = frappe.db.sql(
        """
        select coalesce(sum(debit - credit), 0) as balance
        from `tabGL Entry`
        where company = %(company)s
          and account = %(account)s
          and party_type = %(party_type)s
          and posting_date <= %(to_date)s
          and is_cancelled = 0
        """,
        {"company": company, "account": account, "party_type": party_type, "to_date": to_date},
        as_dict=True,
    )
    return Decimal(str(result[0].balance if result else 0))


def get_party_subledger_items(company: str, account: str, party_type: str, to_date) -> list[dict[str, Any]]:
    return frappe.db.sql(
        """
        select party, voucher_type, voucher_no, posting_date,
               sum(debit) as debit, sum(credit) as credit, sum(debit - credit) as amount
        from `tabGL Entry`
        where company = %(company)s
          and account = %(account)s
          and party_type = %(party_type)s
          and posting_date <= %(to_date)s
          and is_cancelled = 0
        group by party, voucher_type, voucher_no, posting_date
        having abs(amount) > 0.000001
        order by posting_date, party, voucher_no
        """,
        {"company": company, "account": account, "party_type": party_type, "to_date": to_date},
        as_dict=True,
    )
