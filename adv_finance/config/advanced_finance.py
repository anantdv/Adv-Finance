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
            ],
        }
    ]
