frappe.listview_settings["Cash Forecast Scenario"] = {
    get_indicator(doc) {
        if (doc.status === "Approved" || doc.active) return [doc.status || "Active", "green", "status,=," + (doc.status || "Active")];
        if (["Critical", "High"].includes(doc.severity)) return [doc.severity, "red", "severity,=," + doc.severity];
        return [doc.status || "Open", "gray", "status,=," + (doc.status || "Open")];
    }
};
