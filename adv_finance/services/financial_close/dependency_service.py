from __future__ import annotations

import frappe

COMPLETED_STATUSES = ("Completed", "Waived")


def get_unmet_dependencies(task):
    unmet = []
    for row in getattr(task, "dependencies", []) or []:
        if not row.blocking:
            continue
        dep_name = row.depends_on_task
        if not dep_name and row.depends_on_task_code and task.financial_close_period:
            dep_name = frappe.db.get_value(
                "Financial Close Task",
                {"financial_close_period": task.financial_close_period, "task_code": row.depends_on_task_code},
                "name",
            )
            row.depends_on_task = dep_name
        if not dep_name:
            row.dependency_status = "Unmet"
            unmet.append(row)
            continue
        status = frappe.db.get_value("Financial Close Task", dep_name, "status")
        row.dependency_status = "Met" if status in COMPLETED_STATUSES else "Unmet"
        if status not in COMPLETED_STATUSES:
            dep = frappe.get_doc("Financial Close Task", dep_name)
            unmet.append(dep)
    return unmet


def can_start_task(task) -> bool:
    return not get_unmet_dependencies(task)


def can_complete_task(task) -> bool:
    return not get_unmet_dependencies(task)


def recalculate_blocked_tasks(close_period: str) -> dict:
    names = frappe.get_all("Financial Close Task", filters={"financial_close_period": close_period}, pluck="name")
    blocked = 0
    for name in names:
        task = frappe.get_doc("Financial Close Task", name)
        unmet = get_unmet_dependencies(task)
        if unmet and task.status not in COMPLETED_STATUSES:
            task.status = "Blocked"
            task.blocked_reason = "Blocked by: " + ", ".join(getattr(row, "task_name", None) or getattr(row, "depends_on_task_code", "") for row in unmet)
            blocked += 1
        elif task.status == "Blocked":
            task.status = "Not Started"
            task.blocked_reason = None
        task.save()
    return {"blocked": blocked}
