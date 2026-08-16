# Remaining Finance Controls Architecture

## Decision Note

1. AP/AR ageing remarks are stored in `Finance Ageing Remark`, but AR reports first prefer live `Customer Dispute`, `Promise to Pay`, and `Collection Activity`; AP reports first prefer live `Payment Hold` and supplier-reconciliation exceptions.
2. EFT Requisition and EFT Remittance Advice are standard Frappe print formats. No parallel payment accounting document is created.
3. Remittance advice reads ERPNext `Payment Entry.references` allocations so invoice settlement details remain sourced from ERPNext.
4. Customer dormancy is based on business activity dates: submitted Sales Invoice, submitted Payment Entry receipt, and submitted Delivery Note.
5. Demand letters use ADV templates/registers for control and audit while staying aligned with ERPNext Dunning concepts. They do not post accounting.
6. The FX Adjusted Invoice Register is read-only and displays FCY outstanding, carrying PGK, month-end spot PGK, and variance while linking ERPNext revaluation references where available.
7. Prior-period approvals extend ERPNext period controls through narrow, time-limited ADV exception requests. They do not globally reopen periods.
8. Supplier onboarding/change controls create maker-checker request records and can create a standard ERPNext Supplier only after approval.
9. Branch reporting resolves an active Accounting Dimension named Branch when present; otherwise it falls back to Cost Center.
10. Branch totals come from read-only GL movement queries and should reconcile to ERPNext company totals when all branches are included.
11. Advanced Trial Balance is a new Script Report and does not modify ERPNext Trial Balance.
12. Budget columns consume the existing ADV Finance approved-budget service.

## Safety

These controls and reports do not insert, update, or delete `GL Entry`, `Payment Ledger Entry`, stock ledger, invoice outstanding amounts, or account balances. Posting remains the responsibility of standard ERPNext accounting documents.
