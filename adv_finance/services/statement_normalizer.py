from __future__ import annotations

import re
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import Any

import frappe
from frappe.utils import getdate


REFERENCE_SEPARATOR_PATTERN = re.compile(r"[\s\-/_.:]+")


def normalize_reference(value: Any) -> str:
    if value is None:
        return ""
    text = str(value).strip().upper()
    return REFERENCE_SEPARATOR_PATTERN.sub("", text)


def normalize_description(value: Any) -> str:
    if value is None:
        return ""
    return " ".join(str(value).strip().split())


def normalize_date(value: Any, configured_format: str | None = None) -> date | None:
    if value in (None, ""):
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value

    text = str(value).strip()
    if not text:
        return None

    if configured_format:
        try:
            return datetime.strptime(text, configured_format).date()
        except ValueError as exc:
            frappe.throw(f'Unable to interpret date "{text}" using format "{configured_format}".')
            raise exc

    try:
        return getdate(text)
    except Exception as exc:
        frappe.throw(f'Unable to interpret date "{text}". Review the statement template date format.')
        raise exc


def normalize_decimal(
    value: Any,
    decimal_separator: str | None = ".",
    thousands_separator: str | None = ",",
) -> Decimal:
    if value in (None, ""):
        return Decimal("0")
    if isinstance(value, Decimal):
        return value
    if isinstance(value, (int, float)):
        return Decimal(str(value))

    text = str(value).strip()
    if not text:
        return Decimal("0")

    text = text.replace(" ", "")
    negative = text.startswith("(") and text.endswith(")")
    text = text.strip("()")
    if thousands_separator:
        text = text.replace(thousands_separator, "")
    if decimal_separator and decimal_separator != ".":
        text = text.replace(decimal_separator, ".")

    try:
        amount = Decimal(text)
    except InvalidOperation as exc:
        frappe.throw(f'Unable to interpret amount "{value}". Review the source file or statement template.')
        raise exc

    return -amount if negative else amount


def classify_transaction_type(description: str = "", debit: Decimal = Decimal("0"), credit: Decimal = Decimal("0")) -> str:
    text = (description or "").upper()
    if "PAY" in text or credit > 0:
        return "Payment"
    if "CREDIT" in text or "CN" in text:
        return "Credit Note"
    if debit > 0:
        return "Invoice"
    return "Unknown Transaction"
