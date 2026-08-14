frappe.listview_settings["Financial Close Task"] = {
  get_indicator(doc) {
    const colors = {Completed: "green", Waived: "gray", Blocked: "red", Rejected: "red", "Ready for Review": "blue", "In Progress": "orange"};
    return [__(doc.status), colors[doc.status] || "gray", `status,=,${doc.status}`];
  }
};
