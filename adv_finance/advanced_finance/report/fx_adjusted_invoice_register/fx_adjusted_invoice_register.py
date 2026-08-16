from __future__ import annotations

from adv_finance.services.finance_controls.fx_register_service import fx_adjusted_invoice_register

def execute(filters=None):
    cols=["Party:Dynamic Link/party_type:160","Invoice:Data:180","Invoice Date:Date:120","Due Date:Date:120","Currency:Link/Currency:100","Outstanding FCY:Currency:140","Carrying Exchange Rate:Float:150","Carrying PGK:Currency:140","Month-End Spot Rate:Float:150","Revalued PGK:Currency:140","FX Difference:Currency:140","Debit/Credit:Data:110","Revaluation Reference:Data:180","Revaluation Posting Date:Date:150"]
    rows=fx_adjusted_invoice_register(filters or {})
    return cols,[[r.get("party"),r.get("invoice"),r.get("invoice_date"),r.get("due_date"),r.get("currency"),r.get("outstanding_fcy"),r.get("carrying_exchange_rate"),r.get("carrying_pgk"),r.get("month_end_spot_rate"),r.get("revalued_pgk"),r.get("fx_difference"),r.get("debit_credit_indicator"),r.get("revaluation_reference"),r.get("revaluation_posting_date")] for r in rows]
