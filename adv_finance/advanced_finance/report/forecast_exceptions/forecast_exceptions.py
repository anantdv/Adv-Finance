from __future__ import annotations

import frappe


def execute(filters=None):
    filters = filters or {}
    q = {}
    if filters.get("cash_forecast"):
        q["cash_forecast"] = filters.get("cash_forecast")
    rows = frappe.get_all("Treasury Forecast Exception", filters=q, fields=["cash_forecast", "exception_type", "severity", "date", "amount", "source_document", "status"], order_by="date asc")
    return ["Forecast:Link/Cash Forecast:180", "Type:Data:180", "Severity:Data:90", "Date:Date:100", "Amount:Currency:120", "Source:Data:180", "Status:Data:100"], [[r.cash_forecast, r.exception_type, r.severity, r.date, r.amount, r.source_document, r.status] for r in rows]
