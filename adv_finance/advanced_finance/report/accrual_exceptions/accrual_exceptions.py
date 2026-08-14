import frappe


def execute(filters=None):
    filters = filters or {}
    columns = [
        {"label": "Accrual", "fieldname": "accrual", "fieldtype": "Link", "options": "Accrual", "width": 160},
        {"label": "Purchase Invoice", "fieldname": "purchase_invoice", "fieldtype": "Link", "options": "Purchase Invoice", "width": 170},
        {"label": "Exception Type", "fieldname": "exception_type", "fieldtype": "Data", "width": 190},
        {"label": "Severity", "fieldname": "severity", "fieldtype": "Data", "width": 90},
        {"label": "Description", "fieldname": "description", "fieldtype": "Small Text", "width": 260},
        {"label": "Amount", "fieldname": "amount", "fieldtype": "Currency", "width": 120},
        {"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 100},
        {"label": "Assigned To", "fieldname": "assigned_to", "fieldtype": "Link", "options": "User", "width": 140},
    ]
    where = ["exc.parenttype = 'Accrual'"]
    values = {}
    if filters.get("company"):
        where.append("acc.company = %(company)s")
        values["company"] = filters["company"]
    if filters.get("exception_type"):
        where.append("exc.exception_type = %(exception_type)s")
        values["exception_type"] = filters["exception_type"]
    if filters.get("status"):
        where.append("exc.status = %(status)s")
        values["status"] = filters["status"]
    data = frappe.db.sql(
        f"""
        select exc.parent as accrual, exc.purchase_invoice, exc.exception_type,
               exc.severity, exc.description, exc.amount, exc.status, exc.assigned_to
        from `tabAccrual Exception` exc
        inner join `tabAccrual` acc on acc.name = exc.parent
        where {" and ".join(where)}
        order by field(exc.severity, 'Critical', 'High', 'Medium', 'Low'), exc.idx asc
        """,
        values,
        as_dict=True,
    )
    return columns, data
