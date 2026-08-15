from __future__ import annotations

from decimal import Decimal

from adv_finance.services.treasury.currency_service import convert_amount


def translate_amount(amount, from_currency: str | None, to_currency: str | None, date=None) -> dict:
    translated, rate = convert_amount(amount, from_currency, to_currency, date)
    return {"native_amount": Decimal(str(amount or 0)), "translated_amount": translated, "translation_rate": rate, "fx_difference": translated - Decimal(str(amount or 0)) if from_currency != to_currency else Decimal("0")}


def calculate_fx_difference(origin_amount, destination_amount, origin_currency, destination_currency, reporting_currency, date=None) -> dict:
    origin = translate_amount(origin_amount, origin_currency, reporting_currency, date)
    destination = translate_amount(destination_amount, destination_currency, reporting_currency, date)
    return {"origin_reporting_amount": origin["translated_amount"], "destination_reporting_amount": destination["translated_amount"], "fx_difference": origin["translated_amount"] - destination["translated_amount"], "origin_rate": origin["translation_rate"], "destination_rate": destination["translation_rate"]}
