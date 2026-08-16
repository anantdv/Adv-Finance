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
                    "Intercompany Accountant",
                    "Intercompany Manager",
                    "Group Finance Manager",
                    "Group Accountant",
                    "Consolidation Reviewer",
                    "CFO",
                    "Auditor",
                    "AP User",
                    "AP Manager",
                    "AR User",
                    "AR Manager",
                    "Finance Controller",
                    "Finance Manager",
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
    "Intercompany Partner": "advanced_finance/doctype/intercompany_partner/intercompany_partner.js",
    "Intercompany Transaction": "advanced_finance/doctype/intercompany_transaction/intercompany_transaction.js",
    "Intercompany Match": "advanced_finance/doctype/intercompany_match/intercompany_match.js",
    "Intercompany Settlement": "advanced_finance/doctype/intercompany_settlement/intercompany_settlement.js",
    "Intercompany Difference": "advanced_finance/doctype/intercompany_difference/intercompany_difference.js",
    "Intercompany Elimination Candidate": "advanced_finance/doctype/intercompany_elimination_candidate/intercompany_elimination_candidate.js",
    "Consolidation Group": "advanced_finance/doctype/consolidation_group/consolidation_group.js",
    "Consolidation Period": "advanced_finance/doctype/consolidation_period/consolidation_period.js",
    "Trial Balance Snapshot": "advanced_finance/doctype/trial_balance_snapshot/trial_balance_snapshot.js",
    "Consolidation Adjustment": "advanced_finance/doctype/consolidation_adjustment/consolidation_adjustment.js",
    "Elimination Journal": "advanced_finance/doctype/elimination_journal/elimination_journal.js",
    "Consolidated Trial Balance Line": "advanced_finance/doctype/consolidated_trial_balance_line/consolidated_trial_balance_line.js",
    "Finance Ageing Remark": "advanced_finance/doctype/finance_ageing_remark/finance_ageing_remark.js",
    "Demand Letter Template": "advanced_finance/doctype/demand_letter_template/demand_letter_template.js",
    "Demand Letter": "advanced_finance/doctype/demand_letter/demand_letter.js",
    "Prior Period Posting Request": "advanced_finance/doctype/prior_period_posting_request/prior_period_posting_request.js",
    "Supplier Onboarding Request": "advanced_finance/doctype/supplier_onboarding_request/supplier_onboarding_request.js",
    "Supplier Change Request": "advanced_finance/doctype/supplier_change_request/supplier_change_request.js",
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
    "Intercompany Partner": "advanced_finance/doctype/intercompany_partner/intercompany_partner_list.js",
    "Intercompany Transaction": "advanced_finance/doctype/intercompany_transaction/intercompany_transaction_list.js",
    "Intercompany Match": "advanced_finance/doctype/intercompany_match/intercompany_match_list.js",
    "Intercompany Settlement": "advanced_finance/doctype/intercompany_settlement/intercompany_settlement_list.js",
    "Intercompany Difference": "advanced_finance/doctype/intercompany_difference/intercompany_difference_list.js",
    "Intercompany Elimination Candidate": "advanced_finance/doctype/intercompany_elimination_candidate/intercompany_elimination_candidate_list.js",
    "Consolidation Group": "advanced_finance/doctype/consolidation_group/consolidation_group_list.js",
    "Consolidation Period": "advanced_finance/doctype/consolidation_period/consolidation_period_list.js",
    "Trial Balance Snapshot": "advanced_finance/doctype/trial_balance_snapshot/trial_balance_snapshot_list.js",
    "Consolidation Adjustment": "advanced_finance/doctype/consolidation_adjustment/consolidation_adjustment_list.js",
    "Elimination Journal": "advanced_finance/doctype/elimination_journal/elimination_journal_list.js",
    "Consolidated Trial Balance Line": "advanced_finance/doctype/consolidated_trial_balance_line/consolidated_trial_balance_line_list.js",
    "Finance Ageing Remark": "advanced_finance/doctype/finance_ageing_remark/finance_ageing_remark_list.js",
    "Demand Letter Template": "advanced_finance/doctype/demand_letter_template/demand_letter_template_list.js",
    "Demand Letter": "advanced_finance/doctype/demand_letter/demand_letter_list.js",
    "Prior Period Posting Request": "advanced_finance/doctype/prior_period_posting_request/prior_period_posting_request_list.js",
    "Supplier Onboarding Request": "advanced_finance/doctype/supplier_onboarding_request/supplier_onboarding_request_list.js",
    "Supplier Change Request": "advanced_finance/doctype/supplier_change_request/supplier_change_request_list.js",
}

doc_events = {
    "Journal Entry": {"before_submit": "adv_finance.services.finance_controls.prior_period_service.validate_prior_period_posting"},
    "Purchase Invoice": {"before_submit": "adv_finance.services.finance_controls.prior_period_service.validate_prior_period_posting"},
    "Sales Invoice": {"before_submit": "adv_finance.services.finance_controls.prior_period_service.validate_prior_period_posting"},
    "Payment Entry": {"before_submit": "adv_finance.services.finance_controls.prior_period_service.validate_prior_period_posting"},
    "Stock Entry": {"before_submit": "adv_finance.services.finance_controls.prior_period_service.validate_prior_period_posting"},
    "Asset Transaction": {"before_submit": "adv_finance.services.finance_controls.prior_period_service.validate_prior_period_posting"},
}

scheduler_events = {
    "daily": [
        "adv_finance.services.accrual.accrual_reversal_service.create_due_reversal_drafts",
        "adv_finance.services.accounts_receivable.promise_fulfilment_service.process_broken_promises",
    ]
}
