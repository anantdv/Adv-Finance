from frappe.model.document import Document
from adv_finance.services.consolidation.group_service import validate_group


class ConsolidationGroup(Document):
    def validate(self):
        validate_group(self)
