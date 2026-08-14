from decimal import Decimal
from frappe.model.document import Document
import frappe


class BudgetCommitment(Document):
    def validate(self):
        if Decimal(str(self.remaining_amount or 0)) < 0:
            frappe.throw("Remaining amount cannot be negative.")
