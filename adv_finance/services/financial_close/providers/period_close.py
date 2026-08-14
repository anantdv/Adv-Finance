from __future__ import annotations

import frappe

from adv_finance.services.financial_close.providers.base import CloseReadinessProvider

from adv_finance.compatibility.erpnext_v16 import get_period_closing_voucher_docstatus


class PeriodCloseProvider(CloseReadinessProvider):
    provider_name = "period_close"

    def check(self, task, close_period):
        status = get_period_closing_voucher_docstatus(close_period.period_closing_voucher)
        ready = status == 1 or (close_period.period_closing_voucher and status == 0)
        message = "Period Closing Voucher is available." if ready else "Draft Period Closing Voucher has not been created."
        return {"ready": ready, "status": "Completed" if ready else "Waiting", "message": message, "exceptions": [] if ready else [{"exception_type": "Period Closing Voucher Missing", "description": message}], "details": {"docstatus": status}}
