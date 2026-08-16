from __future__ import annotations

from adv_finance.services.finance_controls.dormant_customer_service import dormant_customers

def execute(filters=None):
    cols=["Customer:Link/Customer:160","Customer Name:Data:180","Customer Group:Link/Customer Group:150","Territory:Link/Territory:130","Last Invoice Date:Date:130","Last Payment Date:Date:130","Last Delivery Date:Date:130","Last Activity Date:Date:130","Dormant Days:Int:110","Outstanding AR:Currency:130","Credit Limit:Currency:120","Credit Status:Data:120","Account Manager:Link/User:150"]
    rows=dormant_customers(filters or {})
    return cols,[[r.get("name"),r.get("customer_name"),r.get("customer_group"),r.get("territory"),r.get("last_invoice_date"),r.get("last_payment_date"),r.get("last_delivery_date"),r.get("last_business_activity_date"),r.get("dormant_days"),r.get("outstanding_ar"),r.get("credit_limit"),r.get("credit_status"),r.get("account_manager")] for r in rows]
