from __future__ import annotations

import frappe


def execute(filters=None):
    filters = filters or {}
    query = {}
    if filters.get("consolidation_period"):
        query["consolidation_period"] = filters.get("consolidation_period")
    rows = frappe.get_all("Consolidation Adjustment", filters=query, fields=["name", "consolidation_period", "adjustment_type", "company", "account", "amount", "currency", "status", "prepared_by", "approved_by"], order_by="modified desc")
    columns = ["Adjustment:Link/Consolidation Adjustment:180", "Period:Link/Consolidation Period:180", "Type:Data:160", "Company:Link/Company:160", "Account:Link/Account:180", "Amount:Currency:130", "Currency:Link/Currency:100", "Status:Data:110", "Prepared By:Link/User:160", "Approved By:Link/User:160"]
    return columns, [[r.name, r.consolidation_period, r.adjustment_type, r.company, r.account, r.amount, r.currency, r.status, r.prepared_by, r.approved_by] for r in rows]
