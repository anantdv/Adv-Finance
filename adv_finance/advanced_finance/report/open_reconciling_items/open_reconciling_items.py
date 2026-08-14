import frappe


def execute(filters=None):
    filters = filters or {}
    columns = [
        {"label": "Company", "fieldname": "company", "fieldtype": "Link", "options": "Company", "width": 160},
        {"label": "Account", "fieldname": "account", "fieldtype": "Link", "options": "Account", "width": 220},
        {"label": "Reconciliation", "fieldname": "reconciliation", "fieldtype": "Link", "options": "Account Reconciliation", "width": 180},
        {"label": "Item", "fieldname": "reference", "fieldtype": "Data", "width": 140},
        {"label": "Description", "fieldname": "description", "fieldtype": "Small Text", "width": 250},
        {"label": "Amount", "fieldname": "amount", "fieldtype": "Currency", "width": 120},
        {"label": "Age", "fieldname": "days_open", "fieldtype": "Int", "width": 80},
        {"label": "Expected Clearance Date", "fieldname": "expected_clearance_date", "fieldtype": "Date", "width": 150},
        {"label": "Assigned To", "fieldname": "assigned_to", "fieldtype": "Link", "options": "User", "width": 140},
        {"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 120},
    ]
    where = ["item.parenttype = 'Account Reconciliation'", "item.item_type != 'Supporting Item'", "item.status not in ('Resolved', 'Cleared', 'Ignored')"]
    values = {}
    if filters.get("company"):
        where.append("rec.company = %(company)s")
        values["company"] = filters["company"]
    if filters.get("account"):
        where.append("rec.account = %(account)s")
        values["account"] = filters["account"]
    data = frappe.db.sql(
        f"""
        select rec.company, rec.account, item.parent as reconciliation, item.reference,
               item.description, item.amount, item.days_open, item.expected_clearance_date,
               item.assigned_to, item.status
        from `tabAccount Reconciliation Item` item
        inner join `tabAccount Reconciliation` rec on rec.name = item.parent
        where {" and ".join(where)}
        order by item.days_open desc, abs(item.amount) desc
        """,
        values,
        as_dict=True,
    )
    return columns, data
