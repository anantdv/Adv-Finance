from __future__ import annotations

import frappe

from adv_finance.services.financial_close.providers.base import CloseReadinessProvider

class InventoryProvider(CloseReadinessProvider):
    provider_name = "inventory"

    def check(self, task, close_period):
        if not frappe.db.exists("DocType", "Stock Ledger Entry"):
            return {"ready": True, "status": "Completed", "message": "Stock Ledger is not available.", "exceptions": [], "details": {"installed": False}}
        negative = frappe.db.count("Stock Ledger Entry", {"company": close_period.company, "posting_date": ["<=", close_period.period_end], "qty_after_transaction": ["<", 0], "is_cancelled": 0})
        exceptions = []
        if negative:
            exceptions.append({"exception_type": "Negative Stock", "description": f"{negative} stock ledger row(s) show negative quantity."})
        return {"ready": negative == 0, "status": "Completed" if negative == 0 else "Blocked", "message": "Inventory readiness passed." if negative == 0 else f"{negative} negative stock row(s) require review.", "exceptions": exceptions, "details": {"negative_stock_rows": negative}}
