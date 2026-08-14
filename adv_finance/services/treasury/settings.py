from __future__ import annotations

from decimal import Decimal

DEFAULT_RECEIPT_PROBABILITIES = {
    "promise_active": Decimal("95"),
    "promise_broken": Decimal("15"),
    "current_invoice": Decimal("95"),
    "1-30": Decimal("85"),
    "31-60": Decimal("65"),
    "61-90": Decimal("45"),
    "90+": Decimal("25"),
}

DEFAULT_PAYMENT_PROBABILITIES = {
    "payment_run": Decimal("100"),
    "payment_proposal": Decimal("90"),
    "purchase_invoice_due": Decimal("75"),
    "purchase_invoice_future": Decimal("60"),
    "manual": Decimal("100"),
}

DEFAULT_FORECAST_WEEKS = 13


def get_receipt_probability(bucket: str, promised: bool = False, broken: bool = False) -> Decimal:
    if promised and broken:
        return DEFAULT_RECEIPT_PROBABILITIES["promise_broken"]
    if promised:
        return DEFAULT_RECEIPT_PROBABILITIES["promise_active"]
    return DEFAULT_RECEIPT_PROBABILITIES.get(bucket, DEFAULT_RECEIPT_PROBABILITIES["90+"])


def get_payment_probability(source: str, future_due: bool = False) -> Decimal:
    if source in DEFAULT_PAYMENT_PROBABILITIES:
        return DEFAULT_PAYMENT_PROBABILITIES[source]
    return DEFAULT_PAYMENT_PROBABILITIES["purchase_invoice_future" if future_due else "purchase_invoice_due"]
