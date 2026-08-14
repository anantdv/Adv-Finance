from __future__ import annotations

from decimal import Decimal

import frappe


def get_company_currency(company: str) -> str | None:
    return frappe.db.get_value("Company", company, "default_currency")


def get_exchange_rate(from_currency: str | None, to_currency: str | None, date=None) -> Decimal:
    if not from_currency or not to_currency or from_currency == to_currency:
        return Decimal("1")
    try:
        from erpnext.setup.utils import get_exchange_rate as erpnext_get_exchange_rate

        return Decimal(str(erpnext_get_exchange_rate(from_currency, to_currency, date)))
    except Exception:
        rate = frappe.db.get_value(
            "Currency Exchange",
            {"from_currency": from_currency, "to_currency": to_currency, "date": ["<=", date]},
            "exchange_rate",
            order_by="date desc",
        )
        if rate is None:
            frappe.throw(f"Missing exchange rate for {from_currency} to {to_currency} on {date}.")
        return Decimal(str(rate))


def convert_amount(amount, from_currency: str | None, to_currency: str | None, date=None) -> tuple[Decimal, Decimal]:
    native = Decimal(str(amount or 0))
    rate = get_exchange_rate(from_currency, to_currency, date)
    return native * rate, rate
