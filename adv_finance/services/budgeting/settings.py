from __future__ import annotations

import frappe

DEFAULTS = {"commitment_accounting_enabled": True, "include_material_request_precommitments": False, "include_purchase_orders": True, "include_manual_commitments": True, "include_budget_reservations": True, "enforce_available_budget": False, "allow_budget_override": True, "default_warning_percent": 80, "default_block_percent": 100, "rolling_forecast_months": 12, "default_forecast_method": "Manual"}


def get_budget_settings(company: str) -> dict:
    if frappe.db.exists("Budget Settings", company):
        doc = frappe.get_doc("Budget Settings", company)
        return {key: doc.get(key) for key in DEFAULTS} | {key: bool(doc.get(key)) for key in ("commitment_accounting_enabled", "include_material_request_precommitments", "include_purchase_orders", "include_manual_commitments", "include_budget_reservations", "enforce_available_budget", "allow_budget_override")}
    return DEFAULTS.copy()
