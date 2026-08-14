from __future__ import annotations
import frappe
from adv_finance.services.budgeting.available_budget_service import get_available_budget
from adv_finance.services.budgeting.forecast_service import calculate_budget_forecast


def execute(filters=None):
    filters = filters or {}
    lines = frappe.get_all("Budget Plan Line", filters={"parenttype": "Budget Plan"}, fields=["account", "cost_center", "project"], group_by="account, cost_center, project")
    columns = ["Account:Link/Account:200", "Cost Center:Link/Cost Center:160", "Project:Link/Project:160", "Budget:Currency:120", "Effective Budget:Currency:140", "Actual:Currency:120", "Commitments:Currency:130", "Pre-Commitments:Currency:140", "Reservations:Currency:130", "Available:Currency:120", "Forecast:Currency:120", "Forecast Variance:Currency:150", "Consumption %:Percent:120"]
    rows=[]
    for line in lines:
        b=get_available_budget(filters.get('company'), line.account, line.cost_center, line.project, as_of_date=filters.get('to_date'), from_date=filters.get('from_date'))
        f=calculate_budget_forecast(filters.get('company'), line.account, line.cost_center, line.project, filters.get('to_date'))
        rows.append([line.account,line.cost_center,line.project,b['approved_budget'],b['effective_budget'],b['actual'],b['commitments'],b['pre_commitments'],b['reservations'],b['available_budget'],f['full_year_forecast'],f['forecast_variance'],b['consumption_percent']])
    return columns, rows
