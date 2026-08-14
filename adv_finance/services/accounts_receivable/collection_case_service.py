from __future__ import annotations

from decimal import Decimal

import frappe

from adv_finance.services.accounts_receivable.ar_balance_service import get_customer_ar_summary
from adv_finance.services.accounts_receivable.collection_priority_service import score_collection_case
from adv_finance.services.accounts_receivable.credit_exposure_service import get_credit_exposure

ACTIVE_STATUSES = ("Open", "Contact Required", "Promise Received", "Disputed", "Escalated", "On Hold")


def create_collection_case(company: str, customer: str, collector: str | None = None) -> dict:
    existing = frappe.db.exists("Collection Case", {"company": company, "customer": customer, "status": ["in", ACTIVE_STATUSES]})
    if existing:
        return {"collection_case": existing, "created": False}
    case = frappe.new_doc("Collection Case")
    case.update({"company": company, "customer": customer, "collector": collector, "status": "Open"})
    refresh_collection_case(case, save=False)
    case.insert()
    return {"collection_case": case.name, "created": True}


def refresh_collection_case(case, save: bool = True) -> dict:
    summary = get_customer_ar_summary(case.company, case.customer)
    case.currency = case.currency or summary.get("currency")
    for key in ("total_outstanding", "overdue_amount", "current_amount", "oldest_invoice_date", "oldest_overdue_days", "open_invoice_count", "overdue_invoice_count"):
        setattr(case, key, summary.get(key))
    case.promise_count = frappe.db.count("Promise to Pay", {"company": case.company, "customer": case.customer, "status": ["in", ["Active", "Partially Kept"]]}) if getattr(frappe, "db", None) else 0
    case.broken_promise_count = frappe.db.count("Promise to Pay", {"company": case.company, "customer": case.customer, "status": "Broken"}) if getattr(frappe, "db", None) else 0
    case.open_dispute_count = frappe.db.count("Customer Dispute", {"company": case.company, "customer": case.customer, "status": ["not in", ["Resolved", "Rejected", "Closed"]]}) if getattr(frappe, "db", None) else 0
    active_disputed = _active_disputed_amount(case.company, case.customer)
    case.collection_eligible_amount = Decimal(str(case.total_outstanding or 0)) - active_disputed
    score = score_collection_case(case, get_credit_exposure(case.company, case.customer))
    case.risk_score = score["score"]
    case.collection_priority = score["priority"]
    case.risk_level = score["risk_level"]
    case.set("invoices", [])
    for row in summary["invoices"]:
        row["disputed"] = 1 if frappe.db.exists("Customer Dispute Invoice", {"sales_invoice": row["sales_invoice"], "parenttype": "Customer Dispute"}) else 0
        case.append("invoices", row)
    if Decimal(str(case.total_outstanding or 0)) == 0 and not case.open_dispute_count and not case.promise_count and case.status not in ("Closed",):
        case.status = "Resolved"
    if save:
        case.save()
    return {"refreshed": True}


def generate_collection_cases(company: str, as_of_date=None, minimum_overdue_amount=0) -> dict:
    customers = frappe.db.sql("""
        select distinct customer
        from `tabSales Invoice`
        where company = %(company)s and docstatus = 1 and outstanding_amount > 0
    """, {"company": company}, as_dict=True)
    created = []
    for row in customers:
        summary = get_customer_ar_summary(company, row.customer, as_of_date)
        if Decimal(str(summary["overdue_amount"] or 0)) >= Decimal(str(minimum_overdue_amount or 0)) and summary["overdue_amount"]:
            result = create_collection_case(company, row.customer)
            if result.get("created"):
                created.append(result["collection_case"])
    return {"created": created}


def _active_disputed_amount(company: str, customer: str) -> Decimal:
    result = frappe.db.sql("""
        select coalesce(sum(disputed_amount), 0) as amount
        from `tabCustomer Dispute`
        where company = %(company)s and customer = %(customer)s
          and status not in ('Resolved', 'Rejected', 'Closed')
    """, {"company": company, "customer": customer}, as_dict=True)
    return Decimal(str(result[0].amount if result else 0))
