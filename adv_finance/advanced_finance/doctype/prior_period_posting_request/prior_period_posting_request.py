import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime

class PriorPeriodPostingRequest(Document):
    def validate(self):
        self.requested_by = self.requested_by or frappe.session.user
        self.requested_on = self.requested_on or now_datetime()
        if self.status == "Approved" and self.approved_by == self.requested_by and not frappe.has_role("System Manager"):
            frappe.throw("Requester cannot approve the same prior-period posting request.")
