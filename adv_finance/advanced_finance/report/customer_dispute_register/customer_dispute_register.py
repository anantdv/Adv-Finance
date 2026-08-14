from __future__ import annotations
import frappe
from frappe.utils import date_diff, today
def execute(filters=None):
    cols=[{"label":"Dispute","fieldname":"name","fieldtype":"Link","options":"Customer Dispute","width":160},{"label":"Customer","fieldname":"customer","fieldtype":"Link","options":"Customer","width":150},{"label":"Invoice","fieldname":"sales_invoice","fieldtype":"Link","options":"Sales Invoice","width":150},{"label":"Amount","fieldname":"disputed_amount","fieldtype":"Currency","width":120},{"label":"Type","fieldname":"dispute_type","fieldtype":"Data","width":130},{"label":"Age","fieldname":"age","fieldtype":"Int","width":70},{"label":"Owner","fieldname":"assigned_to","fieldtype":"Link","options":"User","width":150},{"label":"Status","fieldname":"status","fieldtype":"Data","width":120}]
    data=frappe.db.sql("""select name,customer,sales_invoice,disputed_amount,dispute_type,dispute_date,assigned_to,status from `tabCustomer Dispute` order by dispute_date desc""", as_dict=True)
    for r in data: r.age=date_diff(today(), r.dispute_date) if r.dispute_date else 0
    return cols,data
