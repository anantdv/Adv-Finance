from __future__ import annotations

from decimal import Decimal

import frappe

from adv_finance.compatibility.erpnext_v16 import get_actual_cash_movements


def get_forecast_accuracy(cash_forecast: str) -> dict:
    forecast = frappe.get_doc("Cash Forecast", cash_forecast)
    actuals = get_actual_cash_movements(forecast.company, forecast.forecast_from, forecast.forecast_to)
    forecast_receipts = sum(Decimal(str(row.probability_weighted_amount or 0)) for row in forecast.lines if row.direction == "Inflow")
    forecast_payments = sum(Decimal(str(row.probability_weighted_amount or 0)) for row in forecast.lines if row.direction == "Outflow")
    actual_receipts = sum(Decimal(str(row.received_amount or row.paid_amount or 0)) for row in actuals if row.payment_type == "Receive")
    actual_payments = sum(Decimal(str(row.paid_amount or row.received_amount or 0)) for row in actuals if row.payment_type == "Pay")
    forecast_net = forecast_receipts - forecast_payments
    actual_net = actual_receipts - actual_payments
    variance = actual_net - forecast_net
    denominator = abs(forecast_net) if forecast_net else Decimal("1")
    accuracy = max(Decimal("0"), Decimal("100") - (abs(variance) / denominator * Decimal("100")))
    return {
        "forecast_receipts": forecast_receipts,
        "actual_receipts": actual_receipts,
        "forecast_payments": forecast_payments,
        "actual_payments": actual_payments,
        "forecast_net_flow": forecast_net,
        "actual_net_flow": actual_net,
        "variance": variance,
        "accuracy_percent": accuracy,
    }
