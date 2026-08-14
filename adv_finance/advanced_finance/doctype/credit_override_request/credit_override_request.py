from __future__ import annotations

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime

from adv_finance.services.accounts_receivable.credit_override_service import refresh_override_exposure


class CreditOverrideRequest(Document):
    def before_insert(self):
        self.requested_by = self.requested_by or frappe.session.user
        self.requested_on = self.requested_on or now_datetime()

    def validate(self):
        refresh_override_exposure(self, save=False)
        if self.status == "Approved" and self.requested_by == frappe.session.user and not frappe.has_role("System Manager"):
            frappe.throw("Requester cannot approve their own credit override.")
