from decimal import Decimal
from frappe.model.document import Document
import frappe


class ManualBudgetCommitment(Document):
    def validate(self):
        if Decimal(str(self.amount or 0)) <= 0:
            frappe.throw("Manual commitment amount must be greater than zero.")
