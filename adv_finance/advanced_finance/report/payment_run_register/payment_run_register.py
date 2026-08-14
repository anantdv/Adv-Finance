import frappe


def execute(filters=None):
    filters = filters or {}
    columns = [
        {"label": "Payment Run", "fieldname": "name", "fieldtype": "Link", "options": "Payment Run", "width": 180},
        {"label": "Payment Date", "fieldname": "payment_date", "fieldtype": "Date", "width": 120},
        {"label": "Company", "fieldname": "company", "fieldtype": "Link", "options": "Company", "width": 160},
        {"label": "Bank", "fieldname": "bank_account", "fieldtype": "Link", "options": "Bank Account", "width": 160},
        {"label": "Suppliers", "fieldname": "supplier_count", "fieldtype": "Int", "width": 90},
        {"label": "Invoice Count", "fieldname": "invoice_count", "fieldtype": "Int", "width": 110},
        {"label": "Net Payment Amount", "fieldname": "net_payment_amount", "fieldtype": "Currency", "width": 150},
        {"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 140},
        {"label": "Approved By", "fieldname": "approved_by", "fieldtype": "Link", "options": "User", "width": 140},
    ]
    query_filters = {}
    for key in ("company", "status"):
        if filters.get(key):
            query_filters[key] = filters[key]
    data = frappe.get_all(
        "Payment Run",
        filters=query_filters,
        fields=[
            "name", "payment_date", "company", "bank_account", "supplier_count", "invoice_count",
            "net_payment_amount", "status", "approved_by",
        ],
        order_by="payment_date desc, modified desc",
    )
    return columns, data
