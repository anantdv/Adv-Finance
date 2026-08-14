from __future__ import annotations
import frappe
def execute(filters=None):
    filters=filters or {}; cols=[{"label":"Promise","fieldname":"name","fieldtype":"Link","options":"Promise to Pay","width":160},{"label":"Customer","fieldname":"customer","fieldtype":"Link","options":"Customer","width":150},{"label":"Promise Date","fieldname":"promised_payment_date","fieldtype":"Date","width":110},{"label":"Amount","fieldname":"promised_amount","fieldtype":"Currency","width":120},{"label":"Received","fieldname":"actual_received_amount","fieldtype":"Currency","width":120},{"label":"Remaining","fieldname":"remaining_promised_amount","fieldtype":"Currency","width":120},{"label":"Status","fieldname":"status","fieldtype":"Data","width":100},{"label":"Collector","fieldname":"collector","fieldtype":"Link","options":"User","width":150}]
    data=frappe.db.sql("""select p.name,p.customer,p.promised_payment_date,p.promised_amount,p.actual_received_amount,p.remaining_promised_amount,p.status,c.collector from `tabPromise to Pay` p left join `tabCollection Case` c on c.name=p.collection_case order by p.promised_payment_date desc""", as_dict=True)
    return cols,data
