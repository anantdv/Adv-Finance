from __future__ import annotations

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime


class FinancialCloseException(Document):
    def before_insert(self):
        if not self.created_on:
            self.created_on = now_datetime()

    def validate(self):
        if self.status in ("Resolved", "Accepted", "Ignored") and not self.resolved_by:
            self.resolved_by = frappe.session.user
            self.resolved_on = now_datetime()
