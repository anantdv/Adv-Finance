frappe.ui.form.on("Customer Dispute", {
  refresh(frm) {
    if (!frm.is_new()) {
      frm.add_custom_button(__("Create Draft Credit Note"), () => ar_call(frm, "create_dispute_credit_note"));
    }
  }
});
function ar_call(frm, method, args = {}) { return frappe.call({method: `adv_finance.api.accounts_receivable.${method}`, args: {name: frm.doc.name, ...args}, freeze: true, callback: () => frm.reload_doc()}); }
