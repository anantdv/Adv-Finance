from __future__ import annotations

from adv_finance.compatibility.erpnext_v16 import get_gl_account_balance


def get_account_balance(company: str, account: str, from_date, to_date):
    return get_gl_account_balance(company, account, from_date, to_date)
