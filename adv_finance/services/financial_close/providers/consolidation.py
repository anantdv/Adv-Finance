from __future__ import annotations

import frappe

from adv_finance.services.consolidation.close_service import get_consolidation_close_readiness
from adv_finance.services.financial_close.providers.base import CloseReadinessProvider


class ConsolidationProvider(CloseReadinessProvider):
    provider_name = "consolidation"

    def check(self, task, close_period):
        periods = frappe.get_all("Consolidation Period", filters={"end_date": close_period.period_end}, fields=["name"], limit=1)
        if not periods:
            return {"ready": False, "exceptions": [{"type": "Consolidation Period Missing", "message": "No consolidation period found for period end."}], "details": {}}
        readiness = get_consolidation_close_readiness(periods[0].name)
        exceptions = []
        if not readiness["snapshots"]:
            exceptions.append({"type": "Snapshots Missing", "message": "Trial balance snapshots have not been collected."})
        if readiness["open_adjustments"]:
            exceptions.append({"type": "Open Adjustments", "message": f"{readiness['open_adjustments']} consolidation adjustments are not approved."})
        if readiness["blocked_eliminations"]:
            exceptions.append({"type": "Blocked Eliminations", "message": f"{readiness['blocked_eliminations']} intercompany eliminations are blocked."})
        return {"ready": readiness["ready"], "exceptions": exceptions, "details": readiness}
