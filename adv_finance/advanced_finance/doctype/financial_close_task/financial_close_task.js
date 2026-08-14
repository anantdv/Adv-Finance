frappe.ui.form.on("Financial Close Task", {
  refresh(frm) {
    if (!frm.is_new()) {
      frm.add_custom_button(__("Start"), () => close_task_call(frm, "start_task"));
      frm.add_custom_button(__("Refresh Readiness"), () => close_task_call(frm, "refresh_task_readiness"));
      frm.add_custom_button(__("Submit for Review"), () => {
        frappe.prompt([{fieldname: "notes", fieldtype: "Small Text", label: __("Notes")}],
          values => close_task_call(frm, "submit_task_for_review", values));
      });
      frm.add_custom_button(__("Complete"), () => {
        frappe.prompt([{fieldname: "notes", fieldtype: "Small Text", label: __("Completion Notes")}],
          values => close_task_call(frm, "complete_task", values));
      });
      frm.add_custom_button(__("Approve Task"), () => close_task_call(frm, "review_task", {approve: 1}));
      frm.add_custom_button(__("Reject Task"), () => {
        frappe.prompt([{fieldname: "notes", fieldtype: "Small Text", label: __("Review Notes"), reqd: 1}],
          values => close_task_call(frm, "review_task", {approve: 0, ...values}));
      });
      frm.add_custom_button(__("Waive"), () => {
        frappe.prompt([{fieldname: "reason", fieldtype: "Small Text", label: __("Reason"), reqd: 1}],
          values => close_task_call(frm, "waive_task", values));
      });
    }
  }
});

function close_task_call(frm, method, args = {}) {
  return frappe.call({
    method: `adv_finance.api.financial_close.${method}`,
    args: { name: frm.doc.name, ...args },
    freeze: true,
    callback: () => frm.reload_doc()
  });
}
