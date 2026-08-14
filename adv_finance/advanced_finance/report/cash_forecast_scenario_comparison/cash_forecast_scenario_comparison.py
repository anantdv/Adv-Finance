from __future__ import annotations

import frappe


def execute(filters=None):
    filters = filters or {}
    forecasts = frappe.get_all("Cash Forecast", filters={"company": filters.get("company"), "status": ["in", ["Generated", "Reviewed", "Approved"]]}, fields=["name", "scenario", "minimum_projected_cash", "lowest_liquidity_date", "liquidity_shortfall"], order_by="forecast_date desc", limit=20)
    columns = ["Forecast:Link/Cash Forecast:180", "Scenario:Link/Cash Forecast Scenario:160", "Minimum Cash:Currency:140", "Week/Date of Min:Date:130", "Shortfall:Currency:130"]
    return columns, [[f.name, f.scenario, f.minimum_projected_cash, f.lowest_liquidity_date, f.liquidity_shortfall] for f in forecasts]
