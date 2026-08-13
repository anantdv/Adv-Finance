from __future__ import annotations

from collections import defaultdict
from datetime import date
from decimal import Decimal
from typing import Any


AMOUNT_TOLERANCE = Decimal("0.01")


def run_exact_matching(statement_lines: list[Any], erp_lines: list[Any]) -> list[dict[str, Any]]:
    matches: list[dict[str, Any]] = []
    erp_lookup = _build_erp_lookup(erp_lines)
    used_statement = set()
    used_erp = set()

    for statement in statement_lines:
        if not statement.normalized_reference:
            continue
        key = (statement.normalized_reference, _quantize(statement.amount))
        candidates = [line for line in erp_lookup.get(key, []) if line.name not in used_erp]
        if len(candidates) != 1:
            continue

        candidate = candidates[0]
        if _sign_conflicts(statement.amount, candidate.amount):
            continue

        matches.append(
            {
                "match_rule": "Reference + Exact Amount",
                "confidence": 100,
                "status": "Auto Accepted",
                "statement_total": statement.amount,
                "erp_total": candidate.amount,
                "difference": Decimal("0"),
                "statement_lines": [statement],
                "erp_lines": [candidate],
            }
        )
        used_statement.add(statement.name)
        used_erp.add(candidate.name)

    return matches


def suggest_matches(statement_lines: list[Any], erp_lines: list[Any]) -> list[dict[str, Any]]:
    suggestions = []
    for statement in statement_lines:
        if statement.match_status == "Matched":
            continue
        scored = []
        for erp_line in erp_lines:
            if erp_line.match_status == "Matched":
                continue
            score = score_candidate(statement, erp_line)
            if score >= 50:
                scored.append((score, erp_line))
        scored.sort(key=lambda item: item[0], reverse=True)
        if scored and (len(scored) == 1 or scored[0][0] > scored[1][0]):
            score, erp_line = scored[0]
            suggestions.append(
                {
                    "match_rule": "Suggested Score",
                    "confidence": score,
                    "status": "Suggested",
                    "statement_total": statement.amount,
                    "erp_total": erp_line.amount,
                    "difference": Decimal(str(statement.amount or 0)) - Decimal(str(erp_line.amount or 0)),
                    "statement_lines": [statement],
                    "erp_lines": [erp_line],
                }
            )
    return suggestions


def score_candidate(statement, erp_line) -> int:
    score = 0
    if statement.normalized_reference and statement.normalized_reference == erp_line.normalized_reference:
        score += 60
    elif statement.normalized_reference and erp_line.normalized_reference:
        if statement.normalized_reference in erp_line.normalized_reference or erp_line.normalized_reference in statement.normalized_reference:
            score += 40

    amount_delta = abs(Decimal(str(statement.amount or 0)) - Decimal(str(erp_line.amount or 0)))
    if amount_delta == 0:
        score += 30
    elif amount_delta <= AMOUNT_TOLERANCE:
        score += 25

    date_delta = _date_delta(statement.transaction_date, erp_line.posting_date)
    if date_delta == 0:
        score += 10
    elif date_delta <= 1:
        score += 8
    elif date_delta <= 3:
        score += 5
    elif date_delta <= 7:
        score += 2

    return min(score, 100)


def _build_erp_lookup(erp_lines: list[Any]) -> dict[tuple[str, Decimal], list[Any]]:
    lookup = defaultdict(list)
    for line in erp_lines:
        if line.normalized_reference:
            lookup[(line.normalized_reference, _quantize(line.amount))].append(line)
    return lookup


def _quantize(value) -> Decimal:
    return Decimal(str(value or 0)).quantize(AMOUNT_TOLERANCE)


def _sign_conflicts(statement_amount, erp_amount) -> bool:
    return (Decimal(str(statement_amount or 0)) > 0) != (Decimal(str(erp_amount or 0)) > 0)


def _date_delta(left: date | None, right: date | None) -> int:
    if not left or not right:
        return 9999
    return abs((left - right).days)
