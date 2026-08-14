import frappe
from frappe.model.document import Document


class AccountReconciliationPeriod(Document):
    def validate(self):
        if self.period_start and self.period_end and self.period_start > self.period_end:
            frappe.throw("Period Start cannot be after Period End.")
