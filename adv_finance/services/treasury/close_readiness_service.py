from __future__ import annotations

import frappe


def get_treasury_close_readiness(company: str, period_end) -> dict:
    critical_exceptions = frappe.db.count("Treasury Forecast Exception", {"status": ["not in", ["Resolved", "Closed"]], "severity": "Critical", "date": ["<=", period_end]})
    cash_forecasts = frappe.db.count("Cash Forecast", {"company": company, "forecast_from": ["<=", period_end], "forecast_to": [">=", period_end], "status": ["in", ["Generated", "Reviewed", "Approved"]]})
    treasury_accounts = frappe.db.count("Treasury Account", {"company": company, "active": 1, "include_in_cash_position": 1})
    ready = bool(treasury_accounts and cash_forecasts and not critical_exceptions)
    return {"ready": ready, "treasury_accounts": treasury_accounts, "period_forecasts": cash_forecasts, "critical_exceptions": critical_exceptions}
