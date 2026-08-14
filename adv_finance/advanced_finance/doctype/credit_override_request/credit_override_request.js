frappe.ui.form.on("Credit Override Request", {
  refresh(frm) {
    if (!frm.is_new()) {
      frm.add_custom_button(__("Approve"), () => ar_call(frm, "approve_credit_override"));
      frm.add_custom_button(__("Mark Used"), () => ar_call(frm, "mark_credit_override_used"));
    }
  }
});
function ar_call(frm, method, args = {}) { return frappe.call({method: `adv_finance.api.accounts_receivable.${method}`, args: {name: frm.doc.name, ...args}, freeze: true, callback: () => frm.reload_doc()}); }
