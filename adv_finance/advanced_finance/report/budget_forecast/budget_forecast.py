from __future__ import annotations
import frappe
from adv_finance.services.budgeting.forecast_service import calculate_budget_forecast

def execute(filters=None):
    filters=filters or {}; lines=frappe.get_all("Budget Plan Line", filters={"parenttype":"Budget Plan"}, fields=["account","cost_center","project"], group_by="account,cost_center,project")
    cols=["Account:Link/Account:200","Cost Center:Link/Cost Center:160","Project:Link/Project:160","Original Budget:Currency:130","Effective Budget:Currency:140","Actual YTD:Currency:120","Commitments:Currency:130","Forecast Remaining:Currency:150","Full-Year Forecast:Currency:150","Variance:Currency:120"]
    rows=[]
    for l in lines:
        f=calculate_budget_forecast(filters.get('company'),l.account,l.cost_center,l.project,filters.get('to_date'),filters.get('method') or 'Actual + Open Commitments')
        rows.append([l.account,l.cost_center,l.project,f['effective_budget'],f['effective_budget'],f['actual_ytd'],f['open_commitments'],f['forecast_remaining'],f['full_year_forecast'],f['forecast_variance']])
    return cols,rows
