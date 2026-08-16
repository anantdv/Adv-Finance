from __future__ import annotations

from adv_finance.services.consolidation.report_service import balance_sheet


def execute(filters=None):
    period = (filters or {}).get("consolidation_period")
    columns = ["Line:Data:240", "Amount:Currency:160"]
    if not period:
        return columns, []
    data = balance_sheet(period)
    return columns, [[key, value] for key, value in data.items()]
