import frappe
from frappe.model.document import Document


class SupplierStatementTemplate(Document):
    def validate(self):
        if self.header_row_number and self.header_row_number < 1:
            frappe.throw("Header row number must be 1 or greater.")
        if self.file_type == "XLSX" and not self.sheet_name:
            self.sheet_name = None
