from __future__ import annotations

from decimal import Decimal
from typing import Any

import frappe


def validate_erpnext_installed() -> None:
    if not frappe.db.exists("Module Def", "ERPNext"):
        frappe.throw("ERPNext must be installed before using ADV Finance accounting features.")


def get_supplier_account(company: str, supplier: str, payable_account: str | None = None) -> str | None:
    if payable_account:
        return payable_account

    account = frappe.db.get_value(
        "Party Account",
        {"parenttype": "Supplier", "parent": supplier, "company": company},
        "account",
    )
    if account:
        return account

    return frappe.db.get_value("Company", company, "default_payable_account")


def get_supplier_ledger_entries(company: str, supplier: str, payable_account: str | None, from_date, to_date) -> list[dict[str, Any]]:
    """Read supplier ledger-affecting GL entries through a parameterized query.

    ERPNext does not expose a compact public function that returns the exact line
    shape required by this reconciliation module. This query is isolated here so
    v16 compatibility can be verified and upgraded without spreading GL details.
    It is read-only and never mutates accounting tables.
    """

    account = get_supplier_account(company, supplier, payable_account)
    filters: dict[str, Any] = {
        "company": company,
        "supplier": supplier,
        "from_date": from_date,
        "to_date": to_date,
    }
    account_clause = ""
    if account:
        filters["account"] = account
        account_clause = "and account = %(account)s"

    return frappe.db.sql(
        f"""
        select
            posting_date, voucher_type, voucher_no, against_voucher_type,
            against_voucher, remarks, debit, credit, account,
            account_currency as currency, party_type, party
        from `tabGL Entry`
        where company = %(company)s
          and party_type = 'Supplier'
          and party = %(supplier)s
          and posting_date between %(from_date)s and %(to_date)s
          and is_cancelled = 0
          {account_clause}
        order by posting_date, creation, name
        """,
        filters,
        as_dict=True,
    )


def get_supplier_opening_balance(company: str, supplier: str, payable_account: str | None, from_date) -> Decimal:
    account = get_supplier_account(company, supplier, payable_account)
    filters: dict[str, Any] = {"company": company, "supplier": supplier, "from_date": from_date}
    account_clause = ""
    if account:
        filters["account"] = account
        account_clause = "and account = %(account)s"

    result = frappe.db.sql(
        f"""
        select coalesce(sum(credit - debit), 0) as balance
        from `tabGL Entry`
        where company = %(company)s
          and party_type = 'Supplier'
          and party = %(supplier)s
          and posting_date < %(from_date)s
          and is_cancelled = 0
          {account_clause}
        """,
        filters,
        as_dict=True,
    )
    return Decimal(str(result[0].balance if result else 0))


def get_supplier_invoice_reference(voucher_type: str, voucher_no: str) -> str | None:
    if voucher_type == "Purchase Invoice":
        return frappe.db.get_value("Purchase Invoice", voucher_no, "bill_no")
    return None


def get_payment_reference(voucher_type: str, voucher_no: str) -> str | None:
    if voucher_type == "Payment Entry":
        return frappe.db.get_value("Payment Entry", voucher_no, "reference_no")
    return None


def get_outstanding_purchase_invoices(
    company: str,
    payable_account: str | None = None,
    supplier: str | None = None,
    supplier_group: str | None = None,
    currency: str | None = None,
    due_date_from=None,
    due_date_to=None,
    include_overdue: bool = True,
    include_due_today: bool = True,
    include_future_due: bool = False,
    minimum_amount=None,
    maximum_amount=None,
) -> list[dict[str, Any]]:
    validate_erpnext_installed()
    conditions = [
        "pi.company = %(company)s",
        "pi.docstatus = 1",
        "pi.outstanding_amount > 0",
    ]
    values: dict[str, Any] = {"company": company}
    if payable_account:
        conditions.append("pi.credit_to = %(payable_account)s")
        values["payable_account"] = payable_account
    if supplier:
        conditions.append("pi.supplier = %(supplier)s")
        values["supplier"] = supplier
    if supplier_group:
        conditions.append("sup.supplier_group = %(supplier_group)s")
        values["supplier_group"] = supplier_group
    if currency:
        conditions.append("pi.currency = %(currency)s")
        values["currency"] = currency
    if due_date_from:
        conditions.append("pi.due_date >= %(due_date_from)s")
        values["due_date_from"] = due_date_from
    if due_date_to:
        conditions.append("pi.due_date <= %(due_date_to)s")
        values["due_date_to"] = due_date_to
    if minimum_amount:
        conditions.append("pi.outstanding_amount >= %(minimum_amount)s")
        values["minimum_amount"] = minimum_amount
    if maximum_amount:
        conditions.append("pi.outstanding_amount <= %(maximum_amount)s")
        values["maximum_amount"] = maximum_amount
    if not include_future_due:
        conditions.append("pi.due_date <= curdate()")
    if not include_overdue:
        conditions.append("pi.due_date >= curdate()")
    if not include_due_today:
        conditions.append("pi.due_date != curdate()")

    return frappe.db.sql(
        f"""
        select
            pi.name, pi.supplier, pi.supplier_name, pi.bill_no, pi.posting_date,
            pi.due_date, pi.currency, pi.grand_total, pi.outstanding_amount,
            pi.credit_to as payable_account
        from `tabPurchase Invoice` pi
        left join `tabSupplier` sup on sup.name = pi.supplier
        where {" and ".join(conditions)}
        order by pi.due_date asc, pi.supplier asc, pi.name asc
        """,
        values,
        as_dict=True,
    )


def get_purchase_invoice_payment_state(purchase_invoice: str):
    return frappe.db.get_value(
        "Purchase Invoice",
        purchase_invoice,
        [
            "name",
            "company",
            "supplier",
            "docstatus",
            "currency",
            "credit_to",
            "outstanding_amount",
            "modified",
        ],
        as_dict=True,
    )


def get_supplier_bank_account(supplier: str) -> str | None:
    return frappe.db.get_value(
        "Bank Account",
        {"party_type": "Supplier", "party": supplier, "is_default": 1},
        "name",
    ) or frappe.db.get_value(
        "Bank Account",
        {"party_type": "Supplier", "party": supplier},
        "name",
    )


def get_bank_gl_account(bank_account: str | None) -> str | None:
    if not bank_account:
        return None
    return frappe.db.get_value("Bank Account", bank_account, "account") or bank_account


def create_draft_supplier_payment_entry(payment_run, supplier: str, invoices) -> Any:
    bank_gl_account = get_bank_gl_account(payment_run.bank_account)
    if not bank_gl_account:
        frappe.throw("Payment Run requires a bank account with a linked ledger account.")
    if not payment_run.payable_account:
        frappe.throw("Payment Run requires a payable account.")

    payment_entry = frappe.new_doc("Payment Entry")
    payment_entry.update(
        {
            "payment_type": "Pay",
            "company": payment_run.company,
            "posting_date": payment_run.payment_date,
            "mode_of_payment": payment_run.mode_of_payment,
            "party_type": "Supplier",
            "party": supplier,
            "paid_from": bank_gl_account,
            "paid_to": payment_run.payable_account,
            "paid_amount": sum(Decimal(str(row.selected_amount or 0)) for row in invoices),
            "received_amount": sum(Decimal(str(row.selected_amount or 0)) for row in invoices),
            "reference_no": payment_run.name,
            "reference_date": payment_run.payment_date,
        }
    )
    for row in invoices:
        payment_entry.append(
            "references",
            {
                "reference_doctype": "Purchase Invoice",
                "reference_name": row.purchase_invoice,
                "allocated_amount": row.selected_amount,
            },
        )
    payment_entry.insert()
    return payment_entry


def get_gl_account_balance(company: str, account: str, from_date, to_date) -> dict[str, Any]:
    """Return GL movement using the same sign convention as GL Entry.

    Debit balances are positive and credit balances are negative. The query is
    read-only, parameterized, and isolated here for validation against ERPNext v16
    General Ledger and Trial Balance reports in the deployment bench.
    """

    opening = frappe.db.sql(
        """
        select coalesce(sum(debit - credit), 0) as balance
        from `tabGL Entry`
        where company = %(company)s
          and account = %(account)s
          and posting_date < %(from_date)s
          and is_cancelled = 0
        """,
        {"company": company, "account": account, "from_date": from_date},
        as_dict=True,
    )
    movement = frappe.db.sql(
        """
        select coalesce(sum(debit), 0) as debit, coalesce(sum(credit), 0) as credit
        from `tabGL Entry`
        where company = %(company)s
          and account = %(account)s
          and posting_date between %(from_date)s and %(to_date)s
          and is_cancelled = 0
        """,
        {"company": company, "account": account, "from_date": from_date, "to_date": to_date},
        as_dict=True,
    )
    opening_balance = Decimal(str(opening[0].balance if opening else 0))
    period_debit = Decimal(str(movement[0].debit if movement else 0))
    period_credit = Decimal(str(movement[0].credit if movement else 0))
    return {
        "opening_balance": opening_balance,
        "period_debit": period_debit,
        "period_credit": period_credit,
        "closing_balance": opening_balance + period_debit - period_credit,
        "currency": frappe.db.get_value("Account", account, "account_currency"),
    }


def get_cash_account_balance(company: str, account: str, as_of_date) -> dict[str, Any]:
    """Return the accounting balance for a treasury cash/bank account.

    GL Entry remains authoritative. Treasury uses this value for visibility and
    planning only; it never writes balances back to Account, Bank Account, or GL.
    """

    result = frappe.db.sql(
        """
        select coalesce(sum(debit - credit), 0) as balance
        from `tabGL Entry`
        where company = %(company)s
          and account = %(account)s
          and posting_date <= %(as_of_date)s
          and is_cancelled = 0
        """,
        {"company": company, "account": account, "as_of_date": as_of_date},
        as_dict=True,
    )
    return {
        "balance": Decimal(str(result[0].balance if result else 0)),
        "currency": frappe.db.get_value("Account", account, "account_currency"),
    }


def get_open_sales_invoices_for_forecast(company: str, from_date=None, to_date=None) -> list[dict[str, Any]]:
    conditions = ["company = %(company)s", "docstatus = 1", "outstanding_amount > 0"]
    values: dict[str, Any] = {"company": company}
    if to_date:
        conditions.append("coalesce(due_date, posting_date) <= %(to_date)s")
        values["to_date"] = to_date
    return frappe.db.sql(
        f"""
        select name, company, customer, customer_name, posting_date, due_date,
               currency, grand_total, outstanding_amount
        from `tabSales Invoice`
        where {" and ".join(conditions)}
        order by coalesce(due_date, posting_date), name
        """,
        values,
        as_dict=True,
    )


def get_active_promises_for_forecast(company: str, from_date=None, to_date=None) -> list[dict[str, Any]]:
    conditions = [
        "ptp.company = %(company)s",
        "ptp.status in ('Active', 'Partially Kept', 'Broken')",
        "ptp.remaining_promised_amount > 0",
    ]
    values: dict[str, Any] = {"company": company}
    if from_date:
        conditions.append("ptp.promised_payment_date >= %(from_date)s")
        values["from_date"] = from_date
    if to_date:
        conditions.append("ptp.promised_payment_date <= %(to_date)s")
        values["to_date"] = to_date
    return frappe.db.sql(
        f"""
        select ptp.name, ptp.company, ptp.customer, ptp.customer_name,
               ptp.promised_payment_date, ptp.currency, ptp.promised_amount,
               ptp.remaining_promised_amount, ptp.status,
               inv.sales_invoice, inv.promised_amount as invoice_promised_amount
        from `tabPromise to Pay` ptp
        left join `tabPromise to Pay Invoice` inv on inv.parent = ptp.name
        where {" and ".join(conditions)}
        order by ptp.promised_payment_date, ptp.name
        """,
        values,
        as_dict=True,
    )


def get_open_purchase_invoices_for_forecast(company: str, to_date=None) -> list[dict[str, Any]]:
    conditions = ["company = %(company)s", "docstatus = 1", "outstanding_amount > 0"]
    values: dict[str, Any] = {"company": company}
    if to_date:
        conditions.append("coalesce(due_date, posting_date) <= %(to_date)s")
        values["to_date"] = to_date
    return frappe.db.sql(
        f"""
        select name, company, supplier, supplier_name, posting_date, due_date,
               currency, grand_total, outstanding_amount
        from `tabPurchase Invoice`
        where {" and ".join(conditions)}
        order by coalesce(due_date, posting_date), name
        """,
        values,
        as_dict=True,
    )


def get_payment_runs_for_forecast(company: str, from_date=None, to_date=None) -> list[dict[str, Any]]:
    conditions = ["run.company = %(company)s", "run.status in ('Approved', 'Processing', 'Payment Entries Created')"]
    values: dict[str, Any] = {"company": company}
    if from_date:
        conditions.append("run.payment_date >= %(from_date)s")
        values["from_date"] = from_date
    if to_date:
        conditions.append("run.payment_date <= %(to_date)s")
        values["to_date"] = to_date
    return frappe.db.sql(
        f"""
        select run.name, run.company, run.payment_date, run.currency, run.status,
               inv.supplier, inv.purchase_invoice, inv.selected_amount
        from `tabPayment Run` run
        inner join `tabPayment Run Invoice` inv on inv.parent = run.name
        where {" and ".join(conditions)}
        order by run.payment_date, run.name
        """,
        values,
        as_dict=True,
    )


def get_payment_proposals_for_forecast(company: str, from_date=None, to_date=None) -> list[dict[str, Any]]:
    conditions = ["prop.company = %(company)s", "prop.status in ('Approved', 'Under Approval')"]
    values: dict[str, Any] = {"company": company}
    if from_date:
        conditions.append("prop.posting_date >= %(from_date)s")
        values["from_date"] = from_date
    if to_date:
        conditions.append("prop.posting_date <= %(to_date)s")
        values["to_date"] = to_date
    return frappe.db.sql(
        f"""
        select prop.name, prop.company, prop.posting_date, prop.currency, prop.status,
               item.supplier, item.purchase_invoice, item.selected_amount
        from `tabPayment Proposal` prop
        inner join `tabPayment Proposal Item` item on item.parent = prop.name
        where {" and ".join(conditions)}
          and item.selected = 1
        order by prop.posting_date, prop.name
        """,
        values,
        as_dict=True,
    )


def get_manual_treasury_items_for_forecast(company: str, from_date=None, to_date=None, scenario=None) -> list[dict[str, Any]]:
    conditions = ["company = %(company)s", "active = 1"]
    values: dict[str, Any] = {"company": company}
    if from_date:
        conditions.append("expected_date >= %(from_date)s")
        values["from_date"] = from_date
    if to_date:
        conditions.append("expected_date <= %(to_date)s")
        values["to_date"] = to_date
    if scenario:
        conditions.append("(scenario is null or scenario = '' or scenario = %(scenario)s)")
        values["scenario"] = scenario
    return frappe.db.sql(
        f"""
        select name, company, direction, category, description, party_type, party,
               expected_date, currency, amount, probability_percent, recurrence,
               source_reference, scenario
        from `tabTreasury Forecast Item`
        where {" and ".join(conditions)}
        order by expected_date, name
        """,
        values,
        as_dict=True,
    )


def get_actual_cash_movements(company: str, from_date=None, to_date=None) -> list[dict[str, Any]]:
    conditions = ["company = %(company)s", "docstatus = 1"]
    values: dict[str, Any] = {"company": company}
    if from_date:
        conditions.append("posting_date >= %(from_date)s")
        values["from_date"] = from_date
    if to_date:
        conditions.append("posting_date <= %(to_date)s")
        values["to_date"] = to_date
    return frappe.db.sql(
        f"""
        select name, posting_date, payment_type, party_type, party, paid_amount,
               received_amount, reference_no, reference_date, paid_from, paid_to
        from `tabPayment Entry`
        where {" and ".join(conditions)}
        order by posting_date, name
        """,
        values,
        as_dict=True,
    )


def get_budget_actual_gl_amount(
    company: str,
    account: str,
    from_date=None,
    to_date=None,
    cost_center: str | None = None,
    project: str | None = None,
    dimensions: dict[str, Any] | None = None,
) -> Decimal:
    """Return budget actual from GL using account sign conventions.

    Expense and Asset/Capex budgets consume debit minus credit. Income budgets
    consume credit minus debit. This function is read-only and intentionally
    isolated because ERPNext Budget reports are the benchmark for deployment
    validation.
    """

    conditions = ["gle.company = %(company)s", "gle.account = %(account)s", "gle.is_cancelled = 0"]
    values: dict[str, Any] = {"company": company, "account": account}
    if from_date:
        conditions.append("gle.posting_date >= %(from_date)s")
        values["from_date"] = from_date
    if to_date:
        conditions.append("gle.posting_date <= %(to_date)s")
        values["to_date"] = to_date
    if cost_center:
        conditions.append("gle.cost_center = %(cost_center)s")
        values["cost_center"] = cost_center
    if project:
        conditions.append("gle.project = %(project)s")
        values["project"] = project
    for fieldname, value in (dimensions or {}).items():
        conditions.append(f"gle.`{fieldname}` = %({fieldname})s")
        values[fieldname] = value
    row = frappe.db.sql(
        f"""
        select coalesce(sum(gle.debit), 0) as debit, coalesce(sum(gle.credit), 0) as credit
        from `tabGL Entry` gle
        where {" and ".join(conditions)}
        """,
        values,
        as_dict=True,
    )
    debit = Decimal(str(row[0].debit if row else 0))
    credit = Decimal(str(row[0].credit if row else 0))
    root_type = frappe.db.get_value("Account", account, "root_type")
    return credit - debit if root_type == "Income" else debit - credit


def get_purchase_order_commitments(
    company: str,
    account: str | None = None,
    cost_center: str | None = None,
    project: str | None = None,
    as_of_date=None,
) -> list[dict[str, Any]]:
    conditions = [
        "po.company = %(company)s",
        "po.docstatus = 1",
        "po.status not in ('Closed', 'Completed', 'Cancelled')",
    ]
    values: dict[str, Any] = {"company": company}
    if account:
        conditions.append("item.expense_account = %(account)s")
        values["account"] = account
    if cost_center:
        conditions.append("item.cost_center = %(cost_center)s")
        values["cost_center"] = cost_center
    if project:
        conditions.append("coalesce(item.project, po.project) = %(project)s")
        values["project"] = project
    if as_of_date:
        conditions.append("po.transaction_date <= %(as_of_date)s")
        values["as_of_date"] = as_of_date
    return frappe.db.sql(
        f"""
        select
            po.name as purchase_order, po.supplier, item.name as source_line,
            item.expense_account as account, item.cost_center,
            coalesce(item.project, po.project) as project,
            item.schedule_date as expected_date,
            item.base_amount as original_amount,
            coalesce(item.billed_amt, 0) as consumed_amount,
            greatest(item.base_amount - coalesce(item.billed_amt, 0), 0) as remaining_amount,
            po.currency, po.status
        from `tabPurchase Order` po
        inner join `tabPurchase Order Item` item on item.parent = po.name
        where {" and ".join(conditions)}
        order by item.schedule_date, po.name, item.idx
        """,
        values,
        as_dict=True,
    )


def get_material_request_precommitments(
    company: str,
    account: str | None = None,
    cost_center: str | None = None,
    project: str | None = None,
    as_of_date=None,
) -> list[dict[str, Any]]:
    conditions = [
        "mr.company = %(company)s",
        "mr.docstatus = 1",
        "mr.status not in ('Stopped', 'Cancelled', 'Ordered')",
    ]
    values: dict[str, Any] = {"company": company}
    if account:
        conditions.append("item.expense_account = %(account)s")
        values["account"] = account
    if cost_center:
        conditions.append("item.cost_center = %(cost_center)s")
        values["cost_center"] = cost_center
    if project:
        conditions.append("coalesce(item.project, mr.project) = %(project)s")
        values["project"] = project
    if as_of_date:
        conditions.append("mr.transaction_date <= %(as_of_date)s")
        values["as_of_date"] = as_of_date
    return frappe.db.sql(
        f"""
        select
            mr.name as material_request, item.name as source_line,
            item.expense_account as account, item.cost_center,
            coalesce(item.project, mr.project) as project,
            item.schedule_date as expected_date,
            item.base_amount as original_amount,
            coalesce(item.ordered_qty, 0) * coalesce(item.rate, 0) as consumed_amount,
            greatest(item.base_amount - coalesce(item.ordered_qty, 0) * coalesce(item.rate, 0), 0) as remaining_amount,
            mr.status
        from `tabMaterial Request` mr
        inner join `tabMaterial Request Item` item on item.parent = mr.name
        where {" and ".join(conditions)}
        order by item.schedule_date, mr.name, item.idx
        """,
        values,
        as_dict=True,
    )


def create_draft_erpnext_budget_from_plan(plan) -> Any:
    """Create a standard draft ERPNext Budget from an approved ADV Budget Plan.

    This does not submit the Budget. ERPNext remains responsible for standard
    budget validation and any accounting/procurement integration.
    """

    budget = frappe.new_doc("Budget")
    budget.update(
        {
            "company": plan.company,
            "fiscal_year": plan.fiscal_year,
            "budget_against": "Project" if plan.project else "Cost Center",
            "cost_center": plan.cost_center,
            "project": plan.project,
            "action_if_annual_budget_exceeded": "Warn",
            "action_if_accumulated_monthly_budget_exceeded": "Warn",
        }
    )
    for line in plan.lines:
        budget.append(
            "accounts",
            {
                "account": line.account,
                "budget_amount": line.company_currency_amount or line.annual_budget,
                "monthly_distribution": line.monthly_distribution,
            },
        )
    budget.insert()
    return budget


def get_party_subledger_balance(company: str, account: str, party_type: str, to_date) -> Decimal:
    result = frappe.db.sql(
        """
        select coalesce(sum(debit - credit), 0) as balance
        from `tabGL Entry`
        where company = %(company)s
          and account = %(account)s
          and party_type = %(party_type)s
          and posting_date <= %(to_date)s
          and is_cancelled = 0
        """,
        {"company": company, "account": account, "party_type": party_type, "to_date": to_date},
        as_dict=True,
    )
    return Decimal(str(result[0].balance if result else 0))


def get_party_subledger_items(company: str, account: str, party_type: str, to_date) -> list[dict[str, Any]]:
    return frappe.db.sql(
        """
        select party, voucher_type, voucher_no, posting_date,
               sum(debit) as debit, sum(credit) as credit, sum(debit - credit) as amount
        from `tabGL Entry`
        where company = %(company)s
          and account = %(account)s
          and party_type = %(party_type)s
          and posting_date <= %(to_date)s
          and is_cancelled = 0
        group by party, voucher_type, voucher_no, posting_date
        having abs(amount) > 0.000001
        order by posting_date, party, voucher_no
        """,
        {"company": company, "account": account, "party_type": party_type, "to_date": to_date},
        as_dict=True,
    )


def create_draft_accrual_journal_entry(accrual) -> Any:
    _validate_accrual_accounts(accrual)
    journal_entry = frappe.new_doc("Journal Entry")
    journal_entry.update(
        {
            "voucher_type": "Journal Entry",
            "company": accrual.company,
            "posting_date": accrual.posting_date,
            "finance_book": accrual.finance_book,
            "user_remark": f"ADV Finance Accrual {accrual.name}: {accrual.description or ''}",
        }
    )
    journal_entry.append(
        "accounts",
        {
            "account": accrual.expense_account,
            "debit_in_account_currency": accrual.accrual_amount,
            "credit_in_account_currency": 0,
            "cost_center": accrual.cost_center,
            "project": accrual.project,
        },
    )
    journal_entry.append(
        "accounts",
        {
            "account": accrual.accrual_liability_account,
            "debit_in_account_currency": 0,
            "credit_in_account_currency": accrual.accrual_amount,
            "cost_center": accrual.cost_center,
            "project": accrual.project,
        },
    )
    journal_entry.insert()
    return journal_entry


def create_draft_accrual_reversal_journal_entry(accrual) -> Any:
    _validate_accrual_accounts(accrual)
    journal_entry = frappe.new_doc("Journal Entry")
    journal_entry.update(
        {
            "voucher_type": "Journal Entry",
            "company": accrual.company,
            "posting_date": accrual.reversal_date,
            "finance_book": accrual.finance_book,
            "user_remark": f"ADV Finance Accrual Reversal {accrual.name}: {accrual.description or ''}",
        }
    )
    journal_entry.append(
        "accounts",
        {
            "account": accrual.accrual_liability_account,
            "debit_in_account_currency": accrual.accrual_amount,
            "credit_in_account_currency": 0,
            "cost_center": accrual.cost_center,
            "project": accrual.project,
        },
    )
    journal_entry.append(
        "accounts",
        {
            "account": accrual.expense_account,
            "debit_in_account_currency": 0,
            "credit_in_account_currency": accrual.accrual_amount,
            "cost_center": accrual.cost_center,
            "project": accrual.project,
        },
    )
    journal_entry.insert()
    return journal_entry


def get_journal_entry_docstatus(journal_entry: str | None) -> int | None:
    if not journal_entry:
        return None
    return frappe.db.get_value("Journal Entry", journal_entry, "docstatus")


def get_purchase_invoice_expense_candidates(
    company: str,
    supplier: str | None = None,
    expense_account: str | None = None,
    currency: str | None = None,
    from_date=None,
    to_date=None,
) -> list[dict[str, Any]]:
    conditions = ["pi.company = %(company)s", "pi.docstatus = 1"]
    values: dict[str, Any] = {"company": company}
    if supplier:
        conditions.append("pi.supplier = %(supplier)s")
        values["supplier"] = supplier
    if currency:
        conditions.append("pi.currency = %(currency)s")
        values["currency"] = currency
    if expense_account:
        conditions.append("item.expense_account = %(expense_account)s")
        values["expense_account"] = expense_account
    if from_date:
        conditions.append("pi.posting_date >= %(from_date)s")
        values["from_date"] = from_date
    if to_date:
        conditions.append("pi.posting_date <= %(to_date)s")
        values["to_date"] = to_date

    return frappe.db.sql(
        f"""
        select
            pi.name as purchase_invoice, item.name as purchase_invoice_item,
            pi.company, pi.supplier, pi.supplier_name, pi.currency, pi.posting_date,
            pi.bill_date, item.expense_account, item.cost_center, item.project,
            item.amount as invoice_amount, item.description
        from `tabPurchase Invoice` pi
        inner join `tabPurchase Invoice Item` item on item.parent = pi.name
        where {" and ".join(conditions)}
        order by pi.posting_date desc, pi.name desc, item.idx asc
        """,
        values,
        as_dict=True,
    )


def get_purchase_invoice_docstatus(purchase_invoice: str | None) -> int | None:
    if not purchase_invoice:
        return None
    return frappe.db.get_value("Purchase Invoice", purchase_invoice, "docstatus")


def create_draft_period_closing_voucher(close_period) -> Any:
    """Create a standard draft ERPNext Period Closing Voucher.

    This deliberately does not submit the voucher. ERPNext remains responsible
    for validation, P&L closing entries, and GL posting when a finance user
    submits the standard document.
    """

    closing_account = frappe.db.get_value("Company", close_period.company, "default_income_account") or frappe.db.get_value(
        "Company", close_period.company, "default_expense_account"
    )
    if not closing_account:
        frappe.throw("Company requires a default closing account before creating Period Closing Voucher.")
    voucher = frappe.new_doc("Period Closing Voucher")
    voucher.update(
        {
            "company": close_period.company,
            "posting_date": close_period.period_end,
            "fiscal_year": close_period.fiscal_year,
            "closing_account_head": closing_account,
            "remarks": f"ADV Finance Financial Close {close_period.name}",
        }
    )
    voucher.insert()
    return voucher


def get_period_closing_voucher_docstatus(period_closing_voucher: str | None) -> int | None:
    if not period_closing_voucher:
        return None
    return frappe.db.get_value("Period Closing Voucher", period_closing_voucher, "docstatus")


def find_late_gl_postings(company: str, period_start, period_end, cutoff_timestamp) -> list[dict[str, Any]]:
    return frappe.db.sql(
        """
        select distinct voucher_type, voucher_no, posting_date, creation, owner
        from `tabGL Entry`
        where company = %(company)s
          and posting_date between %(period_start)s and %(period_end)s
          and creation > %(cutoff_timestamp)s
          and is_cancelled = 0
        order by creation desc, posting_date desc
        """,
        {
            "company": company,
            "period_start": period_start,
            "period_end": period_end,
            "cutoff_timestamp": cutoff_timestamp,
        },
        as_dict=True,
    )


def get_customer_open_sales_invoices(company: str, customer: str, as_of_date=None) -> list[dict[str, Any]]:
    conditions = ["company = %(company)s", "customer = %(customer)s", "docstatus = 1", "outstanding_amount > 0"]
    values: dict[str, Any] = {"company": company, "customer": customer}
    if as_of_date:
        conditions.append("posting_date <= %(as_of_date)s")
        values["as_of_date"] = as_of_date
    return frappe.db.sql(
        f"""
        select name, posting_date, due_date, grand_total, outstanding_amount,
               currency, customer, customer_name, company
        from `tabSales Invoice`
        where {" and ".join(conditions)}
        order by due_date asc, posting_date asc, name asc
        """,
        values,
        as_dict=True,
    )


def get_customer_receipts(company: str, customer: str, from_date=None, to_date=None) -> list[dict[str, Any]]:
    conditions = ["pe.company = %(company)s", "pe.party_type = 'Customer'", "pe.party = %(customer)s", "pe.docstatus = 1"]
    values: dict[str, Any] = {"company": company, "customer": customer}
    if from_date:
        conditions.append("pe.posting_date >= %(from_date)s")
        values["from_date"] = from_date
    if to_date:
        conditions.append("pe.posting_date <= %(to_date)s")
        values["to_date"] = to_date
    return frappe.db.sql(
        f"""
        select pe.name, pe.posting_date, pe.paid_amount, pe.received_amount,
               per.reference_doctype, per.reference_name, per.allocated_amount
        from `tabPayment Entry` pe
        left join `tabPayment Entry Reference` per on per.parent = pe.name
        where {" and ".join(conditions)}
        order by pe.posting_date asc, pe.name asc
        """,
        values,
        as_dict=True,
    )


def get_customer_credit_limit(company: str, customer: str):
    credit_limit = frappe.db.get_value(
        "Customer Credit Limit",
        {"parent": customer, "parenttype": "Customer", "company": company},
        "credit_limit",
    )
    if credit_limit is None:
        credit_limit = frappe.db.get_value("Customer", customer, "credit_limit")
    return credit_limit or 0


def get_customer_open_sales_orders(company: str, customer: str) -> Decimal:
    result = frappe.db.sql(
        """
        select coalesce(sum(base_grand_total - coalesce(per_billed, 0) * base_grand_total / 100), 0) as amount
        from `tabSales Order`
        where company = %(company)s
          and customer = %(customer)s
          and docstatus = 1
          and status not in ('Closed', 'Completed', 'Cancelled')
        """,
        {"company": company, "customer": customer},
        as_dict=True,
    )
    return Decimal(str(result[0].amount if result else 0))


def get_customer_unbilled_delivery_amount(company: str, customer: str) -> Decimal:
    result = frappe.db.sql(
        """
        select coalesce(sum(base_grand_total - coalesce(per_billed, 0) * base_grand_total / 100), 0) as amount
        from `tabDelivery Note`
        where company = %(company)s
          and customer = %(customer)s
          and docstatus = 1
          and status not in ('Closed', 'Completed', 'Cancelled')
        """,
        {"company": company, "customer": customer},
        as_dict=True,
    )
    return Decimal(str(result[0].amount if result else 0))


def create_draft_customer_credit_note(dispute) -> Any:
    if not dispute.sales_invoice:
        frappe.throw("Sales Invoice is required before creating a draft credit note.")
    source = frappe.get_doc("Sales Invoice", dispute.sales_invoice)
    credit_note = frappe.copy_doc(source)
    credit_note.is_return = 1
    credit_note.return_against = source.name
    credit_note.posting_date = dispute.dispute_date
    credit_note.remarks = f"ADV Finance Customer Dispute {dispute.name}: {dispute.description or ''}"
    for item in getattr(credit_note, "items", []):
        item.qty = -abs(item.qty or 0)
    credit_note.insert()
    return credit_note


def _validate_accrual_accounts(accrual) -> None:
    if not accrual.company:
        frappe.throw("Company is required.")
    for field in ("expense_account", "accrual_liability_account"):
        account = accrual.get(field)
        if not account:
            frappe.throw(f"{field.replace('_', ' ').title()} is required.")
        account_company = frappe.db.get_value("Account", account, "company")
        if account_company and account_company != accrual.company:
            frappe.throw(f"Account {account} does not belong to company {accrual.company}.")
