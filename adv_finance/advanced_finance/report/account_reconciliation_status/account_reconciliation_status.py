import frappe


def execute(filters=None):
    filters = filters or {}
    columns = [
        {"label": "Account", "fieldname": "account", "fieldtype": "Link", "options": "Account", "width": 220},
        {"label": "GL Balance", "fieldname": "gl_closing_balance", "fieldtype": "Currency", "width": 130},
        {"label": "Supporting Balance", "fieldname": "supporting_balance", "fieldtype": "Currency", "width": 150},
        {"label": "Gross Difference", "fieldname": "gross_difference", "fieldtype": "Currency", "width": 140},
        {"label": "Explained Difference", "fieldname": "explained_difference", "fieldtype": "Currency", "width": 160},
        {"label": "Unexplained Difference", "fieldname": "unexplained_difference", "fieldtype": "Currency", "width": 170},
        {"label": "Risk", "fieldname": "risk_level", "fieldtype": "Data", "width": 90},
        {"label": "Preparer", "fieldname": "prepared_by", "fieldtype": "Link", "options": "User", "width": 140},
        {"label": "Reviewer", "fieldname": "reviewed_by", "fieldtype": "Link", "options": "User", "width": 140},
        {"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 130},
    ]
    query_filters = {}
    for key in ("company", "account", "risk_level", "prepared_by", "reviewed_by", "status", "period"):
        if filters.get(key):
            query_filters[key] = filters[key]
    data = frappe.get_all(
        "Account Reconciliation",
        filters=query_filters,
        fields=["account", "gl_closing_balance", "supporting_balance", "gross_difference", "explained_difference", "unexplained_difference", "risk_level", "prepared_by", "reviewed_by", "status"],
        order_by="risk_level asc, modified desc",
    )
    return columns, data
