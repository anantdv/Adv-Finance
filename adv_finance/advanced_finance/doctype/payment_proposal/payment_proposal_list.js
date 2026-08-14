frappe.listview_settings["Payment Proposal"] = {
  get_indicator(doc) {
    const colors = {
      Draft: "gray",
      Generated: "blue",
      "Under Review": "orange",
      Approved: "green",
      Rejected: "red",
      "Converted to Payment Run": "green",
      Cancelled: "red",
    };
    return [__(doc.status), colors[doc.status] || "gray", "status,=," + doc.status];
  },
};
