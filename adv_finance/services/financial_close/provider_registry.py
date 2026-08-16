from __future__ import annotations

from adv_finance.services.financial_close.providers.account_reconciliation import AccountReconciliationProvider
from adv_finance.services.financial_close.providers.accounts_receivable import AccountsReceivableProvider
from adv_finance.services.financial_close.providers.accrual import AccrualProvider
from adv_finance.services.financial_close.providers.bank_reconciliation import BankReconciliationProvider
from adv_finance.services.financial_close.providers.base import CloseReadinessProvider
from adv_finance.services.financial_close.providers.budgeting import BudgetingProvider
from adv_finance.services.financial_close.providers.consolidation import ConsolidationProvider
from adv_finance.services.financial_close.providers.erpnext_document import ERPNextDocumentProvider
from adv_finance.services.financial_close.providers.fixed_assets import FixedAssetsProvider
from adv_finance.services.financial_close.providers.fx_revaluation import FXRevaluationProvider
from adv_finance.services.financial_close.providers.inventory import InventoryProvider
from adv_finance.services.financial_close.providers.intercompany import IntercompanyProvider
from adv_finance.services.financial_close.providers.payroll import PayrollProvider
from adv_finance.services.financial_close.providers.period_close import PeriodCloseProvider
from adv_finance.services.financial_close.providers.supplier_reconciliation import SupplierReconciliationProvider
from adv_finance.services.financial_close.providers.treasury import TreasuryProvider

PROVIDERS = {
    "manual": CloseReadinessProvider,
    "supplier_reconciliation": SupplierReconciliationProvider,
    "account_reconciliation": AccountReconciliationProvider,
    "accounts_receivable": AccountsReceivableProvider,
    "accrual": AccrualProvider,
    "bank_reconciliation": BankReconciliationProvider,
    "budgeting": BudgetingProvider,
    "fixed_assets": FixedAssetsProvider,
    "inventory": InventoryProvider,
    "intercompany": IntercompanyProvider,
    "payroll": PayrollProvider,
    "fx_revaluation": FXRevaluationProvider,
    "period_close": PeriodCloseProvider,
    "erpnext_document": ERPNextDocumentProvider,
    "treasury": TreasuryProvider,
    "consolidation": ConsolidationProvider,
}


def get_provider(provider_name: str | None):
    return PROVIDERS.get((provider_name or "manual").strip().lower(), CloseReadinessProvider)()
