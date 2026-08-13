from __future__ import annotations

from decimal import Decimal
from typing import Any

import frappe

from adv_finance.compatibility.erpnext_v16 import (
    get_payment_reference,
    get_supplier_invoice_reference,
    get_supplier_ledger_entries,
    get_supplier_opening_balance,
    validate_erpnext_installed,
)
from adv_finance.services.statement_normalizer import normalize_reference


def get_supplier_ledger(company: str, supplier: str, payable_account: str | None, from_date, to_date) -> dict[str, Any]:
    validate_erpnext_installed()
    opening_balance = get_supplier_opening_balance(company, supplier, payable_account, from_date)
    raw_entries = get_supplier_ledger_entries(company, supplier, payable_account, from_date, to_date)
    running_balance = opening_balance
    lines = []

    for entry in raw_entries:
        debit = Decimal(str(entry.debit or 0))
        credit = Decimal(str(entry.credit or 0))
        amount = credit - debit
        running_balance += amount
        reference = (
            get_supplier_invoice_reference(entry.voucher_type, entry.voucher_no)
            or get_payment_reference(entry.voucher_type, entry.voucher_no)
            or entry.voucher_no
        )
        lines.append(
            {
                "posting_date": entry.posting_date,
                "voucher_type": entry.voucher_type,
                "voucher_no": entry.voucher_no,
                "against_voucher_type": entry.against_voucher_type,
                "against_voucher": entry.against_voucher,
                "supplier_invoice_number": get_supplier_invoice_reference(entry.voucher_type, entry.voucher_no),
                "reference_no": get_payment_reference(entry.voucher_type, entry.voucher_no),
                "remarks": entry.remarks,
                "debit": debit,
                "credit": credit,
                "amount": amount,
                "running_balance": running_balance,
                "account": entry.account,
                "currency": entry.currency,
                "normalized_reference": normalize_reference(reference),
                "match_status": "Unmatched",
                "matched": 0,
            }
        )

    currency = lines[0]["currency"] if lines else frappe.db.get_value("Company", company, "default_currency")
    return {
        "opening_balance": opening_balance,
        "closing_balance": running_balance,
        "currency": currency,
        "lines": lines,
    }
