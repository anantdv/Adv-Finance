from __future__ import annotations

from adv_finance.services.finance_controls.ageing_remark_service import ap_ageing_with_remarks

def execute(filters=None):
    cols=["Supplier:Link/Supplier:160","Supplier Name:Data:180","Purchase Invoice:Link/Purchase Invoice:180","Posting Date:Date:110","Due Date:Date:110","Currency:Link/Currency:90","Original Amount:Currency:130","Outstanding:Currency:130","Outstanding Company Currency:Currency:170","Age:Int:70","Bucket:Data:110","Remark Type:Data:130","Latest Remark:Data:300","Remark Date:Date:110","Payment Hold:Link/Payment Hold:150","Reconciliation Status:Data:150"]
    rows=ap_ageing_with_remarks(filters or {})
    data=[[r.get("supplier"),r.get("supplier_name"),r.get("name"),r.get("posting_date"),r.get("due_date"),r.get("currency"),r.get("grand_total"),r.get("outstanding_amount"),r.get("outstanding_company_currency"),r.get("age"),r.get("ageing_bucket"),r.get("remark_type"),r.get("remark"),r.get("date"),r.get("payment_hold"),r.get("reconciliation_status")] for r in rows]
    return cols,data
