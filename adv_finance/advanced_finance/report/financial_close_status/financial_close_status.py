from __future__ import annotations

import frappe


def execute(filters=None):
    filters = filters or {}
    columns = [
        {"label": "Close Period", "fieldname": "name", "fieldtype": "Link", "options": "Financial Close Period", "width": 190},
        {"label": "Target Date", "fieldname": "target_close_date", "fieldtype": "Date", "width": 110},
        {"label": "Completion %", "fieldname": "overall_completion_percent", "fieldtype": "Percent", "width": 110},
        {"label": "Completed", "fieldname": "completed_tasks", "fieldtype": "Int", "width": 95},
        {"label": "Blocked", "fieldname": "blocked_tasks", "fieldtype": "Int", "width": 90},
        {"label": "Overdue", "fieldname": "overdue_tasks", "fieldtype": "Int", "width": 90},
        {"label": "Critical Open", "fieldname": "critical_open_tasks", "fieldtype": "Int", "width": 110},
        {"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 130},
        {"label": "Close Manager", "fieldname": "close_manager", "fieldtype": "Link", "options": "User", "width": 170},
    ]
    where = ["1=1"]
    values = {}
    for key in ("company", "close_manager", "status"):
        if filters.get(key):
            where.append(f"{key} = %({key})s")
            values[key] = filters[key]
    if filters.get("period_end"):
        where.append("period_end = %(period_end)s")
        values["period_end"] = filters["period_end"]
    data = frappe.db.sql(f"""
        select name, target_close_date, overall_completion_percent, completed_tasks, blocked_tasks, overdue_tasks, critical_open_tasks, status, close_manager
        from `tabFinancial Close Period`
        where {' and '.join(where)}
        order by period_end desc, company asc
    """, values, as_dict=True)
    return columns, data
