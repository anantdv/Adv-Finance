frappe.listview_settings["Financial Close Period"] = {
  get_indicator(doc) {
    const colors = {Closed: "green", "Approved for Close": "blue", Blocked: "red", Reopened: "orange", Cancelled: "gray"};
    return [__(doc.status), colors[doc.status] || "orange", `status,=,${doc.status}`];
  }
};
