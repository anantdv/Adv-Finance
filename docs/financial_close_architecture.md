# Month-End Financial Close Architecture

ADV Finance Financial Close is a control layer over ERPNext. It coordinates close tasks, owners, dependencies, evidence, readiness checks, review, approval, certification, and final close status. It does not write GL Entry records and does not submit ERPNext accounting documents.

## Modeling

- `Financial Close Template` stores reusable close procedures.
- `Financial Close Template Task` stores task defaults, risk, automation provider, and dependency task codes.
- `Financial Close Period` represents one company period close.
- `Financial Close Task` is a standalone assigned task linked to a close period.
- `Financial Close Task Dependency` stores task dependencies copied from the template.
- `Financial Close Exception` and `Late Posting Exception` store close-level references without duplicating underlying module records.

## Readiness

Readiness providers are isolated under `adv_finance.services.financial_close.providers`. The first providers integrate Supplier Reconciliation, Account Reconciliation, Accrual Management, Bank Transaction, Fixed Assets, Inventory, HRMS Payroll, FX Revaluation, generic ERPNext document checks, and Period Closing Voucher status. Provider failures fail closed and leave tasks incomplete.

## ERPNext Accounting

The close workflow itself does not affect GL. Period Closing Voucher integration creates only a draft ERPNext `Period Closing Voucher` through the compatibility layer. ERPNext remains responsible for validation, submission, and GL posting.

## Late Postings

Late posting detection scans submitted GL Entry rows posted inside the close period but created after the close review/approval/certification cutoff. It creates `Late Posting Exception` records for review and does not modify accounting data.

## Group Close Readiness

The design keeps each `Financial Close Period` company-specific. A future Group Close can depend on multiple company close periods without changing the task/provider architecture.

## Local Constraint

This workspace does not include a live Frappe/ERPNext v16 bench. Period Closing Voucher fields, Accounting Period behavior, Bank Transaction status values, Exchange Rate Revaluation, Asset, Stock, and HRMS checks must be validated on the deployment server.
