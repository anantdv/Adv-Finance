from __future__ import annotations
from adv_finance.services.intercompany.report_service import dashboard_summary

def execute(filters=None):
    s=dashboard_summary((filters or {}).get("company"))
    return ["Metric:Data:240","Value:Data:140"], [["Transactions",s["transactions"]],["Matched",s["matched"]],["Matched %",s["matched_percent"]],["Unreconciled",s["unreconciled"]],["Settled",s["settled"]]]
