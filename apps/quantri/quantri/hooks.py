app_name = "quantri"
app_title = "Quản trị"
app_publisher = "GPC"
app_description = "GPC ERP - Quản trị hệ thống (User, Role, Phân quyền)"
app_email = "trieu.nt93@gmail.com"
app_license = "mit"

# Website / SPA
website_route_rules = [
	{"from_route": "/quantri_app/<path:app_path>", "to_route": "quantri_app"},
]
