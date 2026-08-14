from __future__ import annotations

import frappe


def get_ar_close_readiness(company: str, period_end) -> dict:
    open_high_disputes = frappe.db.count("Customer Dispute", {"company": company, "dispute_date": ["<=", period_end], "severity": ["in", ["Critical", "High"]], "status": ["not in", ["Resolved", "Rejected", "Closed"]]})
    broken_promises = frappe.db.count("Promise to Pay", {"company": company, "promised_payment_date": ["<=", period_end], "status": "Broken"})
    active_holds = frappe.db.count("Credit Hold", {"company": company, "active": 1})
    return {"ready": not any([open_high_disputes]), "open_high_disputes": open_high_disputes, "broken_promises": broken_promises, "active_credit_holds": active_holds, "exceptions": []}
