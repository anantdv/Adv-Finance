import frappe


def execute(filters=None):
    filters = filters or {}
    columns = [
        {"label": "Accrual", "fieldname": "name", "fieldtype": "Link", "options": "Accrual", "width": 160},
        {"label": "Description", "fieldname": "description", "fieldtype": "Small Text", "width": 220},
        {"label": "Supplier", "fieldname": "supplier", "fieldtype": "Link", "options": "Supplier", "width": 160},
        {"label": "Accrual Amount", "fieldname": "accrual_amount", "fieldtype": "Currency", "width": 130},
        {"label": "Matched", "fieldname": "consumed_amount", "fieldtype": "Currency", "width": 120},
        {"label": "Remaining", "fieldname": "remaining_amount", "fieldtype": "Currency", "width": 120},
        {"label": "Age", "fieldname": "days_open", "fieldtype": "Int", "width": 80},
        {"label": "Bucket", "fieldname": "age_bucket", "fieldtype": "Data", "width": 110},
        {"label": "Reversal Status", "fieldname": "reversal_status", "fieldtype": "Data", "width": 130},
        {"label": "Matching Status", "fieldname": "matching_status", "fieldtype": "Data", "width": 130},
    ]
    query_filters = {"workflow_status": ["!=", "Closed"]}
    if filters.get("company"):
        query_filters["company"] = filters["company"]
    if filters.get("age_bucket"):
        query_filters["age_bucket"] = filters["age_bucket"]
    data = frappe.get_all(
        "Accrual",
        filters=query_filters,
        fields=[
            "name", "description", "supplier", "accrual_amount", "consumed_amount",
            "remaining_amount", "days_open", "age_bucket", "reversal_status", "matching_status",
        ],
        order_by="days_open desc, remaining_amount desc",
    )
    return columns, data
