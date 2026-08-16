from __future__ import annotations

from decimal import Decimal

from adv_finance.compatibility.erpnext_v16 import get_trial_balance_movement_rows
from adv_finance.services.budgeting.available_budget_service import get_approved_budget


def advanced_trial_balance(filters=None):
    filters = filters or {}
    rows=[]
    for row in get_trial_balance_movement_rows(**filters):
        monthly_net = Decimal(str(row.monthly_debit or 0)) - Decimal(str(row.monthly_credit or 0))
        ytd_net = Decimal(str(row.ytd_debit or 0)) - Decimal(str(row.ytd_credit or 0))
        cumulative_net = Decimal(str(row.cumulative_debit or 0)) - Decimal(str(row.cumulative_credit or 0))
        budget_ytd = get_approved_budget(filters.get("company"), row.account, filters.get("cost_center") or filters.get("branch"), filters.get("project"), filters.get("to_date"))
        budget_mtd = budget_ytd / Decimal("12") if budget_ytd else Decimal("0")
        rows.append({**row.__dict__, "monthly_net_change": monthly_net, "ytd_net_change": ytd_net, "cumulative_net_change": cumulative_net, "budget_mtd": budget_mtd, "budget_ytd": budget_ytd, "budget_variance_ytd": ytd_net - budget_ytd})
    return rows
