from frappe.model.document import Document
from adv_finance.services.intercompany.settlement_service import recalculate_settlement


class IntercompanySettlement(Document):
    def validate(self):
        recalculate_settlement(self)
