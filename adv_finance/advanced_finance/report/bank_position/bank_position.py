from __future__ import annotations

from adv_finance.services.treasury.cash_position_service import get_cash_position


def execute(filters=None):
    filters = filters or {}
    data = get_cash_position(filters.get("company"), filters.get("date"))
    columns = ["Bank:Link/Bank Account:180", "Account:Link/Account:220", "Currency:Link/Currency:90", "Current Balance:Currency:150", "Available Balance:Currency:150", "Restricted:Currency:120", "Pending Receipts:Currency:140", "Planned Payments:Currency:140", "Projected End-of-Day:Currency:160"]
    rows = [[a["bank_account"], a["account"], a["currency"], a["company_currency_balance"], a["available_liquidity"], a["restricted_cash"], 0, 0, a["available_liquidity"]] for a in data["accounts"]]
    return columns, rows
