from __future__ import annotations

from decimal import Decimal

from adv_finance.services.budgeting.available_budget_service import get_available_budget


def calculate_budget_forecast(company: str, account: str, cost_center=None, project=None, as_of_date=None, method: str = "Actual + Open Commitments") -> dict:
    budget = get_available_budget(company, account, cost_center, project, as_of_date=as_of_date)
    actual = Decimal(str(budget["actual"] or 0))
    commitments = Decimal(str(budget["commitments"] or 0))
    effective = Decimal(str(budget["effective_budget"] or 0))
    if method == "Actual + Remaining Budget":
        forecast_remaining = max(effective - actual, Decimal("0"))
    elif method == "Run Rate":
        forecast_remaining = actual
    else:
        forecast_remaining = commitments + max(effective - actual - commitments, Decimal("0"))
    full_year = actual + forecast_remaining
    return {"effective_budget": effective, "actual_ytd": actual, "open_commitments": commitments, "forecast_remaining": forecast_remaining, "full_year_forecast": full_year, "forecast_variance": effective - full_year}


def get_budget_cash_projection(company: str, from_date=None, to_date=None) -> list[dict]:
    # Budget is not cash timing. Only periodized, cash-relevant forecast lines should be consumed by Treasury.
    return []
