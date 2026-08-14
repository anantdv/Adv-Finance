frappe.ui.form.on("Credit Hold", {
  refresh(frm) {
    if (!frm.is_new() && frm.doc.active) {
      frm.add_custom_button(__("Release Hold"), () => {
        frappe.prompt([{fieldname: "reason", fieldtype: "Small Text", label: __("Release Reason"), reqd: 1}], values => ar_call(frm, "release_credit_hold", values));
      });
    }
  }
});
function ar_call(frm, method, args = {}) { return frappe.call({method: `adv_finance.api.accounts_receivable.${method}`, args: {name: frm.doc.name, ...args}, freeze: true, callback: () => frm.reload_doc()}); }
