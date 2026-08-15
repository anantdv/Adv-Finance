from __future__ import annotations

import frappe


def dashboard_summary(company=None) -> dict:
    total = frappe.db.count("Intercompany Transaction", {"origin_company": company}) if company else frappe.db.count("Intercompany Transaction")
    matched = frappe.db.count("Intercompany Transaction", {"origin_company": company, "matching_status": "Matched"}) if company else frappe.db.count("Intercompany Transaction", {"matching_status": "Matched"})
    differences = frappe.db.count("Intercompany Difference", {"origin_company": company, "status": ["not in", ["Resolved", "Closed"]]}) if company else frappe.db.count("Intercompany Difference", {"status": ["not in", ["Resolved", "Closed"]]})
    settlements = frappe.db.count("Intercompany Settlement", {"origin_company": company, "status": "Settled"}) if company else frappe.db.count("Intercompany Settlement", {"status": "Settled"})
    return {"transactions": total, "matched": matched, "matched_percent": (matched / total * 100) if total else 0, "unreconciled": differences, "settled": settlements}
