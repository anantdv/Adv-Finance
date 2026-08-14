import frappe


def execute(filters=None):
    columns = [
        {"label": "Company", "fieldname": "company", "fieldtype": "Link", "options": "Company", "width": 160},
        {"label": "Account", "fieldname": "account", "fieldtype": "Link", "options": "Account", "width": 220},
        {"label": "Current", "fieldname": "current", "fieldtype": "Currency", "width": 120},
        {"label": "1-30", "fieldname": "one_to_thirty", "fieldtype": "Currency", "width": 120},
        {"label": "31-60", "fieldname": "thirty_one_to_sixty", "fieldtype": "Currency", "width": 120},
        {"label": "61-90", "fieldname": "sixty_one_to_ninety", "fieldtype": "Currency", "width": 120},
        {"label": "91-180", "fieldname": "ninety_one_to_one_eighty", "fieldtype": "Currency", "width": 120},
        {"label": "180+", "fieldname": "over_one_eighty", "fieldtype": "Currency", "width": 120},
    ]
    filters = filters or {}
    where = ["item.parenttype = 'Account Reconciliation'", "item.item_type != 'Supporting Item'", "item.status not in ('Resolved', 'Cleared', 'Ignored')"]
    values = {}
    if filters.get("company"):
        where.append("rec.company = %(company)s")
        values["company"] = filters["company"]
    data = frappe.db.sql(
        f"""
        select rec.company, rec.account,
               sum(case when item.age_bucket = 'Current' then item.amount else 0 end) as current,
               sum(case when item.age_bucket = '1-30' then item.amount else 0 end) as one_to_thirty,
               sum(case when item.age_bucket = '31-60' then item.amount else 0 end) as thirty_one_to_sixty,
               sum(case when item.age_bucket = '61-90' then item.amount else 0 end) as sixty_one_to_ninety,
               sum(case when item.age_bucket = '91-180' then item.amount else 0 end) as ninety_one_to_one_eighty,
               sum(case when item.age_bucket = '180+' then item.amount else 0 end) as over_one_eighty
        from `tabAccount Reconciliation Item` item
        inner join `tabAccount Reconciliation` rec on rec.name = item.parent
        where {" and ".join(where)}
        group by rec.company, rec.account
        order by over_one_eighty desc, ninety_one_to_one_eighty desc
        """,
        values,
        as_dict=True,
    )
    return columns, data
