import frappe
from frappe.model.document import Document
from frappe.utils import today

class FinanceAgeingRemark(Document):
    def validate(self):
        self.entered_by = self.entered_by or frappe.session.user
        self.remark_date = self.remark_date or today()
