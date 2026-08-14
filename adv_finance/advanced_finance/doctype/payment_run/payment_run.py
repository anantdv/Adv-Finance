import frappe
from frappe.model.document import Document

from adv_finance.services.accounts_payable.payment_run_service import recalculate_payment_run


class PaymentRun(Document):
    def before_insert(self):
        if not self.status:
            self.status = "Draft"

    def validate(self):
        if not self.payment_proposal:
            frappe.throw("Payment Proposal is required.")
        recalculate_payment_run(self)
