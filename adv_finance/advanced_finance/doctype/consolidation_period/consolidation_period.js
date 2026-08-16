frappe.ui.form.on("Consolidation Period", {
    refresh(frm) {
        if (!frm.is_new() && !["Approved", "Published", "Closed"].includes(frm.doc.status)) {
            frm.add_custom_button("Collect TB", () => frappe.call({method: "adv_finance.api.consolidation.collect_trial_balance", args: {name: frm.doc.name, force: 1}, callback: () => frm.reload_doc()}));
            frm.add_custom_button("Run Consolidation", () => frappe.call({method: "adv_finance.api.consolidation.run_consolidation", args: {name: frm.doc.name, force: 1}, callback: () => frm.reload_doc()}));
            frm.add_custom_button("Generate Eliminations", () => frappe.call({method: "adv_finance.api.consolidation.generate_eliminations", args: {name: frm.doc.name}, callback: () => frm.reload_doc()}));
        }
    }
});
