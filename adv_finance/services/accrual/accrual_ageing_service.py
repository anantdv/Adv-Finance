from __future__ import annotations

from frappe.utils import date_diff, nowdate


def days_open(accrual_date, as_of_date=None) -> int:
    if not accrual_date:
        return 0
    return max(date_diff(as_of_date or nowdate(), accrual_date), 0)


def age_bucket(days: int) -> str:
    if days <= 0:
        return "Current"
    if days <= 30:
        return "1-30 Days"
    if days <= 60:
        return "31-60 Days"
    if days <= 90:
        return "61-90 Days"
    if days <= 180:
        return "91-180 Days"
    return "180+ Days"
