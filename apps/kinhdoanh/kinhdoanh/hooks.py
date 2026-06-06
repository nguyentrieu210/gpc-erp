app_name = "kinhdoanh"
app_title = "Sales"
app_publisher = "GPC"
app_description = "GPC ERP - Sales module"
app_email = "trieu.nt93@gmail.com"
app_license = "mit"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "kinhdoanh",
# 		"logo": "/assets/kinhdoanh/logo.png",
# 		"title": "Sales",
# 		"route": "/kinhdoanh",
# 		"has_permission": "kinhdoanh.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/kinhdoanh/css/kinhdoanh.css"
# app_include_js = "/assets/kinhdoanh/js/kinhdoanh.js"

# include js, css files in header of web template
# web_include_css = "/assets/kinhdoanh/css/kinhdoanh.css"
# web_include_js = "/assets/kinhdoanh/js/kinhdoanh.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "kinhdoanh/public/scss/website"

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
# app_include_icons = "kinhdoanh/public/icons.svg"

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

# automatically load and sync documents of this doctype from downstream apps
# importable_doctypes = [doctype_1]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "kinhdoanh.utils.jinja_methods",
# 	"filters": "kinhdoanh.utils.jinja_filters"
# }

# Website / SPA
website_route_rules = [
	{"from_route": "/kinhdoanh_app/<path:app_path>", "to_route": "kinhdoanh_app"},
]

# Installation
# ------------

# before_install = "kinhdoanh.install.before_install"
# after_install = "kinhdoanh.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "kinhdoanh.uninstall.before_uninstall"
# after_uninstall = "kinhdoanh.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "kinhdoanh.utils.before_app_install"
# after_app_install = "kinhdoanh.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "kinhdoanh.utils.before_app_uninstall"
# after_app_uninstall = "kinhdoanh.utils.after_app_uninstall"

# Build
# ------------------
# To hook into the build process

# after_build = "kinhdoanh.build.after_build"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "kinhdoanh.notifications.get_notification_config"

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
# 		"kinhdoanh.tasks.all"
# 	],
# 	"daily": [
# 		"kinhdoanh.tasks.daily"
# 	],
# 	"hourly": [
# 		"kinhdoanh.tasks.hourly"
# 	],
# 	"weekly": [
# 		"kinhdoanh.tasks.weekly"
# 	],
# 	"monthly": [
# 		"kinhdoanh.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "kinhdoanh.install.before_tests"

# Extend DocType Class
# ------------------------------
#
# Specify custom mixins to extend the standard doctype controller.
# extend_doctype_class = {
# 	"Task": "kinhdoanh.custom.task.CustomTaskMixin"
# }

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "kinhdoanh.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "kinhdoanh.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["kinhdoanh.utils.before_request"]
# after_request = ["kinhdoanh.utils.after_request"]

# Job Events
# ----------
# before_job = ["kinhdoanh.utils.before_job"]
# after_job = ["kinhdoanh.utils.after_job"]

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
# 	"kinhdoanh.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Translation
# ------------
# List of apps whose translatable strings should be excluded from this app's translations.
# ignore_translatable_strings_from = []

