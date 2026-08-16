from __future__ import annotations

import frappe


def validate_group(group) -> None:
    if getattr(group, "parent_consolidation_group", None) and group.parent_consolidation_group == getattr(group, "name", None):
        frappe.throw("Parent Consolidation Group cannot be the same group.")
    companies = set()
    for row in group.companies:
        if row.company in companies:
            frappe.throw(f"Company {row.company} is duplicated in the consolidation group.")
        companies.add(row.company)
        if row.ownership_percent < 0 or row.ownership_percent > 100:
            frappe.throw("Ownership percent must be between 0 and 100.")
        if not row.reporting_currency:
            row.reporting_currency = group.reporting_currency


def get_group_companies(consolidation_group: str) -> list:
    group = frappe.get_doc("Consolidation Group", consolidation_group)
    return [row for row in group.companies if row.active and row.consolidation_method != "Not Consolidated"]
