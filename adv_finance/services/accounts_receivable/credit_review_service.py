from __future__ import annotations

import frappe
from frappe.utils import today, now_datetime

from adv_finance.services.accounts_receivable.credit_exposure_service import get_credit_exposure
from adv_finance.services.accounts_receivable.payment_behaviour_service import get_payment_behaviour


def refresh_credit_review(review, save: bool = True) -> dict:
    exposure = get_credit_exposure(review.company, review.customer, review.review_date or today())
    behaviour = get_payment_behaviour(review.company, review.customer)
    review.current_credit_limit = exposure["credit_limit"]
    review.receivable_outstanding = exposure["receivables"]
    review.overdue_amount = exposure["overdue"]
    review.open_sales_orders = exposure["sales_orders"]
    review.unbilled_delivery_amount = exposure["unbilled_deliveries"]
    review.available_credit = exposure["available_credit"]
    review.total_credit_exposure = exposure["total_exposure"] + (review.other_exposure or 0)
    review.average_days_to_pay = behaviour["average_days_to_pay"]
    review.maximum_days_overdue = behaviour["maximum_days_overdue"]
    review.broken_promises = behaviour["broken_promises"]
    review.disputes_count = behaviour["disputes_count"]
    review.payment_behaviour_score = behaviour["payment_behaviour_score"]
    if review.available_credit < 0 or review.broken_promises >= 2:
        review.risk_rating = "High"
        review.recommendation = review.recommendation or "Credit Hold"
    if save:
        review.save()
    return exposure


def submit_review(name: str) -> dict:
    doc = frappe.get_doc("Credit Review", name)
    doc.status = "Under Review"
    doc.reviewed_by = frappe.session.user
    doc.save()
    return {"status": doc.status}


def approve_review(name: str) -> dict:
    doc = frappe.get_doc("Credit Review", name)
    if doc.prepared_by == frappe.session.user and not frappe.has_role("System Manager"):
        frappe.throw("Preparer cannot approve their own credit review.")
    doc.status = "Approved"
    doc.approved_by = frappe.session.user
    doc.save()
    return {"status": doc.status}
