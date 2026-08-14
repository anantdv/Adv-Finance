from __future__ import annotations

import frappe


def get_budget_close_readiness(company: str, period_end) -> dict:
    pending_overrides = frappe.db.count("Budget Override Request", {"company": company, "status": "Pending"})
    stale_commitments = frappe.db.count("Budget Commitment", {"company": company, "status": "Open", "expected_date": ["<", period_end]})
    approved_budget = frappe.db.count("Budget Plan", {"company": company, "status": "Approved", "from_date": ["<=", period_end], "to_date": [">=", period_end]})
    return {"ready": bool(approved_budget and not pending_overrides), "approved_budget_plans": approved_budget, "pending_overrides": pending_overrides, "stale_commitments": stale_commitments}
