from __future__ import annotations

import frappe
from frappe.utils import date_diff


def execute(filters=None):
    filters = filters or {}
    columns = [
        {"label": "Close Period", "fieldname": "name", "fieldtype": "Link", "options": "Financial Close Period", "width": 190},
        {"label": "Company", "fieldname": "company", "fieldtype": "Link", "options": "Company", "width": 160},
        {"label": "Target Close Days", "fieldname": "target_close_days", "fieldtype": "Int", "width": 130},
        {"label": "Actual Close Days", "fieldname": "actual_close_days", "fieldtype": "Int", "width": 130},
        {"label": "Late Tasks", "fieldname": "late_tasks", "fieldtype": "Int", "width": 100},
        {"label": "Average Task Delay", "fieldname": "average_task_delay", "fieldtype": "Float", "width": 140},
        {"label": "Critical Exceptions", "fieldname": "critical_exceptions", "fieldtype": "Int", "width": 140},
    ]
    where = ["status in ('Closed', 'Reopened')"]
    values = {}
    if filters.get("company"):
        where.append("company = %(company)s")
        values["company"] = filters["company"]
    periods = frappe.db.sql(f"""
        select name, company, period_end, opened_on, target_close_date, actual_close_date
        from `tabFinancial Close Period`
        where {' and '.join(where)}
        order by period_end desc
    """, values, as_dict=True)
    data = []
    for period in periods:
        late_rows = frappe.db.sql("""
            select due_date, completed_on from `tabFinancial Close Task`
            where financial_close_period = %(period)s and completed_on is not null and due_date is not null and date(completed_on) > due_date
        """, {"period": period.name}, as_dict=True)
        delays = [date_diff(row.completed_on, row.due_date) for row in late_rows]
        critical = frappe.db.count("Financial Close Exception", {"financial_close_period": period.name, "risk_level": "Critical"})
        data.append({"name": period.name, "company": period.company, "target_close_days": date_diff(period.target_close_date, period.period_end) if period.target_close_date else 0, "actual_close_days": date_diff(period.actual_close_date, period.period_end) if period.actual_close_date else 0, "late_tasks": len(late_rows), "average_task_delay": sum(delays) / len(delays) if delays else 0, "critical_exceptions": critical})
    return columns, data
