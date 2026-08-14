frappe.listview_settings["Collection Case"] = {
  get_indicator(doc) {
    const colors = {Closed: "green", Resolved: "green", Kept: "green", Active: "blue", Broken: "red", Escalated: "red", Open: "orange", Approved: "green", Pending: "orange"};
    return [__(doc.status || (doc.active ? "Active" : "Inactive")), colors[doc.status] || (doc.active ? "red" : "gray"), doc.status ? `status,=,${doc.status}` : ""];
  }
};
