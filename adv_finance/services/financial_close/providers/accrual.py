from __future__ import annotations

import frappe

from adv_finance.services.financial_close.providers.base import CloseReadinessProvider

from adv_finance.services.accrual.close_readiness_service import get_accrual_close_readiness


class AccrualProvider(CloseReadinessProvider):
    provider_name = "accrual"

    def check(self, task, close_period):
        result = get_accrual_close_readiness(close_period.company, close_period.period_end)
        exceptions = []
        for key in ("unapproved", "unposted", "missing_reversals", "material_variances"):
            if result.get(key):
                exceptions.append({"exception_type": key.replace("_", " ").title(), "description": f"{result[key]} accrual issue(s): {key.replace('_', ' ')}.", "risk_level": "High" if key in ("unposted", "missing_reversals") else "Medium"})
        return {"ready": bool(result.get("ready")), "status": "Completed" if result.get("ready") else "Blocked", "message": "Accrual close readiness passed." if result.get("ready") else "Accrual close readiness has open items.", "exceptions": exceptions, "details": result}
