frappe.ui.form.on("Account Reconciliation", {
  refresh(frm) {
    if (frm.is_new()) return;

    frm.add_custom_button(__("Load GL Balance"), () => call_reconciliation(frm, "load_gl_balance"));
    frm.add_custom_button(__("Load Supporting Balance"), () => call_reconciliation(frm, "load_supporting_balance"));

    if (["Draft", "Preparing", "Review Rejected", "Reopened"].includes(frm.doc.status)) {
      frm.add_custom_button(__("Submit for Review"), () => call_reconciliation(frm, "submit_for_review"));
    }

    if (frm.doc.status === "Ready for Review") {
      frm.add_custom_button(__("Review"), () => call_reconciliation(frm, "review_reconciliation"));
      frm.add_custom_button(__("Reject"), () =>
        frappe.prompt(
          [{ fieldname: "comments", fieldtype: "Small Text", label: __("Reviewer Comments") }],
          (values) => call_reconciliation(frm, "reject_reconciliation", values)
        )
      );
    }

    if (frm.doc.status === "Reviewed") {
      frm.add_custom_button(__("Approve"), () => call_reconciliation(frm, "approve_reconciliation"));
    }

    if (frm.doc.status === "Approved") {
      frm.add_custom_button(__("Close"), () => call_reconciliation(frm, "close_reconciliation"));
    }

    if (frm.doc.status === "Closed") {
      frm.add_custom_button(__("Reopen"), () =>
        frappe.prompt(
          [{ fieldname: "reason", fieldtype: "Small Text", label: __("Reason"), reqd: 1 }],
          (values) => call_reconciliation(frm, "reopen_reconciliation", values)
        )
      );
    }
  },
});

function call_reconciliation(frm, method, args = {}) {
  return frappe
    .call({
      method: `adv_finance.api.account_reconciliation.${method}`,
      args: { name: frm.doc.name, ...args },
      freeze: true,
    })
    .then(() => frm.reload_doc());
}
