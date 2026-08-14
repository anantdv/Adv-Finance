from __future__ import annotations

from decimal import Decimal

import frappe


def get_accrual_supporting_balance(company: str, account: str, period_end) -> Decimal:
    result = frappe.db.sql(
        """
        select coalesce(sum(remaining_amount), 0) as balance
        from `tabAccrual`
        where company = %(company)s
          and accrual_liability_account = %(account)s
          and accrual_date <= %(period_end)s
          and workflow_status != 'Cancelled'
        """,
        {"company": company, "account": account, "period_end": period_end},
        as_dict=True,
    )
    return Decimal(str(result[0].balance if result else 0))
