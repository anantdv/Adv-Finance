frappe.ui.form.on("Cash Forecast", {
    refresh(frm) {
        if (!frm.is_new() && ["Draft", "Generated"].includes(frm.doc.status)) {
            frm.add_custom_button("Generate / Refresh", () => {
                frappe.call({method: "adv_finance.api.treasury.generate_forecast", args: {name: frm.doc.name, force: 1}, callback: () => frm.reload_doc()});
            });
        }
        if (!frm.is_new() && frm.doc.status === "Generated") {
            frm.add_custom_button("Review", () => {
                frappe.call({method: "adv_finance.api.treasury.review_cash_forecast", args: {name: frm.doc.name}, callback: () => frm.reload_doc()});
            });
        }
        if (!frm.is_new() && ["Generated", "Reviewed"].includes(frm.doc.status)) {
            frm.add_custom_button("Approve", () => {
                frappe.call({method: "adv_finance.api.treasury.approve_cash_forecast", args: {name: frm.doc.name}, callback: () => frm.reload_doc()});
            });
        }
        if (!frm.is_new()) {
            frm.add_custom_button("New Version", () => {
                frappe.prompt({fieldname: "reason", fieldtype: "Small Text", label: "Reason"}, values => {
                    frappe.call({method: "adv_finance.api.treasury.new_forecast_version", args: {name: frm.doc.name, reason: values.reason}, callback: r => frappe.set_route("Form", "Cash Forecast", r.message.cash_forecast)});
                });
            });
        }
    }
});
