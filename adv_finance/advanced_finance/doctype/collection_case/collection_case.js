frappe.ui.form.on("Collection Case", {
  refresh(frm) {
    if (!frm.is_new()) {
      frm.add_custom_button(__("Refresh AR"), () => ar_call(frm, "refresh_collection_case"));
    }
  }
});
function ar_call(frm, method, args = {}) {
  return frappe.call({method: `adv_finance.api.accounts_receivable.${method}`, args: {name: frm.doc.name, ...args}, freeze: true, callback: () => frm.reload_doc()});
}
