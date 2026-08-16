from __future__ import annotations

import frappe
from frappe.utils import now_datetime


def generate_elimination_journals(consolidation_period: str) -> dict:
    period = frappe.get_doc("Consolidation Period", consolidation_period)
    candidates = frappe.get_all("Intercompany Elimination Candidate", filters={"status": "Ready"}, fields=["name", "origin_company", "destination_company", "amount", "currency", "intercompany_match", "intercompany_transaction"])
    count = 0
    for candidate in candidates:
        exists = frappe.db.exists("Elimination Journal", {"consolidation_period": period.name, "source_elimination_candidate": candidate.name})
        if exists:
            continue
        doc = frappe.new_doc("Elimination Journal")
        doc.update({"consolidation_period": period.name, "source_companies": f"{candidate.origin_company}, {candidate.destination_company}", "source_elimination_candidate": candidate.name, "amount": candidate.amount, "currency": candidate.currency, "status": "Generated", "reason": "Generated from Intercompany Elimination Candidate", "prepared_by": frappe.session.user})
        doc.insert(ignore_permissions=True)
        count += 1
    period.status = "Eliminating"
    period.elimination_status = "Generated"
    period.save()
    return {"elimination_journals": count}


def approve_elimination_journal(name: str) -> dict:
    doc = frappe.get_doc("Elimination Journal", name)
    doc.status = "Approved"
    doc.approved_by = frappe.session.user
    doc.approved_on = now_datetime()
    doc.save()
    return {"status": doc.status}
