from __future__ import annotations

import frappe

from adv_finance.services.account_reconciliation import reconciliation_service


def _assert_write(doctype: str, name: str):
    doc = frappe.get_doc(doctype, name)
    doc.check_permission("write")
    return doc


@frappe.whitelist()
def load_gl_balance(name: str):
    _assert_write("Account Reconciliation", name)
    return reconciliation_service.load_gl_balance(name)


@frappe.whitelist()
def load_supporting_balance(name: str):
    _assert_write("Account Reconciliation", name)
    return reconciliation_service.load_supporting_balance(name)


@frappe.whitelist()
def submit_for_review(name: str):
    _assert_write("Account Reconciliation", name)
    return reconciliation_service.submit_for_review(name)


@frappe.whitelist()
def review_reconciliation(name: str, comments: str | None = None):
    _assert_write("Account Reconciliation", name)
    return reconciliation_service.review_reconciliation(name, approve=True, comments=comments)


@frappe.whitelist()
def reject_reconciliation(name: str, comments: str | None = None):
    _assert_write("Account Reconciliation", name)
    return reconciliation_service.review_reconciliation(name, approve=False, comments=comments)


@frappe.whitelist()
def approve_reconciliation(name: str, comments: str | None = None):
    _assert_write("Account Reconciliation", name)
    return reconciliation_service.approve_reconciliation(name, comments=comments)


@frappe.whitelist()
def close_reconciliation(name: str):
    _assert_write("Account Reconciliation", name)
    return reconciliation_service.close_reconciliation(name)


@frappe.whitelist()
def reopen_reconciliation(name: str, reason: str):
    _assert_write("Account Reconciliation", name)
    return reconciliation_service.reopen_reconciliation(name, reason)


@frappe.whitelist()
def generate_reconciliations(name: str):
    _assert_write("Account Reconciliation Period", name)
    return reconciliation_service.generate_reconciliations(name)
