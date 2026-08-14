from __future__ import annotations

import frappe

from adv_finance.compatibility.erpnext_v16 import find_late_gl_postings


def scan_late_postings(close_period: str) -> dict:
    period = frappe.get_doc("Financial Close Period", close_period)
    cutoff = period.reviewed_on or period.approved_on or period.closed_on
    if not cutoff:
        return {"created": 0, "message": "Close period has no review/approval cutoff yet."}
    rows = find_late_gl_postings(period.company, period.period_start, period.period_end, cutoff)
    created = 0
    for row in rows:
        if frappe.db.exists("Late Posting Exception", {"financial_close_period": period.name, "voucher_type": row.voucher_type, "voucher_no": row.voucher_no}):
            continue
        doc = frappe.new_doc("Late Posting Exception")
        doc.update({"financial_close_period": period.name, "posting_date": row.posting_date, "voucher_type": row.voucher_type, "voucher_no": row.voucher_no, "created_on": row.creation, "created_by": row.owner, "category": "Late Posting", "status": "Open"})
        doc.insert()
        created += 1
    return {"created": created}
