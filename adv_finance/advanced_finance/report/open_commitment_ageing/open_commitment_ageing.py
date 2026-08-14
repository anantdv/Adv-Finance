from __future__ import annotations
from frappe.utils import date_diff, getdate
from adv_finance.services.budgeting.commitment_service import get_open_commitments

def bucket(days):
    return '180+' if days>=180 else '90+' if days>=90 else '60+' if days>=60 else '30+' if days>=30 else 'Current'

def execute(filters=None):
    filters=filters or {}; asof=filters.get('to_date')
    rows=[]
    for r in get_open_commitments(filters.get('company'), filters.get('account'), filters.get('cost_center'), filters.get('project'), asof):
        days=max(date_diff(getdate(asof), getdate(r.get('expected_date') or asof)),0)
        rows.append([r.get('source_doctype'),r.get('source_document'),r.get('account'),r.get('remaining_amount'),r.get('expected_date'),days,bucket(days)])
    return ["Source:Data:140","Document:Data:180","Account:Link/Account:180","Remaining:Currency:120","Expected Date:Date:110","Age Days:Int:90","Bucket:Data:90"], rows
