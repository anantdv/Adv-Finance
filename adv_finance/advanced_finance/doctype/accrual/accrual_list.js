frappe.listview_settings["Accrual"] = {
  get_indicator(doc) {
    const colors = {
      Draft: "gray",
      "Under Review": "orange",
      Approved: "blue",
      Closed: "green",
      Cancelled: "red",
    };
    return [__(doc.workflow_status || doc.status), colors[doc.workflow_status] || "gray", "workflow_status,=," + doc.workflow_status];
  },
};
