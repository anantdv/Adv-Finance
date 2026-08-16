from __future__ import annotations

import frappe


def execute(filters=None):
    group = (filters or {}).get("consolidation_group")
    columns = ["Group:Link/Consolidation Group:180", "Company:Link/Company:180", "Ownership %:Percent:120", "Method:Data:160", "Functional Currency:Link/Currency:130", "Reporting Currency:Link/Currency:130", "Active:Check:80"]
    if not group:
        return columns, []
    doc = frappe.get_doc("Consolidation Group", group)
    return columns, [[doc.name, r.company, r.ownership_percent, r.consolidation_method, r.functional_currency, r.reporting_currency, r.active] for r in doc.companies]
