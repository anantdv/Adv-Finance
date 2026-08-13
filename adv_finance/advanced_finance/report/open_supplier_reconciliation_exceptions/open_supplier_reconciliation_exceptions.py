from __future__ import annotations

import frappe


def execute(filters=None):
    filters = filters or {}
    columns = [
        {"label": "Reconciliation", "fieldname": "reconciliation", "fieldtype": "Link", "options": "Supplier Reconciliation", "width": 180},
        {"label": "Supplier", "fieldname": "supplier", "fieldtype": "Link", "options": "Supplier", "width": 180},
        {"label": "Date", "fieldname": "statement_to_date", "fieldtype": "Date", "width": 120},
        {"label": "Exception Type", "fieldname": "exception_type", "fieldtype": "Data", "width": 180},
        {"label": "Reference", "fieldname": "reference", "fieldtype": "Data", "width": 140},
        {"label": "Statement Amount", "fieldname": "statement_amount", "fieldtype": "Currency", "width": 140},
        {"label": "ERP Amount", "fieldname": "erp_amount", "fieldtype": "Currency", "width": 130},
        {"label": "Difference", "fieldname": "difference", "fieldtype": "Currency", "width": 120},
        {"label": "Assigned To", "fieldname": "assigned_to", "fieldtype": "Link", "options": "User", "width": 140},
        {"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 160},
    ]
    where = ["exc.parenttype = 'Supplier Reconciliation'", "exc.status not in ('Resolved', 'Ignored')"]
    values = {}
    if filters.get("company"):
        where.append("rec.company = %(company)s")
        values["company"] = filters["company"]
    if filters.get("reconciliation"):
        where.append("rec.name = %(reconciliation)s")
        values["reconciliation"] = filters["reconciliation"]
    if filters.get("supplier"):
        where.append("rec.supplier = %(supplier)s")
        values["supplier"] = filters["supplier"]
    if filters.get("exception_type"):
        where.append("exc.exception_type = %(exception_type)s")
        values["exception_type"] = filters["exception_type"]
    if filters.get("assigned_to"):
        where.append("exc.assigned_to = %(assigned_to)s")
        values["assigned_to"] = filters["assigned_to"]
    if filters.get("status"):
        where.append("exc.status = %(status)s")
        values["status"] = filters["status"]

    data = frappe.db.sql(
        f"""
        select
            exc.parent as reconciliation, rec.supplier, rec.statement_to_date,
            exc.exception_type, exc.reference, exc.statement_amount, exc.erp_amount,
            exc.difference, exc.assigned_to, exc.status
        from `tabSupplier Reconciliation Exception` exc
        inner join `tabSupplier Reconciliation` rec on rec.name = exc.parent
        where {" and ".join(where)}
        order by rec.statement_to_date desc, exc.idx asc
        """,
        values,
        as_dict=True,
    )
    return columns, data
