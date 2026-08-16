import frappe

from adv_finance.services.consolidation.adjustment_service import approve_adjustment as approve_adjustment_service
from adv_finance.services.consolidation.close_service import advance_period_status, get_consolidation_close_readiness
from adv_finance.services.consolidation.consolidation_service import run_consolidation as run_consolidation_service
from adv_finance.services.consolidation.elimination_service import approve_elimination_journal as approve_elimination_journal_service, generate_elimination_journals
from adv_finance.services.consolidation.ratio_service import group_ratios
from adv_finance.services.consolidation.report_service import balance_sheet, cash_flow, consolidated_trial_balance, dashboard, profit_loss
from adv_finance.services.consolidation.snapshot_service import collect_trial_balance_snapshot


@frappe.whitelist()
def collect_trial_balance(name, force=False):
    doc = frappe.get_doc("Consolidation Period", name)
    doc.check_permission("write")
    return collect_trial_balance_snapshot(name, force=bool(int(force)) if isinstance(force, str) else bool(force))


@frappe.whitelist()
def generate_eliminations(name):
    doc = frappe.get_doc("Consolidation Period", name)
    doc.check_permission("write")
    return generate_elimination_journals(name)


@frappe.whitelist()
def run_consolidation(name, force=False):
    doc = frappe.get_doc("Consolidation Period", name)
    doc.check_permission("write")
    return run_consolidation_service(name, force=bool(int(force)) if isinstance(force, str) else bool(force))


@frappe.whitelist()
def approve_adjustment(name):
    doc = frappe.get_doc("Consolidation Adjustment", name)
    doc.check_permission("write")
    return approve_adjustment_service(name)


@frappe.whitelist()
def approve_elimination_journal(name):
    doc = frappe.get_doc("Elimination Journal", name)
    doc.check_permission("write")
    return approve_elimination_journal_service(name)


@frappe.whitelist()
def set_period_status(name, status):
    doc = frappe.get_doc("Consolidation Period", name)
    doc.check_permission("write")
    return advance_period_status(name, status)


@frappe.whitelist()
def close_readiness(name):
    doc = frappe.get_doc("Consolidation Period", name)
    doc.check_permission("read")
    return get_consolidation_close_readiness(name)


@frappe.whitelist()
def report_trial_balance(name):
    return consolidated_trial_balance(name)


@frappe.whitelist()
def report_balance_sheet(name):
    return balance_sheet(name)


@frappe.whitelist()
def report_profit_loss(name):
    return profit_loss(name)


@frappe.whitelist()
def report_cash_flow(name):
    return cash_flow(name)


@frappe.whitelist()
def report_ratios(name):
    return group_ratios(name)


@frappe.whitelist()
def report_dashboard(name):
    return dashboard(name)
