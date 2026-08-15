from __future__ import annotations

import frappe


def get_partner(origin_company: str, destination_company: str):
    name = frappe.db.get_value("Intercompany Partner", {"company": origin_company, "partner_company": destination_company, "active": 1}, "name")
    return frappe.get_doc("Intercompany Partner", name) if name else None


def validate_partner(partner) -> None:
    if partner.company == partner.partner_company:
        frappe.throw("Company and Partner Company cannot be the same.")
    for field in ("receivable_account", "payable_account", "settlement_account"):
        account = partner.get(field)
        if not account:
            continue
        company = frappe.db.get_value("Account", account, "company")
        if company and company not in (partner.company, partner.partner_company):
            frappe.throw(f"Account {account} must belong to one of the configured companies.")
