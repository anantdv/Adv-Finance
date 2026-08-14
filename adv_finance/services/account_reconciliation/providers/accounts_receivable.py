from __future__ import annotations

from adv_finance.compatibility.erpnext_v16 import get_party_subledger_balance, get_party_subledger_items
from adv_finance.services.account_reconciliation.providers.base import ReconciliationProvider


class AccountsReceivableProvider(ReconciliationProvider):
    provider_name = "Accounts Receivable"

    def get_supporting_balance(self, reconciliation):
        return get_party_subledger_balance(
            reconciliation.company, reconciliation.account, "Customer", reconciliation.period_end
        )

    def get_supporting_items(self, reconciliation):
        return [
            {
                "item_type": "Supporting Item",
                "reference": row.voucher_no,
                "description": f"{row.party} - {row.voucher_type}",
                "transaction_date": row.posting_date,
                "debit": row.debit,
                "credit": row.credit,
                "amount": row.amount,
                "source_doctype": row.voucher_type,
                "source_document": row.voucher_no,
                "status": "Confirmed",
            }
            for row in get_party_subledger_items(
                reconciliation.company, reconciliation.account, "Customer", reconciliation.period_end
            )
        ]
