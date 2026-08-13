from __future__ import annotations

import frappe


def execute(filters=None):
    filters = filters or {}
    columns = [
        {"label": "Reconciliation", "fieldname": "name", "fieldtype": "Link", "options": "Supplier Reconciliation", "width": 180},
        {"label": "Supplier", "fieldname": "supplier", "fieldtype": "Link", "options": "Supplier", "width": 180},
        {"label": "Statement Date", "fieldname": "statement_date", "fieldtype": "Date", "width": 120},
        {"label": "ERP Balance", "fieldname": "erp_closing_balance", "fieldtype": "Currency", "width": 130},
        {"label": "Statement Balance", "fieldname": "statement_closing_balance", "fieldtype": "Currency", "width": 150},
        {"label": "Difference", "fieldname": "reconciliation_difference", "fieldtype": "Currency", "width": 130},
        {"label": "Status", "fieldname": "reconciliation_status", "fieldtype": "Data", "width": 130},
        {"label": "Closed By", "fieldname": "closed_by", "fieldtype": "Link", "options": "User", "width": 140},
        {"label": "Closed On", "fieldname": "closed_on", "fieldtype": "Datetime", "width": 160},
    ]
    conditions = {}
    for key in ("company", "supplier", "reconciliation_status"):
        if filters.get(key):
            conditions[key] = filters[key]
    if filters.get("from_date"):
        conditions["statement_to_date"] = [">=", filters["from_date"]]
    if filters.get("to_date"):
        existing = conditions.get("statement_to_date")
        conditions["statement_to_date"] = ["between", [filters.get("from_date") if existing else "1900-01-01", filters["to_date"]]]

    data = frappe.get_all(
        "Supplier Reconciliation",
        filters=conditions,
        fields=[
            "name", "supplier", "statement_date", "erp_closing_balance", "statement_closing_balance",
            "reconciliation_difference", "reconciliation_status", "closed_by", "closed_on",
        ],
        order_by="statement_to_date desc, modified desc",
    )
    return columns, data
