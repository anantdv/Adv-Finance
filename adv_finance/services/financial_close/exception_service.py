from __future__ import annotations

import frappe
from frappe.utils import now_datetime


def replace_task_exceptions(task, exceptions: list[dict]) -> None:
    existing = frappe.get_all("Financial Close Exception", filters={"financial_close_task": task.name, "status": ["in", ["Open", "Investigating"]]}, pluck="name")
    for name in existing:
        frappe.delete_doc("Financial Close Exception", name, force=True)
    for row in exceptions:
        doc = frappe.new_doc("Financial Close Exception")
        doc.update(
            {
                "financial_close_period": task.financial_close_period,
                "financial_close_task": task.name,
                "category": task.category,
                "exception_type": row.get("exception_type") or row.get("type") or "Readiness Exception",
                "description": row.get("description") or row.get("message"),
                "amount": row.get("amount"),
                "risk_level": row.get("risk_level") or task.risk_level,
                "assigned_to": task.assigned_to,
                "source_doctype": row.get("source_doctype"),
                "source_document": row.get("source_document"),
                "status": "Open",
                "created_on": now_datetime(),
            }
        )
        doc.insert()


def resolve_exception(name: str, notes: str | None = None) -> dict:
    doc = frappe.get_doc("Financial Close Exception", name)
    doc.status = "Resolved"
    doc.resolution_notes = notes
    doc.resolved_by = frappe.session.user
    doc.resolved_on = now_datetime()
    doc.save()
    return {"resolved": True}
