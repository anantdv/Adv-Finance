from __future__ import annotations

from decimal import Decimal

from adv_finance.services.account_reconciliation.providers.base import ReconciliationProvider


class ManualSupportingBalanceProvider(ReconciliationProvider):
    provider_name = "Manual Supporting Balance"

    def get_supporting_balance(self, reconciliation) -> Decimal:
        return Decimal(str(reconciliation.supporting_balance or 0))
