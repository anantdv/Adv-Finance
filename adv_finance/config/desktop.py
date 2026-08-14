from frappe import _


def get_data():
    return [
        {
            "module_name": "Advanced Finance",
            "category": "Modules",
            "color": "blue",
            "icon": "octicon octicon-checklist",
            "type": "module",
            "label": _("Advanced Finance"),
            "description": _("Advanced finance controls and supplier reconciliation tools."),
        }
    ]
