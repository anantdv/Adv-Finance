from decimal import Decimal

import frappe
from frappe.model.document import Document


class SupplierReconciliationMatch(Document):
    def validate(self):
        statement_total = Decimal(str(self.statement_total or 0))
        erp_total = Decimal(str(self.erp_total or 0))
        self.difference = statement_total - erp_total

        if self.status in ("Accepted", "Manual Match", "Auto Accepted") and self.difference:
            frappe.throw("Accepted grouped matches must balance before they can be saved.")
