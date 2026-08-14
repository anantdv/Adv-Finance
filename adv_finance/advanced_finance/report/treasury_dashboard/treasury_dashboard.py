from __future__ import annotations

import frappe
from adv_finance.services.treasury.cash_position_service import get_cash_position


def execute(filters=None):
    filters = filters or {}
    position = get_cash_position(filters.get("company"), filters.get("date"))
    exceptions = frappe.db.count("Treasury Forecast Exception", {"status": ["not in", ["Resolved", "Closed"]]})
    columns = ["Metric:Data:240", "Value:Currency:160"]
    rows = [["Actual Cash", position["actual_cash"]], ["Available Liquidity", position["available_liquidity"]], ["Restricted Cash", position["restricted_cash"]], ["Minimum Cash Buffer", position["minimum_cash_buffer"]], ["Liquidity Headroom", position["liquidity_headroom"]], ["Open Forecast Exceptions", exceptions]]
    return columns, rows
