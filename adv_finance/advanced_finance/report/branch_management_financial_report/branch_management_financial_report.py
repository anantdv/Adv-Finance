from __future__ import annotations

from adv_finance.services.finance_controls.branch_report_service import branch_management_financial_report

def execute(filters=None):
    cols=["Account:Link/Account:180","Financial Line:Data:220","MTD Actual:Currency:130","MTD Budget:Currency:130","MTD Variance:Currency:130","MTD Variance %:Percent:120","MTD Last Year:Currency:130","MTD YoY Variance:Currency:140","MTD YoY %:Percent:110","YTD Actual:Currency:130","YTD Budget:Currency:130","YTD Variance:Currency:130","YTD Variance %:Percent:120","YTD Last Year:Currency:130","YTD YoY Variance:Currency:140","YTD YoY %:Percent:110"]
    rows=branch_management_financial_report(filters or {})
    return cols,[[r["account"],r["account_name"],r["mtd_actual"],r["mtd_budget"],r["mtd_variance"],r["mtd_variance_percent"],r["mtd_last_year"],r["mtd_yoy_variance"],r["mtd_yoy_percent"],r["ytd_actual"],r["ytd_budget"],r["ytd_variance"],r["ytd_variance_percent"],r["ytd_last_year"],r["ytd_yoy_variance"],r["ytd_yoy_percent"]] for r in rows]
