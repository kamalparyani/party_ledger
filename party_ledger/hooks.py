app_name = "party_ledger"
app_title = "Party Ledger"
app_publisher = "Mubeen"
app_description = "Party Ledger"
app_email = "dining_reeds.0s@icloud.com"
app_license = "gpl-3.0"
# required_apps = []

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/party_ledger/css/party_ledger.css"
# app_include_js = "/assets/party_ledger/js/party_ledger.js"

# include js, css files in header of web template
# web_include_css = "/assets/party_ledger/css/party_ledger.css"
# web_include_js = "/assets/party_ledger/js/party_ledger.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "party_ledger/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "party_ledger/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "party_ledger.utils.jinja_methods",
# 	"filters": "party_ledger.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "party_ledger.install.before_install"
# after_install = "party_ledger.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "party_ledger.uninstall.before_uninstall"
# after_uninstall = "party_ledger.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "party_ledger.utils.before_app_install"
# after_app_install = "party_ledger.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "party_ledger.utils.before_app_uninstall"
# after_app_uninstall = "party_ledger.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "party_ledger.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"party_ledger.tasks.all"
# 	],
# 	"daily": [
# 		"party_ledger.tasks.daily"
# 	],
# 	"hourly": [
# 		"party_ledger.tasks.hourly"
# 	],
# 	"weekly": [
# 		"party_ledger.tasks.weekly"
# 	],
# 	"monthly": [
# 		"party_ledger.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "party_ledger.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "party_ledger.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "party_ledger.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["party_ledger.utils.before_request"]
# after_request = ["party_ledger.utils.after_request"]

# Job Events
# ----------
# before_job = ["party_ledger.utils.before_job"]
# after_job = ["party_ledger.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"party_ledger.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# All existing content remains the same

reports = [
    "Party Ledger"
]

doctype_js = {
    "GL Entry": "public/js/gl_entry.js"
}

global_search_doctypes = {
    "Default": [
        {"doctype": "GL Entry"},
    ]
}

get_data = {
    "accounts": "party_ledger.config.accounts.get_data"
}

# Rest of the existing content remains the same