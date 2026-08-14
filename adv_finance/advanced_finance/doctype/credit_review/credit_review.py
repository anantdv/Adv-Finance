from __future__ import annotations

import frappe
from frappe.model.document import Document

from adv_finance.services.accounts_receivable.credit_review_service import refresh_credit_review


class CreditReview(Document):
    def before_insert(self):
        self.prepared_by = self.prepared_by or frappe.session.user

    def validate(self):
        refresh_credit_review(self, save=False)
