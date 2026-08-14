from __future__ import annotations

from decimal import Decimal

import frappe
from frappe.utils import date_diff, now_datetime, nowdate

from adv_finance.compatibility.erpnext_v16 import (
    get_purchase_invoice_docstatus,
    get_purchase_invoice_expense_candidates,
)
from adv_finance.services.accrual.accrual_service import recalculate_accrual


def suggest_purchase_invoice_matches(accrual_name: str) -> dict:
    accrual = frappe.get_doc("Accrual", accrual_name)
    accrual.matches = [row for row in accrual.matches if row.status != "Suggested"]
    candidates = get_purchase_invoice_expense_candidates(
        company=accrual.company,
        supplier=accrual.supplier,
        expense_account=accrual.expense_account,
        currency=accrual.currency,
        from_date=accrual.accrual_date,
    )
    suggestions = []
    for candidate in candidates:
        available = get_available_invoice_item_amount(candidate.purchase_invoice_item, candidate.invoice_amount)
        if available <= 0:
            continue
        score = score_candidate(accrual, candidate)
        if score < 50:
            continue
        suggestions.append((score, candidate, available))
    suggestions.sort(key=lambda item: item[0], reverse=True)
    created = []
    for score, candidate, available in suggestions[:10]:
        match = _append_match(
            accrual,
            candidate.purchase_invoice,
            candidate.purchase_invoice_item,
            min(Decimal(str(accrual.remaining_amount or accrual.accrual_amount or 0)), available),
            candidate.invoice_amount,
            "Suggested" if score < 100 else "Exact",
            "Suggested",
            f"Deterministic score {score}",
        )
        created.append(match.purchase_invoice)
    accrual.save()
    return {"suggestions": created}


def accept_match(accrual_name: str, purchase_invoice: str, matched_amount, purchase_invoice_item: str | None = None) -> dict:
    accrual = frappe.get_doc("Accrual", accrual_name)
    if get_purchase_invoice_docstatus(purchase_invoice) != 1:
        frappe.throw("Purchase Invoice must be submitted before matching.")
    amount = Decimal(str(matched_amount or 0))
    if amount <= 0:
        frappe.throw("Matched amount must be greater than zero.")
    available = get_available_invoice_item_amount(purchase_invoice_item, amount)
    if purchase_invoice_item and amount > available:
        frappe.throw("Matched amount exceeds available Purchase Invoice item amount.")
    match = _append_match(accrual, purchase_invoice, purchase_invoice_item, amount, amount, "Manual", "Accepted", "")
    recalculate_accrual(accrual)
    accrual.save()
    return {"match": match.purchase_invoice}


def refresh_matches(accrual_name: str) -> dict:
    accrual = frappe.get_doc("Accrual", accrual_name)
    exceptions = 0
    for match in accrual.matches:
        if match.status in ("Rejected", "Closed"):
            continue
        if get_purchase_invoice_docstatus(match.purchase_invoice) != 1:
            accrual.append(
                "exceptions",
                {
                    "accrual": accrual.name,
                    "purchase_invoice": match.purchase_invoice,
                    "exception_type": "Purchase Invoice Cancelled",
                    "severity": "High",
                    "description": "Matched Purchase Invoice is no longer submitted.",
                    "amount": match.matched_amount,
                    "status": "Open",
                },
            )
            exceptions += 1
    recalculate_accrual(accrual)
    accrual.save()
    return {"exceptions": exceptions}


def score_candidate(accrual, candidate) -> int:
    score = 0
    if accrual.supplier and accrual.supplier == candidate.supplier:
        score += 30
    delta = abs(Decimal(str(accrual.remaining_amount or accrual.accrual_amount or 0)) - Decimal(str(candidate.invoice_amount or 0)))
    if delta == 0:
        score += 30
    elif delta <= Decimal(str(accrual.variance_tolerance_amount or 0)):
        score += 25
    if accrual.expense_account == candidate.expense_account:
        score += 20
    if candidate.posting_date and accrual.reversal_date:
        days = abs(date_diff(candidate.posting_date, accrual.reversal_date))
        if days <= 7:
            score += 10
        elif days <= 30:
            score += 5
    text = f"{candidate.description or ''} {accrual.external_reference or ''}".upper()
    if accrual.external_reference and accrual.external_reference.upper() in text:
        score += 10
    return min(score, 100)


def get_available_invoice_item_amount(purchase_invoice_item: str | None, invoice_amount) -> Decimal:
    if not purchase_invoice_item:
        return Decimal(str(invoice_amount or 0))
    matched = frappe.db.sql(
        """
        select coalesce(sum(matched_amount), 0) as matched
        from `tabAccrual Match`
        where purchase_invoice_item = %(purchase_invoice_item)s
          and status in ('Accepted', 'Posted', 'Closed')
        """,
        {"purchase_invoice_item": purchase_invoice_item},
        as_dict=True,
    )
    return Decimal(str(invoice_amount or 0)) - Decimal(str(matched[0].matched if matched else 0))


def _append_match(accrual, purchase_invoice, purchase_invoice_item, matched_amount, invoice_amount, match_type, status, notes):
    variance = Decimal(str(invoice_amount or 0)) - Decimal(str(matched_amount or 0))
    return accrual.append(
        "matches",
        {
            "accrual": accrual.name,
            "purchase_invoice": purchase_invoice,
            "purchase_invoice_item": purchase_invoice_item,
            "matching_date": nowdate(),
            "accrual_amount_available": accrual.remaining_amount,
            "invoice_amount": invoice_amount,
            "matched_amount": matched_amount,
            "variance": variance,
            "match_type": match_type,
            "status": status,
            "matched_by": frappe.session.user,
            "matched_on": now_datetime(),
            "notes": notes,
        },
    )
