from __future__ import annotations


class CloseReadinessProvider:
    provider_name = "manual"

    def check(self, task, close_period):
        return {
            "ready": task.status in ("Ready for Review", "Completed", "Waived"),
            "status": task.status or "Not Started",
            "message": "Manual task requires user evidence and review.",
            "exceptions": [],
            "details": {},
        }
