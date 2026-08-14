frappe.ui.form.on("Budget Plan", {
    refresh(frm) {
        if (!frm.is_new() && ["Submitted", "Under Review"].includes(frm.doc.status)) {
            frm.add_custom_button("Approve", () => frappe.call({method: "adv_finance.api.budgeting.approve_budget_plan", args: {name: frm.doc.name}, callback: () => frm.reload_doc()}));
        }
        if (!frm.is_new() && frm.doc.status === "Approved") {
            frm.add_custom_button("Create Reforecast", () => {
                frappe.prompt({fieldname: "reason", fieldtype: "Small Text", label: "Reason"}, values => {
                    frappe.call({method: "adv_finance.api.budgeting.create_reforecast", args: {name: frm.doc.name, reason: values.reason}, callback: r => frappe.set_route("Form", "Budget Plan", r.message.budget_plan)});
                });
            });
            frm.add_custom_button("Publish ERPNext Budget", () => frappe.call({method: "adv_finance.api.budgeting.publish_budget_plan", args: {name: frm.doc.name}, callback: () => frm.reload_doc()}));
        }
    }
});
