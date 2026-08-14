from __future__ import annotations
import frappe
def execute(filters=None):
    cols=[{"label":"Review","fieldname":"name","fieldtype":"Link","options":"Credit Review","width":160},{"label":"Customer","fieldname":"customer","fieldtype":"Link","options":"Customer","width":150},{"label":"Review Date","fieldname":"review_date","fieldtype":"Date","width":110},{"label":"Exposure","fieldname":"total_credit_exposure","fieldtype":"Currency","width":130},{"label":"Limit","fieldname":"current_credit_limit","fieldtype":"Currency","width":120},{"label":"Risk","fieldname":"risk_rating","fieldtype":"Data","width":100},{"label":"Recommendation","fieldname":"recommendation","fieldtype":"Data","width":130},{"label":"Status","fieldname":"status","fieldtype":"Data","width":100}]
    return cols, frappe.db.sql("""select name,customer,review_date,total_credit_exposure,current_credit_limit,risk_rating,recommendation,status from `tabCredit Review` order by review_date desc""", as_dict=True)
