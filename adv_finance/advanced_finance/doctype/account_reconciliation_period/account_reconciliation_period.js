frappe.ui.form.on("Account Reconciliation Period", {
  refresh(frm) {
    if (frm.is_new()) return;

    frm.add_custom_button(__("Generate Reconciliations"), () =>
      frappe
        .call({
          method: "adv_finance.api.account_reconciliation.generate_reconciliations",
          args: { name: frm.doc.name },
          freeze: true,
        })
        .then(() => frm.reload_doc())
    );
  },
});
