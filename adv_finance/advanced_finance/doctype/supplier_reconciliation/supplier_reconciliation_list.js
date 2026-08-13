frappe.listview_settings["Supplier Reconciliation"] = {
  get_indicator(doc) {
    const colors = {
      Draft: "gray",
      Uploaded: "blue",
      Parsed: "blue",
      Matching: "orange",
      "Review Required": "orange",
      Reconciled: "green",
      Closed: "green",
      Failed: "red",
    };
    return [__(doc.reconciliation_status), colors[doc.reconciliation_status] || "gray", "reconciliation_status,=," + doc.reconciliation_status];
  },
};
