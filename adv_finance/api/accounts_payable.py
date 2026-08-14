from __future__ import annotations

import frappe

from adv_finance.services.accounts_payable import payment_proposal_service, payment_run_service


def _assert_write(doctype: str, name: str):
    doc = frappe.get_doc(doctype, name)
    doc.check_permission("write")
    return doc


@frappe.whitelist()
def generate_payment_proposal(name: str):
    _assert_write("Payment Proposal", name)
    return payment_proposal_service.generate_payment_proposal(name)


@frappe.whitelist()
def approve_payment_proposal(name: str):
    _assert_write("Payment Proposal", name)
    return payment_proposal_service.approve_payment_proposal(name)


@frappe.whitelist()
def create_payment_run_from_proposal(name: str):
    _assert_write("Payment Proposal", name)
    return payment_run_service.create_payment_run_from_proposal(name)


@frappe.whitelist()
def revalidate_payment_run(name: str):
    _assert_write("Payment Run", name)
    return payment_run_service.revalidate_payment_run(name)


@frappe.whitelist()
def create_draft_payment_entries(name: str):
    _assert_write("Payment Run", name)
    return payment_run_service.create_draft_payment_entries(name)
