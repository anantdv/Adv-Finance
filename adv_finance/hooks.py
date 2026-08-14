app_name = "adv_finance"
app_title = "ADV Finance"
app_publisher = "Anantdv"
app_description = "Advanced finance controls and reconciliation extensions for ERPNext"
app_email = "support@anantdv.com"
app_license = "MIT"
required_apps = ["frappe", "erpnext"]

app_include_js = []
fixtures = [
    {
        "dt": "Role",
        "filters": [
            [
                "name",
                "in",
                [
                    "Supplier Reconciliation User",
                    "Supplier Reconciliation Manager",
                    "Financial Close User",
                    "Financial Close Manager",
                ],
            ]
        ],
    },
]

before_install = "adv_finance.install.before_install"
after_install = "adv_finance.install.after_install"
after_migrate = "adv_finance.install.after_migrate"

doctype_js = {
    "Supplier Reconciliation": "advanced_finance/doctype/supplier_reconciliation/supplier_reconciliation.js",
    "Payment Proposal": "advanced_finance/doctype/payment_proposal/payment_proposal.js",
    "Payment Run": "advanced_finance/doctype/payment_run/payment_run.js",
    "Account Reconciliation": "advanced_finance/doctype/account_reconciliation/account_reconciliation.js",
    "Account Reconciliation Period": "advanced_finance/doctype/account_reconciliation_period/account_reconciliation_period.js",
    "Accrual": "advanced_finance/doctype/accrual/accrual.js",
    "Financial Close Period": "advanced_finance/doctype/financial_close_period/financial_close_period.js",
    "Financial Close Task": "advanced_finance/doctype/financial_close_task/financial_close_task.js",
}

doctype_list_js = {
    "Supplier Reconciliation": "advanced_finance/doctype/supplier_reconciliation/supplier_reconciliation_list.js",
    "Payment Proposal": "advanced_finance/doctype/payment_proposal/payment_proposal_list.js",
    "Payment Run": "advanced_finance/doctype/payment_run/payment_run_list.js",
    "Account Reconciliation": "advanced_finance/doctype/account_reconciliation/account_reconciliation_list.js",
    "Accrual": "advanced_finance/doctype/accrual/accrual_list.js",
    "Financial Close Period": "advanced_finance/doctype/financial_close_period/financial_close_period_list.js",
    "Financial Close Task": "advanced_finance/doctype/financial_close_task/financial_close_task_list.js",
}

scheduler_events = {
    "daily": [
        "adv_finance.services.accrual.accrual_reversal_service.create_due_reversal_drafts",
    ]
}
