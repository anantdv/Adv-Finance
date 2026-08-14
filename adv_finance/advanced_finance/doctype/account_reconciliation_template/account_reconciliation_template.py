import frappe
from frappe.model.document import Document


class AccountReconciliationTemplate(Document):
    def validate(self):
        account = frappe.db.get_value("Account", self.account, ["company", "account_name", "account_currency"], as_dict=True)
        if not account:
            frappe.throw("Selected account does not exist.")
        if self.company and account.company != self.company:
            frappe.throw("Account must belong to the selected company.")
        self.account_name = account.account_name
        self.account_currency = account.account_currency
