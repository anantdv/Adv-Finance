from frappe.model.document import Document
import frappe


class TrialBalanceSnapshot(Document):
    def validate(self):
        before = self.get_doc_before_save() if not self.is_new() else None
        if before and before.immutable:
            frappe.throw("Trial Balance Snapshots are immutable. Rebuild the open period snapshot instead.")
