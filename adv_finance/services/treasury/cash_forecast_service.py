from __future__ import annotations

from collections import defaultdict
from datetime import timedelta
from decimal import Decimal

import frappe
from frappe.utils import add_days, date_diff, getdate, now_datetime

from adv_finance.compatibility.erpnext_v16 import (
    get_active_promises_for_forecast,
    get_manual_treasury_items_for_forecast,
    get_open_purchase_invoices_for_forecast,
    get_open_sales_invoices_for_forecast,
    get_payment_proposals_for_forecast,
    get_payment_runs_for_forecast,
)
from adv_finance.services.accounts_receivable.ar_balance_service import ageing_bucket
from adv_finance.services.accounts_receivable.dispute_service import get_active_disputed_amounts
from adv_finance.services.accounts_receivable.payment_behaviour_service import get_payment_behaviour
from adv_finance.services.accounts_payable.payment_hold_service import get_active_hold
from adv_finance.services.treasury.cash_position_service import get_cash_position
from adv_finance.services.treasury.currency_service import convert_amount, get_company_currency
from adv_finance.services.treasury.liquidity_service import get_liquidity_threshold, liquidity_status
from adv_finance.services.treasury.settings import get_payment_probability, get_receipt_probability

RECEIPT_PRECEDENCE = ("Promise to Pay", "Sales Invoice")
PAYMENT_PRECEDENCE = ("Payment Run", "Payment Proposal", "Purchase Invoice", "Manual Forecast Item")


def generate_cash_forecast(name: str, force: bool = False) -> dict:
    forecast = frappe.get_doc("Cash Forecast", name)
    if forecast.status == "Approved" and force:
        frappe.throw("Approved forecasts are frozen. Create a new version instead of rebuilding the approved snapshot.")
    if getattr(forecast, "lines", None) and not force and forecast.status not in ("Draft", "Generated"):
        frappe.throw("Use force only on Draft or Generated forecasts, or create a new version.")
    if force and forecast.status not in ("Draft", "Generated"):
        frappe.throw("Only Draft or Generated forecasts can be rebuilt in place.")

    company_currency = forecast.base_currency or get_company_currency(forecast.company)
    forecast.base_currency = company_currency
    opening = get_cash_position(forecast.company, forecast.forecast_from, forecast.scenario)
    lines = build_forecast_lines(forecast.company, forecast.forecast_from, forecast.forecast_to, forecast.scenario, company_currency)
    weekly = aggregate_weekly(lines, opening["available_liquidity"], forecast.company, forecast.forecast_from)

    forecast.set("lines", [])
    for line in lines:
        forecast.append("lines", line)

    inflows = sum(Decimal(str(line["company_currency_amount"])) for line in lines if line["direction"] == "Inflow")
    outflows = sum(Decimal(str(line["company_currency_amount"])) for line in lines if line["direction"] == "Outflow")
    weighted_inflows = sum(Decimal(str(line["probability_weighted_amount"])) for line in lines if line["direction"] == "Inflow")
    weighted_outflows = sum(Decimal(str(line["probability_weighted_amount"])) for line in lines if line["direction"] == "Outflow")
    closing = Decimal(str(opening["available_liquidity"])) + weighted_inflows - weighted_outflows
    forecast.opening_cash = opening["available_liquidity"]
    forecast.total_forecast_inflows = inflows
    forecast.total_forecast_outflows = outflows
    forecast.projected_closing_cash = closing
    forecast.minimum_projected_cash = min((week["closing_cash"] for week in weekly), default=closing)
    forecast.maximum_projected_cash = max((week["closing_cash"] for week in weekly), default=closing)
    lowest = min(weekly, key=lambda row: row["closing_cash"], default=None)
    forecast.lowest_liquidity_date = lowest["week_start"] if lowest else forecast.forecast_to
    forecast.liquidity_shortfall = max((week["liquidity_shortfall"] for week in weekly), default=Decimal("0"))
    forecast.forecast_confidence = _average_probability(lines)
    forecast.generated_by = frappe.session.user
    forecast.generated_on = now_datetime()
    forecast.status = "Generated"
    forecast.save()
    create_forecast_exceptions(forecast, weekly, lines)
    return {"cash_forecast": forecast.name, "lines": len(lines), "weekly": weekly}


def build_forecast_lines(company: str, from_date, to_date, scenario=None, company_currency: str | None = None) -> list[dict]:
    company_currency = company_currency or get_company_currency(company)
    scenario_doc = _get_scenario(scenario)
    lines = []
    promised_by_sales_invoice = defaultdict(Decimal)
    covered_purchase_invoices = set()

    for row in get_active_promises_for_forecast(company, from_date, to_date):
        amount = Decimal(str(row.invoice_promised_amount or row.remaining_promised_amount or 0))
        if amount <= 0:
            continue
        expected_date, adjustment = _apply_scenario_date(row.promised_payment_date, "Inflow", scenario_doc)
        probability = _apply_probability(get_receipt_probability("", promised=True, broken=row.status == "Broken"), "Inflow", scenario_doc)
        line = _line(company_currency, expected_date, from_date, "Inflow", "Promise to Pay", "Promise to Pay", row.name, "Customer", row.customer, f"Promise to Pay {row.name}", row.currency, amount, probability, "Promise to Pay", row.promised_payment_date, adjustment, "Broken" if row.status == "Broken" else "Included")
        lines.append(line)
        if row.sales_invoice:
            promised_by_sales_invoice[row.sales_invoice] += amount

    sales_invoices = get_open_sales_invoices_for_forecast(company, from_date, to_date)
    disputed_amounts = get_active_disputed_amounts(company, [row.name for row in sales_invoices])
    for row in sales_invoices:
        disputed = Decimal(str(disputed_amounts.get(row.name) or 0))
        amount = max(Decimal(str(row.outstanding_amount or 0)) - disputed, Decimal("0"))
        if amount <= 0:
            continue
        if row.name in promised_by_sales_invoice:
            amount = max(amount - promised_by_sales_invoice[row.name], Decimal("0"))
        if amount <= 0:
            continue
        due = row.due_date or row.posting_date or from_date
        behaviour = _payment_delay(company, row.customer)
        original_expected = add_days(due, behaviour) if behaviour else due
        expected_date, adjustment = _apply_scenario_date(original_expected, "Inflow", scenario_doc)
        days_overdue = max(date_diff(getdate(from_date), getdate(due)), 0)
        bucket = ageing_bucket(days_overdue)
        probability = _apply_probability(get_receipt_probability(bucket), "Inflow", scenario_doc)
        basis = "Payment Behaviour" if behaviour else "Due Date"
        confidence = "Low" if disputed else "Medium"
        lines.append(_line(company_currency, expected_date, from_date, "Inflow", "Sales Invoice", "Sales Invoice", row.name, "Customer", row.customer, f"Sales Invoice {row.name}", row.currency, amount, probability, basis, due, adjustment, confidence_level=confidence))

    for row in get_payment_runs_for_forecast(company, from_date, to_date):
        amount = Decimal(str(row.selected_amount or 0))
        if amount <= 0:
            continue
        covered_purchase_invoices.add(row.purchase_invoice)
        expected_date, adjustment = _apply_scenario_date(row.payment_date, "Outflow", scenario_doc)
        lines.append(_line(company_currency, expected_date, from_date, "Outflow", "Payment Run", "Payment Run", row.name, "Supplier", row.supplier, f"Payment Run {row.name}", row.currency, amount, _apply_probability(get_payment_probability("payment_run"), "Outflow", scenario_doc), "Payment Run", row.payment_date, adjustment))

    for row in get_payment_proposals_for_forecast(company, from_date, to_date):
        if row.purchase_invoice in covered_purchase_invoices:
            continue
        amount = Decimal(str(row.selected_amount or 0))
        if amount <= 0:
            continue
        covered_purchase_invoices.add(row.purchase_invoice)
        expected_date, adjustment = _apply_scenario_date(row.posting_date, "Outflow", scenario_doc)
        lines.append(_line(company_currency, expected_date, from_date, "Outflow", "Payment Proposal", "Payment Proposal", row.name, "Supplier", row.supplier, f"Payment Proposal {row.name}", row.currency, amount, _apply_probability(get_payment_probability("payment_proposal"), "Outflow", scenario_doc), "Payment Proposal", row.posting_date, adjustment))

    for row in get_open_purchase_invoices_for_forecast(company, to_date):
        if row.name in covered_purchase_invoices:
            continue
        if get_active_hold(company, row.supplier, row.name):
            continue
        due = row.due_date or row.posting_date or from_date
        amount = Decimal(str(row.outstanding_amount or 0))
        if amount <= 0:
            continue
        expected_date, adjustment = _apply_scenario_date(due, "Outflow", scenario_doc)
        future_due = date_diff(getdate(due), getdate(from_date)) > 0
        lines.append(_line(company_currency, expected_date, from_date, "Outflow", "Purchase Invoice", "Purchase Invoice", row.name, "Supplier", row.supplier, f"Purchase Invoice {row.name}", row.currency, amount, _apply_probability(get_payment_probability("purchase_invoice", future_due), "Outflow", scenario_doc), "Due Date", due, adjustment))

    for item in _expand_manual_items(company, from_date, to_date, scenario):
        expected_date, adjustment = _apply_scenario_date(item.expected_date, item.direction, scenario_doc)
        lines.append(_line(company_currency, expected_date, from_date, item.direction, "Manual Forecast Item", "Treasury Forecast Item", item.name, item.party_type, item.party, item.description, item.currency or company_currency, item.amount, _apply_probability(Decimal(str(item.probability_percent or 100)), item.direction, scenario_doc), "Recurring" if item.recurrence else "Manual Override", item.expected_date, adjustment))

    return sorted(_dedupe(lines), key=lambda row: (row["forecast_date"], row["direction"], row["source_type"], row["source_document"] or ""))


def aggregate_weekly(lines: list[dict], opening_cash, company: str, from_date) -> list[dict]:
    threshold = get_liquidity_threshold(company, from_date)
    by_week = defaultdict(lambda: {"inflows": Decimal("0"), "outflows": Decimal("0"), "other_inflows": Decimal("0"), "other_outflows": Decimal("0")})
    for line in lines:
        week = int(line["week_number"])
        amount = Decimal(str(line["probability_weighted_amount"] or 0))
        if line["direction"] == "Inflow":
            by_week[week]["inflows"] += amount
            if line["source_type"] == "Manual Forecast Item":
                by_week[week]["other_inflows"] += amount
        else:
            by_week[week]["outflows"] += amount
            if line["source_type"] == "Manual Forecast Item":
                by_week[week]["other_outflows"] += amount
    rows = []
    opening = Decimal(str(opening_cash or 0))
    start = getdate(from_date)
    for week in range(1, 14):
        data = by_week[week]
        net = data["inflows"] - data["outflows"]
        closing = opening + net
        status = liquidity_status(closing, threshold)
        rows.append({
            "week": week,
            "week_start": start + timedelta(days=(week - 1) * 7),
            "opening_cash": opening,
            "receipts": data["inflows"],
            "payments": data["outflows"],
            "other_inflows": data["other_inflows"],
            "other_outflows": data["other_outflows"],
            "net_movement": net,
            "closing_cash": closing,
            "minimum_buffer": status["minimum_cash_buffer"],
            "headroom": status["liquidity_headroom"],
            "status": status["status"],
            "liquidity_shortfall": status["liquidity_shortfall"],
        })
        opening = closing
    return rows


def create_forecast_exceptions(forecast, weekly: list[dict], lines: list[dict]) -> list[str]:
    created = []
    for week in weekly:
        if week["status"] in ("Warning", "Critical", "Shortfall"):
            exc = frappe.new_doc("Treasury Forecast Exception")
            exc.update({
                "cash_forecast": forecast.name,
                "exception_type": "Liquidity Shortfall" if week["status"] == "Shortfall" else "Low Liquidity",
                "severity": "Critical" if week["status"] in ("Critical", "Shortfall") else "High",
                "date": week["week_start"],
                "amount": week["liquidity_shortfall"],
                "description": f"Projected liquidity status is {week['status']} in week {week['week']}.",
                "status": "Open",
            })
            exc.insert(ignore_permissions=True)
            created.append(exc.name)
    for line in lines:
        if line["source_type"] == "Promise to Pay" and line["status"] == "Broken":
            exc = frappe.new_doc("Treasury Forecast Exception")
            exc.update({"cash_forecast": forecast.name, "exception_type": "Broken Promise", "severity": "High", "date": line["forecast_date"], "amount": line["company_currency_amount"], "description": line["description"], "source_doctype": line["source_doctype"], "source_document": line["source_document"], "status": "Open"})
            exc.insert(ignore_permissions=True)
            created.append(exc.name)
    return created


def create_forecast_version(source_name: str, reason: str | None = None) -> dict:
    source = frappe.get_doc("Cash Forecast", source_name)
    new_doc = frappe.copy_doc(source)
    new_doc.status = "Draft"
    new_doc.version_number = int(source.version_number or 1) + 1
    new_doc.supersedes_forecast = source.name
    new_doc.forecast_version_reason = reason
    new_doc.set("lines", [])
    new_doc.insert()
    source.db_set("superseded_by", new_doc.name)
    return {"cash_forecast": new_doc.name}


def review_forecast(name: str) -> dict:
    doc = frappe.get_doc("Cash Forecast", name)
    if doc.status != "Generated":
        frappe.throw("Only Generated forecasts can be reviewed.")
    doc.status = "Reviewed"
    doc.reviewed_by = frappe.session.user
    doc.reviewed_on = now_datetime()
    doc.save()
    return {"status": doc.status}


def approve_forecast(name: str) -> dict:
    doc = frappe.get_doc("Cash Forecast", name)
    if doc.status not in ("Generated", "Reviewed"):
        frappe.throw("Only Generated or Reviewed forecasts can be approved.")
    if doc.generated_by == frappe.session.user and not frappe.has_role("System Manager"):
        frappe.throw("Forecast preparer cannot approve the same forecast.")
    doc.status = "Approved"
    doc.approved_by = frappe.session.user
    doc.approved_on = now_datetime()
    doc.save()
    return {"status": doc.status}


def _line(company_currency, expected_date, from_date, direction, source_type, source_doctype, source_document, party_type, party, description, currency, amount, probability, basis, original_date, adjustment, status="Included", confidence_level="High"):
    converted, rate = convert_amount(amount, currency, company_currency, expected_date)
    weighted = converted * Decimal(str(probability or 0)) / Decimal("100")
    week = int(date_diff(getdate(expected_date), getdate(from_date)) // 7) + 1
    return {
        "forecast_date": expected_date,
        "week_number": max(1, week),
        "direction": direction,
        "source_type": source_type,
        "source_doctype": source_doctype,
        "source_document": source_document,
        "party_type": party_type,
        "party": party,
        "description": description,
        "currency": currency,
        "native_amount": Decimal(str(amount or 0)),
        "exchange_rate": rate,
        "company_currency_amount": converted,
        "probability_percent": probability,
        "probability_weighted_amount": weighted,
        "confidence_level": confidence_level,
        "due_date": original_date,
        "expected_date": expected_date,
        "original_expected_date": original_date,
        "forecast_basis": basis,
        "scenario_adjustment": adjustment,
        "status": status,
        "manually_adjusted": 0,
    }


def _dedupe(lines):
    precedence = {source: idx for idx, source in enumerate(RECEIPT_PRECEDENCE + PAYMENT_PRECEDENCE)}
    selected = {}
    for line in lines:
        key = (line["direction"], line["source_doctype"], line["source_document"])
        if line["source_type"] == "Manual Forecast Item":
            key = (*key, line["forecast_date"])
        existing = selected.get(key)
        if not existing or precedence.get(line["source_type"], 99) < precedence.get(existing["source_type"], 99):
            selected[key] = line
    return list(selected.values())


def _get_scenario(name):
    if not name:
        return None
    if isinstance(name, str):
        return frappe.get_doc("Cash Forecast Scenario", name)
    return name


def _apply_probability(probability: Decimal, direction: str, scenario) -> Decimal:
    multiplier = Decimal(str((getattr(scenario, "receipt_probability_multiplier", None) if direction == "Inflow" else getattr(scenario, "payment_probability_multiplier", None)) or 1))
    return max(Decimal("0"), min(Decimal("100"), Decimal(str(probability or 0)) * multiplier))


def _apply_scenario_date(value, direction: str, scenario) -> tuple:
    if not scenario:
        return value, None
    days = int((getattr(scenario, "receipt_delay_days", 0) if direction == "Inflow" else -getattr(scenario, "payment_acceleration_days", 0)) or 0)
    if not days:
        return value, None
    return add_days(value, days), f"Scenario adjusted {days} days"


def _payment_delay(company: str, customer: str | None) -> int:
    if not customer:
        return 0
    try:
        behaviour = get_payment_behaviour(company, customer)
        return int(behaviour.get("average_days_late") or 0)
    except Exception:
        return 0


def _expand_manual_items(company, from_date, to_date, scenario):
    rows = get_manual_treasury_items_for_forecast(company, from_date, to_date, scenario)
    expanded = []
    end = getdate(to_date)
    for row in rows:
        expanded.append(row)
        recurrence = getattr(row, "recurrence", None)
        if not recurrence:
            continue
        step = {"Monthly": 30, "Quarterly": 91, "Half-Yearly": 182, "Yearly": 365}.get(recurrence)
        if not step:
            continue
        next_date = add_days(row.expected_date, step)
        while getdate(next_date) <= end:
            clone = frappe._dict(row.copy() if hasattr(row, "copy") else dict(row))
            clone.expected_date = next_date
            expanded.append(clone)
            next_date = add_days(next_date, step)
    return expanded


def _average_probability(lines):
    if not lines:
        return Decimal("0")
    return sum(Decimal(str(line["probability_percent"] or 0)) for line in lines) / Decimal(str(len(lines)))
