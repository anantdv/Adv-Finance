from __future__ import annotations

import frappe


def execute(filters=None):
    filters = filters or {}
    columns = [
        {"label": "Close Period", "fieldname": "financial_close_period", "fieldtype": "Link", "options": "Financial Close Period", "width": 180},
        {"label": "Company", "fieldname": "company", "fieldtype": "Link", "options": "Company", "width": 160},
        {"label": "Task", "fieldname": "task_name", "fieldtype": "Data", "width": 240},
        {"label": "Category", "fieldname": "category", "fieldtype": "Data", "width": 150},
        {"label": "Due Date", "fieldname": "due_date", "fieldtype": "Date", "width": 110},
        {"label": "Risk", "fieldname": "risk_level", "fieldtype": "Data", "width": 90},
        {"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 130},
        {"label": "Blocked By", "fieldname": "blocked_reason", "fieldtype": "Data", "width": 260},
    ]
    where = ["1=1"]
    values = {}
    owner = filters.get("assigned_to") or frappe.session.user
    if owner:
        where.append("(assigned_to = %(assigned_to)s or reviewer = %(assigned_to)s)")
        values["assigned_to"] = owner
    if filters.get("status"):
        where.append("status = %(status)s")
        values["status"] = filters["status"]
    data = frappe.db.sql(f"""
        select financial_close_period, company, task_name, category, due_date, risk_level, status, blocked_reason
        from `tabFinancial Close Task`
        where {' and '.join(where)}
        order by due_date asc, sequence asc
    """, values, as_dict=True)
    return columns, data
