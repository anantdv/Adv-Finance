from __future__ import annotations
import frappe

def execute(filters=None):
    filters=filters or {}; q={}
    if filters.get('company'): q['company']=filters.get('company')
    rows=frappe.get_all("Budget Override Request", filters=q, fields=["name","company","status","modified"], order_by="modified desc")
    return ["Document:Link/Budget Override Request:190","Company:Link/Company:180","Status:Data:120","Modified:Datetime:160"], [[r.name,r.company,r.status,r.modified] for r in rows]
