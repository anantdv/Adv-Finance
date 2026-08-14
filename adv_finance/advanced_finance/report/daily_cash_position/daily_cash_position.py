from __future__ import annotations

from adv_finance.services.treasury.cash_position_service import get_cash_position


def execute(filters=None):
    filters = filters or {}
    data = get_cash_position(filters.get("company"), filters.get("date"), treasury_group=filters.get("treasury_group"))
    columns = ["Account:Link/Account:220", "Bank:Link/Bank Account:180", "Currency:Link/Currency:90", "Native Balance:Currency:140", "Exchange Rate:Float:110", "Company Currency Balance:Currency:170", "Restricted:Currency:130", "Available:Currency:130", "Minimum Balance:Currency:140", "Headroom:Currency:130"]
    rows = [[a["account"], a["bank_account"], a["currency"], a["native_balance"], a["exchange_rate"], a["company_currency_balance"], a["restricted_cash"], a["available_liquidity"], a["minimum_balance"], a["available_liquidity"] - a["minimum_balance"]] for a in data["accounts"]]
    return columns, rows
