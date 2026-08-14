from __future__ import annotations

from adv_finance.services.accounts_receivable.close_readiness_service import get_ar_close_readiness
from adv_finance.services.financial_close.providers.base import CloseReadinessProvider


class AccountsReceivableProvider(CloseReadinessProvider):
    provider_name = "accounts_receivable"

    def check(self, task, close_period):
        result = get_ar_close_readiness(close_period.company, close_period.period_end)
        exceptions = []
        if result.get("open_high_disputes"):
            exceptions.append({"exception_type": "Open High-Risk AR Dispute", "description": f"{result['open_high_disputes']} high-risk AR dispute(s) remain open.", "risk_level": "High"})
        return {"ready": result.get("ready"), "status": "Completed" if result.get("ready") else "Blocked", "message": "AR close readiness passed." if result.get("ready") else "AR close readiness has open items.", "exceptions": exceptions, "details": result}
