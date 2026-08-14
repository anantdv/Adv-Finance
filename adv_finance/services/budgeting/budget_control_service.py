from __future__ import annotations

from decimal import Decimal

import frappe

from adv_finance.services.budgeting.available_budget_service import get_available_budget
from adv_finance.services.budgeting.override_service import find_valid_override


def get_budget_control_rule(company: str, source_doctype: str, account: str, cost_center=None, project=None):
    filters = {"company": company, "applies_to": source_doctype, "active": 1}
    rules = frappe.get_all("Budget Control Rule", filters=filters, fields=["name", "account", "cost_center", "project", "control_basis", "warning_threshold_percent", "block_threshold_percent", "control_level", "allow_override", "override_role"], order_by="modified desc")
    for rule in rules:
        if rule.account and rule.account != account:
            continue
        if rule.cost_center and rule.cost_center != cost_center:
            continue
        if rule.project and rule.project != project:
            continue
        return rule
    return None


def validate_budget_availability(company: str, account: str, amount, source_doctype: str, source_document: str, cost_center=None, project=None, dimensions=None, as_of_date=None) -> dict:
    requested = Decimal(str(amount or 0))
    available = get_available_budget(company, account, cost_center, project, dimensions, as_of_date)
    projected = Decimal(str(available["consumed"] or 0)) + requested
    shortfall = max(requested - Decimal(str(available["available_budget"] or 0)), Decimal("0"))
    rule = get_budget_control_rule(company, source_doctype, account, cost_center, project)
    warning = Decimal(str(getattr(rule, "warning_threshold_percent", 80) if rule else 80))
    block = Decimal(str(getattr(rule, "block_threshold_percent", 100) if rule else 100))
    effective = Decimal(str(available["effective_budget"] or 0))
    projected_pct = (projected / effective * Decimal("100")) if effective else Decimal("0")
    level = "Normal"
    allowed = True
    if projected_pct >= block or shortfall > 0:
        level = "Blocking" if getattr(rule, "control_level", "Warning") == "Blocking" else "Warning"
        allowed = level != "Blocking"
    elif projected_pct >= warning:
        level = "Warning"
    override = find_valid_override(company, source_doctype, source_document, account, requested)
    if override:
        allowed = True
    return {**available, "allowed": allowed, "control_level": level, "new_commitment": requested, "projected_consumption": projected, "available_before": available["available_budget"], "shortfall": shortfall, "override_allowed": bool(getattr(rule, "allow_override", True) if rule else True), "override": getattr(override, "name", None) if override else None, "projected_consumption_percent": projected_pct}
