from frappe.model.document import Document
from adv_finance.services.budgeting.override_service import prepare_override_request


class BudgetOverrideRequest(Document):
    def validate(self):
        prepare_override_request(self)
