app_name = "adv_finance"
app_title = "ADV Finance"
app_publisher = "Anantdv"
app_description = "Advanced finance controls and reconciliation extensions for ERPNext"
app_email = "support@anantdv.com"
app_license = "MIT"
required_apps = ["frappe", "erpnext"]

app_include_js = []
fixtures = [
    {"dt": "Role", "filters": [["name", "in", ["Supplier Reconciliation User", "Supplier Reconciliation Manager"]]]},
]

before_install = "adv_finance.install.before_install"
after_install = "adv_finance.install.after_install"
