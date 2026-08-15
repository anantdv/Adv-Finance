from frappe.model.document import Document
from adv_finance.services.intercompany.partner_service import validate_partner


class IntercompanyPartner(Document):
    def validate(self):
        validate_partner(self)
