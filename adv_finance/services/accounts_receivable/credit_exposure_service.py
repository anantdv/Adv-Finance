from __future__ import annotations

from decimal import Decimal

from adv_finance.compatibility.erpnext_v16 import get_customer_credit_limit, get_customer_open_sales_orders, get_customer_unbilled_delivery_amount
from adv_finance.services.accounts_receivable.ar_balance_service import get_customer_ar_summary


def get_credit_exposure(company: str, customer: str, as_of_date=None) -> dict:
    ar = get_customer_ar_summary(company, customer, as_of_date)
    receivables = Decimal(str(ar["total_outstanding"] or 0))
    overdue = Decimal(str(ar["overdue_amount"] or 0))
    sales_orders = get_customer_open_sales_orders(company, customer)
    unbilled = get_customer_unbilled_delivery_amount(company, customer)
    advances = Decimal("0")
    credits = Decimal("0")
    limit = Decimal(str(get_customer_credit_limit(company, customer) or 0))
    total = receivables + sales_orders + unbilled - advances - credits
    return {"receivables": receivables, "overdue": overdue, "sales_orders": sales_orders, "unbilled_deliveries": unbilled, "advances": advances, "credits": credits, "total_exposure": total, "credit_limit": limit, "available_credit": limit - total}
