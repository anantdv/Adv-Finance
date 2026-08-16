frappe.pages["consolidation-manual"].on_page_load = function (wrapper) {
  const page = frappe.ui.make_app_page({
    parent: wrapper,
    title: __("Consolidation Manual"),
    single_column: true,
  });

  page.set_primary_action(__("New Consolidation Period"), () => {
    frappe.new_doc("Consolidation Period");
  });

  page.add_menu_item(__("Consolidation Groups"), () => {
    frappe.set_route("List", "Consolidation Group");
  });

  page.add_menu_item(__("Consolidation Dashboard"), () => {
    frappe.set_route("query-report", "Consolidation Dashboard");
  });

  $(page.body).html(`
    <div class="adv-book-manual">
      <section class="book-cover">
        <div>
          <p class="book-kicker">${__("ADV Finance Book")}</p>
          <h1>${__("Enterprise Financial Consolidation Manual")}</h1>
          <p class="book-lead">
            ${__("A practical book-style guide for group accountants, reviewers, CFOs, and auditors to collect trial balances, translate currencies, prepare consolidation-only eliminations, enter approved adjustments, calculate ownership and minority interest, and publish consolidated reports.")}
          </p>
        </div>
        <div class="book-safety">
          <h3>${__("Accounting Safety")}</h3>
          <p>${__("Consolidation uses ADV Finance snapshots and consolidation records only. It does not post consolidation journals to ERPNext GL and does not modify subsidiary accounting ledgers.")}</p>
        </div>
      </section>

      <section class="book-layout">
        <aside class="book-toc">
          <h3>${__("Contents")}</h3>
          <ol>
            <li><a href="#chapter-1">${__("Purpose and Roles")}</a></li>
            <li><a href="#chapter-2">${__("Setup")}</a></li>
            <li><a href="#chapter-3">${__("Monthly Workflow")}</a></li>
            <li><a href="#chapter-4">${__("Translation")}</a></li>
            <li><a href="#chapter-5">${__("Eliminations and Adjustments")}</a></li>
            <li><a href="#chapter-6">${__("Review and Publish")}</a></li>
            <li><a href="#chapter-7">${__("Reports")}</a></li>
            <li><a href="#chapter-8">${__("Controls")}</a></li>
          </ol>
        </aside>

        <div>
          ${chapter("chapter-1", __("Chapter 1: Purpose and Roles"), `
            <p>${__("Enterprise Financial Consolidation converts multiple ERPNext company ledgers into group reporting views without changing company books.")}</p>
            <div class="book-grid">
              ${note(__("Group Accountant"), __("Maintains groups, collects trial balance snapshots, prepares adjustments, and runs consolidation."))}
              ${note(__("Consolidation Reviewer"), __("Reviews snapshots, translation results, adjustments, eliminations, and consolidated statements."))}
              ${note(__("Group Finance Manager"), __("Approves key consolidation records and coordinates period close readiness."))}
              ${note(__("CFO and Auditor"), __("Review published reports, audit trail, controls, and final period status."))}
            </div>
          `)}

          ${chapter("chapter-2", __("Chapter 2: Setup"), `
            <ol class="book-steps">
              <li>${__("Open Consolidation Group and create the group master.")}</li>
              <li>${__("Select reporting currency and fiscal year.")}</li>
              <li>${__("Add each ERPNext company in the Group Company table.")}</li>
              <li>${__("Enter ownership percent, functional currency, reporting currency, effective date, and consolidation method.")}</li>
              <li>${__("Use parent consolidation group only when building a multi-level group structure.")}</li>
              <li>${__("Keep inactive or excluded companies marked inactive or Not Consolidated.")}</li>
            </ol>
          `)}

          ${chapter("chapter-3", __("Chapter 3: Monthly Workflow"), `
            <ol class="book-steps">
              <li>${__("Create a Consolidation Period for the group, fiscal year, start date, and end date.")}</li>
              <li>${__("Click Collect TB to create immutable trial balance snapshots for each active group company.")}</li>
              <li>${__("Review Currency Translation Report for exchange rate and translation difference visibility.")}</li>
              <li>${__("Generate elimination journals from ready intercompany elimination candidates.")}</li>
              <li>${__("Enter consolidation adjustments where group-only reporting corrections are required.")}</li>
              <li>${__("Approve adjustments and elimination journals according to internal controls.")}</li>
              <li>${__("Click Run Consolidation to create consolidated trial balance lines.")}</li>
              <li>${__("Review reports, move the period through Review, Approved, Published, and Closed.")}</li>
            </ol>
          `)}

          ${chapter("chapter-4", __("Chapter 4: Currency Translation"), `
            <div class="book-table">
              ${row(__("Assets and Liabilities"), __("Translated using closing-rate logic."))}
              ${row(__("Income and Expenses"), __("Translated using average-rate logic."))}
              ${row(__("Equity"), __("Classified as historical-rate logic."))}
              ${row(__("Translation Difference"), __("Stored separately from native balance and translated amount for audit review."))}
            </div>
          `)}

          ${chapter("chapter-5", __("Chapter 5: Eliminations and Adjustments"), `
            <h3>${__("Elimination Journals")}</h3>
            <ul class="book-list">
              <li>${__("Generated from ready intercompany elimination candidates.")}</li>
              <li>${__("Stored as consolidation-only records.")}</li>
              <li>${__("Used to reduce consolidated report balances only.")}</li>
            </ul>
            <h3>${__("Consolidation Adjustments")}</h3>
            <ul class="book-list">
              <li>${__("Use for group reporting adjustments that should not change subsidiary books.")}</li>
              <li>${__("Attach support and record a reason for each adjustment.")}</li>
              <li>${__("Approved adjustments are included in consolidated trial balance lines.")}</li>
            </ul>
          `)}

          ${chapter("chapter-6", __("Chapter 6: Review and Publish"), `
            <div class="book-table">
              ${row(__("Draft"), __("Period is being prepared."))}
              ${row(__("Open"), __("Ready for collection and processing."))}
              ${row(__("Collecting"), __("Trial balance snapshots are being collected or reviewed."))}
              ${row(__("Translating"), __("Currency translation is being checked."))}
              ${row(__("Eliminating"), __("Intercompany elimination preparation is in progress."))}
              ${row(__("Consolidating"), __("Consolidated trial balance lines have been generated."))}
              ${row(__("Review"), __("Reviewer checks reports, adjustments, eliminations, and exceptions."))}
              ${row(__("Approved"), __("Management approval is complete."))}
              ${row(__("Published"), __("Reports are available for final group reporting use."))}
              ${row(__("Closed"), __("Period is complete and protected from normal rebuild activity."))}
            </div>
          `)}

          ${chapter("chapter-7", __("Chapter 7: Reports"), `
            <ul class="book-list">
              <li>${__("Consolidation Dashboard: period progress, snapshots, eliminations, adjustments, profit, cash, and minority interest.")}</li>
              <li>${__("Consolidated Trial Balance: company totals, ownership, translation, elimination, adjustment, minority interest, and final amount.")}</li>
              <li>${__("Consolidated Balance Sheet, Profit and Loss, and Cash Flow: statement views generated from consolidated trial balance lines.")}</li>
              <li>${__("Group Ratio Analysis: liquidity, leverage, margin, and return ratios.")}</li>
              <li>${__("Ownership, Currency Translation, Elimination Summary, Minority Interest, and Adjustment Register: audit and review reports.")}</li>
            </ul>
          `)}

          ${chapter("chapter-8", __("Chapter 8: Controls"), `
            <ul class="book-list">
              <li>${__("Collect snapshots only after subsidiary ledgers are ready for group reporting.")}</li>
              <li>${__("Use force rebuild only on open periods and only with reviewer approval.")}</li>
              <li>${__("Keep ERPNext accounting corrections in standard ERPNext documents.")}</li>
              <li>${__("Use consolidation adjustments only for group reporting entries that should not alter company ledgers.")}</li>
              <li>${__("Close readiness checks require snapshots, consolidated lines, approved adjustments, and no blocked intercompany elimination candidates.")}</li>
            </ul>
          `)}
        </div>
      </section>
    </div>
  `);
};

function chapter(id, title, body) {
  return `
    <article id="${id}" class="book-chapter">
      <h2>${title}</h2>
      ${body}
    </article>
  `;
}

function note(title, text) {
  return `
    <div class="book-note">
      <strong>${title}</strong>
      <p>${text}</p>
    </div>
  `;
}

function row(label, text) {
  return `
    <div class="book-row">
      <strong>${label}</strong>
      <span>${text}</span>
    </div>
  `;
}
