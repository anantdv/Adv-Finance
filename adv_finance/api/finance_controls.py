from __future__ import annotations

import frappe

from adv_finance.services.finance_controls.demand_letter_service import generate_demand_letter
from adv_finance.services.finance_controls.eft_service import send_remittance_advice
from adv_finance.services.finance_controls.prior_period_service import approve_prior_period_request
from adv_finance.services.finance_controls.supplier_master_service import approve_supplier_change, approve_supplier_onboarding, create_supplier_from_onboarding, verify_supplier_change


@frappe.whitelist()
def create_demand_letter(**kwargs):
    return generate_demand_letter(**kwargs).name


@frappe.whitelist()
def send_remittance(payment_entry, recipients=None):
    return send_remittance_advice(payment_entry, recipients=frappe.parse_json(recipients) if isinstance(recipients, str) else recipients)


@frappe.whitelist()
def approve_prior_period(name, valid_from=None, valid_until=None):
    return approve_prior_period_request(name, valid_from, valid_until)


@frappe.whitelist()
def approve_supplier_onboarding_request(name):
    return approve_supplier_onboarding(name)


@frappe.whitelist()
def create_supplier_from_request(name):
    return create_supplier_from_onboarding(name).name


@frappe.whitelist()
def verify_supplier_change_request(name, method=None, notes=None):
    return verify_supplier_change(name, method, notes)


@frappe.whitelist()
def approve_supplier_change_request(name):
    return approve_supplier_change(name)
