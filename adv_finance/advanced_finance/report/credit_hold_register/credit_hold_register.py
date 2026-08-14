from __future__ import annotations
import frappe
def execute(filters=None):
    cols=[{"label":"Hold","fieldname":"name","fieldtype":"Link","options":"Credit Hold","width":160},{"label":"Customer","fieldname":"customer","fieldtype":"Link","options":"Customer","width":150},{"label":"Hold Date","fieldname":"hold_date","fieldtype":"Date","width":110},{"label":"Type","fieldname":"hold_type","fieldtype":"Data","width":150},{"label":"Reason","fieldname":"hold_reason","fieldtype":"Data","width":220},{"label":"Active","fieldname":"active","fieldtype":"Check","width":80},{"label":"Released By","fieldname":"released_by","fieldtype":"Link","options":"User","width":150}]
    return cols, frappe.db.sql("""select name,customer,hold_date,hold_type,hold_reason,active,released_by from `tabCredit Hold` order by active desc, hold_date desc""", as_dict=True)
