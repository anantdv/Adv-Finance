from __future__ import annotations

import frappe

from adv_finance.services.accrual import (
    accrual_exception_service,
    accrual_matching_service,
    accrual_posting_service,
    accrual_reversal_service,
    accrual_service,
)


def _assert_write(name: str):
    doc = frappe.get_doc("Accrual", name)
    doc.check_permission("write")
    return doc


@frappe.whitelist()
def submit_for_review(name: str):
    _assert_write(name)
    return accrual_service.submit_for_review(name)


@frappe.whitelist()
def approve_accrual(name: str):
    _assert_write(name)
    return accrual_service.approve_accrual(name)


@frappe.whitelist()
def create_accrual_journal_entry(name: str):
    _assert_write(name)
    return accrual_posting_service.create_accrual_journal_entry(name)


@frappe.whitelist()
def create_reversal_journal_entry(name: str):
    _assert_write(name)
    return accrual_reversal_service.create_reversal_journal_entry(name)


@frappe.whitelist()
def refresh_accrual_status(name: str):
    _assert_write(name)
    return accrual_service.refresh_accrual_status(name)


@frappe.whitelist()
def suggest_purchase_invoice_matches(name: str):
    _assert_write(name)
    return accrual_matching_service.suggest_purchase_invoice_matches(name)


@frappe.whitelist()
def refresh_accrual_exceptions(name: str):
    _assert_write(name)
    return accrual_exception_service.refresh_accrual_exceptions(name)


@frappe.whitelist()
def close_accrual(name: str):
    _assert_write(name)
    return accrual_service.close_accrual(name)


@frappe.whitelist()
def reopen_accrual(name: str, reason: str):
    _assert_write(name)
    return accrual_service.reopen_accrual(name, reason)
