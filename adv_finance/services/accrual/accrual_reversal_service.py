from __future__ import annotations

import frappe
from frappe.utils import nowdate

from adv_finance.compatibility.erpnext_v16 import create_draft_accrual_reversal_journal_entry, get_journal_entry_docstatus


def create_reversal_journal_entry(accrual_name: str) -> dict:
    accrual = frappe.get_doc("Accrual", accrual_name)
    if not accrual.reversal_required:
        frappe.throw("Reversal is not required for this accrual.")
    if accrual.reversal_method != "Automatic Draft Reversal":
        frappe.throw("Only Automatic Draft Reversal accruals can create reversal drafts from this action.")
    if not accrual.reversal_date:
        frappe.throw("Reversal date is required.")
    if accrual.reversal_journal_entry:
        return {"journal_entry": accrual.reversal_journal_entry, "created": False}
    if accrual.accrual_journal_entry and get_journal_entry_docstatus(accrual.accrual_journal_entry) != 1:
        frappe.throw("Original accrual Journal Entry must be submitted before reversal draft creation.")
    journal_entry = create_draft_accrual_reversal_journal_entry(accrual)
    accrual.reversal_journal_entry = journal_entry.name
    accrual.reversal_status = "Draft Created"
    accrual.status = "Reversal Scheduled"
    accrual.save()
    return {"journal_entry": journal_entry.name, "created": True}


def create_due_reversal_drafts(limit: int = 100) -> dict:
    names = frappe.get_all(
        "Accrual",
        filters={
            "reversal_required": 1,
            "reversal_method": "Automatic Draft Reversal",
            "reversal_date": ["<=", nowdate()],
            "reversal_journal_entry": ["is", "not set"],
            "posting_status": "Posted",
        },
        pluck="name",
        limit=limit,
    )
    created = []
    for name in names:
        result = create_reversal_journal_entry(name)
        if result.get("created"):
            created.append(result["journal_entry"])
    return {"created": created}
