from __future__ import annotations

import frappe

from adv_finance.services.financial_close import close_generation_service, close_service, late_posting_service, period_closing_service, readiness_service, task_service


def _assert_period_write(name: str):
    doc = frappe.get_doc("Financial Close Period", name)
    doc.check_permission("write")
    return doc


def _assert_task_write(name: str):
    doc = frappe.get_doc("Financial Close Task", name)
    doc.check_permission("write")
    return doc


@frappe.whitelist()
def create_close_period(company: str, template: str, period_start, period_end):
    return close_generation_service.create_close_period(company, template, period_start, period_end)


@frappe.whitelist()
def refresh_close_readiness(name: str):
    _assert_period_write(name)
    return readiness_service.refresh_close_readiness(name)


@frappe.whitelist()
def submit_for_review(name: str):
    _assert_period_write(name)
    return close_service.submit_for_review(name)


@frappe.whitelist()
def start_review(name: str):
    _assert_period_write(name)
    return close_service.start_review(name)


@frappe.whitelist()
def approve_for_close(name: str):
    _assert_period_write(name)
    return close_service.approve_for_close(name)


@frappe.whitelist()
def certify_close(name: str, statement: str | None = None):
    _assert_period_write(name)
    return close_service.certify_close(name, statement)


@frappe.whitelist()
def close_period(name: str):
    _assert_period_write(name)
    return close_service.close_period(name)


@frappe.whitelist()
def reopen_close(name: str, reason: str):
    _assert_period_write(name)
    return close_service.reopen_close(name, reason)


@frappe.whitelist()
def create_period_closing_voucher(name: str):
    _assert_period_write(name)
    return period_closing_service.create_period_closing_voucher(name)


@frappe.whitelist()
def refresh_period_closing_voucher_status(name: str):
    _assert_period_write(name)
    return period_closing_service.refresh_period_closing_voucher_status(name)


@frappe.whitelist()
def scan_late_postings(name: str):
    _assert_period_write(name)
    return late_posting_service.scan_late_postings(name)


@frappe.whitelist()
def start_task(name: str):
    _assert_task_write(name)
    return task_service.start_task(name)


@frappe.whitelist()
def complete_task(name: str, notes: str | None = None):
    _assert_task_write(name)
    return task_service.complete_task(name, notes)


@frappe.whitelist()
def submit_task_for_review(name: str, notes: str | None = None):
    _assert_task_write(name)
    return task_service.submit_task_for_review(name, notes)


@frappe.whitelist()
def review_task(name: str, approve: bool = True, notes: str | None = None):
    _assert_task_write(name)
    return task_service.review_task(name, approve, notes)


@frappe.whitelist()
def waive_task(name: str, reason: str):
    _assert_task_write(name)
    return task_service.waive_task(name, reason)


@frappe.whitelist()
def refresh_task_readiness(name: str):
    _assert_task_write(name)
    return readiness_service.refresh_task_readiness(name)
