from __future__ import annotations
import frappe
from frappe.utils import date_diff, getdate

def bucket(days): return "180+" if days>=180 else "90+" if days>=90 else "60+" if days>=60 else "30+" if days>=30 else "Current"
def execute(filters=None):
    f=filters or {}; asof=f.get("as_of_date")
    rows=frappe.get_all("Intercompany Transaction",filters={"settlement_status":["not in",["Settled"]]},fields=["name","origin_company","destination_company","due_date","amount","currency"],order_by="due_date asc")
    data=[]
    for r in rows:
        days=max(date_diff(getdate(asof),getdate(r.due_date or asof)),0)
        data.append([r.name,r.origin_company,r.destination_company,r.due_date,r.amount,r.currency,days,bucket(days)])
    return ["Transaction:Link/Intercompany Transaction:180","Origin:Link/Company:150","Destination:Link/Company:150","Due Date:Date:100","Amount:Currency:120","Currency:Link/Currency:80","Age Days:Int:90","Bucket:Data:90"], data
