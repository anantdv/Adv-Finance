from __future__ import annotations

from collections import Counter, defaultdict
from decimal import Decimal
from typing import Any


def generate_exception_rows(reconciliation, statement_lines: list[Any], erp_lines: list[Any]) -> list[dict[str, Any]]:
    exceptions = []

    if Decimal(str(reconciliation.statement_opening_balance or 0)) != Decimal(str(reconciliation.erp_opening_balance or 0)):
        exceptions.append(
            {
                "exception_type": "Opening Balance Difference",
                "description": "Supplier statement opening balance differs from ERP opening balance.",
                "statement_amount": reconciliation.statement_opening_balance,
                "erp_amount": reconciliation.erp_opening_balance,
                "difference": Decimal(str(reconciliation.statement_opening_balance or 0))
                - Decimal(str(reconciliation.erp_opening_balance or 0)),
                "status": "Open",
            }
        )

    for key, count in Counter(_line_key(line) for line in statement_lines if _line_key(line)).items():
        if count > 1:
            exceptions.append(
                {
                    "exception_type": "Duplicate Statement Transaction",
                    "reference": key[0],
                    "statement_amount": key[1],
                    "description": "Same reference and amount appears multiple times on the statement.",
                    "status": "Open",
                }
            )

    erp_by_reference = defaultdict(list)
    for line in erp_lines:
        if line.normalized_reference:
            erp_by_reference[line.normalized_reference].append(line)

    for statement in statement_lines:
        if statement.match_status == "Matched":
            continue
        candidates = erp_by_reference.get(statement.normalized_reference, [])
        if candidates:
            closest = min(candidates, key=lambda item: abs(Decimal(str(item.amount or 0)) - Decimal(str(statement.amount or 0))))
            exceptions.append(
                {
                    "exception_type": "Amount Mismatch",
                    "statement_line": statement.name,
                    "reference": statement.reference,
                    "statement_amount": statement.amount,
                    "erp_amount": closest.amount,
                    "difference": Decimal(str(statement.amount or 0)) - Decimal(str(closest.amount or 0)),
                    "description": "Reference matches an ERP transaction but the amount differs.",
                    "suggested_action": "Review source documents and correct ERP or supplier statement outside this reconciliation.",
                    "status": "Open",
                }
            )
        else:
            exceptions.append(
                {
                    "exception_type": "Statement Only",
                    "statement_line": statement.name,
                    "reference": statement.reference,
                    "statement_amount": statement.amount,
                    "description": "Statement transaction has no ERP counterpart.",
                    "suggested_action": "Review whether the supplier transaction was received, posted, or belongs to another period.",
                    "status": "Open",
                }
            )

    for erp_line in erp_lines:
        if erp_line.match_status == "Matched":
            continue
        exceptions.append(
            {
                "exception_type": "ERP Only",
                "erp_ledger_line": erp_line.name,
                "reference": erp_line.supplier_invoice_number or erp_line.reference_no or erp_line.voucher_no,
                "erp_amount": erp_line.amount,
                "description": "ERP supplier ledger transaction has no supplier statement counterpart.",
                "status": "Open",
            }
        )

    return exceptions


def _line_key(line) -> tuple[str, Decimal] | None:
    if not line.normalized_reference:
        return None
    return (line.normalized_reference, Decimal(str(line.amount or 0)))
