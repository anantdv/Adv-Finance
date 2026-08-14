from __future__ import annotations
import frappe
def execute(filters=None):
    cols=[{"label":"Collector","fieldname":"collector","fieldtype":"Link","options":"User","width":160},{"label":"Open Overdue","fieldname":"opening_overdue","fieldtype":"Currency","width":130},{"label":"Promises Kept","fieldname":"promises_kept","fieldtype":"Int","width":110},{"label":"Promises Broken","fieldname":"promises_broken","fieldtype":"Int","width":120},{"label":"Disputes Resolved","fieldname":"disputes_resolved","fieldtype":"Int","width":130},{"label":"Closing Overdue","fieldname":"closing_overdue","fieldtype":"Currency","width":130}]
    rows=frappe.db.sql("""select collector, sum(overdue_amount) opening_overdue, sum(overdue_amount) closing_overdue from `tabCollection Case` group by collector order by closing_overdue desc""", as_dict=True)
    for r in rows:
        r.promises_kept=frappe.db.count('Promise to Pay', {'status': 'Kept'})
        r.promises_broken=frappe.db.count('Promise to Pay', {'status': 'Broken'})
        r.disputes_resolved=frappe.db.count('Customer Dispute', {'status': ['in', ['Resolved','Closed']]})
    return cols, rows
