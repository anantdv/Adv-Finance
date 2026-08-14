from __future__ import annotations

import frappe
from frappe.utils import add_days, getdate, now_datetime

from adv_finance.services.financial_close.readiness_service import refresh_close_readiness


def create_close_period(company: str, template: str, period_start, period_end) -> dict:
    template_doc = frappe.get_doc("Financial Close Template", template)
    if template_doc.company and template_doc.company != company:
        frappe.throw("Template company must match selected company.")
    if getdate(period_start) > getdate(period_end):
        frappe.throw("Period Start must be on or before Period End.")
    existing = frappe.db.exists(
        "Financial Close Period",
        {
            "company": company,
            "close_template": template,
            "period_start": period_start,
            "period_end": period_end,
            "status": ["not in", ["Cancelled"]],
        },
    )
    if existing:
        return {"financial_close_period": existing, "created": False}

    period = frappe.new_doc("Financial Close Period")
    period.update(
        {
            "company": company,
            "close_template": template,
            "period_start": period_start,
            "period_end": period_end,
            "target_close_date": add_days(period_end, template_doc.target_close_days or 0),
            "status": "Open",
            "opened_on": now_datetime(),
            "close_manager": template_doc.default_close_manager,
            "reviewer": template_doc.default_reviewer,
            "approver": template_doc.default_approver,
            "require_close_certification": 1 if template_doc.require_review else 0,
        }
    )
    period.insert()
    created_tasks = _copy_template_tasks(period, template_doc)
    _copy_dependencies(period, template_doc)
    refresh_close_readiness(period.name)
    return {"financial_close_period": period.name, "tasks": created_tasks, "created": True}


def _copy_template_tasks(period, template_doc) -> int:
    created = 0
    for row in sorted(template_doc.tasks, key=lambda item: item.sequence or 0):
        if frappe.db.exists("Financial Close Task", {"financial_close_period": period.name, "task_code": row.task_code}):
            continue
        task = frappe.new_doc("Financial Close Task")
        task.update(
            {
                "financial_close_period": period.name,
                "company": period.company,
                "period_end": period.period_end,
                "sequence": row.sequence,
                "category": row.category,
                "task_name": row.task_name,
                "task_code": row.task_code,
                "description": row.description,
                "assigned_to": row.default_owner or template_doc.default_close_manager,
                "responsible_role": row.responsible_role,
                "reviewer": row.reviewer or template_doc.default_reviewer,
                "planned_start_date": add_days(period.period_end, template_doc.start_offset_days or 0),
                "due_date": add_days(period.period_end, row.due_day_offset or 0),
                "risk_level": row.risk_level or "Medium",
                "blocking": row.blocking,
                "required": row.required,
                "evidence_required": row.evidence_required or template_doc.require_evidence,
                "readiness_provider": row.readiness_provider,
                "source_doctype": row.source_doctype,
                "source_report": row.source_report,
                "automated_check": 1 if row.automation_type != "Manual" or row.readiness_provider else 0,
                "auto_complete_when_ready": row.auto_complete_when_ready,
                "status": "Not Started",
            }
        )
        task.insert()
        created += 1
    return created


def _copy_dependencies(period, template_doc) -> None:
    task_by_code = {row.task_code: row.name for row in frappe.get_all("Financial Close Task", filters={"financial_close_period": period.name}, fields=["name", "task_code"])}
    for row in template_doc.tasks:
        target = task_by_code.get(row.task_code)
        if not target or not row.depends_on_task_codes:
            continue
        task = frappe.get_doc("Financial Close Task", target)
        existing_codes = {dep.depends_on_task_code for dep in task.dependencies}
        for code in [part.strip() for part in row.depends_on_task_codes.replace(",", "\n").splitlines() if part.strip()]:
            if code in existing_codes:
                continue
            task.append(
                "dependencies",
                {
                    "depends_on_task_code": code,
                    "depends_on_task": task_by_code.get(code),
                    "blocking": 1,
                    "dependency_status": "Unmet",
                },
            )
        task.save()
