from frappe.model.document import Document
import frappe
from frappe.utils import now_datetime
from adv_finance.services.budgeting.budget_service import recalculate_budget_plan


class BudgetPlan(Document):
    def before_insert(self):
        if not self.prepared_by:
            self.prepared_by = frappe.session.user

    def validate(self):
        if self.from_date and self.to_date and self.from_date > self.to_date:
            frappe.throw("Budget From Date cannot be after To Date.")
        before = self.get_doc_before_save() if not self.is_new() else None
        if before and before.status == "Approved" and self.status == "Approved":
            frappe.throw("Approved Budget Plans are immutable. Create a reforecast or new version.")
        recalculate_budget_plan(self)
