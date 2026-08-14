from __future__ import annotations

import frappe
from frappe.utils import date_diff, today


def execute(filters=None):
    filters = filters or {}
    columns = [
        {"label": "Period", "fieldname": "financial_close_period", "fieldtype": "Link", "options": "Financial Close Period", "width": 180},
        {"label": "Task", "fieldname": "financial_close_task", "fieldtype": "Link", "options": "Financial Close Task", "width": 180},
        {"label": "Category", "fieldname": "category", "fieldtype": "Data", "width": 140},
        {"label": "Exception", "fieldname": "exception_type", "fieldtype": "Data", "width": 180},
        {"label": "Amount", "fieldname": "amount", "fieldtype": "Currency", "width": 110},
        {"label": "Risk", "fieldname": "risk_level", "fieldtype": "Data", "width": 90},
        {"label": "Owner", "fieldname": "assigned_to", "fieldtype": "Link", "options": "User", "width": 160},
        {"label": "Age", "fieldname": "age", "fieldtype": "Int", "width": 70},
        {"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 110},
    ]
    where = ["1=1"]
    values = {}
    for key in ("financial_close_period", "status", "risk_level"):
        if filters.get(key):
            where.append(f"{key} = %({key})s")
            values[key] = filters[key]
    data = frappe.db.sql(f"""
        select financial_close_period, financial_close_task, category, exception_type, amount, risk_level, assigned_to, created_on, status
        from `tabFinancial Close Exception`
        where {' and '.join(where)}
        order by field(risk_level, 'Critical', 'High', 'Medium', 'Low'), created_on desc
    """, values, as_dict=True)
    for row in data:
        row.age = date_diff(today(), row.created_on) if row.created_on else 0
    return columns, data
