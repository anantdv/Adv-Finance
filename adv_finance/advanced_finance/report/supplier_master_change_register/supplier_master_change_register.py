from __future__ import annotations

from adv_finance.services.finance_controls.supplier_master_service import supplier_master_change_register

def execute(filters=None):
    cols=["Supplier:Link/Supplier:160","Change Type:Data:160","Previous Value:Data:220","New Value:Data:220","Requested By:Link/User:150","Verified By:Link/User:150","Approved By:Link/User:150","Applied Date:Datetime:160","Status:Data:120"]
    rows=supplier_master_change_register(filters or {})
    return cols,[[r.supplier,r.change_type,r.old_value,r.proposed_value,r.requested_by,r.verified_by,r.approved_by,r.applied_date,r.status] for r in rows]
