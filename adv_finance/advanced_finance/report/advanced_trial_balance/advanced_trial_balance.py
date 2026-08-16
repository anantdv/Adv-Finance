from __future__ import annotations

from adv_finance.services.finance_controls.advanced_trial_balance_service import advanced_trial_balance

def execute(filters=None):
    cols=["Account:Link/Account:180","Account Name:Data:220","Opening Balance:Currency:130","Monthly Debit:Currency:120","Monthly Credit:Currency:120","Monthly Net Change:Currency:150","YTD Debit:Currency:120","YTD Credit:Currency:120","YTD Net Change:Currency:140","Cumulative Debit:Currency:140","Cumulative Credit:Currency:140","Cumulative Net Change:Currency:160","Closing Balance:Currency:130","Budget MTD:Currency:120","Budget YTD:Currency:120","Budget Variance YTD:Currency:160"]
    rows=advanced_trial_balance(filters or {})
    return cols,[[r.get("account"),r.get("account_name"),r.get("opening_balance"),r.get("monthly_debit"),r.get("monthly_credit"),r.get("monthly_net_change"),r.get("ytd_debit"),r.get("ytd_credit"),r.get("ytd_net_change"),r.get("cumulative_debit"),r.get("cumulative_credit"),r.get("cumulative_net_change"),r.get("closing_balance"),r.get("budget_mtd"),r.get("budget_ytd"),r.get("budget_variance_ytd")] for r in rows]
