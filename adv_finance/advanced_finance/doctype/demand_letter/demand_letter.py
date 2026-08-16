import frappe
from frappe.model.document import Document
from frappe.utils import today

class DemandLetter(Document):
    def validate(self):
        self.generated_by = self.generated_by or frappe.session.user
        self.generated_date = self.generated_date or today()
