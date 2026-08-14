from frappe.model.document import Document
from adv_finance.services.budgeting.reservation_service import validate_reservation


class BudgetReservation(Document):
    def validate(self):
        validate_reservation(self)
