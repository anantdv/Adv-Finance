from __future__ import annotations

from decimal import Decimal

from adv_finance.services.treasury.currency_service import get_exchange_rate
from adv_finance.compatibility.erpnext_v16 import get_fx_invoice_rows


def calculate_fx_adjustment(outstanding_fcy, carrying_rate, spot_rate):
    outstanding = Decimal(str(outstanding_fcy or 0))
    carrying = outstanding * Decimal(str(carrying_rate or 0))
    revalued = outstanding * Decimal(str(spot_rate or 0))
    diff = revalued - carrying
    return {"carrying_pgk": carrying, "revalued_pgk": revalued, "fx_difference": diff, "debit_credit_indicator": "Debit" if diff > 0 else "Credit" if diff < 0 else "Nil"}


def fx_adjusted_invoice_register(filters=None):
    filters = filters or {}
    rows=[]
    for inv in get_fx_invoice_rows(**filters):
        spot = filters.get("month_end_spot_rate") or get_exchange_rate(inv.currency, filters.get("company_currency") or "PGK", filters.get("period_end"))
        calc = calculate_fx_adjustment(inv.outstanding_fcy, inv.carrying_exchange_rate, spot)
        rows.append({**inv.__dict__, "month_end_spot_rate": spot, **calc})
    return rows
