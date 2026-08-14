from __future__ import annotations

from adv_finance.services.financial_close.providers.base import CloseReadinessProvider
from adv_finance.services.treasury.close_readiness_service import get_treasury_close_readiness


class TreasuryProvider(CloseReadinessProvider):
    provider_name = "treasury"

    def check(self, task, close_period):
        readiness = get_treasury_close_readiness(close_period.company, close_period.period_end)
        exceptions = []
        if not readiness["treasury_accounts"]:
            exceptions.append({"type": "Treasury Accounts Missing", "message": "No active Treasury Accounts are configured."})
        if not readiness["period_forecasts"]:
            exceptions.append({"type": "Cash Forecast Missing", "message": "No generated/reviewed/approved cash forecast covers period end."})
        if readiness["critical_exceptions"]:
            exceptions.append({"type": "Critical Treasury Exceptions", "message": f"{readiness['critical_exceptions']} critical treasury exceptions remain open."})
        return {"ready": readiness["ready"], "exceptions": exceptions, "details": readiness}
