from __future__ import annotations

import frappe

from adv_finance.services.erp_supplier_ledger import get_supplier_ledger
from adv_finance.services.exception_engine import generate_exception_rows
from adv_finance.services.matching_engine import run_exact_matching, suggest_matches
from adv_finance.services.statement_parser import parse_supplier_statement


def refresh_erp_ledger(name: str) -> dict:
    reconciliation = frappe.get_doc("Supplier Reconciliation", name)
    reconciliation.mark_processing("Matching", "Loading ERP supplier ledger.")
    try:
        ledger = get_supplier_ledger(
            reconciliation.company,
            reconciliation.supplier,
            reconciliation.payable_account,
            reconciliation.statement_from_date,
            reconciliation.statement_to_date,
        )
        reconciliation.set("erp_ledger_lines", [])
        for line in ledger["lines"]:
            reconciliation.append("erp_ledger_lines", line)
        reconciliation.update(
            {
                "erp_opening_balance": ledger["opening_balance"],
                "erp_closing_balance": ledger["closing_balance"],
                "currency": reconciliation.currency or ledger["currency"],
                "total_erp_lines": len(ledger["lines"]),
                "reconciliation_status": "Parsed",
            }
        )
        reconciliation.save()
        recalculate_summary(name)
        return {"erp_lines": len(ledger["lines"])}
    except Exception:
        frappe.db.rollback()
        _mark_failed(name)
        raise


def run_matching(name: str) -> dict:
    reconciliation = frappe.get_doc("Supplier Reconciliation", name)
    reconciliation.mark_processing("Matching", "Running deterministic matching.")
    try:
        _clear_matches(reconciliation)
        exact_matches = run_exact_matching(reconciliation.statement_lines, reconciliation.erp_ledger_lines)
        suggested = suggest_matches(reconciliation.statement_lines, reconciliation.erp_ledger_lines)
        for match in [*exact_matches, *suggested]:
            _append_match(reconciliation, match)
        reconciliation.reconciliation_status = "Review Required" if suggested else "Reconciled"
        reconciliation.save()
        recalculate_summary(name)
        return {"exact_matches": len(exact_matches), "suggested_matches": len(suggested)}
    except Exception:
        frappe.db.rollback()
        _mark_failed(name)
        raise


def run_reconciliation(name: str) -> dict:
    refresh_erp_ledger(name)
    matching = run_matching(name)
    exceptions = generate_exceptions(name)
    return {**matching, **exceptions}


def generate_exceptions(name: str) -> dict:
    reconciliation = frappe.get_doc("Supplier Reconciliation", name)
    reconciliation.set("exceptions", [])
    rows = generate_exception_rows(reconciliation, reconciliation.statement_lines, reconciliation.erp_ledger_lines)
    for row in rows:
        reconciliation.append("exceptions", row)
    if rows:
        reconciliation.reconciliation_status = "Review Required"
    reconciliation.save()
    recalculate_summary(name)
    return {"exceptions": len(rows)}


def recalculate_summary(name: str) -> dict:
    reconciliation = frappe.get_doc("Supplier Reconciliation", name)
    exact = sum(1 for row in reconciliation.reconciliation_matches if row.status == "Auto Accepted")
    suggested = sum(1 for row in reconciliation.reconciliation_matches if row.status == "Suggested")
    statement_unmatched = sum(1 for row in reconciliation.statement_lines if row.match_status != "Matched")
    erp_unmatched = sum(1 for row in reconciliation.erp_ledger_lines if row.match_status != "Matched")
    reconciliation.update(
        {
            "total_statement_lines": len(reconciliation.statement_lines),
            "total_erp_lines": len(reconciliation.erp_ledger_lines),
            "exact_matches": exact,
            "suggested_matches": suggested,
            "unmatched_statement_lines": statement_unmatched,
            "unmatched_erp_lines": erp_unmatched,
            "exception_count": len(reconciliation.exceptions),
        }
    )
    reconciliation.save()
    return {"updated": True}


def close_reconciliation(name: str) -> dict:
    if not frappe.has_role("Supplier Reconciliation Manager"):
        frappe.throw("Only Supplier Reconciliation Managers can close reconciliations.")
    reconciliation = frappe.get_doc("Supplier Reconciliation", name)
    reconciliation.set_closed()
    return {"closed": True}


def reopen_reconciliation(name: str) -> dict:
    if not frappe.has_role("Supplier Reconciliation Manager"):
        frappe.throw("Only Supplier Reconciliation Managers can reopen reconciliations.")
    frappe.db.set_value(
        "Supplier Reconciliation",
        name,
        {"reconciliation_status": "Review Required", "closed_by": None, "closed_on": None},
    )
    return {"reopened": True}


def parse_statement(name: str, force: bool = False) -> dict:
    return parse_supplier_statement(name, force=force)


def _clear_matches(reconciliation):
    reconciliation.set("reconciliation_matches", [])
    for row in reconciliation.statement_lines:
        row.match_status = "Unmatched"
        row.match_type = None
        row.match_confidence = None
    for row in reconciliation.erp_ledger_lines:
        row.match_status = "Unmatched"
        row.matched = 0


def _append_match(reconciliation, match: dict):
    child = reconciliation.append(
        "reconciliation_matches",
        {
            "match_rule": match["match_rule"],
            "confidence": match["confidence"],
            "status": match["status"],
            "statement_total": match["statement_total"],
            "erp_total": match["erp_total"],
            "difference": match["difference"],
        },
    )
    for statement in match["statement_lines"]:
        child.append("statement_lines", {"statement_line": statement.name})
        statement.match_status = "Matched" if match["status"] == "Auto Accepted" else "Suggested"
        statement.match_type = match["match_rule"]
        statement.match_confidence = match["confidence"]
    for erp_line in match["erp_lines"]:
        child.append("erp_lines", {"erp_ledger_line": erp_line.name})
        erp_line.match_status = "Matched" if match["status"] == "Auto Accepted" else "Suggested"
        erp_line.matched = 1


def _mark_failed(name: str):
    frappe.db.set_value(
        "Supplier Reconciliation",
        name,
        {
            "reconciliation_status": "Failed",
            "processing_message": frappe.get_traceback()[-1000:],
        },
    )
