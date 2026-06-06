"""API Dự án — reuse ERPNext Project & Task."""
import frappe


@frappe.whitelist()
def get_csrf_token():
	return frappe.sessions.get_csrf_token()


# ── Dashboard ──────────────────────────────────────────

@frappe.whitelist()
def get_dashboard():
	"""Số liệu tổng quan."""
	projects = frappe.db.count("Project")
	tasks = frappe.db.count("Task")
	return {
		"total_projects": projects,
		"active_projects": frappe.db.count("Project", {"status": "Open"}),
		"completed_projects": frappe.db.count("Project", {"status": "Completed"}),
		"total_tasks": tasks,
		"open_tasks": frappe.db.count("Task", {"status": ["in", ["Open", "Working", "Pending Review"]]}),
		"overdue_tasks": frappe.db.count("Task", {"exp_end_date": ["<", frappe.utils.today()], "status": ["!=", "Completed"]}),
	}


# ── Projects ───────────────────────────────────────────

@frappe.whitelist()
def get_projects(search="", status=None, page=1, page_length=20):
	"""Danh sách dự án (card view)."""
	filters = {}
	if search:
		filters["project_name"] = ["like", f"%{search}%"]
	if status:
		filters["status"] = status

	projects = frappe.get_all(
		"Project",
		filters=filters,
		fields=[
			"name", "project_name", "status", "percent_complete",
			"priority", "expected_start_date", "expected_end_date",
			"customer", "company",
		],
		order_by="creation desc",
		limit_page_length=page_length,
		start=(page - 1) * page_length,
	)

	# Đếm task mỗi project
	for p in projects:
		p["task_count"] = frappe.db.count("Task", {"project": p["name"]})
		p["open_tasks"] = frappe.db.count("Task", {"project": p["name"], "status": ["in", ["Open", "Working", "Pending Review"]]})
		p["overdue_tasks"] = frappe.db.count("Task", {"project": p["name"], "exp_end_date": ["<", frappe.utils.today()], "status": ["!=", "Completed"]})

	return projects


@frappe.whitelist()
def get_project_detail(name):
	"""Chi tiết 1 dự án."""
	doc = frappe.get_doc("Project", name)
	tasks = frappe.get_all(
		"Task",
		filters={"project": name},
		fields=[
			"name", "subject", "status", "priority",
			"exp_end_date", "progress", "_assign",
		],
		order_by="exp_end_date asc",
		limit_page_length=200,
	)

	return {
		"name": doc.name,
		"project_name": doc.project_name,
		"status": doc.status,
		"priority": doc.priority,
		"percent_complete": doc.percent_complete,
		"expected_start_date": str(doc.expected_start_date) if doc.expected_start_date else None,
		"expected_end_date": str(doc.expected_end_date) if doc.expected_end_date else None,
		"customer": doc.customer,
		"company": doc.company,
		"description": doc.description,
		"tasks": tasks,
		"task_count": len(tasks),
		"completed_tasks": len([t for t in tasks if t["status"] == "Completed"]),
	}


# ── Tasks ──────────────────────────────────────────────

@frappe.whitelist()
def get_tasks(search="", project=None, status=None, priority=None, page=1, page_length=30):
	"""Danh sách task có filter."""
	filters = {}
	if search:
		filters["subject"] = ["like", f"%{search}%"]
	if project:
		filters["project"] = project
	if status:
		filters["status"] = status
	if priority:
		filters["priority"] = priority

	return frappe.get_all(
		"Task",
		filters=filters,
		fields=[
			"name", "subject", "status", "priority",
			"project", "exp_end_date", "progress",
			"_assign", "creation",
		],
		order_by="creation desc",
		limit_page_length=page_length,
		start=(page - 1) * page_length,
	)


@frappe.whitelist()
def get_task_detail(name):
	"""Chi tiết 1 task."""
	doc = frappe.get_doc("Task", name)
	return {
		"name": doc.name,
		"subject": doc.subject,
		"status": doc.status,
		"priority": doc.priority,
		"project": doc.project,
		"progress": doc.progress,
		"exp_start_date": str(doc.exp_start_date) if doc.exp_start_date else None,
		"exp_end_date": str(doc.exp_end_date) if doc.exp_end_date else None,
		"_assign": doc._assign if hasattr(doc, '_assign') else None,
		"description": doc.description,
		"actual_time": doc.actual_time,
	}


@frappe.whitelist()
def update_task_status(name, status):
	"""Cập nhật status của task."""
	if status not in ("Open", "Working", "Pending Review", "Completed"):
		frappe.throw("Trạng thái không hợp lệ")
	frappe.db.set_value("Task", name, "status", status)
	return {"ok": True, "status": status}


@frappe.whitelist()
def get_tasks_by_status(project=None):
	"""Trả task gom theo status — dùng cho kanban."""
	filters = {}
	if project:
		filters["project"] = project
	tasks = frappe.get_all(
		"Task",
		filters=filters,
		fields=[
			"name", "subject", "status", "priority",
			"project", "exp_end_date", "progress", "_assign",
		],
		order_by="priority desc, exp_end_date asc",
		limit_page_length=500,
	)

	columns = {
		"Open": [],
		"Working": [],
		"Pending Review": [],
		"Completed": [],
	}
	for t in tasks:
		s = t.get("status", "Open")
		if s not in columns:
			columns[s] = []
		columns[s].append(t)

	return columns
