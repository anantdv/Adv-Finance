from __future__ import annotations

from collections import defaultdict
from decimal import Decimal

import frappe

from adv_finance.compatibility.erpnext_v16 import get_material_request_precommitments, get_purchase_order_commitments


def get_open_commitments(company: str, account: str | None = None, cost_center=None, project=None, as_of_date=None) -> list[dict]:
    rows = []
    for row in get_purchase_order_commitments(company, account, cost_center, project, as_of_date):
        remaining = Decimal(str(row.remaining_amount or 0))
        if remaining > 0:
            rows.append({"commitment_type": "Commitment", "source_doctype": "Purchase Order", "source_document": row.purchase_order, "source_line": row.source_line, "supplier": row.supplier, "account": row.account, "cost_center": row.cost_center, "project": row.project, "original_amount": Decimal(str(row.original_amount or 0)), "consumed_amount": Decimal(str(row.consumed_amount or 0)), "remaining_amount": remaining, "expected_date": row.expected_date, "status": row.status})
    for row in frappe.get_all("Manual Budget Commitment", filters={"company": company, "status": ["in", ["Approved", "Partially Consumed"]]}, fields=["name", "account", "cost_center", "project", "amount", "expected_date", "description"]):
        if account and row.account != account:
            continue
        if cost_center and row.cost_center != cost_center:
            continue
        if project and row.project != project:
            continue
        rows.append({"commitment_type": "Manual", "source_doctype": "Manual Budget Commitment", "source_document": row.name, "account": row.account, "cost_center": row.cost_center, "project": row.project, "original_amount": Decimal(str(row.amount or 0)), "consumed_amount": Decimal("0"), "remaining_amount": Decimal(str(row.amount or 0)), "expected_date": row.expected_date, "status": "Open"})
    return rows


def get_precommitments(company: str, account: str | None = None, cost_center=None, project=None, as_of_date=None, include_material_requests: bool = False) -> list[dict]:
    if not include_material_requests:
        return []
    rows = []
    for row in get_material_request_precommitments(company, account, cost_center, project, as_of_date):
        amount = Decimal(str(row.remaining_amount or 0))
        if amount > 0:
            rows.append({"commitment_type": "Pre-Commitment", "source_doctype": "Material Request", "source_document": row.material_request, "source_line": row.source_line, "account": row.account, "cost_center": row.cost_center, "project": row.project, "original_amount": Decimal(str(row.original_amount or 0)), "consumed_amount": Decimal(str(row.consumed_amount or 0)), "remaining_amount": amount, "expected_date": row.expected_date, "status": row.status})
    return rows


def summarize_commitments(rows: list[dict]) -> Decimal:
    return sum(Decimal(str(row.get("remaining_amount") or 0)) for row in rows)


def refresh_commitments(company: str, fiscal_year=None) -> dict:
    # Dynamic calculation is authoritative; persistent snapshots are refreshed idempotently for audit/performance.
    existing = { (row.source_doctype, row.source_document, row.source_line): row.name for row in frappe.get_all("Budget Commitment", filters={"company": company}, fields=["name", "source_doctype", "source_document", "source_line"]) }
    refreshed = 0
    for row in get_open_commitments(company):
        key = (row["source_doctype"], row["source_document"], row.get("source_line"))
        doc = frappe.get_doc("Budget Commitment", existing[key]) if key in existing else frappe.new_doc("Budget Commitment")
        doc.update({"company": company, "commitment_type": row["commitment_type"], "source_doctype": row["source_doctype"], "source_document": row["source_document"], "source_line": row.get("source_line"), "account": row["account"], "cost_center": row.get("cost_center"), "project": row.get("project"), "original_amount": row["original_amount"], "consumed_amount": row["consumed_amount"], "remaining_amount": row["remaining_amount"], "expected_date": row.get("expected_date"), "status": row.get("status") or "Open"})
        doc.save() if key in existing else doc.insert()
        refreshed += 1
    return {"refreshed": refreshed}
