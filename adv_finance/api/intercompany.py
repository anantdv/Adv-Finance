import frappe

from adv_finance.services.intercompany.close_service import get_intercompany_close_readiness
from adv_finance.services.intercompany.elimination_service import prepare_elimination_candidate
from adv_finance.services.intercompany.matching_service import approve_match as approve_match_service, refresh_intercompany_transactions, suggest_invoice_matches
from adv_finance.services.intercompany.reconciliation_service import reconcile_due_to_due_from
from adv_finance.services.intercompany.settlement_service import mark_settlement_complete as mark_settlement_complete_service


@frappe.whitelist()
def refresh_transactions(company=None, from_date=None, to_date=None):
    if company:
        frappe.has_permission("Company", "read", company, throw=True)
    return refresh_intercompany_transactions(company, from_date, to_date)


@frappe.whitelist()
def suggest_matches(origin_company, destination_company, from_date=None, to_date=None):
    frappe.has_permission("Company", "read", origin_company, throw=True)
    frappe.has_permission("Company", "read", destination_company, throw=True)
    return suggest_invoice_matches(origin_company, destination_company, from_date, to_date)


@frappe.whitelist()
def approve_match(name):
    doc = frappe.get_doc("Intercompany Match", name)
    doc.check_permission("write")
    return approve_match_service(name)


@frappe.whitelist()
def mark_settlement_complete(name, payment_entry=None):
    doc = frappe.get_doc("Intercompany Settlement", name)
    doc.check_permission("write")
    return mark_settlement_complete_service(name, payment_entry)


@frappe.whitelist()
def due_to_due_from(origin_company, destination_company, as_of_date=None):
    frappe.has_permission("Company", "read", origin_company, throw=True)
    frappe.has_permission("Company", "read", destination_company, throw=True)
    return reconcile_due_to_due_from(origin_company, destination_company, as_of_date)


@frappe.whitelist()
def create_elimination_candidate(transaction=None, match=None):
    if transaction:
        doc = frappe.get_doc("Intercompany Transaction", transaction)
        doc.check_permission("read")
        return prepare_elimination_candidate(transaction=doc)
    doc = frappe.get_doc("Intercompany Match", match)
    doc.check_permission("read")
    return prepare_elimination_candidate(match=doc)


@frappe.whitelist()
def close_readiness(company=None, period_end=None):
    if company:
        frappe.has_permission("Company", "read", company, throw=True)
    return get_intercompany_close_readiness(company, period_end)
