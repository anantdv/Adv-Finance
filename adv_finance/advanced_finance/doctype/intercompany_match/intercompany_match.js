frappe.ui.form.on("Intercompany Match", {
    refresh(frm) {
        if (!frm.is_new() && ["Draft", "Suggested"].includes(frm.doc.status)) {
            frm.add_custom_button("Approve Match", () => frappe.call({method: "adv_finance.api.intercompany.approve_match", args: {name: frm.doc.name}, callback: () => frm.reload_doc()}));
        }
    }
});
