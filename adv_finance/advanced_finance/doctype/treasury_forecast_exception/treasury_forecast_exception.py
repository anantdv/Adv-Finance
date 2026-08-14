from frappe.model.document import Document
import frappe
from frappe.utils import now_datetime


class TreasuryForecastException(Document):
    def validate(self):
        if self.status in ("Resolved", "Closed") and not self.resolved_on:
            self.resolved_by = frappe.session.user
            self.resolved_on = now_datetime()
