from __future__ import annotations

from decimal import Decimal

import frappe

from adv_finance.services.budgeting.budget_actual_service import get_actual_spend
from adv_finance.services.budgeting.commitment_service import get_open_commitments, get_precommitments, summarize_commitments
from adv_finance.services.budgeting.settings import get_budget_settings


def get_approved_budget(company: str, account: str, cost_center=None, project=None, as_of_date=None) -> Decimal:
    filters = {"company": company, "status": "Approved"}
    plans = frappe.get_all("Budget Plan", filters=filters, fields=["name", "from_date", "to_date"], order_by="version_number desc, modified desc")
    for plan in plans:
        lines = frappe.get_all("Budget Plan Line", filters={"parent": plan.name, "account": account}, fields=["annual_budget", "cost_center", "project"])
        total = Decimal("0")
        for line in lines:
            if cost_center and line.cost_center != cost_center:
                continue
            if project and line.project != project:
                continue
            total += Decimal(str(line.annual_budget or 0))
        if total:
            return total
    return Decimal("0")


def get_supplements(company: str, account: str, cost_center=None, project=None, as_of_date=None) -> Decimal:
    rows = frappe.get_all("Budget Supplement", filters={"company": company, "account": account, "status": ["in", ["Approved", "Applied"]]}, fields=["amount", "cost_center", "project"])
    return sum(Decimal(str(r.amount or 0)) for r in rows if (not cost_center or r.cost_center == cost_center) and (not project or r.project == project))


def get_transfers(company: str, account: str, cost_center=None, project=None, as_of_date=None) -> tuple[Decimal, Decimal]:
    rows = frappe.get_all("Budget Transfer", filters={"company": company, "status": ["in", ["Approved", "Applied"]]}, fields=["amount", "from_account", "from_cost_center", "from_project", "to_account", "to_cost_center", "to_project"])
    tin = tout = Decimal("0")
    for r in rows:
        amount = Decimal(str(r.amount or 0))
        if r.to_account == account and (not cost_center or r.to_cost_center == cost_center) and (not project or r.to_project == project):
            tin += amount
        if r.from_account == account and (not cost_center or r.from_cost_center == cost_center) and (not project or r.from_project == project):
            tout += amount
    return tin, tout


def get_reservations(company: str, account: str, cost_center=None, project=None, as_of_date=None) -> Decimal:
    rows = frappe.get_all("Budget Reservation", filters={"company": company, "account": account, "status": ["in", ["Approved", "Partially Consumed"]]}, fields=["amount", "consumed_amount", "cost_center", "project"])
    return sum(max(Decimal(str(r.amount or 0)) - Decimal(str(r.consumed_amount or 0)), Decimal("0")) for r in rows if (not cost_center or r.cost_center == cost_center) and (not project or r.project == project))


def get_available_budget(company: str, account: str, cost_center=None, project=None, dimensions=None, as_of_date=None, from_date=None) -> dict:
    settings = get_budget_settings(company)
    approved = get_approved_budget(company, account, cost_center, project, as_of_date)
    supplements = get_supplements(company, account, cost_center, project, as_of_date)
    transfers_in, transfers_out = get_transfers(company, account, cost_center, project, as_of_date)
    effective = approved + supplements + transfers_in - transfers_out
    actual = get_actual_spend(company, account, from_date, as_of_date, cost_center, project, dimensions)
    commitments = summarize_commitments(get_open_commitments(company, account, cost_center, project, as_of_date)) if settings["include_purchase_orders"] or settings["include_manual_commitments"] else Decimal("0")
    pre = summarize_commitments(get_precommitments(company, account, cost_center, project, as_of_date, settings["include_material_request_precommitments"]))
    reservations = get_reservations(company, account, cost_center, project, as_of_date) if settings["include_budget_reservations"] else Decimal("0")
    available = effective - actual - commitments - pre - reservations
    consumed = actual + commitments
    pct = (consumed / effective * Decimal("100")) if effective else Decimal("0")
    return {"approved_budget": approved, "supplements": supplements, "transfers_in": transfers_in, "transfers_out": transfers_out, "effective_budget": effective, "actual": actual, "commitments": commitments, "pre_commitments": pre, "reservations": reservations, "available_budget": available, "consumed": consumed, "consumption_percent": pct}
