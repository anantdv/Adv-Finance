from __future__ import annotations

from adv_finance.services.account_reconciliation.providers.accounts_payable import AccountsPayableProvider
from adv_finance.services.account_reconciliation.providers.accounts_receivable import AccountsReceivableProvider
from adv_finance.services.account_reconciliation.providers.base import ReconciliationProvider
from adv_finance.services.account_reconciliation.providers.manual import ManualSupportingBalanceProvider
from adv_finance.services.account_reconciliation.providers.uploaded_schedule import UploadedScheduleProvider


PROVIDERS = {
    "Manual Supporting Balance": ManualSupportingBalanceProvider,
    "Uploaded Schedule": UploadedScheduleProvider,
    "ERP Subledger": ReconciliationProvider,
    "ERP Report": ReconciliationProvider,
    "Calculated Supporting Balance": ReconciliationProvider,
    "Custom Reconciliation Provider": ReconciliationProvider,
    "Accounts Payable": AccountsPayableProvider,
    "Accounts Receivable": AccountsReceivableProvider,
}


def get_provider(reconciliation):
    provider_name = reconciliation.reconciliation_provider
    if not provider_name:
        account_type = getattr(reconciliation, "account_type", None)
        if account_type == "Payable":
            provider_name = "Accounts Payable"
        elif account_type == "Receivable":
            provider_name = "Accounts Receivable"
        else:
            provider_name = reconciliation.reconciliation_method or "Manual Supporting Balance"
    return PROVIDERS.get(provider_name, ReconciliationProvider)()
