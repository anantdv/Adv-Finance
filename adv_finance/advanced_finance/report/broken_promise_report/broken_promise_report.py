from __future__ import annotations
import frappe
from frappe.utils import date_diff, today
def execute(filters=None):
    cols=[{"label":"Customer","fieldname":"customer","fieldtype":"Link","options":"Customer","width":150},{"label":"Promise","fieldname":"name","fieldtype":"Link","options":"Promise to Pay","width":160},{"label":"Promised Amount","fieldname":"promised_amount","fieldtype":"Currency","width":120},{"label":"Received","fieldname":"actual_received_amount","fieldtype":"Currency","width":120},{"label":"Shortfall","fieldname":"shortfall","fieldtype":"Currency","width":120},{"label":"Days Late","fieldname":"days_late","fieldtype":"Int","width":90},{"label":"Collector","fieldname":"collector","fieldtype":"Link","options":"User","width":150},{"label":"Priority","fieldname":"collection_priority","fieldtype":"Data","width":90}]
    data=frappe.db.sql("""select p.name,p.customer,p.promised_payment_date,p.promised_amount,p.actual_received_amount,(p.promised_amount-p.actual_received_amount) shortfall,c.collector,c.collection_priority from `tabPromise to Pay` p left join `tabCollection Case` c on c.name=p.collection_case where p.status='Broken' order by p.promised_payment_date asc""", as_dict=True)
    for r in data: r.days_late=date_diff(today(), r.promised_payment_date) if r.promised_payment_date else 0
    return cols,data
