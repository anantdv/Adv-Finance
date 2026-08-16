from __future__ import annotations

from adv_finance.services.finance_controls.prior_period_service import prior_period_posting_register

def execute(filters=None):
    cols=["Request:Link/Prior Period Posting Request:190","Company:Link/Company:160","User:Link/User:150","Posting Date:Date:120","Transaction Type:Data:160","Transaction:Data:180","Reason:Data:220","Approved By:Link/User:150","Approved On:Datetime:160","Used:Data:120","Used On:Datetime:160","Status:Data:120"]
    rows=prior_period_posting_register(filters or {})
    return cols,[[r.name,r.company,r.requested_by,r.posting_date,r.transaction_doctype,r.transaction_name,r.reason,r.approved_by,r.approved_on,r.usage_document,r.used_on,r.status] for r in rows]
