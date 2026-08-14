from __future__ import annotations

import frappe
from frappe.utils import now_datetime


def refresh_accrual_exceptions(accrual_name: str) -> dict:
    accrual = frappe.get_doc("Accrual", accrual_name)
    created = 0
    if accrual.require_supporting_attachment and not accrual.supporting_attachment:
        accrual.append("exceptions", _exception(accrual.name, "Missing Evidence", "Medium", "Supporting evidence is required.", 0))
        created += 1
    if accrual.workflow_status != "Approved" and accrual.posting_status != "Not Posted":
        accrual.append("exceptions", _exception(accrual.name, "Unapproved Accrual", "High", "Accrual has posting activity but is not approved.", accrual.accrual_amount))
        created += 1
    if accrual.reversal_required and accrual.posting_status == "Posted" and not accrual.reversal_journal_entry:
        accrual.append("exceptions", _exception(accrual.name, "Missing Reversal", "High", "Posted accrual has no reversal draft.", accrual.accrual_amount))
        created += 1
    if accrual.variance_status in ("Under Accrued", "Over Accrued"):
        accrual.append("exceptions", _exception(accrual.name, "Amount Variance", "Medium", f"Variance status: {accrual.variance_status}.", accrual.variance_amount))
        created += 1
    accrual.save()
    return {"created": created}


def resolve_exception(accrual_name: str, row_name: str, notes: str | None = None) -> dict:
    accrual = frappe.get_doc("Accrual", accrual_name)
    for row in accrual.exceptions:
        if row.name == row_name:
            row.status = "Resolved"
            row.resolution_notes = notes
            row.resolved_by = frappe.session.user
            row.resolved_on = now_datetime()
            accrual.save()
            return {"resolved": True}
    frappe.throw("Accrual Exception row was not found.")


def _exception(accrual_name, exception_type, severity, description, amount):
    return {
        "accrual": accrual_name,
        "exception_type": exception_type,
        "severity": severity,
        "description": description,
        "amount": amount,
        "status": "Open",
    }
