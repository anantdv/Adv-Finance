from __future__ import annotations

import frappe
from frappe.utils import now_datetime


def approve_supplier_onboarding(name):
    doc = frappe.get_doc("Supplier Onboarding Request", name)
    if doc.requested_by == frappe.session.user and not frappe.has_role("System Manager"):
        frappe.throw("Requester cannot approve the same supplier onboarding request.")
    doc.status = "Approved"; doc.approved_by = frappe.session.user; doc.approved_on = now_datetime(); doc.save()
    return {"status": doc.status}


def create_supplier_from_onboarding(name):
    req = frappe.get_doc("Supplier Onboarding Request", name)
    if req.status != "Approved":
        frappe.throw("Supplier can only be created after onboarding approval.")
    supplier = frappe.new_doc("Supplier")
    supplier.update({"supplier_name": req.proposed_supplier_name, "supplier_group": req.supplier_group, "supplier_type": req.supplier_type, "country": req.country, "tax_id": req.tax_id, "default_currency": req.currency, "payment_terms": req.payment_terms})
    supplier.insert(ignore_permissions=True)
    req.created_supplier = supplier.name; req.status = "Supplier Created"; req.save(ignore_permissions=True)
    return supplier


def verify_supplier_change(name, method=None, notes=None):
    doc = frappe.get_doc("Supplier Change Request", name)
    if doc.requested_by == frappe.session.user and not frappe.has_role("System Manager"):
        frappe.throw("Requester cannot verify the same supplier change.")
    doc.verification_method = method or doc.verification_method; doc.verification_notes = notes or doc.verification_notes; doc.verified_by = frappe.session.user; doc.verified_on = now_datetime(); doc.status = "Verified"; doc.save()
    return {"status": doc.status}


def approve_supplier_change(name):
    doc = frappe.get_doc("Supplier Change Request", name)
    if frappe.session.user in (doc.requested_by, doc.verified_by) and not frappe.has_role("System Manager"):
        frappe.throw("Supplier change approver must be independent.")
    if doc.change_type in ("Bank Account", "Bank Account Number", "Bank Name", "SWIFT/BIC") and not doc.verified_by:
        frappe.throw("Bank changes require independent verification before approval.")
    doc.approved_by = frappe.session.user; doc.approved_on = now_datetime(); doc.status = "Approved"; doc.save()
    return {"status": doc.status}


def supplier_master_change_register(filters=None):
    filters = filters or {}
    query={}
    for key in ("supplier", "change_type", "status"):
        if filters.get(key): query[key]=filters[key]
    return frappe.get_all("Supplier Change Request", filters=query, fields=["supplier", "change_type", "old_value", "proposed_value", "requested_by", "verified_by", "approved_by", "applied_date", "status"], order_by="modified desc")
