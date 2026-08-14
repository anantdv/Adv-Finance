import frappe


def execute(filters=None):
    filters = filters or {}
    columns = [
        {"label": "Payment Hold", "fieldname": "name", "fieldtype": "Link", "options": "Payment Hold", "width": 180},
        {"label": "Company", "fieldname": "company", "fieldtype": "Link", "options": "Company", "width": 160},
        {"label": "Supplier", "fieldname": "supplier", "fieldtype": "Link", "options": "Supplier", "width": 180},
        {"label": "Purchase Invoice", "fieldname": "purchase_invoice", "fieldtype": "Link", "options": "Purchase Invoice", "width": 170},
        {"label": "Scope", "fieldname": "hold_scope", "fieldtype": "Data", "width": 100},
        {"label": "Reason", "fieldname": "reason", "fieldtype": "Data", "width": 220},
        {"label": "Active", "fieldname": "active", "fieldtype": "Check", "width": 80},
    ]
    query_filters = {}
    for key in ("company", "supplier", "active"):
        if filters.get(key) not in (None, ""):
            query_filters[key] = filters[key]
    if filters.get("reason"):
        query_filters["reason"] = filters["reason"]
    data = frappe.get_all(
        "Payment Hold",
        filters=query_filters,
        fields=["name", "company", "supplier", "purchase_invoice", "hold_scope", "reason", "active"],
        order_by="modified desc",
    )
    return columns, data
