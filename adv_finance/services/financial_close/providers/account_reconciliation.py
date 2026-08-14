from __future__ import annotations

import frappe

from adv_finance.services.financial_close.providers.base import CloseReadinessProvider

class AccountReconciliationProvider(CloseReadinessProvider):
    provider_name = "account_reconciliation"

    def check(self, task, close_period):
        filters = {"company": close_period.company, "period_end": close_period.period_end}
        total = frappe.db.count("Account Reconciliation", filters)
        open_count = frappe.db.count("Account Reconciliation", {**filters, "status": ["not in", ["Approved", "Closed"]]})
        rejected = frappe.db.count("Account Reconciliation", {**filters, "status": "Review Rejected"})
        exceptions = []
        if open_count:
            exceptions.append({"exception_type": "Open Account Reconciliation", "description": f"{open_count} account reconciliation(s) are not approved."})
        if rejected:
            exceptions.append({"exception_type": "Rejected Account Reconciliation", "description": f"{rejected} account reconciliation(s) were rejected.", "risk_level": "High"})
        return {"ready": total > 0 and open_count == 0 and rejected == 0, "status": "Completed" if total > 0 and open_count == 0 and rejected == 0 else "Blocked", "message": "Required account reconciliations are approved." if total > 0 and open_count == 0 else f"{open_count} account reconciliation(s) require approval.", "exceptions": exceptions, "details": {"total": total, "open": open_count, "rejected": rejected}}
