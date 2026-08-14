# ADV Finance

ADV Finance is a Frappe/ERPNext v16 application for advanced finance controls.
The first module is Supplier Statement Reconciliation for Accounts Payable teams.

It lets users upload supplier statement files, parse raw and normalized statement
transactions, load the matching ERPNext supplier ledger, run deterministic
matching, classify exceptions, and close reconciliations with an audit trail.

## Compatibility

- Frappe: v16
- ERPNext: v16
- Database: MariaDB-compatible Frappe deployment
- UI: Standard Frappe Desk

This app does not modify ERPNext core and never writes GL Entry or Payment
Ledger Entry records directly. Control workflows may create standard draft
ERPNext accounting documents, but submission and GL posting remain in ERPNext.
Supplier Reconciliation is read-only from a General Ledger perspective.

## Installation

```bash
cd ~/frappe-bench
bench get-app https://github.com/<organisation>/adv_finance.git
bench --site <site-name> install-app adv_finance
bench --site <site-name> migrate
bench build --app adv_finance
bench restart
```

## Development Installation

```bash
cd ~/frappe-bench
bench get-app /path/to/adv_finance
bench --site <site-name> install-app adv_finance
bench --site <site-name> set-config developer_mode 1
bench --site <site-name> migrate
```

## Roles

- Supplier Reconciliation User: create, parse, match, review, and resolve assigned
  reconciliation work.
- Supplier Reconciliation Manager: close and reopen reconciliations, accept
  non-zero differences, and override reviewed matches.

## Supplier Statement Template

Create one template for each recurring supplier statement layout. Configure the
file type, header row, sheet name, date/decimal separators, and source columns
for reference, description, debit, credit, amount, balance, and transaction type.

Example CSV mapping:

- Date column: `Date`
- Reference column: `Invoice No`
- Description column: `Description`
- Debit column: `Debit`
- Credit column: `Credit`
- Balance column: `Balance`

## Workflow

Create Reconciliation -> Upload Statement -> Parse -> Load ERP Ledger -> Run
Reconciliation -> Review Suggested Matches -> Resolve Exceptions -> Close.

The Advanced Finance workspace includes a Supplier Reconciliation Manual page
with setup steps, monthly workflow guidance, status meanings, exception handling,
and closing rules.

## Advanced Finance Module Map

Implemented:

- Supplier Reconciliation
- Payment Hold
- Payment Proposal
- Payment Run
- Account Reconciliation Template
- Account Reconciliation
- Account Reconciliation Period
- Accrual Management
- Month-End Financial Close Management
- Accounts Receivable Collections and Credit Control

In development:

- Payment Order integration
- Expanded approval workflows
- ERPNext v16 integration validation for account reconciliation providers
- ERPNext v16 integration validation for accrual Journal Entry reversal
- ERPNext v16 integration validation for Financial Close Period Closing Voucher and sidebar
- ERPNext v16 integration validation for AR ageing, receipts, and credit-note creation

Planned:

- AR Collections and Credit Control
- Treasury and Cash Forecasting
- Budget Forecast and Commitment Accounting
- Intercompany Reconciliation
- Consolidation

Accounting guarantee: ADV Finance never directly posts GL Entries. All
accounting postings are generated through standard ERPNext accounting documents.

## Accounting Safety

ADV Finance never inserts, updates, or deletes `GL Entry` or `Payment Ledger
Entry` records. Supplier Reconciliation reads ERPNext accounting data and records
the reconciliation result in ADV Finance DocTypes only. Accrual Management
creates draft ERPNext Journal Entries for accruals and reversals, and ERPNext
remains responsible for validation, submission, and GL posting.

## Testing

Inside a Frappe v16 bench with ERPNext v16 installed:

```bash
bench --site <test-site> run-tests --app adv_finance
```

The test suite includes a GL invariance test to ensure reconciliation does not
create accounting postings.

## Uninstall Considerations

Uninstalling the app removes the custom DocTypes and their data according to
Frappe uninstall behavior. Back up sites before uninstalling from production.

## Current Limitations

- CSV and XLSX are supported. PDF and OCR are intentionally out of scope.
- The initial implementation posts no accounting corrections.
- ERPNext v16 ledger extraction must be validated in a real v16 bench because
  this workspace does not include Frappe/ERPNext source.
