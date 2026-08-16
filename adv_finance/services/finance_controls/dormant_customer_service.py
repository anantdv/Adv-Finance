from __future__ import annotations

import frappe
from frappe.utils import date_diff, getdate, today

from adv_finance.compatibility.erpnext_v16 import get_customer_business_activity_dates


def get_customer_last_activity(company, customer):
    return get_customer_business_activity_dates(company, customer)


def dormant_customers(filters=None):
    filters = filters or {}
    as_of = getdate(filters.get("as_of_date") or today())
    threshold = int(filters.get("dormant_days") or 365)
    customers = frappe.get_all("Customer", filters={k: v for k, v in {"customer_group": filters.get("customer_group"), "territory": filters.get("territory"), "account_manager": filters.get("account_manager")}.items() if v}, fields=["name", "customer_name", "customer_group", "territory", "account_manager"])
    rows=[]
    for c in customers:
        act = get_customer_last_activity(filters.get("company"), c.name)
        last = act.get("last_business_activity_date")
        days = date_diff(as_of, getdate(last)) if last else 999999
        if days >= threshold:
            rows.append({**c.__dict__, **act, "dormant_days": days, "outstanding_ar": get_customer_outstanding(filters.get("company"), c.name), "credit_limit": 0, "credit_status": "Dormant"})
    return rows


def get_customer_outstanding(company, customer):
    rows = frappe.db.sql(
        """
        select coalesce(sum(outstanding_amount), 0) as outstanding
        from `tabSales Invoice`
        where company = %(company)s
          and customer = %(customer)s
          and docstatus = 1
        """,
        {"company": company, "customer": customer},
        as_dict=True,
    )
    return rows[0].outstanding if rows else 0
