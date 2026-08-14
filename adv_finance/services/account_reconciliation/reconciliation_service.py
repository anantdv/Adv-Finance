from __future__ import annotations

from decimal import Decimal

import frappe
from frappe.utils import date_diff, now, now_datetime

from adv_finance.services.account_reconciliation.gl_balance_service import get_account_balance
from adv_finance.services.account_reconciliation.provider_registry import get_provider


def load_gl_balance(name: str) -> dict:
    reconciliation = frappe.get_doc("Account Reconciliation", name)
    balance = get_account_balance(
        reconciliation.company,
        reconciliation.account,
        reconciliation.period_start,
        reconciliation.period_end,
    )
    reconciliation.update(
        {
            "gl_opening_balance": balance["opening_balance"],
            "period_debits": balance["period_debit"],
            "period_credits": balance["period_credit"],
            "gl_closing_balance": balance["closing_balance"],
            "account_currency": reconciliation.account_currency or balance["currency"],
            "gl_balance_loaded": 1,
        }
    )
    recalculate(reconciliation)
    reconciliation.save()
    return {"gl_closing_balance": reconciliation.gl_closing_balance}


def load_supporting_balance(name: str) -> dict:
    reconciliation = frappe.get_doc("Account Reconciliation", name)
    provider = get_provider(reconciliation)
    provider.validate(reconciliation)
    reconciliation.supporting_balance = provider.get_supporting_balance(reconciliation)
    reconciliation.supporting_balance_loaded = 1
    existing_manual = [
        row
        for row in reconciliation.items
        if row.item_type not in ("Supporting Item",)
    ]
    reconciliation.set("items", existing_manual)
    for item in provider.get_supporting_items(reconciliation):
        reconciliation.append("items", item)
    recalculate(reconciliation)
    reconciliation.status = "Preparing"
    reconciliation.save()
    return {"supporting_balance": reconciliation.supporting_balance, "items": len(reconciliation.items)}


def recalculate(reconciliation) -> None:
    gl = Decimal(str(reconciliation.gl_closing_balance or 0))
    support = Decimal(str(reconciliation.supporting_balance or 0))
    reconciliation.gross_difference = gl - support
    reconciliation.explained_difference = sum(
        Decimal(str(row.amount or 0))
        for row in reconciliation.items
        if row.item_type != "Supporting Item" and row.status not in ("Ignored",)
    )
    reconciliation.unexplained_difference = Decimal(str(reconciliation.gross_difference or 0)) - Decimal(
        str(reconciliation.explained_difference or 0)
    )
    tolerance = Decimal(str(reconciliation.tolerance_amount or 0))
    reconciliation.difference_within_tolerance = abs(
        Decimal(str(reconciliation.unexplained_difference or 0))
    ) <= tolerance
    reconciliation.tolerance_used = tolerance if reconciliation.difference_within_tolerance else 0
    for row in reconciliation.items:
        if row.transaction_date:
            row.days_open = max(date_diff(reconciliation.period_end or now(), row.transaction_date), 0)
            row.age_bucket = age_bucket(row.days_open)


def submit_for_review(name: str) -> dict:
    reconciliation = frappe.get_doc("Account Reconciliation", name)
    recalculate(reconciliation)
    reconciliation.prepared_by = frappe.session.user
    reconciliation.prepared_on = now_datetime()
    reconciliation.status = "Ready for Review"
    reconciliation.save()
    return {"status": reconciliation.status}


def review_reconciliation(name: str, approve: bool = True, comments: str | None = None) -> dict:
    reconciliation = frappe.get_doc("Account Reconciliation", name)
    if reconciliation.enforce_segregation_of_duties and reconciliation.prepared_by == frappe.session.user:
        frappe.throw("Preparer cannot review their own reconciliation.")
    reconciliation.reviewed_by = frappe.session.user
    reconciliation.reviewed_on = now_datetime()
    reconciliation.reviewer_comments = comments
    reconciliation.status = "Reviewed" if approve else "Review Rejected"
    reconciliation.save()
    return {"status": reconciliation.status}


def approve_reconciliation(name: str, comments: str | None = None) -> dict:
    reconciliation = frappe.get_doc("Account Reconciliation", name)
    if reconciliation.enforce_segregation_of_duties and reconciliation.reviewed_by == frappe.session.user:
        frappe.throw("Reviewer cannot approve their own reconciliation.")
    reconciliation.approved_by = frappe.session.user
    reconciliation.approved_on = now_datetime()
    reconciliation.approval_comments = comments
    if reconciliation.certification_required:
        reconciliation.certified_by = frappe.session.user
        reconciliation.certified_on = now_datetime()
    reconciliation.status = "Approved"
    reconciliation.save()
    return {"status": reconciliation.status}


def close_reconciliation(name: str) -> dict:
    reconciliation = frappe.get_doc("Account Reconciliation", name)
    _validate_close(reconciliation)
    reconciliation.status = "Closed"
    reconciliation.save()
    return {"closed": True}


def reopen_reconciliation(name: str, reason: str) -> dict:
    if not (frappe.has_role("System Manager") or frappe.has_role("Supplier Reconciliation Manager")):
        frappe.throw("Only an authorized manager can reopen reconciliations.")
    reconciliation = frappe.get_doc("Account Reconciliation", name)
    if not reason:
        frappe.throw("Reopen reason is required.")
    reconciliation.reopen_reason = reason
    reconciliation.reopened_by = frappe.session.user
    reconciliation.reopened_on = now_datetime()
    reconciliation.status = "Reopened"
    reconciliation.save()
    return {"reopened": True}


def generate_reconciliations(period_name: str) -> dict:
    period = frappe.get_doc("Account Reconciliation Period", period_name)
    templates = frappe.get_all(
        "Account Reconciliation Template",
        filters={"company": period.company, "active": 1},
        fields=["name", "account", "reconciliation_method", "reconciliation_provider"],
    )
    created = []
    for template in templates:
        existing = frappe.db.exists(
            "Account Reconciliation",
            {
                "company": period.company,
                "account": template.account,
                "period_start": period.period_start,
                "period_end": period.period_end,
            },
        )
        if existing:
            continue
        doc = frappe.new_doc("Account Reconciliation")
        doc.update(
            {
                "company": period.company,
                "account": template.account,
                "reconciliation_template": template.name,
                "period_start": period.period_start,
                "period_end": period.period_end,
                "reconciliation_date": period.period_end,
                "reconciliation_method": template.reconciliation_method,
                "reconciliation_provider": template.reconciliation_provider,
                "period": period.name,
            }
        )
        doc.insert()
        created.append(doc.name)
    recalculate_period(period.name)
    return {"created": created}


def recalculate_period(period_name: str) -> dict:
    period = frappe.get_doc("Account Reconciliation Period", period_name)
    rows = frappe.get_all(
        "Account Reconciliation",
        filters={"period": period.name},
        fields=["status"],
    )
    period.total_accounts = len(rows)
    period.prepared = sum(1 for row in rows if row.status in ("Ready for Review", "Reviewed", "Approved", "Closed"))
    period.pending_review = sum(1 for row in rows if row.status == "Ready for Review")
    period.approved = sum(1 for row in rows if row.status in ("Approved", "Closed"))
    period.exceptions = sum(1 for row in rows if row.status in ("Review Rejected",))
    period.save()
    return {"updated": True}


def carry_forward_items(source_name: str, target_name: str) -> dict:
    source = frappe.get_doc("Account Reconciliation", source_name)
    target = frappe.get_doc("Account Reconciliation", target_name)
    count = 0
    for row in source.items:
        if row.item_type == "Supporting Item" or row.status in ("Resolved", "Cleared", "Ignored"):
            continue
        child = target.append(
            "items",
            {
                "item_type": "Carry Forward",
                "reference": row.reference,
                "description": row.description,
                "transaction_date": row.transaction_date,
                "expected_clearance_date": row.expected_clearance_date,
                "debit": row.debit,
                "credit": row.credit,
                "amount": row.amount,
                "source_doctype": row.source_doctype,
                "source_document": row.source_document,
                "external_reference": row.external_reference,
                "status": "Carried Forward",
                "assigned_to": row.assigned_to,
                "originating_reconciliation": source.name,
                "originating_item": row.name,
                "carried_forward_from": source.name,
            },
        )
        row.carried_forward_to = target.name
        count += 1
    recalculate(target)
    source.save()
    target.save()
    return {"carried_forward": count}


def age_bucket(days_open: int) -> str:
    if days_open <= 0:
        return "Current"
    if days_open <= 30:
        return "1-30"
    if days_open <= 60:
        return "31-60"
    if days_open <= 90:
        return "61-90"
    if days_open <= 180:
        return "91-180"
    return "180+"


def _validate_close(reconciliation) -> None:
    if not reconciliation.gl_balance_loaded:
        frappe.throw("GL balance must be loaded before closing.")
    if not reconciliation.supporting_balance_loaded:
        frappe.throw("Supporting balance must be loaded before closing.")
    if reconciliation.supporting_document_required and not reconciliation.supporting_document:
        frappe.throw("Supporting document is required before closing.")
    if not reconciliation.reviewed_by:
        frappe.throw("Reconciliation must be reviewed before closing.")
    if not reconciliation.difference_within_tolerance and Decimal(str(reconciliation.unexplained_difference or 0)):
        frappe.throw("Unexplained difference must be within tolerance before closing.")
