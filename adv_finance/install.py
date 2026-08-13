import frappe


def before_install():
    create_roles()


def after_install():
    create_roles()


def create_roles():
    for role_name in ("Supplier Reconciliation User", "Supplier Reconciliation Manager"):
        if not frappe.db.exists("Role", role_name):
            frappe.get_doc({"doctype": "Role", "role_name": role_name, "desk_access": 1}).insert()
