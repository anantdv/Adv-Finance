from __future__ import annotations

from decimal import Decimal

import frappe

from adv_finance.compatibility.erpnext_v16 import create_draft_accrual_journal_entry


def create_accrual_journal_entry(accrual_name: str) -> dict:
    accrual = frappe.get_doc("Accrual", accrual_name)
    if accrual.workflow_status != "Approved":
        frappe.throw("Accrual must be approved before creating a Journal Entry.")
    if accrual.accrual_journal_entry:
        frappe.throw("Accrual Journal Entry already exists.")
    if Decimal(str(accrual.accrual_amount or 0)) <= 0:
        frappe.throw("Accrual amount must be greater than zero.")
    journal_entry = create_draft_accrual_journal_entry(accrual)
    accrual.accrual_journal_entry = journal_entry.name
    accrual.posting_status = "Draft Journal Created"
    accrual.status = "Journal Draft Created"
    if accrual.reversal_required and accrual.reversal_status == "Not Required":
        accrual.reversal_status = "Pending"
    accrual.save()
    return {"journal_entry": journal_entry.name}
