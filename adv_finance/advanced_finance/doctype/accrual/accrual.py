from decimal import Decimal

import frappe
from frappe.model.document import Document

from adv_finance.services.accrual.accrual_service import recalculate_accrual


class Accrual(Document):
    def before_insert(self):
        if not self.workflow_status:
            self.workflow_status = "Draft"
        if not self.posting_status:
            self.posting_status = "Not Posted"
        if not self.reversal_status:
            self.reversal_status = "Pending" if self.reversal_required else "Not Required"
        if not self.matching_status:
            self.matching_status = "Unmatched"
        if not self.status:
            self.status = "Draft"

    def validate(self):
        if Decimal(str(self.accrual_amount or 0)) <= 0:
            frappe.throw("Accrual amount must be greater than zero.")
        self._validate_accounts()
        if self.reversal_required and not self.reversal_date:
            frappe.throw("Reversal date is required when reversal is required.")
        if self.reversal_required and self.reversal_method == "No Reversal":
            frappe.throw("Choose a reversal method when reversal is required.")
        recalculate_accrual(self)

    def _validate_accounts(self):
        for fieldname in ("expense_account", "accrual_liability_account"):
            account = self.get(fieldname)
            if not account:
                frappe.throw(f"{self.meta.get_label(fieldname)} is required.")
            company = frappe.db.get_value("Account", account, "company")
            if company and self.company and company != self.company:
                frappe.throw(f"{account} does not belong to {self.company}.")
