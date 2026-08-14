from frappe.model.document import Document
import frappe


class CashForecastScenario(Document):
    def validate(self):
        for field in ("receipt_probability_multiplier", "payment_probability_multiplier"):
            value = self.get(field) or 0
            if value < 0:
                frappe.throw(f"{field.replace('_', ' ').title()} cannot be negative.")
