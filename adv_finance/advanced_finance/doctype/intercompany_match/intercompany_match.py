from frappe.model.document import Document
from decimal import Decimal


class IntercompanyMatch(Document):
    def validate(self):
        origin = sum(Decimal(str(row.amount or 0)) for row in self.items if row.side == "Origin")
        destination = sum(Decimal(str(row.amount or 0)) for row in self.items if row.side == "Destination")
        self.origin_total = origin
        self.destination_total = destination
        self.difference_amount = origin - destination
