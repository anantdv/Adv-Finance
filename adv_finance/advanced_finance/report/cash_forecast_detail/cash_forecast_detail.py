from __future__ import annotations

import frappe


def execute(filters=None):
    filters = filters or {}
    forecast = frappe.get_doc("Cash Forecast", filters.get("forecast"))
    columns = ["Date:Date:100", "Week:Int:70", "Direction:Data:90", "Category:Data:140", "Party:Dynamic Link/party_type:180", "Source:Data:180", "Description:Data:240", "Nominal Amount:Currency:130", "Probability:Percent:110", "Weighted Amount:Currency:140", "Expected Date:Date:110", "Confidence:Data:90", "Status:Data:100"]
    rows = [[r.forecast_date, r.week_number, r.direction, r.source_type, r.party, f"{r.source_type} {r.source_document or ''}", r.description, r.company_currency_amount, r.probability_percent, r.probability_weighted_amount, r.expected_date, r.confidence_level, r.status] for r in forecast.lines]
    return columns, rows
