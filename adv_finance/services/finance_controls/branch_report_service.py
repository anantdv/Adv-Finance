from __future__ import annotations

from decimal import Decimal

import frappe

from adv_finance.compatibility.erpnext_v16 import get_gl_movement_by_account
from adv_finance.services.budgeting.available_budget_service import get_approved_budget


def resolve_branch_dimension(company=None):
    rows = frappe.get_all("Accounting Dimension", filters={"disabled": 0}, fields=["document_type", "fieldname", "label"], order_by="idx asc")
    for row in rows:
        if (row.label or "").lower() == "branch" or (row.fieldname or "").lower() == "branch":
            return {"dimension_type": "Accounting Dimension", "fieldname": row.fieldname, "document_type": row.document_type}
    return {"dimension_type": "Cost Center", "fieldname": "cost_center", "document_type": "Cost Center"}


def branch_management_financial_report(filters=None):
    filters = filters or {}
    rows=[]
    for row in get_gl_movement_by_account(filters.get("company"), filters.get("from_date"), filters.get("to_date"), filters):
        mtd_actual = Decimal(str(row.mtd_actual or 0)); ytd_actual = Decimal(str(row.ytd_actual or 0)); ly_mtd = Decimal(str(row.ly_mtd or 0)); ly_ytd = Decimal(str(row.ly_ytd or 0))
        mtd_budget = get_approved_budget(filters.get("company"), row.account, filters.get("cost_center") or filters.get("branch"), filters.get("project"), filters.get("to_date")) / Decimal("12")
        ytd_budget = get_approved_budget(filters.get("company"), row.account, filters.get("cost_center") or filters.get("branch"), filters.get("project"), filters.get("to_date"))
        rows.append({"account": row.account, "account_name": row.account_name, "mtd_actual": mtd_actual, "mtd_budget": mtd_budget, "mtd_variance": mtd_actual - mtd_budget, "mtd_variance_percent": _pct(mtd_actual - mtd_budget, mtd_budget), "mtd_last_year": ly_mtd, "mtd_yoy_variance": mtd_actual - ly_mtd, "mtd_yoy_percent": _pct(mtd_actual - ly_mtd, ly_mtd), "ytd_actual": ytd_actual, "ytd_budget": ytd_budget, "ytd_variance": ytd_actual - ytd_budget, "ytd_variance_percent": _pct(ytd_actual - ytd_budget, ytd_budget), "ytd_last_year": ly_ytd, "ytd_yoy_variance": ytd_actual - ly_ytd, "ytd_yoy_percent": _pct(ytd_actual - ly_ytd, ly_ytd)})
    return rows


def _pct(num, den):
    den = Decimal(str(den or 0))
    return Decimal("0") if den == 0 else Decimal(str(num or 0)) / den * Decimal("100")
