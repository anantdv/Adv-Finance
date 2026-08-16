from __future__ import annotations

from decimal import Decimal


def apply_ownership(amount, ownership_percent, method: str = "Full Consolidation") -> dict:
    value = Decimal(str(amount or 0))
    ownership = Decimal(str(ownership_percent or 0))
    if method == "Not Consolidated":
        owned = Decimal("0")
    elif method == "Equity Method":
        owned = value * ownership / Decimal("100")
    elif method == "Proportionate":
        owned = value * ownership / Decimal("100")
    else:
        owned = value
    minority = value - (value * ownership / Decimal("100")) if method == "Full Consolidation" and ownership < 100 else Decimal("0")
    return {"owned_amount": owned, "minority_interest_amount": minority, "ownership_percent": ownership}
