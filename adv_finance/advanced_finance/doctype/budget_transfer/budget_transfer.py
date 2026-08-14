from frappe.model.document import Document
from adv_finance.services.budgeting.transfer_service import validate_transfer


class BudgetTransfer(Document):
    def validate(self):
        validate_transfer(self)
