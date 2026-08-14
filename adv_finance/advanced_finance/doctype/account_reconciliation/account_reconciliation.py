import frappe
from frappe.model.document import Document

from adv_finance.services.account_reconciliation.reconciliation_service import recalculate


class AccountReconciliation(Document):
    def before_insert(self):
        if not self.status:
            self.status = "Draft"

    def validate(self):
        if self.period_start and self.period_end and self.period_start > self.period_end:
            frappe.throw("Period Start cannot be after Period End.")
        account = frappe.db.get_value("Account", self.account, ["company", "account_currency", "account_type"], as_dict=True)
        if account:
            if self.company and account.company != self.company:
                frappe.throw("Account must belong to the selected company.")
            self.account_currency = self.account_currency or account.account_currency
            self.account_type = account.account_type
        if self.reconciliation_template:
            template = frappe.get_doc("Account Reconciliation Template", self.reconciliation_template)
            self.tolerance_amount = self.tolerance_amount or template.tolerance_amount
            self.tolerance_percentage = self.tolerance_percentage or template.tolerance_percentage
            self.require_zero_difference = template.require_zero_difference
            self.allow_explained_difference = template.allow_explained_difference
            self.supporting_document_required = template.supporting_document_required
            self.certification_required = template.certification_required
            self.enforce_segregation_of_duties = template.enforce_segregation_of_duties
            self.risk_level = self.risk_level or template.risk_level
            self.reconciliation_method = self.reconciliation_method or template.reconciliation_method
            self.reconciliation_provider = self.reconciliation_provider or template.reconciliation_provider
        recalculate(self)
