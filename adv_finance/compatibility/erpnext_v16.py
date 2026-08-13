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
