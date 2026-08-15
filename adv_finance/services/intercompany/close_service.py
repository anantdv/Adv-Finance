from __future__ import annotations

import frappe


def get_intercompany_close_readiness(company: str | None = None, period_end=None, materiality=0) -> dict:
    filters = {"status": ["not in", ["Resolved", "Closed"]]}
    if company:
        filters["origin_company"] = company
    open_differences = frappe.db.count("Intercompany Difference", filters)
    unmatched = frappe.db.count("Intercompany Transaction", {"origin_company": company, "matching_status": ["not in", ["Matched", "Ignored"]]}) if company else frappe.db.count("Intercompany Transaction", {"matching_status": ["not in", ["Matched", "Ignored"]]})
    unsettled = frappe.db.count("Intercompany Transaction", {"origin_company": company, "settlement_status": ["not in", ["Settled", "Not Settled"]]}) if company else frappe.db.count("Intercompany Transaction", {"settlement_status": ["not in", ["Settled", "Not Settled"]]})
    ready_candidates = frappe.db.count("Intercompany Elimination Candidate", {"origin_company": company, "status": "Ready"}) if company else frappe.db.count("Intercompany Elimination Candidate", {"status": "Ready"})
    ready = not open_differences and not unmatched and not unsettled
    return {"ready": ready, "open_differences": open_differences, "unmatched_transactions": unmatched, "unsettled_transactions": unsettled, "ready_elimination_candidates": ready_candidates, "ready_for_consolidation": ready}
