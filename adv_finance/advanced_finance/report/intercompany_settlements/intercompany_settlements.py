from __future__ import annotations
import frappe

def execute(filters=None):
    rows=frappe.get_all("Intercompany Settlement",filters={},fields=['name', 'origin_company', 'destination_company', 'settlement_date', 'expected_settlement_amount', 'actual_settlement_amount', 'outstanding_amount', 'status'],order_by="modified desc")
    return ["Document:Link/Intercompany Settlement:190"] + ['Origin Company:Data:140', 'Destination Company:Data:140', 'Settlement Date:Data:140', 'Expected Settlement Amount:Data:140', 'Actual Settlement Amount:Data:140', 'Outstanding Amount:Data:140', 'Status:Data:140'], [[r.name] + [getattr(r,x) for x in ['origin_company', 'destination_company', 'settlement_date', 'expected_settlement_amount', 'actual_settlement_amount', 'outstanding_amount', 'status']] for r in rows]
