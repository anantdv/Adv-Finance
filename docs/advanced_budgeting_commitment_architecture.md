# Advanced Budgeting and Commitment Accounting Architecture

## Decision Note

1. Approved accounting budget should remain standard ERPNext Budget where standard validation is needed. ADV Finance adds the planning, versioning, commitment, reforecast, and available-budget layer.
2. ADV Finance `Budget Plan` is the managed planning source. Approved plans can publish a draft ERPNext `Budget`; ERPNext remains responsible for standard budget behavior and submission.
3. Actual spend is derived from ERPNext `GL Entry`, using account sign conventions: expense and capex consume debit minus credit; income consumes credit minus debit.
4. Purchase Order commitment is calculated as current submitted PO line amount less billed amount. Partial invoicing reduces open commitment and GL actuals carry actual consumption.
5. Material Request pre-commitment is optional and controlled by company-specific `Budget Settings`.
6. Source precedence prevents double counting: Material Request pre-commitment falls away when PO exists; PO commitment falls as Purchase Invoice/GL actual increases; cancelled documents are excluded.
7. Available Budget is calculated as approved budget plus supplements plus transfers in, less transfers out, actual spend, open commitments, enabled pre-commitments, and reservations.
8. Budget validation extends ERPNext controls through `validate_budget_availability`; it returns an explainable result and does not replace ERPNext standard budget validation.
9. Transaction override is one-time, source-document-specific, amount-limited, validity-limited, and can be marked Used only once.
10. Treasury can consume explicit budget cash projection hooks later, but Phase 1 does not assume accounting budget equals cash timing. Financial Close consumes budgeting readiness for pending overrides, stale commitments, and approved plan coverage.

## Safety

Budget Plans, Reservations, Transfers, Supplements, Overrides, and Manual Commitments do not create GL Entries or Payment Ledger Entries. Standard ERPNext documents remain the only path to accounting postings.

## Deferred

Phase 2 can add deeper `doc_events` enforcement, Accounting Dimension API discovery from live ERPNext, automated budget notifications, complex approval thresholds, and richer Treasury cash timing from budget period lines.
