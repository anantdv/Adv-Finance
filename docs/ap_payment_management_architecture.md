# AP Payment Management Architecture

ADV Finance AP Payment Management is a control workflow over ERPNext Accounts
Payable. ERPNext remains the accounting engine and source of truth.

## ERPNext Mechanisms Reused

- `Purchase Invoice` for submitted supplier liabilities and outstanding amounts.
- `Payment Entry` for actual supplier payments.
- `Payment Entry Reference` for invoice allocations.
- `Bank Account` and linked ledger account for funding accounts.
- ERPNext validation and submit flow for accounting postings.

ADV Finance does not write `GL Entry`, `Payment Ledger Entry`, outstanding
amounts, paid amounts, or submitted accounting documents directly.

## New ADV Finance DocTypes

- `Payment Hold` stores reusable supplier or invoice holds.
- `Payment Proposal` stores a proposal header and selectable invoice snapshot.
- `Payment Proposal Item` stores invoice-level proposed and selected amounts.
- `Payment Run` groups approved proposal selections for execution.
- `Payment Run Item` stores supplier-level grouped payment totals.
- `Payment Run Invoice` stores invoice allocations inside a run.
- `Payment Run Exception` stores blocking issues found during preparation or
  execution.

## Duplicate-Payment Protection

Duplicate checks run during proposal generation, run creation, and payment entry
creation. The app checks whether an invoice is already selected in another open
proposal, included in another active run, linked to a submitted Payment Entry, or
represented in an ERPNext Payment Order where available. Blocking conditions are
recorded as exclusions or Payment Run Exceptions.

## Payment Entry Creation

Payment Runs create only draft ERPNext `Payment Entry` documents. Each draft is
grouped by company, supplier, currency, payable account, bank account, and mode
of payment, and references the selected Purchase Invoices using standard Payment
Entry references. Users submit Payment Entries through ERPNext.

## Payment Order Decision

The initial implementation creates draft Payment Entries directly. Payment Order
integration is reserved for the next hardening milestone after validation against
the installed ERPNext v16 Payment Order implementation.

## v16 Considerations

This local workspace does not include a Frappe/ERPNext bench, so live ERPNext v16
source inspection and site installation must be performed in the deployment
bench. ERPNext-specific calls are isolated in `adv_finance.compatibility.erpnext_v16`.
