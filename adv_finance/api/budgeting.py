import frappe

from adv_finance.services.budgeting.available_budget_service import get_available_budget
from adv_finance.services.budgeting.budget_control_service import validate_budget_availability
from adv_finance.services.budgeting.budget_service import (
    approve_budget_plan as approve_budget_plan_service,
    create_reforecast as create_reforecast_service,
    publish_to_erpnext_budget,
)
from adv_finance.services.budgeting.commitment_service import refresh_commitments
from adv_finance.services.budgeting.forecast_service import calculate_budget_forecast, get_budget_cash_projection
from adv_finance.services.budgeting.override_service import approve_override, mark_override_used
from adv_finance.services.budgeting.supplement_service import approve_supplement
from adv_finance.services.budgeting.transfer_service import approve_transfer


@frappe.whitelist()
def available_budget(company, account, cost_center=None, project=None, as_of_date=None):
    frappe.has_permission("Company", "read", company, throw=True)
    return get_available_budget(company, account, cost_center, project, as_of_date=as_of_date)


@frappe.whitelist()
def validate_budget(company, account, amount, source_doctype, source_document, cost_center=None, project=None, as_of_date=None):
    frappe.has_permission("Company", "read", company, throw=True)
    return validate_budget_availability(company, account, amount, source_doctype, source_document, cost_center, project, as_of_date=as_of_date)


@frappe.whitelist()
def approve_budget_plan(name):
    doc = frappe.get_doc("Budget Plan", name)
    doc.check_permission("write")
    return approve_budget_plan_service(name)


@frappe.whitelist()
def create_reforecast(name, reason=None):
    doc = frappe.get_doc("Budget Plan", name)
    doc.check_permission("read")
    return create_reforecast_service(name, reason)


@frappe.whitelist()
def publish_budget_plan(name):
    doc = frappe.get_doc("Budget Plan", name)
    doc.check_permission("write")
    return publish_to_erpnext_budget(name)


@frappe.whitelist()
def approve_budget_transfer(name):
    doc = frappe.get_doc("Budget Transfer", name)
    doc.check_permission("write")
    return approve_transfer(name)


@frappe.whitelist()
def approve_budget_supplement(name):
    doc = frappe.get_doc("Budget Supplement", name)
    doc.check_permission("write")
    return approve_supplement(name)


@frappe.whitelist()
def approve_budget_override(name, notes=None):
    doc = frappe.get_doc("Budget Override Request", name)
    doc.check_permission("write")
    return approve_override(name, notes)


@frappe.whitelist()
def mark_budget_override_used(name):
    doc = frappe.get_doc("Budget Override Request", name)
    doc.check_permission("write")
    return mark_override_used(name)


@frappe.whitelist()
def refresh_budget_commitments(company, fiscal_year=None):
    frappe.has_permission("Company", "read", company, throw=True)
    return refresh_commitments(company, fiscal_year)


@frappe.whitelist()
def budget_forecast(company, account, cost_center=None, project=None, as_of_date=None, method="Actual + Open Commitments"):
    frappe.has_permission("Company", "read", company, throw=True)
    return calculate_budget_forecast(company, account, cost_center, project, as_of_date, method)


@frappe.whitelist()
def budget_cash_projection(company, from_date=None, to_date=None):
    frappe.has_permission("Company", "read", company, throw=True)
    return get_budget_cash_projection(company, from_date, to_date)
