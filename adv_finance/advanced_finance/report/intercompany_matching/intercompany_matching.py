from __future__ import annotations
import frappe

def execute(filters=None):
    rows=frappe.get_all("Intercompany Match",filters={},fields=["name","match_type","origin_company","destination_company","origin_total","destination_total","difference_amount","status"],order_by="modified desc")
    return ["Match:Link/Intercompany Match:180","Type:Data:110","Origin:Link/Company:160","Destination:Link/Company:160","Origin Total:Currency:130","Destination Total:Currency:150","Difference:Currency:120","Status:Data:100"], [[r.name,r.match_type,r.origin_company,r.destination_company,r.origin_total,r.destination_total,r.difference_amount,r.status] for r in rows]
