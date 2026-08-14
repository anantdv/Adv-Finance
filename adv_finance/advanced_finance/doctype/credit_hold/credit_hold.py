from __future__ import annotations

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime, today


class CreditHold(Document):
    def before_insert(self):
        self.created_by = self.created_by or frappe.session.user
        self.hold_date = self.hold_date or today()
        self.effective_from = self.effective_from or self.hold_date

    def validate(self):
        if not self.active and not self.released_by:
            self.released_by = frappe.session.user
            self.released_on = now_datetime()
