from frappe.model.document import Document
import frappe


class ConsolidationPeriod(Document):
    def validate(self):
        if self.start_date and self.end_date and self.start_date > self.end_date:
            frappe.throw("Start Date cannot be after End Date.")
