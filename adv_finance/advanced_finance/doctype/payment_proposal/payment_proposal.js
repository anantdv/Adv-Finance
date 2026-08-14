frappe.ui.form.on("Payment Proposal", {
  refresh(frm) {
    if (frm.is_new()) return;

    if (["Draft", "Generated"].includes(frm.doc.status)) {
      frm.add_custom_button(__("Generate Proposal"), () => call_ap(frm, "generate_payment_proposal"));
    }

    if (["Generated", "Under Review"].includes(frm.doc.status)) {
      frm.add_custom_button(__("Approve"), () => call_ap(frm, "approve_payment_proposal"));
    }

    if (frm.doc.status === "Approved") {
      frm.add_custom_button(__("Create Payment Run"), () => call_ap(frm, "create_payment_run_from_proposal"));
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
    .then((result) => {
      if (result.message && result.message.payment_run) {
        frappe.set_route("Form", "Payment Run", result.message.payment_run);
      } else {
        frm.reload_doc();
      }
    });
}
