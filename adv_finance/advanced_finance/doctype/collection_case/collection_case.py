from __future__ import annotations

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime

from adv_finance.services.accounts_receivable.collection_case_service import refresh_collection_case


class CollectionCase(Document):
    def before_insert(self):
        self.opened_by = self.opened_by or frappe.session.user
        self.opened_on = self.opened_on or now_datetime()

    def validate(self):
        if self.status == "Closed" and not self.closed_by:
            self.closed_by = frappe.session.user
            self.closed_on = now_datetime()
        refresh_collection_case(self, save=False)
