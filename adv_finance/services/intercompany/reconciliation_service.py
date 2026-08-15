from __future__ import annotations

from decimal import Decimal

from adv_finance.compatibility.erpnext_v16 import get_due_to_due_from_balances


def reconcile_due_to_due_from(origin_company: str, destination_company: str, as_of_date=None) -> dict:
    balances = get_due_to_due_from_balances(origin_company, destination_company, as_of_date)
    due_from = Decimal(str(balances.get("due_from") or 0))
    due_to = Decimal(str(balances.get("due_to") or 0))
    difference = due_from - abs(due_to)
    return {"origin_company": origin_company, "destination_company": destination_company, "due_from": due_from, "due_to": due_to, "difference": difference, "status": "Matched" if difference == 0 else "Difference"}
