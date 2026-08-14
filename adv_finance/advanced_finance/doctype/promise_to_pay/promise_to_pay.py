from __future__ import annotations

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime

from adv_finance.services.accounts_receivable.promise_service import validate_promise, recalculate_promise


class PromisetoPay(Document):
    def before_insert(self):
        self.recorded_by = self.recorded_by or frappe.session.user
        self.recorded_on = self.recorded_on or now_datetime()

    def validate(self):
        validate_promise(self)
        recalculate_promise(self)
