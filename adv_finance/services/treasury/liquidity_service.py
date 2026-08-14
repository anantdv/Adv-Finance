from __future__ import annotations

from decimal import Decimal

import frappe


def get_liquidity_threshold(company: str, as_of_date=None) -> dict:
    row = frappe.db.get_value(
        "Treasury Liquidity Threshold",
        {"company": company, "active": 1, "effective_from": ["<=", as_of_date]},
        ["minimum_operating_cash", "warning_threshold", "critical_threshold", "currency"],
        as_dict=True,
        order_by="effective_from desc",
    )
    if not row:
        return {"minimum_operating_cash": Decimal("0"), "warning_threshold": Decimal("0"), "critical_threshold": Decimal("0"), "currency": None}
    return {
        "minimum_operating_cash": Decimal(str(row.minimum_operating_cash or 0)),
        "warning_threshold": Decimal(str(row.warning_threshold or 0)),
        "critical_threshold": Decimal(str(row.critical_threshold or 0)),
        "currency": row.currency,
    }


def liquidity_status(available_liquidity, threshold: dict) -> dict:
    available = Decimal(str(available_liquidity or 0))
    minimum = Decimal(str(threshold.get("minimum_operating_cash") or 0))
    warning = Decimal(str(threshold.get("warning_threshold") or 0))
    critical = Decimal(str(threshold.get("critical_threshold") or 0))
    headroom = available - minimum
    status = "Healthy"
    if headroom < 0:
        status = "Shortfall"
    elif critical and available <= critical:
        status = "Critical"
    elif warning and available <= warning:
        status = "Warning"
    return {"status": status, "minimum_cash_buffer": minimum, "liquidity_headroom": headroom, "liquidity_shortfall": abs(headroom) if headroom < 0 else Decimal("0")}
