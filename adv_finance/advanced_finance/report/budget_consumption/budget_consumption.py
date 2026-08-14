from __future__ import annotations
import frappe
from adv_finance.services.budgeting.available_budget_service import get_available_budget

def execute(filters=None):
    filters=filters or {}; rows=[]
    lines=frappe.get_all("Budget Plan Line", filters={"parenttype":"Budget Plan"}, fields=["account","cost_center","project"], group_by="account,cost_center,project")
    cols=["Account:Link/Account:200","Cost Center:Link/Cost Center:160","Project:Link/Project:160","Budget:Currency:120","Supplement:Currency:120","Transfers In:Currency:120","Transfers Out:Currency:120","Effective Budget:Currency:140","Actual:Currency:120","Commitment:Currency:120","Reservation:Currency:120","Available:Currency:120","Consumption %:Percent:120"]
    for l in lines:
        b=get_available_budget(filters.get('company'),l.account,l.cost_center,l.project,as_of_date=filters.get('to_date'),from_date=filters.get('from_date'))
        rows.append([l.account,l.cost_center,l.project,b['approved_budget'],b['supplements'],b['transfers_in'],b['transfers_out'],b['effective_budget'],b['actual'],b['commitments'],b['reservations'],b['available_budget'],b['consumption_percent']])
    return cols,rows
