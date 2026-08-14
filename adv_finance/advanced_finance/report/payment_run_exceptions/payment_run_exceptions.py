import frappe


def execute(filters=None):
    filters = filters or {}
    columns = [
        {"label": "Payment Run", "fieldname": "payment_run", "fieldtype": "Link", "options": "Payment Run", "width": 180},
        {"label": "Supplier", "fieldname": "supplier", "fieldtype": "Link", "options": "Supplier", "width": 180},
        {"label": "Purchase Invoice", "fieldname": "purchase_invoice", "fieldtype": "Link", "options": "Purchase Invoice", "width": 170},
        {"label": "Exception Type", "fieldname": "exception_type", "fieldtype": "Data", "width": 190},
        {"label": "Description", "fieldname": "description", "fieldtype": "Small Text", "width": 260},
        {"label": "Amount", "fieldname": "amount", "fieldtype": "Currency", "width": 120},
        {"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 120},
    ]
    where = ["exc.parenttype = 'Payment Run'"]
    values = {}
    if filters.get("company"):
        where.append("run.company = %(company)s")
        values["company"] = filters["company"]
    if filters.get("payment_run"):
        where.append("run.name = %(payment_run)s")
        values["payment_run"] = filters["payment_run"]
    if filters.get("supplier"):
        where.append("exc.supplier = %(supplier)s")
        values["supplier"] = filters["supplier"]
    if filters.get("exception_type"):
        where.append("exc.exception_type = %(exception_type)s")
        values["exception_type"] = filters["exception_type"]
    if filters.get("status"):
        where.append("exc.status = %(status)s")
        values["status"] = filters["status"]
    data = frappe.db.sql(
        f"""
        select exc.parent as payment_run, exc.supplier, exc.purchase_invoice,
               exc.exception_type, exc.description, exc.amount, exc.status
        from `tabPayment Run Exception` exc
        inner join `tabPayment Run` run on run.name = exc.parent
        where {" and ".join(where)}
        order by run.payment_date desc, exc.idx asc
        """,
        values,
        as_dict=True,
    )
    return columns, data
