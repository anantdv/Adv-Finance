from __future__ import annotations

import frappe

from adv_finance.services.financial_close.providers.base import CloseReadinessProvider

class PayrollProvider(CloseReadinessProvider):
    provider_name = "payroll"

    def check(self, task, close_period):
        if "hrms" not in frappe.get_installed_apps():
            return {"ready": True, "status": "Completed", "message": "HRMS is not installed; payroll close task is not applicable.", "exceptions": [], "details": {"installed": False}}
        if not frappe.db.exists("DocType", "Salary Slip"):
            return {"ready": True, "status": "Completed", "message": "Salary Slip DocType is not available.", "exceptions": [], "details": {"installed": False}}
        draft = frappe.db.count("Salary Slip", {"company": close_period.company, "end_date": ["<=", close_period.period_end], "docstatus": 0})
        exceptions = []
        if draft:
            exceptions.append({"exception_type": "Draft Salary Slip", "description": f"{draft} salary slip(s) are still Draft."})
        return {"ready": draft == 0, "status": "Completed" if draft == 0 else "Blocked", "message": "Payroll readiness passed." if draft == 0 else f"{draft} salary slip(s) need submission or cancellation.", "exceptions": exceptions, "details": {"draft_salary_slips": draft}}
