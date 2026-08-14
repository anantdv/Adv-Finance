from __future__ import annotations

from adv_finance.services.treasury.forecast_accuracy_service import get_forecast_accuracy


def execute(filters=None):
    filters = filters or {}
    data = get_forecast_accuracy(filters.get("forecast"))
    columns = ["Metric:Data:220", "Amount:Currency:160"]
    rows = [[k.replace('_', ' ').title(), v] for k, v in data.items()]
    return columns, rows
