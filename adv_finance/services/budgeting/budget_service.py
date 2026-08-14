from __future__ import annotations

from decimal import Decimal

import frappe
from frappe.utils import now_datetime


def recalculate_budget_plan(plan) -> None:
    income = expense = capex = Decimal("0")
    for line in getattr(plan, "lines", []):
        amount = Decimal(str(line.annual_budget or 0))
        line.company_currency_amount = amount * Decimal(str(line.exchange_rate or 1))
        if line.account and not getattr(line, "account_name", None):
            line.account_name = frappe.db.get_value("Account", line.account, "account_name")
        typ = (line.account_type or "Expense").lower()
        if typ == "income":
            income += Decimal(str(line.company_currency_amount or 0))
        elif typ in ("asset", "capex"):
            capex += Decimal(str(line.company_currency_amount or 0))
        else:
            expense += Decimal(str(line.company_currency_amount or 0))
    plan.total_income_budget = income
    plan.total_expense_budget = expense
    plan.total_capex_budget = capex
    plan.net_budget = income - expense - capex


def approve_budget_plan(name: str) -> dict:
    doc = frappe.get_doc("Budget Plan", name)
    if doc.status not in ("Submitted", "Under Review"):
        frappe.throw("Only Submitted or Under Review budget plans can be approved.")
    if doc.prepared_by == frappe.session.user and not frappe.has_role("System Manager"):
        frappe.throw("Budget preparer cannot approve the same budget plan.")
    doc.status = "Approved"
    doc.version_type = "Approved"
    doc.approver = frappe.session.user
    doc.approved_on = now_datetime()
    doc.save()
    return {"status": doc.status}


def create_reforecast(source_name: str, reason: str | None = None) -> dict:
    source = frappe.get_doc("Budget Plan", source_name)
    if source.status != "Approved":
        frappe.throw("Only Approved budget plans can be copied into a reforecast.")
    new_doc = frappe.copy_doc(source)
    new_doc.status = "Draft"
    new_doc.version_type = "Reforecast"
    new_doc.version_number = int(source.version_number or 1) + 1
    new_doc.created_from = source.name
    new_doc.supersedes = source.name
    new_doc.change_reason = reason
    new_doc.approver = None
    new_doc.approved_on = None
    new_doc.insert()
    source.db_set("superseded_by", new_doc.name)
    return {"budget_plan": new_doc.name}


def publish_to_erpnext_budget(name: str) -> dict:
    from adv_finance.compatibility.erpnext_v16 import create_draft_erpnext_budget_from_plan

    doc = frappe.get_doc("Budget Plan", name)
    if doc.status != "Approved":
        frappe.throw("Only Approved budget plans can be published to ERPNext Budget.")
    budget = create_draft_erpnext_budget_from_plan(doc)
    doc.db_set("published_erpnext_budget", budget.name)
    return {"budget": budget.name}
