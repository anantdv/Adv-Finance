from frappe.model.document import Document
import frappe


class TreasuryLiquidityThreshold(Document):
    def validate(self):
        if self.warning_threshold and self.critical_threshold and self.critical_threshold > self.warning_threshold:
            frappe.throw("Critical threshold should not be greater than warning threshold.")
