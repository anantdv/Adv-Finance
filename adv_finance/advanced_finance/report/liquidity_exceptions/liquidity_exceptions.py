from __future__ import annotations

import frappe


def execute(filters=None):
    filters = filters or {}
    conditions = {"status": ["not in", ["Resolved", "Closed"]], "exception_type": ["in", ["Liquidity Shortfall", "Low Liquidity"]]}
    if filters.get("cash_forecast"):
        conditions["cash_forecast"] = filters.get("cash_forecast")
    rows = frappe.get_all("Treasury Forecast Exception", filters=conditions, fields=["cash_forecast", "date", "amount", "severity", "description", "status"], order_by="date asc")
    columns = ["Forecast:Link/Cash Forecast:180", "Date:Date:100", "Shortfall/Amount:Currency:140", "Severity:Data:90", "Main Cash Drivers:Data:300", "Status:Data:100"]
    return columns, [[r.cash_forecast, r.date, r.amount, r.severity, r.description, r.status] for r in rows]
