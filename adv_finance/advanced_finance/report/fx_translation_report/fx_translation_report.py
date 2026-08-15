from __future__ import annotations
import frappe

def execute(filters=None):
    rows=frappe.get_all("Intercompany Transaction",filters={},fields=["name","origin_company","destination_company","transaction_currency","currency","reporting_currency","translation_rate","amount","company_currency_amount","fx_difference"],order_by="posting_date desc")
    return ["Transaction:Link/Intercompany Transaction:180","Origin:Link/Company:150","Destination:Link/Company:150","Txn Currency:Link/Currency:100","Currency:Link/Currency:90","Reporting Currency:Link/Currency:120","Rate:Float:90","Amount:Currency:120","Company Amount:Currency:140","FX Difference:Currency:130"], [[r.name,r.origin_company,r.destination_company,r.transaction_currency,r.currency,r.reporting_currency,r.translation_rate,r.amount,r.company_currency_amount,r.fx_difference] for r in rows]
