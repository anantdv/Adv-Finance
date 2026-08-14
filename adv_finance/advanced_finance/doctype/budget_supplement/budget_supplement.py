from frappe.model.document import Document
from adv_finance.services.budgeting.supplement_service import validate_supplement


class BudgetSupplement(Document):
    def validate(self):
        validate_supplement(self)
