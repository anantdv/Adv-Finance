from __future__ import annotations
from adv_finance.services.budgeting.commitment_service import get_open_commitments

def execute(filters=None):
    filters=filters or {}; rows=get_open_commitments(filters.get('company'), filters.get('account'), filters.get('cost_center'), filters.get('project'), filters.get('to_date'))
    cols=["Source:Data:140","Document:Dynamic Link/source_doctype:180","Supplier:Link/Supplier:160","Account:Link/Account:180","Cost Center:Link/Cost Center:150","Project:Link/Project:150","Original Commitment:Currency:160","Consumed:Currency:120","Remaining:Currency:120","Expected Date:Date:110","Status:Data:100"]
    return cols, [[r.get('source_doctype'),r.get('source_document'),r.get('supplier'),r.get('account'),r.get('cost_center'),r.get('project'),r.get('original_amount'),r.get('consumed_amount'),r.get('remaining_amount'),r.get('expected_date'),r.get('status')] for r in rows]
