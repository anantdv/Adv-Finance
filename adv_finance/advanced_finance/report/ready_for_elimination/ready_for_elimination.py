from __future__ import annotations
import frappe

def execute(filters=None):
    rows=frappe.get_all("Intercompany Elimination Candidate",filters={},fields=['name', 'origin_company', 'destination_company', 'amount', 'currency', 'status', 'blocking_reason'],order_by="modified desc")
    return ["Document:Link/Intercompany Elimination Candidate:190"] + ['Origin Company:Data:140', 'Destination Company:Data:140', 'Amount:Data:140', 'Currency:Data:140', 'Status:Data:140', 'Blocking Reason:Data:140'], [[r.name] + [getattr(r,x) for x in ['origin_company', 'destination_company', 'amount', 'currency', 'status', 'blocking_reason']] for r in rows]
