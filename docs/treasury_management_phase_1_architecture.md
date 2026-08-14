# Treasury Management Phase 1 Architecture

## Decision Note

1. Authoritative bank/cash balance comes from ERPNext `GL Entry` summed by cash/bank account as of the reporting date. `Treasury Account` stores configuration only and never stores the actual balance.
2. Receipt forecast precedence is explicit: active or broken `Promise to Pay` first, then the unpromised and undisputed remainder of `Sales Invoice` outstanding. This prevents double counting promised cash.
3. Payment forecast precedence is explicit: `Payment Run`, then approved `Payment Proposal`, then open `Purchase Invoice`, then manual treasury commitments.
4. Double counting is prevented by tracking covered Sales Invoices and Purchase Invoices before lower-priority sources are added.
5. Multi-currency balances preserve native amount and convert to company currency using ERPNext exchange-rate mechanisms or `Currency Exchange`. Missing FX rates fail visibly.
6. `Cash Forecast` is a snapshot. Draft/Generated forecasts can be rebuilt with force; Approved forecasts are frozen and require a new version using `supersedes_forecast`.
7. Liquidity thresholds come from company-specific `Treasury Liquidity Threshold`, with account-level restricted cash and minimum balances respected in Daily Cash Position.
8. Forecast accuracy compares forecast weighted inflows/outflows with actual ERPNext `Payment Entry` cash movements for the forecast period.
9. Financial Close integration uses the `treasury` readiness provider: active treasury accounts, a period-covering forecast, and no unresolved critical treasury exceptions.
10. Phase 2 deliberately defers hedge accounting, derivatives, investment portfolios, automated bank transfers, cash sweep proposals, tax automation, loan accounting, and bank-dealing workflows.

## Accounting Safety

Treasury Phase 1 is planning-only. It does not insert, update, submit, or cancel `GL Entry`, `Payment Ledger Entry`, `Sales Invoice`, `Purchase Invoice`, `Payment Entry`, or `Bank Transaction`. Forecast items are planning records and do not create accounting documents.

## Source Precedence

Receipts:

- `Promise to Pay`
- `Sales Invoice` due-date or payment-behaviour forecast

Payments:

- `Payment Run`
- `Payment Proposal`
- `Purchase Invoice`
- `Treasury Forecast Item`

## Implemented Reports

- Treasury Dashboard
- Daily Cash Position
- Bank Position
- 13-Week Cash Forecast
- Cash Forecast Detail
- Liquidity Exceptions
- Forecast Exceptions
- Unforecast Cash Movements
- Cash Forecast Accuracy
- Cash Forecast Scenario Comparison
