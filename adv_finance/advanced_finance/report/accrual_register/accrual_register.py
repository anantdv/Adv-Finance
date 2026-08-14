import frappe


def execute(filters=None):
    filters = filters or {}
    columns = [
        {"label": "Accrual", "fieldname": "name", "fieldtype": "Link", "options": "Accrual", "width": 160},
        {"label": "Accrual Date", "fieldname": "accrual_date", "fieldtype": "Date", "width": 110},
        {"label": "Description", "fieldname": "description", "fieldtype": "Small Text", "width": 220},
        {"label": "Supplier", "fieldname": "supplier", "fieldtype": "Link", "options": "Supplier", "width": 160},
        {"label": "Expense Account", "fieldname": "expense_account", "fieldtype": "Link", "options": "Account", "width": 190},
        {"label": "Accrual Account", "fieldname": "accrual_liability_account", "fieldtype": "Link", "options": "Account", "width": 190},
        {"label": "Accrual Amount", "fieldname": "accrual_amount", "fieldtype": "Currency", "width": 130},
        {"label": "Consumed Amount", "fieldname": "consumed_amount", "fieldtype": "Currency", "width": 140},
        {"label": "Remaining Amount", "fieldname": "remaining_amount", "fieldtype": "Currency", "width": 140},
        {"label": "Actual Amount", "fieldname": "actual_amount", "fieldtype": "Currency", "width": 130},
        {"label": "Variance", "fieldname": "variance_amount", "fieldtype": "Currency", "width": 120},
        {"label": "Reversal Date", "fieldname": "reversal_date", "fieldtype": "Date", "width": 120},
        {"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 130},
    ]
    query_filters = {}
    for key in ("company", "accrual_type", "supplier", "expense_account", "cost_center", "status"):
        if filters.get(key):
            query_filters[key] = filters[key]
    if filters.get("from_date"):
        query_filters["accrual_date"] = [">=", filters["from_date"]]
    if filters.get("to_date"):
        query_filters["accrual_date"] = ["<=", filters["to_date"]]
    data = frappe.get_all(
        "Accrual",
        filters=query_filters,
        fields=[
            "name", "accrual_date", "description", "supplier", "expense_account",
            "accrual_liability_account", "accrual_amount", "consumed_amount",
            "remaining_amount", "actual_amount", "variance_amount", "reversal_date", "status",
        ],
        order_by="accrual_date desc, modified desc",
    )
    return columns, data
