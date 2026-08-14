from frappe import _


def get_data():
    return [
        {
            "label": _("Accounts Payable"),
            "icon": "octicon octicon-checklist",
            "items": [
                {
                    "type": "doctype",
                    "name": "Supplier Reconciliation",
                    "label": _("Supplier Reconciliation"),
                    "description": _("Upload and reconcile supplier statements against ERPNext ledger entries."),
                    "onboard": 1,
                },
                {
                    "type": "doctype",
                    "name": "Supplier Statement Template",
                    "label": _("Supplier Statement Template"),
                    "description": _("Configure CSV and XLSX supplier statement column mappings."),
                    "onboard": 1,
                },
                {
                    "type": "doctype",
                    "name": "Payment Proposal",
                    "label": _("Payment Proposal"),
                    "description": _("Select due supplier invoices for controlled payment approval."),
                    "onboard": 1,
                },
                {
                    "type": "doctype",
                    "name": "Payment Run",
                    "label": _("Payment Run"),
                    "description": _("Group approved payment selections and create draft Payment Entries."),
                    "onboard": 1,
                },
                {
                    "type": "doctype",
                    "name": "Payment Hold",
                    "label": _("Payment Holds"),
                    "description": _("Block supplier or invoice payments with an auditable reason."),
                    "onboard": 1,
                },
                {
                    "type": "page",
                    "name": "supplier-reconciliation-manual",
                    "label": _("Supplier Reconciliation Manual"),
                    "description": _("User guide and monthly reconciliation workflow."),
                    "onboard": 1,
                },
                {
                    "type": "report",
                    "name": "Supplier Reconciliation History",
                    "doctype": "Supplier Reconciliation",
                    "label": _("Supplier Reconciliation History"),
                    "is_query_report": True,
                    "onboard": 0,
                },
                {
                    "type": "report",
                    "name": "Open Supplier Reconciliation Exceptions",
                    "doctype": "Supplier Reconciliation",
                    "label": _("Open Supplier Reconciliation Exceptions"),
                    "is_query_report": True,
                    "onboard": 0,
                },
                {
                    "type": "report",
                    "name": "Payment Proposal Register",
                    "doctype": "Payment Proposal",
                    "label": _("Payment Proposal Register"),
                    "is_query_report": True,
                    "onboard": 0,
                },
                {
                    "type": "report",
                    "name": "Payment Run Register",
                    "doctype": "Payment Run",
                    "label": _("Payment Run Register"),
                    "is_query_report": True,
                    "onboard": 0,
                },
                {
                    "type": "report",
                    "name": "Payment Hold Register",
                    "doctype": "Payment Hold",
                    "label": _("Payment Hold Register"),
                    "is_query_report": True,
                    "onboard": 0,
                },
                {
                    "type": "report",
                    "name": "Payment Run Exceptions",
                    "doctype": "Payment Run",
                    "label": _("Payment Run Exceptions"),
                    "is_query_report": True,
                    "onboard": 0,
                },
            ],
        }
    ]
