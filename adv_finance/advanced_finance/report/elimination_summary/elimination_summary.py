from __future__ import annotations

import frappe


def execute(filters=None):
    period = (filters or {}).get("consolidation_period")
    columns = ["Elimination:Link/Elimination Journal:180", "Source Companies:Data:180", "Debit Account:Link/Account:180", "Credit Account:Link/Account:180", "Amount:Currency:140", "Currency:Link/Currency:100", "Status:Data:110", "Reason:Data:240"]
    if not period:
        return columns, []
    rows = frappe.get_all("Elimination Journal", filters={"consolidation_period": period}, fields=["name", "source_companies", "debit_account", "credit_account", "amount", "currency", "status", "reason"], order_by="modified desc")
    return columns, [[r.name, r.source_companies, r.debit_account, r.credit_account, r.amount, r.currency, r.status, r.reason] for r in rows]
