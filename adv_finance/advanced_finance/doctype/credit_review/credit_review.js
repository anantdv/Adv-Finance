frappe.ui.form.on("Credit Review", {
  refresh(frm) {
    if (!frm.is_new()) {
      frm.add_custom_button(__("Refresh Exposure"), () => ar_call(frm, "refresh_credit_review"));
      frm.add_custom_button(__("Submit Review"), () => ar_call(frm, "submit_credit_review"));
      frm.add_custom_button(__("Approve Review"), () => ar_call(frm, "approve_credit_review"));
    }
  }
});
function ar_call(frm, method, args = {}) { return frappe.call({method: `adv_finance.api.accounts_receivable.${method}`, args: {name: frm.doc.name, ...args}, freeze: true, callback: () => frm.reload_doc()}); }
