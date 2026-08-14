from __future__ import annotations

from decimal import Decimal

from adv_finance.compatibility.erpnext_v16 import get_budget_actual_gl_amount


def get_actual_spend(company: str, account: str, from_date=None, to_date=None, cost_center=None, project=None, dimensions=None) -> Decimal:
    return Decimal(str(get_budget_actual_gl_amount(company, account, from_date, to_date, cost_center, project, dimensions) or 0))
