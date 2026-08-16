from __future__ import annotations

from adv_finance.services.consolidation.report_service import dashboard


def execute(filters=None):
    period = (filters or {}).get("consolidation_period")
    columns = ["Metric:Data:240", "Value:Data:160"]
    if not period:
        return columns, []
    data = dashboard(period)
    return columns, [[key.replace("_", " ").title(), value] for key, value in data.items()]
