frappe.ui.form.on("Promise to Pay", {
  refresh(frm) {
    if (!frm.is_new()) {
      frm.add_custom_button(__("Activate"), () => ar_call(frm, "activate_promise"));
      frm.add_custom_button(__("Refresh Fulfilment"), () => ar_call(frm, "refresh_promise_fulfilment"));
      frm.add_custom_button(__("Reschedule"), () => {
        frappe.prompt([
          {fieldname: "promised_payment_date", fieldtype: "Date", label: __("New Promise Date"), reqd: 1},
          {fieldname: "promised_amount", fieldtype: "Currency", label: __("Promised Amount")},
          {fieldname: "reason", fieldtype: "Small Text", label: __("Reason"), reqd: 1}
        ], values => ar_call(frm, "reschedule_promise", values));
      });
    }
  }
});
function ar_call(frm, method, args = {}) { return frappe.call({method: `adv_finance.api.accounts_receivable.${method}`, args: {name: frm.doc.name, ...args}, freeze: true, callback: () => frm.reload_doc()}); }
