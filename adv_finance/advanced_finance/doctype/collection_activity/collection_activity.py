from __future__ import annotations

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime


class CollectionActivity(Document):
    def before_insert(self):
        self.created_by = self.created_by or frappe.session.user
        self.activity_date = self.activity_date or now_datetime()

    def validate(self):
        if self.collection_case:
            case = frappe.get_doc("Collection Case", self.collection_case)
            self.company = self.company or case.company
            self.customer = self.customer or case.customer
            if self.next_action_date:
                case.next_action_date = self.next_action_date
            case.last_contact_date = self.activity_date
            if self.outcome == "Promise Received":
                case.status = "Promise Received"
            elif self.outcome == "Dispute Raised":
                case.status = "Disputed"
            elif self.outcome == "Escalated":
                case.status = "Escalated"
            case.save()
