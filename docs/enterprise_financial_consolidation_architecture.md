# Enterprise Financial Consolidation Architecture

## Decision Note

1. ERPNext remains authoritative for company ledgers, accounts, currencies, fiscal years, and posted accounting documents.
2. ADV Finance collects immutable `Trial Balance Snapshot` records from ERPNext GL totals for a consolidation period.
3. Currency translation preserves native balances and stores translated amount, exchange rate, and translation difference separately.
4. Ownership logic supports full consolidation, proportionate consolidation, equity method, and excluded companies.
5. Minority interest is calculated inside consolidated trial balance lines when a fully consolidated company is less than 100 percent owned.
6. `Elimination Journal` is a consolidation-only preparation document. It does not post, amend, or reverse ERPNext `GL Entry` or `Payment Ledger Entry`.
7. Consolidation adjustments are audit-only records used in consolidated reporting. They do not change company books.
8. Consolidated balance sheet, profit and loss, cash flow, ratio, ownership, translation, elimination, minority interest, and dashboard reports read ADV Finance consolidation records.
9. The financial close provider checks consolidation readiness from snapshots, consolidated lines, open adjustments, and blocked eliminations.

## Workflow

Create `Consolidation Group` -> create `Consolidation Period` -> collect trial balance snapshots -> translate balances -> prepare eliminations from intercompany candidates -> approve adjustments and eliminations -> run consolidation -> review consolidated reports -> approve, publish, and close the consolidation period.

## Safety

The consolidation module never inserts, updates, or deletes ERPNext `GL Entry` or `Payment Ledger Entry` records. ERPNext accounting remains unchanged by consolidation processing.
