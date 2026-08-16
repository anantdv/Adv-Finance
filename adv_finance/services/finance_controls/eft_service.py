from __future__ import annotations

import frappe


def get_eft_requisition_context(payment_run):
    doc = frappe.get_doc("Payment Run", payment_run) if isinstance(payment_run, str) else payment_run
    return {"requisition_number": doc.name, "company": doc.company, "payment_date": doc.payment_date, "bank_account": getattr(doc, "bank_account", None), "currency": getattr(doc, "currency", None), "mode_of_payment": getattr(doc, "mode_of_payment", None), "prepared_by": getattr(doc, "owner", None), "items": getattr(doc, "items", [])}


def get_remittance_advice_context(payment_entry):
    doc = frappe.get_doc("Payment Entry", payment_entry) if isinstance(payment_entry, str) else payment_entry
    allocations=[]
    for row in getattr(doc, "references", []) or []:
        allocations.append({"invoice": row.reference_name, "reference_doctype": row.reference_doctype, "amount_applied": row.allocated_amount})
    return {"company": doc.company, "supplier": getattr(doc, "party", None), "payment_date": doc.posting_date, "payment_reference": getattr(doc, "reference_no", None), "currency": getattr(doc, "paid_from_account_currency", None) or getattr(doc, "paid_to_account_currency", None), "mode_of_payment": getattr(doc, "mode_of_payment", None), "payment_entry": doc.name, "allocations": allocations, "total_paid": getattr(doc, "paid_amount", 0)}


def send_remittance_advice(payment_entry, recipients=None):
    ctx = get_remittance_advice_context(payment_entry)
    doc = frappe.get_doc("Payment Entry", payment_entry) if isinstance(payment_entry, str) else payment_entry
    recipients = recipients or []
    frappe.sendmail(recipients=recipients, subject=f"Remittance Advice {doc.name}", message=f"Please find remittance advice for {doc.name}.", reference_doctype="Payment Entry", reference_name=doc.name)
    return {"sent": True, "payment_entry": doc.name, "recipients": recipients, "context": ctx}
