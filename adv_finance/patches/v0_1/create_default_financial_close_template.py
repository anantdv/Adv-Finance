from __future__ import annotations

import frappe


DEFAULT_TASKS = [
    (10, "Accounts Payable", "Supplier Statements Reconciled", "AP_SUPPLIER_RECON", "supplier_reconciliation", 2, "High", 1, "ADV Finance Module Check", "Supplier Reconciliation"),
    (20, "Accounts Payable", "Open Supplier Exceptions Reviewed", "AP_SUPPLIER_EXCEPTIONS", "supplier_reconciliation", 3, "High", 1, "ADV Finance Module Check", "Open Supplier Reconciliation Exceptions"),
    (30, "Accounts Payable", "Payment Runs Finalized", "AP_PAYMENT_RUNS", "erpnext_document", 3, "Medium", 0, "ERPNext Document Check", "Payment Run"),
    (40, "Accounts Receivable", "AR Control Account Reconciled", "AR_CONTROL_RECON", "account_reconciliation", 4, "High", 1, "ADV Finance Module Check", "Account Reconciliation Status"),
    (50, "Accounts Receivable", "Open High-Risk AR Disputes Reviewed", "AR_DISPUTES_REVIEWED", "accounts_receivable", 4, "High", 1, "ADV Finance Module Check", "Customer Dispute Register"),
    (60, "Accounts Receivable", "Broken Promises Reviewed", "AR_BROKEN_PROMISES", "accounts_receivable", 4, "Medium", 0, "ADV Finance Module Check", "Broken Promise Report"),
    (70, "Account Reconciliation", "Critical Balance Sheet Accounts Reconciled", "BS_CRITICAL_RECON", "account_reconciliation", 4, "Critical", 1, "ADV Finance Module Check", "Account Reconciliation Status"),
    (80, "Account Reconciliation", "AP Control Reconciled", "AP_CONTROL_RECON", "account_reconciliation", 4, "High", 1, "ADV Finance Module Check", "Account Reconciliation Status"),
    (90, "Cash & Bank", "Bank Reconciliation Completed", "BANK_RECON", "bank_reconciliation", 3, "Critical", 1, "ERPNext Document Check", ""),
    (95, "Cash & Bank", "Treasury Cash Position Reviewed", "TREASURY_CASH_POSITION", "treasury", 4, "Medium", 0, "ADV Finance Module Check", "Treasury Dashboard"),
    (98, "Planning & Budget", "Budget Overrides and Commitments Reviewed", "BUDGET_CONTROLS_REVIEWED", "budgeting", 4, "Medium", 0, "ADV Finance Module Check", "Budget Consumption"),
    (99, "Intercompany", "Intercompany Balances Matched", "INTERCOMPANY_MATCHED", "intercompany", 4, "High", 0, "ADV Finance Module Check", "Group Close Status"),
    (100, "Accruals", "Accrual Register Reviewed", "ACCRUAL_REGISTER", "accrual", 2, "High", 1, "ADV Finance Module Check", "Accrual Register"),
    (110, "Accruals", "Accrual Journals Posted", "ACCRUAL_JOURNALS", "accrual", 3, "Critical", 1, "ADV Finance Module Check", "Accrual Register"),
    (120, "Accruals", "Accrual Variances Reviewed", "ACCRUAL_VARIANCES", "accrual", 4, "High", 1, "ADV Finance Module Check", "Accrual Variance Analysis"),
    (130, "Fixed Assets", "Depreciation Posted", "FA_DEPRECIATION", "fixed_assets", 4, "High", 1, "ERPNext Document Check", ""),
    (140, "Inventory", "Inventory Valuation Reviewed", "INV_VALUATION", "inventory", 4, "High", 1, "ERPNext Document Check", ""),
    (150, "Payroll", "Payroll Completed", "PAYROLL_COMPLETE", "payroll", 4, "Medium", 1, "ERPNext Document Check", ""),
    (160, "Tax", "Tax Control Accounts Reviewed", "TAX_CONTROL_REVIEW", "manual", 5, "High", 1, "Manual", ""),
    (170, "FX Revaluation", "Foreign Currency Revaluation Completed", "FX_REVALUATION", "fx_revaluation", 4, "High", 1, "ERPNext Document Check", ""),
    (180, "Intercompany", "Intercompany Balances Reviewed", "INTERCO_REVIEW", "manual", 5, "High", 1, "Manual", ""),
    (190, "Management Review", "Finance Manager Approval", "FIN_MANAGER_APPROVAL", "manual", 5, "Critical", 1, "Manual", ""),
    (200, "Final Close", "Period Closing Voucher", "PERIOD_CLOSING_VOUCHER", "period_close", 6, "Critical", 1, "ERPNext Document Check", ""),
    (210, "Final Close", "Close Certification", "CLOSE_CERTIFICATION", "manual", 6, "Critical", 1, "Manual", ""),
]

DEPENDENCIES = {
    "AP_CONTROL_RECON": "AP_SUPPLIER_RECON",
    "ACCRUAL_JOURNALS": "ACCRUAL_REGISTER",
    "ACCRUAL_VARIANCES": "ACCRUAL_JOURNALS",
    "FIN_MANAGER_APPROVAL": "AP_CONTROL_RECON,AR_CONTROL_RECON,BS_CRITICAL_RECON,BANK_RECON,TREASURY_CASH_POSITION,BUDGET_CONTROLS_REVIEWED,INTERCOMPANY_MATCHED,ACCRUAL_VARIANCES,AR_DISPUTES_REVIEWED",
    "PERIOD_CLOSING_VOUCHER": "FIN_MANAGER_APPROVAL",
    "CLOSE_CERTIFICATION": "PERIOD_CLOSING_VOUCHER",
}


def execute():
    create_roles()
    if frappe.db.exists("Financial Close Template", "Monthly Financial Close"):
        template = frappe.get_doc("Financial Close Template", "Monthly Financial Close")
    else:
        template = frappe.get_doc({
            "doctype": "Financial Close Template",
            "template_name": "Monthly Financial Close",
            "active": 1,
            "close_frequency": "Monthly",
            "description": "Default ADV Finance month-end close checklist.",
            "start_offset_days": 0,
            "target_close_days": 5,
            "enforce_dependencies": 1,
            "require_review": 1,
            "require_evidence": 0,
            "require_all_critical_tasks": 1,
            "allow_manager_override": 0,
        })
    existing_codes = {row.task_code for row in template.tasks}
    for seq, category, name, code, provider, due, risk, blocking, automation, report in DEFAULT_TASKS:
        if code in existing_codes:
            continue
        template.append("tasks", {
            "sequence": seq,
            "category": category,
            "task_name": name,
            "task_code": code,
            "responsible_role": "Financial Close Manager" if risk == "Critical" else "Financial Close User",
            "due_day_offset": due,
            "risk_level": risk,
            "required": 1,
            "evidence_required": 1 if provider == "manual" else 0,
            "automation_type": automation,
            "readiness_provider": provider,
            "source_report": report,
            "blocking": blocking,
            "depends_on_task_codes": DEPENDENCIES.get(code),
        })
    if template.is_new():
        template.insert(ignore_permissions=True)
    else:
        template.save(ignore_permissions=True)


def create_roles():
    for role_name in ("Financial Close User", "Financial Close Manager", "AR Collection User", "AR Collection Manager", "Credit Controller", "Credit Manager", "Treasury User", "Treasury Manager", "Budget Preparer", "Budget Owner", "Budget Reviewer", "Budget Manager", "Budget Override Approver", "Intercompany Accountant", "Intercompany Manager", "Group Finance Manager"):
        if not frappe.db.exists("Role", role_name):
            frappe.get_doc({"doctype": "Role", "role_name": role_name, "desk_access": 1}).insert(ignore_permissions=True)
