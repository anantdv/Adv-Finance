from frappe.model.document import Document
from adv_finance.services.consolidation.adjustment_service import validate_adjustment


class ConsolidationAdjustment(Document):
    def validate(self):
        validate_adjustment(self)
