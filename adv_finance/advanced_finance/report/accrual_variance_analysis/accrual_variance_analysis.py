import frappe


def execute(filters=None):
    filters = filters or {}
    columns = [
        {"label": "Accrual", "fieldname": "name", "fieldtype": "Link", "options": "Accrual", "width": 160},
        {"label": "Estimated", "fieldname": "accrual_amount", "fieldtype": "Currency", "width": 120},
        {"label": "Actual", "fieldname": "actual_amount", "fieldtype": "Currency", "width": 120},
        {"label": "Variance", "fieldname": "variance_amount", "fieldtype": "Currency", "width": 120},
        {"label": "Variance Status", "fieldname": "variance_status", "fieldtype": "Data", "width": 140},
        {"label": "Supplier", "fieldname": "supplier", "fieldtype": "Link", "options": "Supplier", "width": 160},
        {"label": "Expense Account", "fieldname": "expense_account", "fieldtype": "Link", "options": "Account", "width": 190},
        {"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 130},
        {"label": "Reviewer", "fieldname": "reviewed_by", "fieldtype": "Link", "options": "User", "width": 140},
    ]
    query_filters = {}
    for key in ("company", "supplier", "accrual_type", "expense_account", "cost_center", "variance_status"):
        if filters.get(key):
            query_filters[key] = filters[key]
    data = frappe.get_all(
        "Accrual",
        filters=query_filters,
        fields=[
            "name", "accrual_amount", "actual_amount", "variance_amount", "variance_status",
            "supplier", "expense_account", "status", "reviewed_by",
        ],
        order_by="modified desc",
    )
    return columns, data
