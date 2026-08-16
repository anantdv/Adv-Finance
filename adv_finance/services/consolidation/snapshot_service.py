from __future__ import annotations

import frappe
from frappe.utils import now_datetime

from adv_finance.compatibility.erpnext_v16 import get_company_trial_balance_rows
from adv_finance.services.consolidation.group_service import get_group_companies
from adv_finance.services.consolidation.translation_service import translate_trial_balance_row


def collect_trial_balance_snapshot(consolidation_period: str, force: bool = False) -> dict:
    period = frappe.get_doc("Consolidation Period", consolidation_period)
    group = frappe.get_doc("Consolidation Group", period.consolidation_group)
    if period.status in ("Approved", "Published", "Closed") and force:
        frappe.throw("Approved, Published, and Closed consolidation periods are immutable.")
    existing = frappe.get_all("Trial Balance Snapshot", filters={"consolidation_period": period.name}, fields=["name"])
    if existing and not force:
        frappe.throw("Trial Balance snapshots already exist. Use force on an open period to rebuild.")
    if force:
        for row in existing:
            frappe.delete_doc("Trial Balance Snapshot", row.name, ignore_permissions=True)
    count = 0
    for company in get_group_companies(period.consolidation_group):
        for row in get_company_trial_balance_rows(company.company, period.start_date, period.end_date):
            row.currency = row.currency or company.functional_currency or company.reporting_currency or group.reporting_currency
            translated = translate_trial_balance_row(row, group.reporting_currency, period.end_date)
            doc = frappe.new_doc("Trial Balance Snapshot")
            doc.update({"consolidation_period": period.name, "company": company.company, "account": row.account, "account_name": row.account_name, "root_type": row.root_type, "balance": row.balance, "currency": row.currency or company.functional_currency or company.reporting_currency, "exchange_rate": translated["exchange_rate"], "translated_amount": translated["translated_amount"], "translation_difference": translated["translation_difference"], "snapshot_date": now_datetime(), "immutable": 1})
            doc.insert(ignore_permissions=True)
            count += 1
    period.status = "Collecting"
    period.companies_collected = len(get_group_companies(period.consolidation_group))
    period.companies_pending = 0
    period.translation_status = "Translated"
    period.save()
    return {"snapshots": count}
