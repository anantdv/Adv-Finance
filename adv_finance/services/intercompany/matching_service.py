from __future__ import annotations

from collections import defaultdict
from decimal import Decimal

import frappe
from frappe.utils import now_datetime

from adv_finance.compatibility.erpnext_v16 import get_intercompany_source_documents
from adv_finance.services.intercompany.difference_service import classify_difference, create_difference
from adv_finance.services.intercompany.partner_service import get_partner


def score_match(origin, target, tolerance_amount=0) -> dict:
    score = 0
    factors = []
    if origin.reference_no and target.reference_no and origin.reference_no == target.reference_no:
        score += 40; factors.append("Reference Number")
    if origin.currency == target.currency:
        score += 15; factors.append("Currency")
    if abs(Decimal(str(origin.amount or 0)) - Decimal(str(target.amount or 0))) <= Decimal(str(tolerance_amount or 0)):
        score += 25; factors.append("Amount")
    if origin.posting_date == target.posting_date:
        score += 10; factors.append("Date")
    if origin.destination_company == target.origin_company or origin.origin_company == target.destination_company:
        score += 10; factors.append("Partner")
    return {"score": score, "factors": factors, "matched": score >= 70}


def suggest_invoice_matches(origin_company: str, destination_company: str, from_date=None, to_date=None) -> list[dict]:
    docs = get_intercompany_source_documents(origin_company, destination_company, from_date, to_date)
    origins = [row for row in docs if row.company == origin_company]
    targets = [row for row in docs if row.company == destination_company]
    partner = get_partner(origin_company, destination_company)
    tolerance = getattr(partner, "matching_tolerance_amount", 0) if partner else 0
    suggestions = []
    for origin in origins:
        best = None
        for target in targets:
            result = score_match(origin, target, tolerance)
            if not best or result["score"] > best["score"]:
                best = {"origin": origin, "target": target, **result}
        if best and best["matched"]:
            suggestions.append(best)
    return suggestions


def create_match(origin_transactions: list, target_transactions: list, match_basis="Manual") -> dict:
    if not origin_transactions or not target_transactions:
        frappe.throw("At least one origin and one destination transaction are required.")
    origin_total = sum(Decimal(str(row.amount or 0)) for row in origin_transactions)
    target_total = sum(Decimal(str(row.amount or 0)) for row in target_transactions)
    first = origin_transactions[0]
    match = frappe.new_doc("Intercompany Match")
    match.update({
        "match_type": _match_type(origin_transactions, target_transactions),
        "origin_company": first.origin_company,
        "destination_company": first.destination_company,
        "match_basis": match_basis,
        "status": "Suggested",
        "origin_total": origin_total,
        "destination_total": target_total,
        "difference_amount": origin_total - target_total,
        "currency": getattr(first, "currency", None),
        "matched_by": frappe.session.user,
        "matched_on": now_datetime(),
    })
    for row in origin_transactions:
        match.append("items", _item(row, "Origin"))
    for row in target_transactions:
        match.append("items", _item(row, "Destination"))
    match.insert()
    return {"intercompany_match": match.name, "difference_amount": match.difference_amount}


def approve_match(name: str) -> dict:
    match = frappe.get_doc("Intercompany Match", name)
    if match.status not in ("Suggested", "Draft"):
        frappe.throw("Only Draft or Suggested matches can be approved.")
    match.status = "Approved"
    match.approved_by = frappe.session.user
    match.approved_on = now_datetime()
    match.save()
    for item in match.items:
        if item.transaction:
            frappe.db.set_value("Intercompany Transaction", item.transaction, {"matching_status": "Matched", "match": match.name, "matched_date": match.approved_on})
    if Decimal(str(match.difference_amount or 0)):
        create_difference(match=match, difference={"difference_type": "Amount Difference", "amount": match.difference_amount, "description": "Approved match has a residual difference."})
    return {"status": match.status}


def refresh_intercompany_transactions(company=None, from_date=None, to_date=None) -> dict:
    docs = get_intercompany_source_documents(company, None, from_date, to_date)
    existing = {(row.source_doctype, row.source_document): row.name for row in frappe.get_all("Intercompany Transaction", filters={}, fields=["name", "source_doctype", "source_document"])}
    count = 0
    for row in docs:
        key = (row.source_doctype, row.source_document)
        doc = frappe.get_doc("Intercompany Transaction", existing[key]) if key in existing else frappe.new_doc("Intercompany Transaction")
        doc.update({"origin_company": row.company, "destination_company": row.partner_company, "source_doctype": row.source_doctype, "source_document": row.source_document, "posting_date": row.posting_date, "due_date": row.due_date, "party": row.party, "reference_no": row.reference_no, "description": row.description, "amount": row.amount, "currency": row.currency, "company_currency_amount": row.company_currency_amount, "matching_status": getattr(doc, "matching_status", None) or "Unmatched", "settlement_status": getattr(doc, "settlement_status", None) or "Not Settled", "created_date": now_datetime()})
        doc.save() if key in existing else doc.insert()
        count += 1
    return {"refreshed": count}


def _match_type(origins, targets):
    if len(origins) == 1 and len(targets) == 1:
        return "One to One"
    if len(origins) == 1:
        return "One to Many"
    if len(targets) == 1:
        return "Many to One"
    return "Many to Many"


def _item(row, side):
    return {"transaction": getattr(row, "name", None), "source_doctype": row.source_doctype, "source_document": row.source_document, "company": row.origin_company if side == "Origin" else row.destination_company, "amount": row.amount, "currency": row.currency, "side": side}
