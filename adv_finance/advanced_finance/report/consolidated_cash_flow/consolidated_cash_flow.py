from __future__ import annotations

from adv_finance.services.consolidation.report_service import cash_flow


def execute(filters=None):
    period = (filters or {}).get("consolidation_period")
    columns = ["Line:Data:240", "Amount:Currency:160"]
    if not period:
        return columns, []
    data = cash_flow(period)
    return columns, [[key, value] for key, value in data.items()]
