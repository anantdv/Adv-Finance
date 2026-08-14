from __future__ import annotations

from adv_finance.services.budgeting.close_readiness_service import get_budget_close_readiness
from adv_finance.services.financial_close.providers.base import CloseReadinessProvider


class BudgetingProvider(CloseReadinessProvider):
    provider_name = "budgeting"

    def check(self, task, close_period):
        readiness = get_budget_close_readiness(close_period.company, close_period.period_end)
        exceptions = []
        if not readiness["approved_budget_plans"]:
            exceptions.append({"type": "Approved Budget Missing", "message": "No approved budget plan covers period end."})
        if readiness["pending_overrides"]:
            exceptions.append({"type": "Pending Budget Overrides", "message": f"{readiness['pending_overrides']} budget overrides are pending."})
        if readiness["stale_commitments"]:
            exceptions.append({"type": "Stale Commitments", "message": f"{readiness['stale_commitments']} commitments are past expected date."})
        return {"ready": readiness["ready"], "exceptions": exceptions, "details": readiness}
