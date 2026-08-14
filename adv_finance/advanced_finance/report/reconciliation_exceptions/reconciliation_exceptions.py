import frappe


def execute(filters=None):
    filters = filters or {}
    columns = [
        {"label": "Reconciliation", "fieldname": "name", "fieldtype": "Link", "options": "Account Reconciliation", "width": 180},
        {"label": "Company", "fieldname": "company", "fieldtype": "Link", "options": "Company", "width": 160},
        {"label": "Account", "fieldname": "account", "fieldtype": "Link", "options": "Account", "width": 220},
        {"label": "Exception", "fieldname": "exception_type", "fieldtype": "Data", "width": 180},
        {"label": "Unexplained Difference", "fieldname": "unexplained_difference", "fieldtype": "Currency", "width": 170},
        {"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 140},
    ]
    values = {}
    conditions = ["(unexplained_difference != 0 or status = 'Review Rejected' or (supporting_document_required = 1 and ifnull(supporting_document, '') = ''))"]
    if filters.get("company"):
        conditions.append("company = %(company)s")
        values["company"] = filters["company"]
    rows = frappe.db.sql(
        f"""
        select name, company, account,
               case
                 when supporting_document_required = 1 and ifnull(supporting_document, '') = '' then 'Missing Evidence'
                 when status = 'Review Rejected' then 'Rejected Reconciliation'
                 when unexplained_difference != 0 then 'Unexplained Difference'
                 else 'Other'
               end as exception_type,
               unexplained_difference, status
        from `tabAccount Reconciliation`
        where {" and ".join(conditions)}
        order by abs(unexplained_difference) desc, modified desc
        """,
        values,
        as_dict=True,
    )
    return columns, rows
