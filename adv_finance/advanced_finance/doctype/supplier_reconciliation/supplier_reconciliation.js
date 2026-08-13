frappe.ui.form.on("Supplier Reconciliation", {
  refresh(frm) {
    frm.trigger("render_summary");

    if (frm.is_new()) return;

    if (frm.doc.reconciliation_status === "Draft" || frm.doc.reconciliation_status === "Uploaded") {
      frm.add_custom_button(__("Parse Statement"), () => call_reconciliation(frm, "parse_statement"));
    }

    if (frm.doc.reconciliation_status === "Parsed") {
      frm.add_custom_button(__("Load ERP Ledger"), () => call_reconciliation(frm, "refresh_erp_ledger"));
      frm.add_custom_button(__("Run Reconciliation"), () => call_reconciliation(frm, "run_reconciliation"));
    }

    if (["Review Required", "Reconciled"].includes(frm.doc.reconciliation_status)) {
      frm.add_custom_button(__("Re-run Matching"), () => call_reconciliation(frm, "run_matching"));
      frm.add_custom_button(__("View Exceptions"), () => {
        frappe.set_route("query-report", "Open Supplier Reconciliation Exceptions", {
          reconciliation: frm.doc.name,
        });
      });
      frm.add_custom_button(__("Close Reconciliation"), () => call_reconciliation(frm, "close_reconciliation"));
    }

    if (frm.doc.reconciliation_status === "Closed" && frappe.user.has_role("Supplier Reconciliation Manager")) {
      frm.add_custom_button(__("Reopen"), () => call_reconciliation(frm, "reopen_reconciliation"));
    }
  },

  render_summary(frm) {
    if (!frm.fields_dict.reconciliation_summary) return;
    const currency = frm.doc.currency || "";
    const rows = [
      [__("Supplier Statement Balance"), format_currency(frm.doc.statement_closing_balance || 0, currency)],
      [__("ERP Supplier Balance"), format_currency(frm.doc.erp_closing_balance || 0, currency)],
      [__("Difference"), format_currency(frm.doc.reconciliation_difference || 0, currency)],
      [__("Statement Lines"), frm.doc.total_statement_lines || 0],
      [__("ERP Transactions"), frm.doc.total_erp_lines || 0],
      [__("Exact Matches"), frm.doc.exact_matches || 0],
      [__("Suggested Matches"), frm.doc.suggested_matches || 0],
      [__("Statement Only"), frm.doc.unmatched_statement_lines || 0],
      [__("ERP Only"), frm.doc.unmatched_erp_lines || 0],
      [__("Exceptions"), frm.doc.exception_count || 0],
    ];
    frm.fields_dict.reconciliation_summary.$wrapper.html(
      `<div class="dashboard-section"><table class="table table-bordered table-condensed">${
        rows.map(([label, value]) => `<tr><td>${label}</td><td class="text-right">${value}</td></tr>`).join("")
      }</table></div>`
    );
  },
});

function call_reconciliation(frm, method) {
  return frappe
    .call({
      method: `adv_finance.api.reconciliation.${method}`,
      args: { name: frm.doc.name },
      freeze: true,
    })
    .then(() => frm.reload_doc());
}
