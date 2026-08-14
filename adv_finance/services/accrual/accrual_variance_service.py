from __future__ import annotations

from decimal import Decimal


def classify_variance(variance: Decimal, tolerance_amount: Decimal = Decimal("0"), tolerance_percentage=None, base_amount=None) -> str:
    variance = Decimal(str(variance or 0))
    tolerance = Decimal(str(tolerance_amount or 0))
    if tolerance_percentage and base_amount:
        tolerance = max(tolerance, abs(Decimal(str(base_amount)) * Decimal(str(tolerance_percentage)) / Decimal("100")))
    if abs(variance) <= tolerance:
        return "Within Tolerance"
    if variance > 0:
        return "Under Accrued"
    if variance < 0:
        return "Over Accrued"
    return "Exact"


def variance_percentage(variance, base_amount) -> Decimal:
    base = Decimal(str(base_amount or 0))
    if not base:
        return Decimal("0")
    return (Decimal(str(variance or 0)) / base) * Decimal("100")
