from __future__ import annotations

import frappe
from frappe.model.document import Document
from frappe.utils import getdate, now_datetime

from adv_finance.services.financial_close.dependency_service import get_unmet_dependencies


class FinancialCloseTask(Document):
    def validate(self):
        self._copy_period_context()
        if self.evidence_required and self.status in ("Ready for Review", "Completed"):
            self._validate_evidence()
        if self.status == "Completed":
            self._validate_completion()

    def _copy_period_context(self):
        if not self.financial_close_period:
            return
        period = frappe.db.get_value(
            "Financial Close Period",
            self.financial_close_period,
            ["company", "period_end"],
            as_dict=True,
        )
        if period:
            self.company = period.company
            self.period_end = period.period_end

    def _validate_evidence(self):
        if self.evidence_reference or self.source_document or self.linked_reconciliation or self.linked_accrual or self.linked_journal_entry:
            return
        if not self.is_new() and frappe.get_all("File", filters={"attached_to_doctype": self.doctype, "attached_to_name": self.name}, limit=1):
            return
        frappe.throw("Evidence is required before this close task can be completed or submitted for review.")

    def _validate_completion(self):
        if self.required and self.status == "Completed":
            unmet = get_unmet_dependencies(self)
            if unmet:
                frappe.throw("Complete dependent tasks first: " + ", ".join(row.task_name for row in unmet))
        if self.reviewer and self.completed_by == self.reviewer:
            frappe.throw("Task preparer cannot review their own task when a reviewer is assigned.")
        if not self.completed_by:
            self.completed_by = frappe.session.user
        if not self.completed_on:
            self.completed_on = now_datetime()
        if self.due_date and getdate(self.due_date) < getdate():
            self.blocked_reason = self.blocked_reason or "Completed after due date."
