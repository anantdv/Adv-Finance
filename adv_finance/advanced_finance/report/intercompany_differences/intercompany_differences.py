from __future__ import annotations
import frappe

def execute(filters=None):
    rows=frappe.get_all("Intercompany Difference",filters={},fields=['name', 'difference_type', 'severity', 'origin_company', 'destination_company', 'amount', 'currency', 'status'],order_by="modified desc")
    return ["Document:Link/Intercompany Difference:190"] + ['Difference Type:Data:140', 'Severity:Data:140', 'Origin Company:Data:140', 'Destination Company:Data:140', 'Amount:Data:140', 'Currency:Data:140', 'Status:Data:140'], [[r.name] + [getattr(r,x) for x in ['difference_type', 'severity', 'origin_company', 'destination_company', 'amount', 'currency', 'status']] for r in rows]
