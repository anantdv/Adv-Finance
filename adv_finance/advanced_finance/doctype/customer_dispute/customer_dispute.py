from __future__ import annotations

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime

from adv_finance.services.accounts_receivable.dispute_service import validate_dispute


class CustomerDispute(Document):
    def validate(self):
        validate_dispute(self)
        if self.status in ("Resolved", "Rejected", "Closed") and not self.resolved_by:
            self.resolved_by = frappe.session.user
            self.resolved_on = now_datetime()
