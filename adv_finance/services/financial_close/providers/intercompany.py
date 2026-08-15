from __future__ import annotations

from adv_finance.services.financial_close.providers.base import CloseReadinessProvider
from adv_finance.services.intercompany.close_service import get_intercompany_close_readiness


class IntercompanyProvider(CloseReadinessProvider):
    provider_name = "intercompany"

    def check(self, task, close_period):
        readiness = get_intercompany_close_readiness(close_period.company, close_period.period_end)
        exceptions = []
        if readiness["open_differences"]:
            exceptions.append({"type": "Open Intercompany Differences", "message": f"{readiness['open_differences']} intercompany differences remain open."})
        if readiness["unmatched_transactions"]:
            exceptions.append({"type": "Unmatched Intercompany Transactions", "message": f"{readiness['unmatched_transactions']} intercompany transactions are unmatched."})
        if readiness["unsettled_transactions"]:
            exceptions.append({"type": "Unsettled Intercompany Transactions", "message": f"{readiness['unsettled_transactions']} intercompany transactions are not settled."})
        return {"ready": readiness["ready"], "exceptions": exceptions, "details": readiness}
