from __future__ import annotations

from decimal import Decimal

from adv_finance.services.treasury.currency_service import convert_amount

RATE_RULES = {"Asset": "Closing Rate", "Liability": "Closing Rate", "Income": "Average Rate", "Expense": "Average Rate", "Equity": "Historical Rate"}


def get_translation_rate_type(root_type: str | None) -> str:
    return RATE_RULES.get(root_type or "Asset", "Closing Rate")


def translate_trial_balance_row(row, reporting_currency: str, period_end=None) -> dict:
    amount = Decimal(str(row.balance or 0))
    translated, rate = convert_amount(amount, row.currency, reporting_currency, period_end)
    return {"exchange_rate": rate, "translated_amount": translated, "translation_difference": translated - amount if row.currency != reporting_currency else Decimal("0"), "rate_type": get_translation_rate_type(getattr(row, "root_type", None))}
