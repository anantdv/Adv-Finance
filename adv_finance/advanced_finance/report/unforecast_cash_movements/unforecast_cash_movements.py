from __future__ import annotations

from adv_finance.compatibility.erpnext_v16 import get_actual_cash_movements


def execute(filters=None):
    filters = filters or {}
    rows = get_actual_cash_movements(filters.get("company"), filters.get("from_date"), filters.get("to_date"))
    columns = ["Payment Entry:Link/Payment Entry:180", "Posting Date:Date:100", "Payment Type:Data:110", "Party:Data:180", "Amount:Currency:140", "Reference:Data:180"]
    return columns, [[r.name, r.posting_date, r.payment_type, r.party, r.received_amount or r.paid_amount, r.reference_no] for r in rows]
