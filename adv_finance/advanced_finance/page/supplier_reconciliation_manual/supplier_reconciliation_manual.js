frappe.pages["supplier-reconciliation-manual"].on_page_load = function (wrapper) {
  const page = frappe.ui.make_app_page({
    parent: wrapper,
    title: __("Supplier Reconciliation Manual"),
    single_column: true,
  });

  page.set_primary_action(__("New Reconciliation"), () => {
    frappe.new_doc("Supplier Reconciliation");
  });

  page.add_menu_item(__("Supplier Reconciliation List"), () => {
    frappe.set_route("List", "Supplier Reconciliation");
  });

  page.add_menu_item(__("Statement Templates"), () => {
    frappe.set_route("List", "Supplier Statement Template");
  });

  $(page.body).html(`
    <div class="adv-finance-manual">
      <section class="manual-hero">
        <div>
          <p class="manual-kicker">${__("ADV Finance")}</p>
          <h1>${__("Supplier Statement Reconciliation")}</h1>
          <p class="manual-lead">
            ${__("Use this guide to upload a supplier statement, compare it with ERPNext supplier ledger transactions, review exceptions, and close the reconciliation without posting anything to the General Ledger.")}
          </p>
        </div>
        <div class="manual-safety">
          <h3>${__("Accounting Safety")}</h3>
          <p>${__("This tool is read-only from an accounting perspective. It does not create Purchase Invoices, Payment Entries, Journal Entries, Debit Notes, GL Entries, or Payment Ledger Entries.")}</p>
        </div>
      </section>

      <section class="manual-grid">
        ${card(__("1. Before You Start"), [
          __("Confirm the supplier exists in ERPNext."),
          __("Confirm the company and payable account are correct."),
          __("Prepare a CSV or XLSX supplier Statement of Account."),
          __("Create a reusable Supplier Statement Template for that supplier format."),
        ])}
        ${card(__("2. Create a Statement Template"), [
          __("Open Supplier Statement Template."),
          __("Select CSV or XLSX and set the header row number."),
          __("Map columns such as date, reference, description, debit, credit, amount, and balance."),
          __("Set date format and decimal/thousands separators if the file is not using standard formatting."),
        ])}
        ${card(__("3. Create Reconciliation"), [
          __("Open Supplier Reconciliation and create a new record."),
          __("Select Company, Supplier, statement period, template, and attach the statement file."),
          __("Enter statement opening and closing balances if the template cannot read them automatically."),
          __("Save the record before running processing actions."),
        ])}
        ${card(__("4. Parse Statement"), [
          __("Click Parse Statement."),
          __("Review imported Statement Lines."),
          __("Raw values are preserved exactly as imported."),
          __("Normalized references and amounts are stored separately for matching."),
        ])}
        ${card(__("5. Load ERP Ledger"), [
          __("Click Load ERP Ledger."),
          __("The app reads ERPNext supplier ledger transactions for the selected supplier, company, payable account, and period."),
          __("ERP opening and closing balances are calculated from ERPNext accounting records."),
          __("No accounting record is changed during this step."),
        ])}
        ${card(__("6. Run Reconciliation"), [
          __("Click Run Reconciliation."),
          __("Exact reference and exact amount matches can be auto-accepted."),
          __("Ambiguous matches are not auto-accepted."),
          __("Suggested matches require user review."),
        ])}
        ${card(__("7. Review Exceptions"), [
          __("Open the exceptions report or the Exceptions table."),
          __("Common exceptions include Statement Only, ERP Only, Amount Mismatch, Date Mismatch, Duplicate Transaction, and Opening Balance Difference."),
          __("Assign exceptions, add resolution notes, and update the status as investigation progresses."),
          __("Any ERP correction must be made in standard ERPNext accounting documents, not inside reconciliation."),
        ])}
        ${card(__("8. Close Reconciliation"), [
          __("A zero-difference reconciliation can be closed by an authorized manager."),
          __("For non-zero differences, enter accepted difference, reason, and closing comments."),
          __("Closed reconciliations are protected from normal editing."),
          __("A Supplier Reconciliation Manager can reopen if further review is needed."),
        ])}
      </section>

      <section class="manual-section">
        <h2>${__("Recommended Monthly Workflow")}</h2>
        <ol class="manual-steps">
          <li>${__("Receive supplier Statement of Account.")}</li>
          <li>${__("Create or reuse the Supplier Statement Template.")}</li>
          <li>${__("Create Supplier Reconciliation for the statement period.")}</li>
          <li>${__("Upload the CSV/XLSX file and parse it.")}</li>
          <li>${__("Load ERP ledger transactions.")}</li>
          <li>${__("Run reconciliation and review matches.")}</li>
          <li>${__("Investigate open exceptions in ERPNext or with the supplier.")}</li>
          <li>${__("Close the reconciliation when balanced or when an approved difference is documented.")}</li>
        </ol>
      </section>

      <section class="manual-section">
        <h2>${__("Status Guide")}</h2>
        <div class="manual-table">
          ${statusRow(__("Draft"), __("Record is being prepared."))}
          ${statusRow(__("Uploaded"), __("Statement file has been attached."))}
          ${statusRow(__("Parsed"), __("Statement lines have been imported and normalized."))}
          ${statusRow(__("Matching"), __("ERP ledger or matching process is running."))}
          ${statusRow(__("Review Required"), __("Exceptions or suggested matches need human review."))}
          ${statusRow(__("Reconciled"), __("Matching completed with no blocking exceptions."))}
          ${statusRow(__("Closed"), __("Final review is complete and locked."))}
          ${statusRow(__("Failed"), __("Processing failed; check the processing message."))}
        </div>
      </section>

      <section class="manual-section">
        <h2>${__("Good Practices")}</h2>
        <ul class="manual-list">
          <li>${__("Use one reconciliation per supplier per statement period.")}</li>
          <li>${__("Do not change supplier statement files after upload; upload a corrected file and re-parse if needed.")}</li>
          <li>${__("Do not force ambiguous matches just to clear the list.")}</li>
          <li>${__("Keep exception notes short, factual, and tied to ERPNext document numbers where possible.")}</li>
          <li>${__("Use ERPNext Payment Reconciliation for payment allocation. Use this module to confirm the supplier ledger agrees with the supplier statement.")}</li>
        </ul>
      </section>
    </div>
  `);
};

function card(title, items) {
  return `
    <article class="manual-card">
      <h2>${title}</h2>
      <ul>${items.map((item) => `<li>${item}</li>`).join("")}</ul>
    </article>
  `;
}

function statusRow(status, meaning) {
  return `
    <div class="manual-row">
      <strong>${status}</strong>
      <span>${meaning}</span>
    </div>
  `;
}
