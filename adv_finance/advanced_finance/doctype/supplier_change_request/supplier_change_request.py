import frappe
from frappe.model.document import Document

class SupplierChangeRequest(Document):
    def validate(self):
        self.requested_by = self.requested_by or frappe.session.user
        if self.change_type in ("Bank Account", "Bank Account Number", "Bank Name", "SWIFT/BIC") and self.status in ("Verified", "Approved", "Applied") and not self.verified_by:
            frappe.throw("Bank changes require independent verification.")
        if self.verified_by and self.verified_by == self.requested_by and not frappe.has_role("System Manager"):
            frappe.throw("Requester cannot verify the same supplier bank change.")
        if self.status == "Approved" and self.approved_by in (self.requested_by, self.verified_by) and not frappe.has_role("System Manager"):
            frappe.throw("Supplier bank change approver must be independent.")
