import frappe


def before_install():
    create_roles()


def after_install():
    create_roles()
    create_default_financial_close_template()


def after_migrate():
    create_roles()
    create_default_financial_close_template()


def create_roles():
    for role_name in (
        "Supplier Reconciliation User",
        "Supplier Reconciliation Manager",
        "Financial Close User",
        "Financial Close Manager",
        "AR Collection User",
        "AR Collection Manager",
        "Credit Controller",
        "Credit Manager",
        "Treasury User",
        "Treasury Manager",
        "Budget Preparer",
        "Budget Owner",
        "Budget Reviewer",
        "Budget Manager",
        "Budget Override Approver",
        "Intercompany Accountant",
        "Intercompany Manager",
        "Group Finance Manager",
        "Group Accountant",
        "Consolidation Reviewer",
        "CFO",
        "Auditor",
    ):
        if not frappe.db.exists("Role", role_name):
            frappe.get_doc({"doctype": "Role", "role_name": role_name, "desk_access": 1}).insert()


def create_default_financial_close_template():
    if not frappe.db.exists("DocType", "Financial Close Template"):
        return
    from adv_finance.patches.v0_1.create_default_financial_close_template import execute

    execute()
