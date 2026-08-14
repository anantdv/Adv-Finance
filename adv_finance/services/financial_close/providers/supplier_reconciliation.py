from __future__ import annotations

import frappe

from adv_finance.services.financial_close.providers.base import CloseReadinessProvider

class SupplierReconciliationProvider(CloseReadinessProvider):
    provider_name = "supplier_reconciliation"

    def check(self, task, close_period):
        open_count = frappe.db.count(
            "Supplier Reconciliation",
            {
                "company": close_period.company,
                "statement_to_date": ["<=", close_period.period_end],
                "reconciliation_status": ["not in", ["Closed", "Reconciled"]],
            },
        )
        exceptions = []
        if open_count:
            exceptions.append({"exception_type": "Open Supplier Reconciliation", "description": f"{open_count} supplier reconciliation(s) remain open."})
        return {"ready": open_count == 0, "status": "Completed" if open_count == 0 else "Blocked", "message": "Supplier reconciliations are closed." if open_count == 0 else f"{open_count} supplier reconciliation(s) remain open.", "exceptions": exceptions, "details": {"open": open_count}}
