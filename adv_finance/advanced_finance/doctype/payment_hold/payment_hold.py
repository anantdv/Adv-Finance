from frappe.model.document import Document
import frappe


class PaymentHold(Document):
    def before_insert(self):
        if not self.created_by:
            self.created_by = frappe.session.user

    def validate(self):
        if self.hold_scope == "Invoice" and not self.purchase_invoice:
            frappe.throw("Purchase Invoice is required for invoice-level holds.")
        if self.hold_scope == "Supplier" and self.purchase_invoice:
            self.purchase_invoice = None
        if self.hold_from and self.hold_until and self.hold_from > self.hold_until:
            frappe.throw("Hold From cannot be after Hold Until.")
