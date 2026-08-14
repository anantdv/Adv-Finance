from __future__ import annotations

import frappe

from adv_finance.services.financial_close.providers.base import CloseReadinessProvider

class FixedAssetsProvider(CloseReadinessProvider):
    provider_name = "fixed_assets"

    def check(self, task, close_period):
        if not frappe.db.exists("DocType", "Asset"):
            return {"ready": True, "status": "Completed", "message": "Asset module is not installed.", "exceptions": [], "details": {"installed": False}}
        draft_assets = frappe.db.count("Asset", {"company": close_period.company, "available_for_use_date": ["<=", close_period.period_end], "docstatus": 0})
        exceptions = []
        if draft_assets:
            exceptions.append({"exception_type": "Draft Asset", "description": f"{draft_assets} asset(s) remain in Draft."})
        return {"ready": draft_assets == 0, "status": "Completed" if draft_assets == 0 else "Blocked", "message": "Fixed asset readiness passed." if draft_assets == 0 else f"{draft_assets} draft asset(s) require review.", "exceptions": exceptions, "details": {"draft_assets": draft_assets}}
