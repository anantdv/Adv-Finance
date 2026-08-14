frappe.listview_settings["Account Reconciliation"] = {
  get_indicator(doc) {
    const colors = {
      Draft: "gray",
      Preparing: "blue",
      "Ready for Review": "orange",
      "Review Rejected": "red",
      Reviewed: "blue",
      Approved: "green",
      Closed: "green",
      Reopened: "orange",
    };
    return [__(doc.status), colors[doc.status] || "gray", "status,=," + doc.status];
  },
};
