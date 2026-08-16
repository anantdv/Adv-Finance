from __future__ import annotations

from collections import defaultdict
from decimal import Decimal

import frappe

from adv_finance.services.consolidation.elimination_service import generate_elimination_journals
from adv_finance.services.consolidation.group_service import get_group_companies
from adv_finance.services.consolidation.ownership_service import apply_ownership
from adv_finance.services.consolidation.snapshot_service import collect_trial_balance_snapshot


def run_consolidation(consolidation_period: str, force: bool = False) -> dict:
    period = frappe.get_doc("Consolidation Period", consolidation_period)
    collect_trial_balance_snapshot(period.name, force=force)
    generate_elimination_journals(period.name)
    result = generate_consolidated_trial_balance(period.name, force=force)
    period.status = "Consolidating"
    period.consolidation_progress = 100
    period.group_profit = result["profit_loss"]
    period.group_cash = result["cash"]
    period.minority_interest = result["minority_interest"]
    period.save()
    return result


def generate_consolidated_trial_balance(consolidation_period: str, force: bool = False) -> dict:
    period = frappe.get_doc("Consolidation Period", consolidation_period)
    if period.status in ("Approved", "Published", "Closed") and force:
        frappe.throw("Approved, Published, and Closed consolidation periods are immutable.")
    existing = frappe.get_all("Consolidated Trial Balance Line", filters={"consolidation_period": period.name}, fields=["name"])
    if force:
        for row in existing:
            frappe.delete_doc("Consolidated Trial Balance Line", row.name, ignore_permissions=True)
    company_config = {row.company: row for row in get_group_companies(period.consolidation_group)}
    eliminations = _eliminations_by_account(period.name)
    adjustments = _adjustments_by_account(period.name)
    totals = defaultdict(Decimal)
    profit_loss = Decimal("0")
    cash = Decimal("0")
    minority_total = Decimal("0")
    snapshots = frappe.get_all("Trial Balance Snapshot", filters={"consolidation_period": period.name}, fields=["company", "account", "account_name", "root_type", "translated_amount", "translation_difference", "currency"])
    for row in snapshots:
        cfg = company_config.get(row.company)
        if not cfg:
            continue
        owned = apply_ownership(row.translated_amount, cfg.ownership_percent, cfg.consolidation_method)
        elimination = eliminations.get(row.account, Decimal("0"))
        adjustment = adjustments.get(row.account, Decimal("0"))
        final = Decimal(str(owned["owned_amount"])) + adjustment - elimination
        minority = owned["minority_interest_amount"]
        doc = frappe.new_doc("Consolidated Trial Balance Line")
        doc.update({"consolidation_period": period.name, "consolidation_group": period.consolidation_group, "company": row.company, "parent": period.consolidation_group, "account": row.account, "account_name": row.account_name, "root_type": row.root_type, "company_total": row.translated_amount, "ownership_percent": owned["ownership_percent"], "owned_amount": owned["owned_amount"], "translation_amount": row.translation_difference, "elimination_amount": elimination, "adjustment_amount": adjustment, "minority_interest_amount": minority, "final_amount": final, "currency": row.currency})
        doc.insert(ignore_permissions=True)
        totals[row.root_type] += final
        minority_total += minority
        if row.root_type in ("Income", "Expense"):
            profit_loss += final if row.root_type == "Income" else -final
        if "cash" in (row.account_name or "").lower():
            cash += final
    return {"lines": len(snapshots), "totals": dict(totals), "profit_loss": profit_loss, "cash": cash, "minority_interest": minority_total}


def _eliminations_by_account(period_name: str) -> dict:
    rows = frappe.get_all("Elimination Journal", filters={"consolidation_period": period_name, "status": ["in", ["Generated", "Approved"]]}, fields=["debit_account", "credit_account", "amount"])
    result = defaultdict(Decimal)
    for row in rows:
        if row.debit_account:
            result[row.debit_account] += Decimal(str(row.amount or 0))
        if row.credit_account:
            result[row.credit_account] += Decimal(str(row.amount or 0))
    return result


def _adjustments_by_account(period_name: str) -> dict:
    rows = frappe.get_all("Consolidation Adjustment", filters={"consolidation_period": period_name, "status": "Approved"}, fields=["account", "amount"])
    result = defaultdict(Decimal)
    for row in rows:
        result[row.account] += Decimal(str(row.amount or 0))
    return result
