frappe.ui.form.on("Accrual", {
  refresh(frm) {
    if (frm.is_new()) return;

    if (frm.doc.workflow_status === "Draft") {
      frm.add_custom_button(__("Submit for Review"), () => call_accrual(frm, "submit_for_review"));
    }

    if (frm.doc.workflow_status === "Under Review") {
      frm.add_custom_button(__("Approve"), () => call_accrual(frm, "approve_accrual"));
    }

    if (frm.doc.workflow_status === "Approved" && !frm.doc.accrual_journal_entry) {
      frm.add_custom_button(__("Create Accrual Journal Draft"), () => call_accrual(frm, "create_accrual_journal_entry"));
    }

    if (frm.doc.reversal_required && !frm.doc.reversal_journal_entry) {
      frm.add_custom_button(__("Create Reversal Draft"), () => call_accrual(frm, "create_reversal_journal_entry"));
    }

    frm.add_custom_button(__("Refresh Status"), () => call_accrual(frm, "refresh_accrual_status"));
    frm.add_custom_button(__("Suggest PI Matches"), () => call_accrual(frm, "suggest_purchase_invoice_matches"));
    frm.add_custom_button(__("Refresh Exceptions"), () => call_accrual(frm, "refresh_accrual_exceptions"));

    if (["Approved", "Posted", "Fully Matched", "Variance Review"].includes(frm.doc.status)) {
      frm.add_custom_button(__("Close"), () => call_accrual(frm, "close_accrual"));
    }

    if (frm.doc.workflow_status === "Closed") {
      frm.add_custom_button(__("Reopen"), () =>
        frappe.prompt(
          [{ fieldname: "reason", fieldtype: "Small Text", label: __("Reason"), reqd: 1 }],
          (values) => call_accrual(frm, "reopen_accrual", values)
        )
      );
    }
  },
});

function call_accrual(frm, method, args = {}) {
  return frappe
    .call({
      method: `adv_finance.api.accrual.${method}`,
      args: { name: frm.doc.name, ...args },
      freeze: true,
    })
    .then(() => frm.reload_doc());
}
