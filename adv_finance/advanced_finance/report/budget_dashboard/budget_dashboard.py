from __future__ import annotations
import frappe

def execute(filters=None):
    filters=filters or {}; company=filters.get('company')
    metrics=[['Approved Budget Plans',frappe.db.count('Budget Plan',{'company':company,'status':'Approved'})],['Open Reservations',frappe.db.count('Budget Reservation',{'company':company,'status':['in',['Approved','Partially Consumed']]})],['Open Commitments',frappe.db.count('Budget Commitment',{'company':company,'status':'Open'})],['Pending Overrides',frappe.db.count('Budget Override Request',{'company':company,'status':'Pending'})]]
    return ["Metric:Data:240","Value:Int:120"], metrics
