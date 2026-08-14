# Accounts Receivable Collections Architecture

ADV Finance AR Collections is an operational control layer over ERPNext Sales Invoice, Payment Entry, Customer, Credit Limit, Dunning, Sales Order, Delivery Note, and Payment Ledger data. ERPNext remains the accounting source of truth.

## Authoritative Balances

Customer receivables are read from submitted ERPNext Sales Invoices with positive outstanding amounts. Collection Cases store refreshable snapshots for audit and display; live ERPNext outstanding remains authoritative.

## Promise Fulfilment

Promise to Pay records customer commitments without changing accounting. Fulfilment reads submitted ERPNext Payment Entries and allocations for the customer and promised invoices. Statuses are Kept, Partially Kept, Broken, Rescheduled, or Cancelled.

## Disputes

Customer Disputes track operationally disputed amounts. Disputes do not reduce Sales Invoice outstanding or GL. Collection Eligible Amount is an operational amount: ERP outstanding less active disputed amount. Draft credit notes are created only through standard ERPNext Sales Invoice return documents and are never submitted automatically.

## Credit Exposure

Credit exposure is calculated as receivables plus open Sales Orders plus unbilled Delivery Notes less advances/credits where reliable support is added. Components are returned separately for audit and to avoid hiding double-counting risks.

## Credit Holds and Overrides

Credit Holds and Credit Override Requests are controlled ADV Finance records. Enforcement is centralized in `validate_customer_credit_status`; no Sales Order or Delivery Note hooks are enabled in this first release until ERPNext v16 credit-control behavior is validated on the deployment bench.

## Financial Close

`get_ar_close_readiness(company, period_end)` exposes AR control readiness to the Financial Close provider. It focuses on accounting/control completeness, not forcing overdue receivables to zero.

## Local Constraint

This workspace does not include a live Frappe/ERPNext v16 bench. Sales Invoice, Payment Entry allocation, Customer Credit Limit, Dunning, Sales Order, Delivery Note, and Sales Invoice return behavior must be validated on the deployment server.
