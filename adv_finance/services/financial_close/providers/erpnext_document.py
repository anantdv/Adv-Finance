from __future__ import annotations

import frappe

from adv_finance.services.financial_close.providers.base import CloseReadinessProvider

class ERPNextDocumentProvider(CloseReadinessProvider):
    provider_name = "erpnext_document"

    def check(self, task, close_period):
        if not task.source_doctype:
            return super().check(task, close_period)
        open_count = frappe.db.count(task.source_doctype, {"company": close_period.company, "docstatus": 0})
        return {"ready": open_count == 0, "status": "Completed" if open_count == 0 else "Blocked", "message": f"No draft {task.source_doctype} records found." if open_count == 0 else f"{open_count} draft {task.source_doctype} record(s) require review.", "exceptions": [] if open_count == 0 else [{"exception_type": "Draft ERPNext Document", "description": f"{open_count} draft {task.source_doctype} record(s)."}], "details": {"open": open_count}}
