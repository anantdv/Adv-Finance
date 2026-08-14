from __future__ import annotations

import frappe


def get_payment_behaviour(company: str, customer: str) -> dict:
    broken = frappe.db.count("Promise to Pay", {"company": company, "customer": customer, "status": "Broken"})
    disputes = frappe.db.count("Customer Dispute", {"company": company, "customer": customer, "status": ["not in", ["Resolved", "Rejected", "Closed"]]})
    rows = frappe.db.sql("""
        select greatest(datediff(coalesce(si.modified, si.due_date), si.due_date), 0) as days_late
        from `tabSales Invoice` si
        where si.company = %(company)s and si.customer = %(customer)s and si.docstatus = 1 and si.outstanding_amount = 0
        order by si.posting_date desc limit 200
    """, {"company": company, "customer": customer}, as_dict=True)
    days = [int(row.days_late or 0) for row in rows]
    avg = sum(days) / len(days) if days else 0
    maximum = max(days) if days else 0
    score = max(0, 100 - int(avg) - broken * 10 - disputes * 5)
    return {"average_days_to_pay": avg, "maximum_days_overdue": maximum, "broken_promises": broken, "disputes_count": disputes, "payment_behaviour_score": score}
