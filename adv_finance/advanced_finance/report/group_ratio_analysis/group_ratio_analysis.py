from __future__ import annotations

from adv_finance.services.consolidation.ratio_service import group_ratios


def execute(filters=None):
    period = (filters or {}).get("consolidation_period")
    columns = ["Ratio:Data:240", "Value:Float:140"]
    if not period:
        return columns, []
    data = group_ratios(period)
    return columns, [[key.replace("_", " ").title(), value] for key, value in data.items()]
