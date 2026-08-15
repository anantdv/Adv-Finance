from __future__ import annotations

from decimal import Decimal

import frappe


def classify_difference(origin, target=None, tolerance_amount=0) -> dict | None:
    if not target:
        return {"difference_type": "Missing Invoice", "amount": Decimal(str(origin.amount or 0)), "description": "No matching intercompany target document was found."}
    amount_diff = Decimal(str(origin.amount or 0)) - Decimal(str(target.amount or 0))
    if abs(amount_diff) > Decimal(str(tolerance_amount or 0)):
        return {"difference_type": "Amount Difference", "amount": amount_diff, "description": "Origin and destination amounts differ beyond tolerance."}
    if getattr(origin, "currency", None) != getattr(target, "currency", None):
        return {"difference_type": "Currency Difference", "amount": amount_diff, "description": "Origin and destination currencies differ."}
    return None


def create_difference(transaction=None, match=None, difference=None) -> str | None:
    if not difference:
        return None
    doc = frappe.new_doc("Intercompany Difference")
    doc.update({
        "intercompany_transaction": getattr(transaction, "name", None),
        "intercompany_match": getattr(match, "name", None),
        "difference_type": difference["difference_type"],
        "origin_company": getattr(transaction, "origin_company", None) or getattr(match, "origin_company", None),
        "destination_company": getattr(transaction, "destination_company", None) or getattr(match, "destination_company", None),
        "amount": difference.get("amount"),
        "currency": getattr(transaction, "currency", None) or getattr(match, "currency", None),
        "description": difference.get("description"),
        "severity": "High" if abs(Decimal(str(difference.get("amount") or 0))) else "Medium",
        "status": "Open",
    })
    doc.insert(ignore_permissions=True)
    return doc.name
