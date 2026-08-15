from frappe.model.document import Document
import frappe
from frappe.utils import now_datetime


class IntercompanyTransaction(Document):
    def before_insert(self):
        if not self.created_date:
            self.created_date = now_datetime()
    def validate(self):
        if self.origin_company == self.destination_company:
            frappe.throw("Origin and destination company cannot be the same.")
