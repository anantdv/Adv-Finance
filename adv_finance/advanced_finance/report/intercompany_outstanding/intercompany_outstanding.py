from __future__ import annotations
import frappe

def execute(filters=None):
    filters=filters or {}; q={"settlement_status":["not in",["Settled"]]}
    if filters.get("company"): q["origin_company"]=filters.get("company")
    rows=frappe.get_all("Intercompany Transaction",filters=q,fields=["name","origin_company","destination_company","source_doctype","source_document","amount","currency","matching_status","settlement_status"],order_by="posting_date desc")
    return ["Transaction:Link/Intercompany Transaction:180","Origin:Link/Company:160","Destination:Link/Company:160","Source Type:Data:140","Source:Dynamic Link/source_doctype:180","Amount:Currency:120","Currency:Link/Currency:80","Match:Data:110","Settlement:Data:130"], [[r.name,r.origin_company,r.destination_company,r.source_doctype,r.source_document,r.amount,r.currency,r.matching_status,r.settlement_status] for r in rows]
