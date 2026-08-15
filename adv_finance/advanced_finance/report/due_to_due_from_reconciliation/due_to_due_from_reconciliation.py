from __future__ import annotations
from adv_finance.services.intercompany.reconciliation_service import reconcile_due_to_due_from

def execute(filters=None):
    f=filters or {}; r=reconcile_due_to_due_from(f.get("origin_company"),f.get("destination_company"),f.get("as_of_date"))
    return ["Origin:Link/Company:160","Destination:Link/Company:160","Due From:Currency:130","Due To:Currency:130","Difference:Currency:130","Status:Data:100"], [[r["origin_company"],r["destination_company"],r["due_from"],r["due_to"],r["difference"],r["status"]]]
