from __future__ import annotations

import frappe
from frappe.model.document import Document


class FinancialCloseTemplate(Document):
    def validate(self):
        if self.company:
            for row in self.tasks:
                if row.default_owner and not frappe.db.exists("User", row.default_owner):
                    frappe.throw(f"Default owner {row.default_owner} was not found.")
        seen = set()
        for row in self.tasks:
            if not row.task_code:
                frappe.throw("Every template task requires a Task Code.")
            code = row.task_code.strip().upper()
            if code in seen:
                frappe.throw(f"Duplicate template task code: {row.task_code}")
            seen.add(code)
