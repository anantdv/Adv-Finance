from frappe.model.document import Document
import frappe


class TreasuryAccount(Document):
    def validate(self):
        if self.account:
            account = frappe.db.get_value("Account", self.account, ["account_name", "account_currency", "company"], as_dict=True)
            if not account:
                frappe.throw(f"Account {self.account} was not found.")
            if account.company and account.company != self.company:
                frappe.throw(f"Account {self.account} does not belong to company {self.company}.")
            self.account_name = account.account_name
            self.account_currency = account.account_currency
        if self.restricted_amount and self.restricted_amount < 0:
            frappe.throw("Restricted amount cannot be negative.")
        if self.minimum_balance and self.minimum_balance < 0:
            frappe.throw("Minimum balance cannot be negative.")
