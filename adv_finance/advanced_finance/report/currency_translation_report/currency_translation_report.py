from __future__ import annotations

import frappe


def execute(filters=None):
    period = (filters or {}).get("consolidation_period")
    columns = ["Company:Link/Company:160", "Account:Link/Account:180", "Root Type:Data:110", "Currency:Link/Currency:100", "Balance:Currency:140", "Rate:Float:100", "Translated:Currency:140", "Translation Difference:Currency:160"]
    if not period:
        return columns, []
    rows = frappe.get_all("Trial Balance Snapshot", filters={"consolidation_period": period}, fields=["company", "account", "root_type", "currency", "balance", "exchange_rate", "translated_amount", "translation_difference"], order_by="company, account")
    return columns, [[r.company, r.account, r.root_type, r.currency, r.balance, r.exchange_rate, r.translated_amount, r.translation_difference] for r in rows]
