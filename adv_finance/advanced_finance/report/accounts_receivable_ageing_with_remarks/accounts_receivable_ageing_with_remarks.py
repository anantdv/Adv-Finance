from __future__ import annotations

from adv_finance.services.finance_controls.ageing_remark_service import ar_ageing_with_remarks

def execute(filters=None):
    cols=["Customer:Link/Customer:160","Customer Name:Data:180","Sales Invoice:Link/Sales Invoice:180","Posting Date:Date:110","Due Date:Date:110","Currency:Link/Currency:90","Original Amount:Currency:130","Outstanding:Currency:130","Outstanding Company Currency:Currency:170","Age:Int:70","Ageing Bucket:Data:110","Remark Type:Data:130","Latest Remark:Data:300","Remark Date:Date:110","Collector:Link/User:150","Dispute Status:Data:130","Promise Status:Data:130"]
    rows=ar_ageing_with_remarks(filters or {})
    data=[[r.get("customer"),r.get("customer_name"),r.get("name"),r.get("posting_date"),r.get("due_date"),r.get("currency"),r.get("grand_total"),r.get("outstanding_amount"),r.get("outstanding_company_currency"),r.get("age"),r.get("ageing_bucket"),r.get("remark_type"),r.get("remark"),r.get("date"),r.get("collector"),r.get("dispute_status"),r.get("promise_status")] for r in rows]
    return cols,data
