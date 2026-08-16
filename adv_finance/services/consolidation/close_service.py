from __future__ import annotations

import frappe
from frappe.utils import now_datetime


def advance_period_status(name: str, status: str) -> dict:
    allowed = ["Draft", "Open", "Collecting", "Translating", "Eliminating", "Consolidating", "Review", "Approved", "Published", "Closed"]
    if status not in allowed:
        frappe.throw("Invalid consolidation period status.")
    doc = frappe.get_doc("Consolidation Period", name)
    doc.status = status
    if status == "Closed":
        doc.closed_by = frappe.session.user
        doc.closed_on = now_datetime()
    doc.save()
    return {"status": doc.status}


def get_consolidation_close_readiness(period: str) -> dict:
    p = frappe.get_doc("Consolidation Period", period)
    snapshots = frappe.db.count("Trial Balance Snapshot", {"consolidation_period": period})
    lines = frappe.db.count("Consolidated Trial Balance Line", {"consolidation_period": period})
    open_adjustments = frappe.db.count("Consolidation Adjustment", {"consolidation_period": period, "status": ["not in", ["Approved", "Cancelled"]]})
    blocked_eliminations = frappe.db.count("Intercompany Elimination Candidate", {"status": ["in", ["Blocked", "Difference Exists", "Awaiting Settlement"]]})
    ready = bool(snapshots and lines and not open_adjustments and not blocked_eliminations)
    return {"ready": ready, "snapshots": snapshots, "consolidated_lines": lines, "open_adjustments": open_adjustments, "blocked_eliminations": blocked_eliminations, "period_status": p.status}
