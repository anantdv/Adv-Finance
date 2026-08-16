from __future__ import annotations

from decimal import Decimal

import frappe
from frappe.utils import nowdate, today


def get_demand_letter_eligibility(company, customer, oldest_overdue_days=0, overdue_amount=0, template=None, manager_override=False):
    tpl = frappe.get_doc("Demand Letter Template", template) if template else None
    min_days = int(getattr(tpl, "minimum_overdue_days", 60) or 60)
    min_amount = Decimal(str(getattr(tpl, "minimum_overdue_amount", 0) or 0))
    eligible = manager_override or (int(oldest_overdue_days or 0) >= min_days and Decimal(str(overdue_amount or 0)) >= min_amount)
    return {"eligible": eligible, "minimum_overdue_days": min_days, "minimum_overdue_amount": min_amount}


def render_demand_letter(template_doc, context):
    subject = frappe.render_template(template_doc.subject or "Demand Letter", context)
    body = "\n".join(filter(None, [template_doc.introduction, template_doc.body, template_doc.closing, template_doc.legal_notice]))
    return {"subject": subject, "body": frappe.render_template(body, context)}


def generate_demand_letter(company, customer, template, overdue_amount, oldest_overdue_days, collection_case=None, manager_override=False):
    eligibility = get_demand_letter_eligibility(company, customer, oldest_overdue_days, overdue_amount, template, manager_override)
    if not eligibility["eligible"]:
        frappe.throw("Customer is not eligible for demand letter generation.")
    tpl = frappe.get_doc("Demand Letter Template", template)
    customer_name = frappe.db.get_value("Customer", customer, "customer_name") or customer
    rendered = render_demand_letter(tpl, {"customer": customer, "customer_name": customer_name, "total_outstanding": overdue_amount, "overdue_amount": overdue_amount, "oldest_overdue_days": oldest_overdue_days, "statement_date": today(), "account_manager": ""})
    doc = frappe.new_doc("Demand Letter")
    doc.update({"company": company, "customer": customer, "customer_name": customer_name, "template": template, "collection_case": collection_case, "generated_date": nowdate(), "overdue_amount": overdue_amount, "oldest_overdue_days": oldest_overdue_days, "subject": rendered["subject"], "letter_body": rendered["body"], "status": "Generated", "generated_by": frappe.session.user})
    doc.insert(ignore_permissions=True)
    return doc


def demand_letter_register(filters=None):
    filters = filters or {}
    query={}
    for key in ("company", "customer", "status", "collection_case"):
        if filters.get(key): query[key]=filters[key]
    return frappe.get_all("Demand Letter", filters=query, fields=["customer", "letter_type", "generated_date", "overdue_amount", "oldest_overdue_days", "generated_by", "sent_date", "status", "collection_case"], order_by="generated_date desc, modified desc")
