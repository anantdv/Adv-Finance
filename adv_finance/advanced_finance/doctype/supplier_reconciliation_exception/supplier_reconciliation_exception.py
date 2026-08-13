from frappe.model.document import Document
from frappe.utils import now_datetime
import frappe


class SupplierReconciliationException(Document):
    def validate(self):
        if self.status in ("Resolved", "Ignored") and not self.resolved_on:
            self.resolved_on = now_datetime()
            self.resolved_by = frappe.session.user
