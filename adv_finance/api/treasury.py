import frappe

from adv_finance.services.treasury.cash_forecast_service import approve_forecast, create_forecast_version, generate_cash_forecast, review_forecast
from adv_finance.services.treasury.cash_position_service import get_cash_position
from adv_finance.services.treasury.forecast_accuracy_service import get_forecast_accuracy
from adv_finance.services.treasury.liquidity_driver_service import get_liquidity_drivers


@frappe.whitelist()
def cash_position(company, as_of_date, scenario=None, treasury_group=None):
    frappe.has_permission("Company", "read", company, throw=True)
    return get_cash_position(company, as_of_date, scenario, treasury_group)


@frappe.whitelist()
def generate_forecast(name, force=False):
    doc = frappe.get_doc("Cash Forecast", name)
    doc.check_permission("write")
    return generate_cash_forecast(name, force=bool(int(force)) if isinstance(force, str) else bool(force))


@frappe.whitelist()
def review_cash_forecast(name):
    doc = frappe.get_doc("Cash Forecast", name)
    doc.check_permission("write")
    return review_forecast(name)


@frappe.whitelist()
def approve_cash_forecast(name):
    doc = frappe.get_doc("Cash Forecast", name)
    doc.check_permission("write")
    return approve_forecast(name)


@frappe.whitelist()
def new_forecast_version(name, reason=None):
    doc = frappe.get_doc("Cash Forecast", name)
    doc.check_permission("read")
    return create_forecast_version(name, reason)


@frappe.whitelist()
def liquidity_drivers(name, start_date=None, end_date=None):
    doc = frappe.get_doc("Cash Forecast", name)
    doc.check_permission("read")
    return get_liquidity_drivers(name, start_date, end_date)


@frappe.whitelist()
def forecast_accuracy(name):
    doc = frappe.get_doc("Cash Forecast", name)
    doc.check_permission("read")
    return get_forecast_accuracy(name)
