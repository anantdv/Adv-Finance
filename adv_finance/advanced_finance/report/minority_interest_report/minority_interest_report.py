from __future__ import annotations

import frappe


def execute(filters=None):
    period = (filters or {}).get("consolidation_period")
    columns = ["Company:Link/Company:160", "Account:Link/Account:180", "Root Type:Data:110", "Ownership %:Percent:120", "Minority Interest:Currency:160", "Final Amount:Currency:140"]
    if not period:
        return columns, []
    rows = frappe.get_all("Consolidated Trial Balance Line", filters={"consolidation_period": period, "minority_interest_amount": [">", 0]}, fields=["company", "account", "root_type", "ownership_percent", "minority_interest_amount", "final_amount"], order_by="company, account")
    return columns, [[r.company, r.account, r.root_type, r.ownership_percent, r.minority_interest_amount, r.final_amount] for r in rows]
