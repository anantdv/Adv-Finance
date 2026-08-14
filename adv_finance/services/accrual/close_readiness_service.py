from __future__ import annotations

import frappe


def get_accrual_close_readiness(company: str, period_end) -> dict:
    filters = {"company": company, "accrual_date": ["<=", period_end]}
    unapproved = frappe.db.count("Accrual", {**filters, "workflow_status": ["not in", ["Approved", "Closed"]]})
    unposted = frappe.db.count("Accrual", {**filters, "workflow_status": "Approved", "posting_status": ["!=", "Posted"]})
    missing_reversals = frappe.db.count(
        "Accrual",
        {**filters, "reversal_required": 1, "posting_status": "Posted", "reversal_journal_entry": ["is", "not set"]},
    )
    material_variances = frappe.db.count(
        "Accrual",
        {**filters, "variance_status": ["in", ["Under Accrued", "Over Accrued"]], "workflow_status": ["!=", "Closed"]},
    )
    return {
        "ready": not any([unapproved, unposted, missing_reversals, material_variances]),
        "unapproved": unapproved,
        "unposted": unposted,
        "missing_reversals": missing_reversals,
        "material_variances": material_variances,
        "exceptions": [],
    }
