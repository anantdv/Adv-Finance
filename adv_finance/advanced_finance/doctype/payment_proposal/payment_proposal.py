from decimal import Decimal

import frappe
from frappe.model.document import Document

from adv_finance.services.accounts_payable.payment_proposal_service import recalculate_payment_proposal
from adv_finance.services.accounts_payable.payment_validation_service import validate_selected_amount


class PaymentProposal(Document):
    def before_insert(self):
        if not self.status:
            self.status = "Draft"

    def validate(self):
        if self.due_date_from and self.due_date_to and self.due_date_from > self.due_date_to:
            frappe.throw("Due Date From cannot be after Due Date To.")
        for item in self.items:
            validate_selected_amount(item.selected_amount, item.outstanding_amount)
            if item.selected and Decimal(str(item.selected_amount or 0)) == 0:
                frappe.throw(f"Selected amount is required for {item.purchase_invoice}.")
        recalculate_payment_proposal(self)
