import frappe
from frappe.model.document import Document

class SupplierOnboardingRequest(Document):
    def validate(self):
        self.requested_by = self.requested_by or frappe.session.user
        if self.status == "Approved" and self.approved_by == self.requested_by and not frappe.has_role("System Manager"):
            frappe.throw("Requester cannot approve the same supplier onboarding request.")
