from frappe.model.document import Document
from frappe.utils import now_datetime
import frappe


class PaymentRunException(Document):
    def validate(self):
        if self.status == "Resolved" and not self.resolved_by:
            self.resolved_by = frappe.session.user
            self.resolved_on = now_datetime()
