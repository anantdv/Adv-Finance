from __future__ import annotations

from decimal import Decimal

import frappe
from frappe.utils import now_datetime


def prepare_elimination_candidate(transaction=None, match=None) -> dict:
    source = match or transaction
    status = "Ready"
    reason = None
    amount = Decimal(str(getattr(source, "difference_amount", 0) or 0))
    if amount:
        status = "Difference Exists"
        reason = "Intercompany difference must be resolved before elimination."
    if transaction and getattr(transaction, "settlement_status", None) not in ("Settled", "Not Settled"):
        status = "Awaiting Settlement"
        reason = "Settlement is not complete."
    doc = frappe.new_doc("Intercompany Elimination Candidate")
    doc.update({"origin_company": source.origin_company, "destination_company": source.destination_company, "intercompany_match": getattr(match, "name", None), "intercompany_transaction": getattr(transaction, "name", None), "amount": getattr(source, "origin_total", None) or getattr(source, "amount", None), "currency": getattr(source, "currency", None), "status": status, "blocking_reason": reason, "prepared_on": now_datetime(), "prepared_by": frappe.session.user})
    doc.insert(ignore_permissions=True)
    return {"elimination_candidate": doc.name, "status": doc.status}
