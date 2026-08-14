from __future__ import annotations

import frappe

from adv_finance.services.accounts_receivable import collection_case_service, credit_hold_service, credit_override_service, credit_review_service, dispute_service, promise_fulfilment_service, promise_service


def _assert_write(doctype: str, name: str):
    doc = frappe.get_doc(doctype, name)
    doc.check_permission("write")
    return doc


@frappe.whitelist()
def create_collection_case(company: str, customer: str, collector: str | None = None):
    return collection_case_service.create_collection_case(company, customer, collector)


@frappe.whitelist()
def refresh_collection_case(name: str):
    doc = _assert_write("Collection Case", name)
    return collection_case_service.refresh_collection_case(doc)


@frappe.whitelist()
def generate_collection_cases(company: str, as_of_date=None, minimum_overdue_amount=0):
    return collection_case_service.generate_collection_cases(company, as_of_date, minimum_overdue_amount)


@frappe.whitelist()
def activate_promise(name: str):
    _assert_write("Promise to Pay", name)
    return promise_service.activate_promise(name)


@frappe.whitelist()
def refresh_promise_fulfilment(name: str):
    _assert_write("Promise to Pay", name)
    return promise_fulfilment_service.refresh_promise_fulfilment(name)


@frappe.whitelist()
def reschedule_promise(name: str, promised_payment_date, promised_amount=None, reason: str | None = None):
    _assert_write("Promise to Pay", name)
    return promise_service.reschedule_promise(name, promised_payment_date, promised_amount, reason)


@frappe.whitelist()
def create_dispute_credit_note(name: str):
    _assert_write("Customer Dispute", name)
    return dispute_service.create_credit_note(name)


@frappe.whitelist()
def refresh_credit_review(name: str):
    doc = _assert_write("Credit Review", name)
    return credit_review_service.refresh_credit_review(doc)


@frappe.whitelist()
def submit_credit_review(name: str):
    _assert_write("Credit Review", name)
    return credit_review_service.submit_review(name)


@frappe.whitelist()
def approve_credit_review(name: str):
    _assert_write("Credit Review", name)
    return credit_review_service.approve_review(name)


@frappe.whitelist()
def release_credit_hold(name: str, reason: str):
    _assert_write("Credit Hold", name)
    return credit_hold_service.release_credit_hold(name, reason)


@frappe.whitelist()
def approve_credit_override(name: str, valid_days: int = 7, notes: str | None = None):
    _assert_write("Credit Override Request", name)
    return credit_override_service.approve_override(name, valid_days, notes)


@frappe.whitelist()
def mark_credit_override_used(name: str):
    _assert_write("Credit Override Request", name)
    return credit_override_service.mark_override_used(name)
