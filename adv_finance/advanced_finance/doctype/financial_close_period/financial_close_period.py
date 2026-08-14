from __future__ import annotations

import frappe
from frappe.model.document import Document
from frappe.utils import getdate, now_datetime

from adv_finance.services.financial_close.close_service import recalculate_close_period


class FinancialClosePeriod(Document):
    def before_insert(self):
        if not self.status:
            self.status = "Draft"
        if not self.opened_on:
            self.opened_on = now_datetime()
        if not self.created_by:
            self.created_by = frappe.session.user

    def validate(self):
        if self.period_start and self.period_end and getdate(self.period_start) > getdate(self.period_end):
            frappe.throw("Period Start must be on or before Period End.")
        self._validate_template_company()
        if not self.close_name and self.company and self.period_end:
            self.close_name = f"Financial Close - {self.company} - {getdate(self.period_end).strftime('%B %Y')}"

    def before_save(self):
        if not getattr(frappe.flags, "skip_financial_close_recalculate", False):
            recalculate_close_period(self, save=False)

    def _validate_template_company(self):
        if not self.close_template:
            return
        template_company = frappe.db.get_value("Financial Close Template", self.close_template, "company")
        if template_company and self.company and template_company != self.company:
            frappe.throw("Close Template company must match the Financial Close Period company.")
