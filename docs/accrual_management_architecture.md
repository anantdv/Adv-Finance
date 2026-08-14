# Accrual Management Architecture

ADV Finance Accrual Management is a control workflow over ERPNext Journal Entry
and Purchase Invoice. ERPNext remains the accounting engine.

## Journal Entry Creation

Approved accruals create a standard draft ERPNext `Journal Entry`:

- Dr Expense Account
- Cr Accrual Liability Account

ADV Finance never writes `GL Entry` directly. GL changes only occur when users
submit the standard ERPNext Journal Entry.

## Reversal Creation

The first implementation creates a standard draft reversing Journal Entry through
the same compatibility layer. It is idempotent and will not create a second
reversal if `reversal_journal_entry` already exists. ERPNext v16 reversal APIs
should be evaluated on the deployment bench and substituted if they provide a
safer native reversal mechanism.

## Actual Matching

Accrual matches are child records and support partial matching, one accrual to
many invoices, and many accruals to one invoice. Purchase Invoice item references
are stored so only the relevant expense line is matched.

## Variance Sign Convention

Variance = Actual Matched Amount - Accrual Amount Consumed.

- Positive variance means Under Accrued.
- Negative variance means Over Accrued.
- Within configured tolerance is stored without forcing the variance to zero.

## Account Reconciliation Integration

`get_accrual_supporting_balance(company, account, period_end)` exposes the
remaining accrual control balance for future Account Reconciliation providers.

## Close Readiness

`get_accrual_close_readiness(company, period_end)` returns counts for unapproved,
unposted, missing reversal, and material variance conditions for the future
Financial Close module.

## Local Constraint

This workspace does not include a Frappe/ERPNext v16 bench, so Journal Entry,
Purchase Invoice, and any native ERPNext reversal APIs must be validated on the
deployment server.
