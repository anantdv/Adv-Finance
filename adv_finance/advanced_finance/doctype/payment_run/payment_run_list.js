frappe.listview_settings["Payment Run"] = {
  get_indicator(doc) {
    const colors = {
      Draft: "gray",
      Prepared: "blue",
      "Under Approval": "orange",
      Approved: "green",
      Processing: "orange",
      "Payment Entries Created": "green",
      Completed: "green",
      Failed: "red",
      Cancelled: "red",
    };
    return [__(doc.status), colors[doc.status] || "gray", "status,=," + doc.status];
  },
};
