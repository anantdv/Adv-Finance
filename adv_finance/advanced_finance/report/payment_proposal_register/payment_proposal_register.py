import frappe


def execute(filters=None):
    filters = filters or {}
    columns = [
        {"label": "Proposal", "fieldname": "name", "fieldtype": "Link", "options": "Payment Proposal", "width": 180},
        {"label": "Date", "fieldname": "proposal_date", "fieldtype": "Date", "width": 110},
        {"label": "Company", "fieldname": "company", "fieldtype": "Link", "options": "Company", "width": 160},
        {"label": "Bank Account", "fieldname": "bank_account", "fieldtype": "Link", "options": "Bank Account", "width": 160},
        {"label": "Suppliers", "fieldname": "suppliers_count", "fieldtype": "Int", "width": 90},
        {"label": "Invoice Count", "fieldname": "invoices_count", "fieldtype": "Int", "width": 110},
        {"label": "Proposed Amount", "fieldname": "proposed_payment_total", "fieldtype": "Currency", "width": 140},
        {"label": "Selected Amount", "fieldname": "selected_payment_total", "fieldtype": "Currency", "width": 140},
        {"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 140},
        {"label": "Prepared By", "fieldname": "owner", "fieldtype": "Link", "options": "User", "width": 140},
    ]
    query_filters = {}
    for key in ("company", "supplier", "status"):
        if filters.get(key):
            query_filters[key] = filters[key]
    data = frappe.get_all(
        "Payment Proposal",
        filters=query_filters,
        fields=[
            "name", "proposal_date", "company", "bank_account", "suppliers_count", "invoices_count",
            "proposed_payment_total", "selected_payment_total", "status", "owner",
        ],
        order_by="proposal_date desc, modified desc",
    )
    return columns, data
