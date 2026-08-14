from __future__ import annotations

import frappe

from adv_finance.services.financial_close.providers.base import CloseReadinessProvider

class FXRevaluationProvider(CloseReadinessProvider):
    provider_name = "fx_revaluation"

    def check(self, task, close_period):
        if not frappe.db.exists("DocType", "Exchange Rate Revaluation"):
            return {"ready": False, "status": "Not Ready", "message": "Exchange Rate Revaluation DocType was not found; keep this task manual for this site.", "exceptions": [], "details": {}}
        submitted = frappe.db.count("Exchange Rate Revaluation", {"company": close_period.company, "posting_date": ["between", [close_period.period_start, close_period.period_end]], "docstatus": 1})
        return {"ready": submitted > 0, "status": "Completed" if submitted else "Waiting", "message": "Submitted Exchange Rate Revaluation found." if submitted else "No submitted Exchange Rate Revaluation found for this period.", "exceptions": [] if submitted else [{"exception_type": "FX Revaluation Missing", "description": "No submitted Exchange Rate Revaluation found."}], "details": {"submitted": submitted}}
