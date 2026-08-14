from __future__ import annotations

from decimal import Decimal

import frappe

from adv_finance.compatibility.erpnext_v16 import get_cash_account_balance
from adv_finance.services.treasury.currency_service import convert_amount, get_company_currency
from adv_finance.services.treasury.liquidity_service import get_liquidity_threshold, liquidity_status


def get_treasury_accounts(company: str, treasury_group: str | None = None) -> list:
    filters = {"company": company, "active": 1, "include_in_cash_position": 1}
    if treasury_group:
        filters["treasury_group"] = treasury_group
    return frappe.get_all(
        "Treasury Account",
        filters=filters,
        fields=["name", "company", "account", "bank_account", "treasury_account_type", "treasury_group", "account_currency", "restricted_amount", "minimum_balance", "include_in_available_liquidity", "display_order"],
        order_by="display_order asc, account asc",
    )


def get_cash_position(company: str, as_of_date, scenario=None, treasury_group: str | None = None) -> dict:
    company_currency = get_company_currency(company)
    accounts = []
    actual_cash = Decimal("0")
    restricted_cash = Decimal("0")
    available_liquidity = Decimal("0")
    minimum_balances = Decimal("0")
    for account in get_treasury_accounts(company, treasury_group):
        balance = get_cash_account_balance(company, account.account, as_of_date)
        native_amount = Decimal(str(balance.get("balance") or 0))
        currency = account.account_currency or balance.get("currency") or company_currency
        converted, rate = convert_amount(native_amount, currency, company_currency, as_of_date)
        restricted_native = Decimal(str(account.restricted_amount or 0))
        restricted_converted, _ = convert_amount(restricted_native, currency, company_currency, as_of_date)
        minimum_native = Decimal(str(account.minimum_balance or 0))
        minimum_converted, _ = convert_amount(minimum_native, currency, company_currency, as_of_date)
        available = converted - restricted_converted if account.include_in_available_liquidity else Decimal("0")
        accounts.append({
            "treasury_account": account.name,
            "account": account.account,
            "bank_account": account.bank_account,
            "treasury_group": account.treasury_group,
            "treasury_account_type": account.treasury_account_type,
            "currency": currency,
            "native_balance": native_amount,
            "exchange_rate": rate,
            "company_currency_balance": converted,
            "restricted_cash": restricted_converted,
            "available_liquidity": available,
            "minimum_balance": minimum_converted,
        })
        actual_cash += converted
        restricted_cash += restricted_converted
        available_liquidity += available
        minimum_balances += minimum_converted
    threshold = get_liquidity_threshold(company, as_of_date)
    minimum_buffer = max(minimum_balances, Decimal(str(threshold.get("minimum_operating_cash") or 0)))
    status = liquidity_status(available_liquidity, {**threshold, "minimum_operating_cash": minimum_buffer})
    return {
        "company": company,
        "as_of_date": as_of_date,
        "scenario": scenario,
        "accounts": accounts,
        "opening_cash": actual_cash,
        "actual_cash": actual_cash,
        "expected_receipts": Decimal("0"),
        "planned_payments": Decimal("0"),
        "other_inflows": Decimal("0"),
        "other_outflows": Decimal("0"),
        "projected_closing_cash": actual_cash,
        "restricted_cash": restricted_cash,
        "available_liquidity": available_liquidity,
        "minimum_cash_buffer": minimum_buffer,
        "liquidity_headroom": status["liquidity_headroom"],
        "liquidity_status": status["status"],
        "liquidity_shortfall": status["liquidity_shortfall"],
        "currency": company_currency,
    }
