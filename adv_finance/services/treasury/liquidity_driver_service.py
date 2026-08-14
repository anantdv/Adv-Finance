from __future__ import annotations

from decimal import Decimal

import frappe


def get_liquidity_drivers(cash_forecast: str, start_date=None, end_date=None) -> dict:
    forecast = frappe.get_doc("Cash Forecast", cash_forecast)
    drivers = []
    for row in forecast.lines:
        if start_date and row.forecast_date < start_date:
            continue
        if end_date and row.forecast_date > end_date:
            continue
        amount = Decimal(str(row.probability_weighted_amount or row.company_currency_amount or 0))
        drivers.append({
            "date": row.forecast_date,
            "direction": row.direction,
            "source_type": row.source_type,
            "source_document": row.source_document,
            "party": row.party,
            "description": row.description,
            "amount": amount,
        })
    payments = sorted([d for d in drivers if d["direction"] == "Outflow"], key=lambda d: d["amount"], reverse=True)[:10]
    missing_receipts = sorted([d for d in drivers if d["direction"] == "Inflow" and d["amount"]], key=lambda d: d["amount"], reverse=True)[:10]
    return {"payments": payments, "missing_receipts": missing_receipts, "drivers": sorted(drivers, key=lambda d: abs(d["amount"]), reverse=True)[:20]}
