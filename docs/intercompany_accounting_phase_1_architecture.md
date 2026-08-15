# Intercompany Accounting Phase 1 Architecture

## Decision Note

1. ERPNext remains authoritative for `GL Entry`, `Journal Entry`, `Sales Invoice`, `Purchase Invoice`, `Payment Entry`, companies, and the chart of accounts.
2. ADV Finance stores intercompany registry, matches, differences, settlements, FX analysis, and elimination candidates only.
3. Due-to/due-from reconciliation reads configured partner receivable/payable accounts and compares ERPNext GL balances.
4. Matching uses deterministic rules: reference number, amount within tolerance, currency, date, partner, and description. It supports one-to-one, one-to-many, many-to-one, and many-to-many.
5. Settlement is tracked in ADV Finance and may reference standard ERPNext `Payment Entry`; ADV Finance does not create a separate payment ledger.
6. FX translation preserves original amount and currency, records reporting currency rate and FX difference, and never overwrites accounting values.
7. Elimination candidates are preparation records only. Phase 1 does not post elimination journals or consolidated ledgers.
8. Group Close Readiness checks unmatched transactions, unsettled items, open differences, and ready elimination candidates.

## Deferred

Financial Consolidation, consolidated financial statements, multi-GAAP reporting, and actual elimination journal posting are deferred to the next group-finance phase.

## Safety

Intercompany matching, settlement tracking, difference resolution, and elimination preparation never insert, update, or delete `GL Entry` or `Payment Ledger Entry`.
