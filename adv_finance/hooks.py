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
                    "AR Collection User",
                    "AR Collection Manager",
                    "Credit Controller",
                    "Credit Manager",
                    "Treasury User",
                    "Treasury Manager",
                    "Budget Preparer",
                    "Budget Owner",
                    "Budget Reviewer",
                    "Budget Manager",
                    "Budget Override Approver",
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
    "Collection Case": "advanced_finance/doctype/collection_case/collection_case.js",
    "Promise to Pay": "advanced_finance/doctype/promise_to_pay/promise_to_pay.js",
    "Customer Dispute": "advanced_finance/doctype/customer_dispute/customer_dispute.js",
    "Credit Review": "advanced_finance/doctype/credit_review/credit_review.js",
    "Credit Hold": "advanced_finance/doctype/credit_hold/credit_hold.js",
    "Credit Override Request": "advanced_finance/doctype/credit_override_request/credit_override_request.js",
    "Treasury Account": "advanced_finance/doctype/treasury_account/treasury_account.js",
    "Cash Forecast": "advanced_finance/doctype/cash_forecast/cash_forecast.js",
    "Treasury Forecast Item": "advanced_finance/doctype/treasury_forecast_item/treasury_forecast_item.js",
    "Cash Forecast Scenario": "advanced_finance/doctype/cash_forecast_scenario/cash_forecast_scenario.js",
    "Treasury Liquidity Threshold": "advanced_finance/doctype/treasury_liquidity_threshold/treasury_liquidity_threshold.js",
    "Treasury Forecast Exception": "advanced_finance/doctype/treasury_forecast_exception/treasury_forecast_exception.js",
    "Treasury Settings": "advanced_finance/doctype/treasury_settings/treasury_settings.js",
    "Budget Plan": "advanced_finance/doctype/budget_plan/budget_plan.js",
    "Manual Budget Commitment": "advanced_finance/doctype/manual_budget_commitment/manual_budget_commitment.js",
    "Budget Reservation": "advanced_finance/doctype/budget_reservation/budget_reservation.js",
    "Budget Transfer": "advanced_finance/doctype/budget_transfer/budget_transfer.js",
    "Budget Supplement": "advanced_finance/doctype/budget_supplement/budget_supplement.js",
    "Budget Control Rule": "advanced_finance/doctype/budget_control_rule/budget_control_rule.js",
    "Budget Override Request": "advanced_finance/doctype/budget_override_request/budget_override_request.js",
    "Budget Settings": "advanced_finance/doctype/budget_settings/budget_settings.js",
}

doctype_list_js = {
    "Supplier Reconciliation": "advanced_finance/doctype/supplier_reconciliation/supplier_reconciliation_list.js",
    "Payment Proposal": "advanced_finance/doctype/payment_proposal/payment_proposal_list.js",
    "Payment Run": "advanced_finance/doctype/payment_run/payment_run_list.js",
    "Account Reconciliation": "advanced_finance/doctype/account_reconciliation/account_reconciliation_list.js",
    "Accrual": "advanced_finance/doctype/accrual/accrual_list.js",
    "Financial Close Period": "advanced_finance/doctype/financial_close_period/financial_close_period_list.js",
    "Financial Close Task": "advanced_finance/doctype/financial_close_task/financial_close_task_list.js",
    "Collection Case": "advanced_finance/doctype/collection_case/collection_case_list.js",
    "Promise to Pay": "advanced_finance/doctype/promise_to_pay/promise_to_pay_list.js",
    "Customer Dispute": "advanced_finance/doctype/customer_dispute/customer_dispute_list.js",
    "Credit Review": "advanced_finance/doctype/credit_review/credit_review_list.js",
    "Credit Hold": "advanced_finance/doctype/credit_hold/credit_hold_list.js",
    "Credit Override Request": "advanced_finance/doctype/credit_override_request/credit_override_request_list.js",
    "Treasury Account": "advanced_finance/doctype/treasury_account/treasury_account_list.js",
    "Cash Forecast": "advanced_finance/doctype/cash_forecast/cash_forecast_list.js",
    "Treasury Forecast Item": "advanced_finance/doctype/treasury_forecast_item/treasury_forecast_item_list.js",
    "Cash Forecast Scenario": "advanced_finance/doctype/cash_forecast_scenario/cash_forecast_scenario_list.js",
    "Treasury Liquidity Threshold": "advanced_finance/doctype/treasury_liquidity_threshold/treasury_liquidity_threshold_list.js",
    "Treasury Forecast Exception": "advanced_finance/doctype/treasury_forecast_exception/treasury_forecast_exception_list.js",
    "Treasury Settings": "advanced_finance/doctype/treasury_settings/treasury_settings_list.js",
    "Budget Plan": "advanced_finance/doctype/budget_plan/budget_plan_list.js",
    "Manual Budget Commitment": "advanced_finance/doctype/manual_budget_commitment/manual_budget_commitment_list.js",
    "Budget Reservation": "advanced_finance/doctype/budget_reservation/budget_reservation_list.js",
    "Budget Transfer": "advanced_finance/doctype/budget_transfer/budget_transfer_list.js",
    "Budget Supplement": "advanced_finance/doctype/budget_supplement/budget_supplement_list.js",
    "Budget Control Rule": "advanced_finance/doctype/budget_control_rule/budget_control_rule_list.js",
    "Budget Override Request": "advanced_finance/doctype/budget_override_request/budget_override_request_list.js",
    "Budget Settings": "advanced_finance/doctype/budget_settings/budget_settings_list.js",
}

scheduler_events = {
    "daily": [
        "adv_finance.services.accrual.accrual_reversal_service.create_due_reversal_drafts",
        "adv_finance.services.accounts_receivable.promise_fulfilment_service.process_broken_promises",
    ]
}
