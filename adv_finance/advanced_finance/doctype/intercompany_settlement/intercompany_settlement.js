frappe.ui.form.on("Intercompany Settlement", {
    refresh(frm) {
        if (!frm.is_new() && !["Settled", "Cancelled"].includes(frm.doc.status)) {
            frm.add_custom_button("Mark Settled", () => frappe.call({method: "adv_finance.api.intercompany.mark_settlement_complete", args: {name: frm.doc.name, payment_entry: frm.doc.payment_entry}, callback: () => frm.reload_doc()}));
        }
    }
});
