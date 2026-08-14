from frappe.model.document import Document
import frappe


class CashForecast(Document):
    def validate(self):
        if self.forecast_from and self.forecast_to and self.forecast_from > self.forecast_to:
            frappe.throw("Forecast From cannot be after Forecast To.")
        if self.has_value_changed("status") and self.get_doc_before_save() and self.get_doc_before_save().status == "Approved":
            frappe.throw("Approved forecasts are frozen. Create a new version instead.")
        if self.status == "Approved" and self.generated_by == frappe.session.user and not frappe.has_role("System Manager"):
            frappe.throw("Forecast preparer cannot approve the same forecast.")
