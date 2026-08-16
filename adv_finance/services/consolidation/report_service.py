from __future__ import annotations

from collections import defaultdict
from decimal import Decimal

import frappe


def consolidated_trial_balance(period: str) -> list:
    return frappe.get_all("Consolidated Trial Balance Line", filters={"consolidation_period": period}, fields=["company", "account", "account_name", "root_type", "company_total", "translation_amount", "elimination_amount", "adjustment_amount", "minority_interest_amount", "final_amount", "currency"], order_by="root_type, account")


def balance_sheet(period: str) -> dict:
    rows = consolidated_trial_balance(period)
    totals = defaultdict(Decimal)
    for row in rows:
        if row.root_type in ("Asset", "Liability", "Equity"):
            totals[row.root_type] += Decimal(str(row.final_amount or 0))
    totals["Minority Interest"] = sum(Decimal(str(row.minority_interest_amount or 0)) for row in rows)
    return dict(totals)


def profit_loss(period: str) -> dict:
    rows = consolidated_trial_balance(period)
    revenue = sum(Decimal(str(row.final_amount or 0)) for row in rows if row.root_type == "Income")
    expense = sum(Decimal(str(row.final_amount or 0)) for row in rows if row.root_type == "Expense")
    return {"Revenue": revenue, "Operating Expense": expense, "Operating Profit": revenue - expense, "Net Profit": revenue - expense}


def cash_flow(period: str) -> dict:
    rows = consolidated_trial_balance(period)
    cash = sum(Decimal(str(row.final_amount or 0)) for row in rows if "cash" in (row.account_name or "").lower())
    profit = profit_loss(period)["Net Profit"]
    return {"Opening Cash": Decimal("0"), "Operating": profit, "Investing": Decimal("0"), "Financing": Decimal("0"), "FX Impact": Decimal("0"), "Closing Cash": cash}


def dashboard(period: str) -> dict:
    p = frappe.get_doc("Consolidation Period", period)
    adjustments = frappe.db.count("Consolidation Adjustment", {"consolidation_period": period})
    eliminations = frappe.db.count("Elimination Journal", {"consolidation_period": period})
    return {"companies_collected": p.companies_collected, "companies_pending": p.companies_pending, "translation_status": p.translation_status, "elimination_status": p.elimination_status, "adjustments": adjustments, "eliminations": eliminations, "consolidation_progress": p.consolidation_progress, "minority_interest": p.minority_interest, "group_profit": p.group_profit, "group_cash": p.group_cash}
