frappe.ui.form.on("Payment Run", {
  refresh(frm) {
    if (frm.is_new()) return;

    if (["Prepared", "Approved", "Failed"].includes(frm.doc.status)) {
      frm.add_custom_button(__("Revalidate"), () => call_ap(frm, "revalidate_payment_run"));
    }

    if (["Prepared", "Approved"].includes(frm.doc.status)) {
      frm.add_custom_button(__("Create Draft Payment Entries"), () => call_ap(frm, "create_draft_payment_entries"));
    }
  },
});

function call_ap(frm, method) {
  return frappe
    .call({
      method: `adv_finance.api.accounts_payable.${method}`,
      args: { name: frm.doc.name },
      freeze: true,
    })
    .then(() => frm.reload_doc());
}
