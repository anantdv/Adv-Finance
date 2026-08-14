frappe.ui.form.on("Financial Close Period", {
  refresh(frm) {
    if (!frm.is_new()) {
      frm.add_custom_button(__("Refresh Readiness"), () => adv_finance_call(frm, "refresh_close_readiness"));
      frm.add_custom_button(__("Submit for Review"), () => adv_finance_call(frm, "submit_for_review"));
      frm.add_custom_button(__("Start Review"), () => adv_finance_call(frm, "start_review"));
      frm.add_custom_button(__("Approve for Close"), () => adv_finance_call(frm, "approve_for_close"));
      frm.add_custom_button(__("Create Period Closing Voucher"), () => adv_finance_call(frm, "create_period_closing_voucher"));
      frm.add_custom_button(__("Refresh PCV Status"), () => adv_finance_call(frm, "refresh_period_closing_voucher_status"));
      frm.add_custom_button(__("Scan Late Postings"), () => adv_finance_call(frm, "scan_late_postings"));
      frm.add_custom_button(__("Certify Close"), () => {
        frappe.prompt([{fieldname: "statement", fieldtype: "Text", label: __("Certification Statement"), reqd: 1}],
          values => adv_finance_call(frm, "certify_close", values));
      });
      frm.add_custom_button(__("Close Period"), () => adv_finance_call(frm, "close_period"));
      frm.add_custom_button(__("Reopen Close"), () => {
        frappe.prompt([{fieldname: "reason", fieldtype: "Small Text", label: __("Reason"), reqd: 1}],
          values => adv_finance_call(frm, "reopen_close", values));
      });
    }
  }
});

function adv_finance_call(frm, method, args = {}) {
  return frappe.call({
    method: `adv_finance.api.financial_close.${method}`,
    args: { name: frm.doc.name, ...args },
    freeze: true,
    callback: () => frm.reload_doc()
  });
}
