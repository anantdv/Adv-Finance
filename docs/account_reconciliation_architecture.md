# Balance Sheet Account Reconciliation Architecture

Account Reconciliation is a control and evidence layer over ERPNext General
Ledger. It does not post accounting entries and does not modify submitted
ERPNext accounting documents.

## ERPNext Mechanisms Reused

- `GL Entry` read-only balances for opening, period debit, period credit, and
  closing balance.
- Party-specific GL movements for AP and AR subledger providers.
- Standard Frappe DocTypes, child tables, reports, permissions, versioning, and
  attachments.

## ADV Finance DocTypes

- `Account Reconciliation Template` defines account method, frequency,
  tolerance, evidence requirements, responsibility, and risk.
- `Account Reconciliation Period` batches month-end reconciliations.
- `Account Reconciliation` stores GL balance, supporting balance, differences,
  review, approval, evidence, and close/reopen state.
- `Account Reconciliation Item` stores supporting lines and reconciling items,
  including ageing and carry-forward links.

## Provider Strategy

Providers implement a small contract: validate, load supporting balance, and
load supporting items. Initial providers include Manual Supporting Balance,
Uploaded Schedule CSV, Accounts Payable, and Accounts Receivable. ERPNext-facing
queries remain isolated in `adv_finance.compatibility.erpnext_v16`.

## Balance Sign Convention

GL balances use `debit - credit`. Debit balances are positive and credit
balances are negative. The app stores actual differences and does not silently
invert or force balances to zero.

## Current Validation Constraint

This local workspace does not contain a Frappe/ERPNext v16 bench, so GL/AP/AR
provider outputs must be validated on the deployment server against ERPNext
General Ledger, Trial Balance, Accounts Payable, and Accounts Receivable reports.
