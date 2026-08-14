from decimal import Decimal
from frappe.model.document import Document
import frappe


class TreasuryForecastItem(Document):
    def validate(self):
        if Decimal(str(self.amount or 0)) <= 0:
            frappe.throw("Forecast item amount must be greater than zero.")
        if self.probability_percent is None:
            self.probability_percent = 100
        if self.probability_percent < 0 or self.probability_percent > 100:
            frappe.throw("Probability must be between 0 and 100.")
