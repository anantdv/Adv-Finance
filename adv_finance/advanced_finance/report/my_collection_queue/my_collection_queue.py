from __future__ import annotations

import frappe


def execute(filters=None):
    filters = filters or {}
    filters.setdefault("collector", frappe.session.user)
    columns = [
        {"label":"Priority","fieldname":"collection_priority","fieldtype":"Data","width":90}, {"label":"Customer","fieldname":"customer","fieldtype":"Link","options":"Customer","width":150}, {"label":"Customer Name","fieldname":"customer_name","fieldtype":"Data","width":190},
        {"label":"Collector","fieldname":"collector","fieldtype":"Link","options":"User","width":150}, {"label":"Total Outstanding","fieldname":"total_outstanding","fieldtype":"Currency","width":130}, {"label":"Overdue","fieldname":"overdue_amount","fieldtype":"Currency","width":120},
        {"label":"Oldest Days","fieldname":"oldest_overdue_days","fieldtype":"Int","width":95}, {"label":"Broken Promises","fieldname":"broken_promise_count","fieldtype":"Int","width":120}, {"label":"Open Disputes","fieldname":"open_dispute_count","fieldtype":"Int","width":110},
        {"label":"Credit Status","fieldname":"credit_status","fieldtype":"Data","width":110}, {"label":"Next Action","fieldname":"next_action_date","fieldtype":"Date","width":110}, {"label":"Last Contact","fieldname":"last_contact_date","fieldtype":"Date","width":110},
        {"label":"Case","fieldname":"name","fieldtype":"Link","options":"Collection Case","width":160},
    ]
    where=["1=1"]; values={}
    for key in ("company","collector","customer","customer_group","territory","collection_priority","risk_level","status"):
        if filters.get(key): where.append(f"{key} = %({key})s"); values[key]=filters[key]
    if filters.get("minimum_overdue_amount"):
        where.append("overdue_amount >= %(minimum_overdue_amount)s"); values["minimum_overdue_amount"]=filters["minimum_overdue_amount"]
    data=frappe.db.sql(f"""select name, collection_priority, customer, customer_name, collector, total_outstanding, overdue_amount, oldest_overdue_days, broken_promise_count, open_dispute_count, next_action_date, last_contact_date, company from `tabCollection Case` where {' and '.join(where)} order by field(collection_priority,'Critical','High','Normal','Low'), broken_promise_count desc, overdue_amount desc, oldest_overdue_days desc""", values, as_dict=True)
    for row in data:
        row.credit_status = "HOLD" if frappe.db.exists("Credit Hold", {"company": row.company, "customer": row.customer, "active": 1}) else "Open"
    return columns, data
