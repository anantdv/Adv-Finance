frappe.listview_settings["Credit Override Request"] = {
  get_indicator(doc) {
    const colors = {Closed: "green", Resolved: "green", Kept: "green", Active: "blue", Broken: "red", Escalated: "red", Open: "orange", Approved: "green", Pending: "orange"};
    return [__(doc.status || (doc.active ? "Active" : "Inactive")), colors[doc.status] || (doc.active ? "red" : "gray"), doc.status ? `status,=,${doc.status}` : ""];
  }
};
