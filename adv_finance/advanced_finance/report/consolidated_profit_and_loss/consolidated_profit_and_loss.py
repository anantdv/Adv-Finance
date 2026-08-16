from __future__ import annotations

from adv_finance.services.consolidation.report_service import profit_loss


def execute(filters=None):
    period = (filters or {}).get("consolidation_period")
    columns = ["Line:Data:240", "Amount:Currency:160"]
    if not period:
        return columns, []
    data = profit_loss(period)
    return columns, [[key, value] for key, value in data.items()]
