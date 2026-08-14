from __future__ import annotations

import frappe
from adv_finance.services.treasury.cash_forecast_service import aggregate_weekly


def execute(filters=None):
    filters = filters or {}
    forecast = frappe.get_doc("Cash Forecast", filters.get("forecast"))
    lines = [row.as_dict() for row in forecast.lines]
    rows = aggregate_weekly(lines, forecast.opening_cash, forecast.company, forecast.forecast_from)
    columns = ["Week:Int:70", "Opening Cash:Currency:140", "Receipts:Currency:130", "Payments:Currency:130", "Other Inflows:Currency:130", "Other Outflows:Currency:130", "Net Movement:Currency:130", "Closing Cash:Currency:140", "Minimum Buffer:Currency:140", "Headroom:Currency:130", "Status:Data:100"]
    return columns, [[r["week"], r["opening_cash"], r["receipts"], r["payments"], r["other_inflows"], r["other_outflows"], r["net_movement"], r["closing_cash"], r["minimum_buffer"], r["headroom"], r["status"]] for r in rows]
