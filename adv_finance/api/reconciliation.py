from __future__ import annotations

import frappe

from adv_finance.services import reconciliation_service


def _assert_can_write(name: str):
    doc = frappe.get_doc("Supplier Reconciliation", name)
    doc.check_permission("write")
    return doc


@frappe.whitelist()
def parse_statement(name: str | None = None, force: bool = False):
    doc = _assert_can_write(name or frappe.form_dict.get("docname"))
    return reconciliation_service.parse_statement(doc.name, force=frappe.utils.cint(force))


@frappe.whitelist()
def refresh_erp_ledger(name: str | None = None):
    doc = _assert_can_write(name or frappe.form_dict.get("docname"))
    return reconciliation_service.refresh_erp_ledger(doc.name)


@frappe.whitelist()
def run_matching(name: str | None = None):
    doc = _assert_can_write(name or frappe.form_dict.get("docname"))
    return reconciliation_service.run_matching(doc.name)


@frappe.whitelist()
def generate_exceptions(name: str | None = None):
    doc = _assert_can_write(name or frappe.form_dict.get("docname"))
    return reconciliation_service.generate_exceptions(doc.name)


@frappe.whitelist()
def run_reconciliation(name: str | None = None):
    doc = _assert_can_write(name or frappe.form_dict.get("docname"))
    return reconciliation_service.run_reconciliation(doc.name)


@frappe.whitelist()
def close_reconciliation(name: str | None = None):
    doc = _assert_can_write(name or frappe.form_dict.get("docname"))
    return reconciliation_service.close_reconciliation(doc.name)


@frappe.whitelist()
def reopen_reconciliation(name: str | None = None):
    doc = _assert_can_write(name or frappe.form_dict.get("docname"))
    return reconciliation_service.reopen_reconciliation(doc.name)
