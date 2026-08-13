from __future__ import annotations

from decimal import Decimal

import frappe
from frappe.model.document import Document
from frappe.utils import now, now_datetime


CLOSED_STATUS = "Closed"


class SupplierReconciliation(Document):
    def autoname(self):
        if not self.naming_series:
            self.naming_series = "SUP-REC-.YYYY.-.#####"

    def validate(self):
        self._validate_dates()
        self._validate_payable_account()
        self._calculate_difference()
        self._protect_closed_document()

    def before_insert(self):
        if not self.reconciliation_status:
            self.reconciliation_status = "Draft"

    def _validate_dates(self):
        if self.statement_from_date and self.statement_to_date:
            if self.statement_from_date > self.statement_to_date:
                frappe.throw("Statement From Date cannot be after Statement To Date.")

    def _validate_payable_account(self):
        if not self.payable_account:
            return

        account = frappe.db.get_value("Account", self.payable_account, ["company", "account_type"], as_dict=True)
        if not account:
            frappe.throw("Selected payable account does not exist.")
        if self.company and account.company != self.company:
            frappe.throw("Payable account must belong to the selected company.")
        if account.account_type and account.account_type not in ("Payable", "Liability"):
            frappe.throw("Payable account must be a payable/liability account.")

    def _calculate_difference(self):
        statement = Decimal(str(self.statement_closing_balance or 0))
        erp = Decimal(str(self.erp_closing_balance or 0))
        self.reconciliation_difference = statement - erp

    def _protect_closed_document(self):
        if self.is_new() or self.reconciliation_status != CLOSED_STATUS:
            return

        previous_status = frappe.db.get_value(self.doctype, self.name, "reconciliation_status")
        if previous_status == CLOSED_STATUS and not frappe.has_role("Supplier Reconciliation Manager"):
            frappe.throw("Closed reconciliations can only be changed after manager-controlled reopening.")

    def mark_processing(self, status: str, message: str | None = None):
        frappe.db.set_value(
            self.doctype,
            self.name,
            {
                "reconciliation_status": status,
                "processing_message": message,
                "last_processed_on": now(),
                "last_processed_by": frappe.session.user,
            },
        )

    def set_closed(self):
        if self.reconciliation_difference and not (
            self.accepted_difference and self.difference_reason and self.closing_comments
        ):
            frappe.throw("Non-zero differences require accepted difference, reason, and closing comments.")

        frappe.db.set_value(
            self.doctype,
            self.name,
            {
                "reconciliation_status": CLOSED_STATUS,
                "closed_by": frappe.session.user,
                "closed_on": now_datetime(),
            },
        )
