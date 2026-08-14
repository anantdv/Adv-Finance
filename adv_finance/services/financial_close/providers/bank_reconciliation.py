from __future__ import annotations

import frappe

from adv_finance.services.financial_close.providers.base import CloseReadinessProvider

class BankReconciliationProvider(CloseReadinessProvider):
    provider_name = "bank_reconciliation"

    def check(self, task, close_period):
        if not frappe.db.exists("DocType", "Bank Transaction"):
            return {"ready": False, "status": "Not Ready", "message": "Bank Transaction DocType is not available.", "exceptions": [], "details": {}}
        unreconciled = frappe.db.count("Bank Transaction", {"company": close_period.company, "date": ["<=", close_period.period_end], "status": ["not in", ["Reconciled", "Settled"]]})
        exceptions = []
        if unreconciled:
            exceptions.append({"exception_type": "Unreconciled Bank Transaction", "description": f"{unreconciled} bank transaction(s) need review."})
        return {"ready": unreconciled == 0, "status": "Completed" if unreconciled == 0 else "Blocked", "message": "No unreconciled bank transactions found." if unreconciled == 0 else f"{unreconciled} unreconciled bank transaction(s).", "exceptions": exceptions, "details": {"unreconciled": unreconciled}}
