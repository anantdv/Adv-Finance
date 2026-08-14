from __future__ import annotations

from decimal import Decimal


class ReconciliationProvider:
    provider_name = "Base"

    def validate(self, reconciliation) -> None:
        return None

    def get_supporting_balance(self, reconciliation) -> Decimal:
        return Decimal(str(reconciliation.supporting_balance or 0))

    def get_supporting_items(self, reconciliation) -> list[dict]:
        return []
