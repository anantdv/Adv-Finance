from __future__ import annotations

from adv_finance.services.consolidation.report_service import consolidated_trial_balance


def execute(filters=None):
    period = (filters or {}).get("consolidation_period")
    columns = [
        "Company:Link/Company:160",
        "Account:Link/Account:180",
        "Account Name:Data:220",
        "Root Type:Data:110",
        "Company Total:Currency:140",
        "Translation:Currency:130",
        "Elimination:Currency:130",
        "Adjustment:Currency:130",
        "Minority Interest:Currency:150",
        "Final Amount:Currency:140",
        "Currency:Link/Currency:100",
    ]
    if not period:
        return columns, []
    rows = consolidated_trial_balance(period)
    return columns, [[r.company, r.account, r.account_name, r.root_type, r.company_total, r.translation_amount, r.elimination_amount, r.adjustment_amount, r.minority_interest_amount, r.final_amount, r.currency] for r in rows]
