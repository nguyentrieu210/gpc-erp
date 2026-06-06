"""API mỏng cho HR — reuse doctype HRMS."""
import frappe
from datetime import datetime


def _log(doctype, docname, action, detail=""):
	"""Ghi activity log vào notes của document (dùng chung cho mọi write op)."""
	try:
		user = frappe.session.user or "System"
		ts = datetime.now().strftime("%Y-%m-%d %H:%M")
		entry = f"[LOG {ts}] {user} | {action}" + (f" | {detail}" if detail else "")
		doc = frappe.get_doc(doctype, docname)
		existing = (doc.notes or "").strip()
		doc.notes = (existing + "\n" + entry).strip()
		doc.save(ignore_permissions=True)
	except Exception:
		pass  # Log fail không block nghiệp vụ chính


@frappe.whitelist()
def get_activity_log(doctype, docname):
	"""Lấy activity log đã parse từ notes."""
	doc = frappe.get_doc(doctype, docname)
	notes = (doc.notes or "").split("\n")
	logs = []
	for line in notes:
		line = line.strip()
		if line.startswith("[LOG "):
			# Parse: [LOG 2026-06-05 14:30] user | action | detail
			rest = line[5:]  # bỏ "[LOG "
			parts = rest.split("]", 1)
			if len(parts) == 2:
				ts = parts[0].strip()
				rest2 = parts[1].strip().split(" | ", 2)
				user = rest2[0] if len(rest2) > 0 else ""
				action = rest2[1] if len(rest2) > 1 else ""
				detail = rest2[2] if len(rest2) > 2 else ""
				logs.append({"time": ts, "user": user, "action": action, "detail": detail})
	return logs


@frappe.whitelist()
def get_csrf_token():
	"""Trả về CSRF token từ session để SPA dùng cho POST requests."""
	return frappe.sessions.get_csrf_token()


@frappe.whitelist()
def seed_test_data():
	"""Seed data test — gọi 1 lần là có data."""
	from frappe import db

	if db.count("Job Opening") < 3:
		desig = db.get_value("Designation", {}, "name") or "Associate"
		for title, num in [
			("Senior Developer", 3),
			("Nhân viên Kinh doanh", 2),
			("Kế toán tổng hợp", 1),
			("Tester QA", 1),
		]:
			if not db.exists("Job Opening", {"job_title": title}):
				try:
					frappe.get_doc({
						"doctype": "Job Opening", "job_title": title,
						"designation": desig, "no_of_positions": num,
						"status": "Open", "posted_on": frappe.utils.today(),
		"closes_on": closes_on,
					}).insert(ignore_permissions=True)
				except Exception as e:
					print(f"Skip {title}: {e}")

	# Applicants — job_title là Link tới Job Opening, cần dùng name (ID)
	jobs = db.get_all("Job Opening", filters={"status": "Open"}, limit=5, fields=["name", "job_title"])
	if jobs and db.count("Job Applicant") < 5:
		names = ["Nguyễn Văn F", "Trần Thị G", "Lê Văn H", "Phạm Thị I", "Hoàng Văn K", "Đỗ Thị L", "Bùi Văn M"]
		for i, name in enumerate(names):
			j = jobs[i % len(jobs)]
			if not db.exists("Job Applicant", {"applicant_name": name}):
				try:
					frappe.get_doc({
						"doctype": "Job Applicant",
						"applicant_name": name,
						"job_title": j["name"],
						"email_id": f"app{i}@email.com",
						"status": ["Open", "Open", "Shortlisted", "Replied", "Open", "Shortlisted", "Replied"][i],
					}).insert(ignore_permissions=True)
				except Exception as e:
					print(f"Skip applicant {name}: {e}")

	frappe.db.commit()
	return {"job_openings": db.count("Job Opening"), "applicants": db.count("Job Applicant")}


@frappe.whitelist()
def get_employees(search="", page=1, page_length=200):
    """Danh sách nhân viên Active (reuse Employee của HRMS). Mặc định 200 — đủ cho dropdown chọn người phỏng vấn / các trang gọi không tham số."""
    filters = {"status": "Active"}
    if search:
        filters["employee_name"] = ["like", f"%{search}%"]
    return frappe.get_all(
        "Employee",
        filters=filters,
        fields=[
            "name", "employee_name", "designation", "department",
            "company", "date_of_joining", "cell_number",
        ],
        order_by="employee_name asc",
        limit_page_length=page_length,
        start=(page - 1) * page_length,
    )


@frappe.whitelist()
def get_employee_detail(name):
    """Chi tiết 1 nhân viên."""
    return frappe.get_doc("Employee", name).as_dict()


@frappe.whitelist()
def get_leaves(employee=None, year=None):
    """Đơn nghỉ phép (Leave Application) — lọc theo employee."""
    filters = {}
    if employee:
        filters["employee"] = employee
    if year:
        filters["from_date"] = [">=", f"{year}-01-01"]
        filters["to_date"] = ["<=", f"{year}-12-31"]
    return frappe.get_all(
        "Leave Application",
        filters=filters,
        fields=[
            "name", "employee", "employee_name", "leave_type",
            "from_date", "to_date", "status", "total_leave_days",
        ],
        order_by="from_date desc",
        limit_page_length=50,
    )


@frappe.whitelist()
def get_departments():
	"""Danh sách phòng ban."""
	return frappe.get_all("Department", filters={"is_group": 0}, pluck="name", limit=50)


@frappe.whitelist()
def get_salary_slips(employee=None, year=None, month=None):
	"""Bảng lương (Salary Slip) — lọc theo employee / năm / tháng."""
	import calendar as _cal
	filters = {}
	if employee:
		filters["employee"] = employee
	if year and month:
		year, month = int(year), int(month)
		last = _cal.monthrange(year, month)[1]
		filters["start_date"] = [">=", f"{year}-{month:02d}-01"]
		filters["end_date"] = ["<=", f"{year}-{month:02d}-{last:02d}"]
	elif year:
		filters["start_date"] = [">=", f"{year}-01-01"]
		filters["end_date"] = ["<=", f"{year}-12-31"]
	return frappe.get_all(
		"Salary Slip",
		filters=filters,
		fields=[
			"name", "employee", "employee_name", "designation",
			"start_date", "end_date", "total_working_days",
			"gross_pay", "total_deduction", "net_pay", "docstatus",
		],
		order_by="start_date desc",
		limit_page_length=100,
	)


@frappe.whitelist()
def get_job_openings(status=None):
	"""Danh sách vị trí tuyển dụng (Job Opening)."""
	import re
	filters = {}
	if status:
		filters["status"] = status
	openings = frappe.get_all(
		"Job Opening",
		filters=filters,
		fields=[
			"name", "job_title", "designation", "department",
			"status", "posted_on", "closes_on",
			"description", "planned_vacancies",
		],
		order_by="posted_on desc",
		limit_page_length=30,
	)
	for jo in openings:
		desc = jo.get("description") or ""
		# Extract recruiter
		rec_match = re.search(r'\[RECRUITER\]\s*(.*)', desc)
		jo["recruiter"] = rec_match.group(1).strip() if rec_match else ""
		
		# Extract salary_range
		sal_match = re.search(r'💰 Mức lương:\s*(.*)', desc)
		jo["salary_range"] = sal_match.group(1).strip() if sal_match else ""
		
		# Clean description by removing recruiter marker
		if "[RECRUITER]" in desc:
			jo["description"] = desc.split("\n\n[RECRUITER]")[0].strip()
			
		jo["positions"] = int(jo.get("planned_vacancies") or 1)
	return openings


@frappe.whitelist()
def get_job_applicants(job=None, status=None):
	"""Danh sách ứng viên (Job Applicant)."""
	_ensure_applicant_fields()
	filters = {}
	if job:
		filters["job_title"] = job
	if status:
		filters["status"] = status
	apps = frappe.get_all(
		"Job Applicant",
		filters=filters,
		fields=[
			"name", "applicant_name", "email_id",
			"job_title", "status", "source_name", "source",
			"creation", "designation", "phone_number",
			"resume_attachment", "owner",
			"custom_offered_salary", "lower_range", "upper_range"
		],
		order_by="creation desc",
		limit_page_length=50,
	)
	# Resolve actual job titles from Job Opening
	from collections import defaultdict as _dd
	jt_map = {}
	owner_map = {}
	for a in apps:
		if a.get("job_title") and a["job_title"] not in jt_map:
			try:
				real = frappe.db.get_value("Job Opening", a["job_title"], "job_title")
				jt_map[a["job_title"]] = real or a["job_title"]
			except:
				jt_map[a["job_title"]] = a["job_title"]
		
		owner_email = a.get("owner")
		if owner_email and owner_email not in owner_map:
			try:
				fn = frappe.db.get_value("User", owner_email, "full_name")
				owner_map[owner_email] = fn or owner_email
			except:
				owner_map[owner_email] = owner_email

	for a in apps:
		a["job_opening_title"] = jt_map.get(a["job_title"], a["job_title"])
		rec = ""
		try:
			notes = frappe.db.get_value("Job Applicant", a["name"], "notes") or ""
			for line in notes.split("\n"):
				if line.strip().startswith("[RECRUITER] "):
					rec = line.strip()[12:].strip()
					break
		except: pass
		a["recruiter"] = rec or owner_map.get(a.get("owner"), a.get("owner") or "")
		# Extract fit_score from notes if available
		try:
			notes = frappe.db.get_value("Job Applicant", a["name"], "notes") or ""
			for line in notes.split("\n"):
				if line.strip().startswith("[CVDATA] "):
					try:
						import json as _j2
						cv = _j2.loads(line.strip()[8:])
						a["cv_fit_score"] = cv.get("fit_score")
						a["cv_avatar"] = cv.get("avatar_base64", "") or ""
						a["cv_suggested"] = cv.get("suggested_positions", []) or []
					except: pass
					break
		except: pass
	return apps

@frappe.whitelist()
def create_job_opening(job_title, designation=None, department=None, description=None, closes_on=None, recruiter=None):
	"""Tạo vị trí tuyển dụng mới."""
	if not designation:
		designation = frappe.db.get_value("Designation", {}, "name") or "Associate"
	
	positions = frappe.form_dict.get("positions") or 1
	desc_val = description or ""
	if recruiter:
		desc_val = f"{desc_val}\n\n[RECRUITER] {recruiter}"
		
	doc = frappe.get_doc({
		"doctype": "Job Opening",
		"job_title": job_title,
		"designation": designation,
		"department": (department and frappe.db.exists("Department", department) and department) or None,
		"description": desc_val,
		"planned_vacancies": positions,
		"status": "Open",
		"posted_on": frappe.utils.today(),
		"closes_on": closes_on,
	})
	doc.insert(ignore_permissions=True)
	_log("Job Opening", doc.name, "create_job", job_title)
	return doc.as_dict()


@frappe.whitelist()
def update_job_opening(name, job_title=None, designation=None, department=None, description=None, status=None, closes_on=None, recruiter=None):
	"""Sửa vị trí tuyển dụng."""
	doc = frappe.get_doc("Job Opening", name)
	if job_title: doc.job_title = job_title
	if designation and frappe.db.exists("Designation", designation): doc.designation = designation
	if department and frappe.db.exists("Department", department): doc.department = department
	
	desc_val = description if description is not None else doc.description or ""
	# Remove any existing [RECRUITER] marker from description before appending new one
	if "[RECRUITER]" in desc_val:
		desc_val = desc_val.split("\n\n[RECRUITER]")[0].strip()
	if recruiter:
		desc_val = f"{desc_val}\n\n[RECRUITER] {recruiter}"
	doc.description = desc_val
	
	if status: doc.status = status
	if closes_on is not None: doc.closes_on = closes_on
	
	positions = frappe.form_dict.get("positions")
	if positions:
		doc.planned_vacancies = positions
		
	doc.save(ignore_permissions=True)
	return doc.as_dict()


@frappe.whitelist()
def delete_job_opening(name):
	"""Xoa vi tri + tat ca ung vien."""
	applicants = frappe.db.get_all("Job Applicant", filters={"job_title": name}, pluck="name")
	for a in applicants:
		try:
			frappe.delete_doc("Job Applicant", a, ignore_permissions=True)
		except Exception as e:
			frappe.log_error(title="cv_data save failed", message=str(e)[:300])
	frappe.delete_doc("Job Opening", name, ignore_permissions=True)
	return {"ok": True, "deleted_applicants": len(applicants)}


def _ensure_source(source_name):
	if not source_name:
		return None
	if not frappe.db.exists("Job Applicant Source", source_name):
		try:
			s_doc = frappe.get_doc({
				"doctype": "Job Applicant Source",
				"source_name": source_name
			})
			s_doc.insert(ignore_permissions=True)
		except Exception as e:
			frappe.log_error(title="Failed to create Job Applicant Source", message=str(e))
	return source_name


@frappe.whitelist()
def create_job_applicant(job_title, applicant_name, email_id=None, phone_number=None, source_name=None, cv_data=None, resume_attachment=None, designation=None, country=None, lower_range=None, upper_range=None, cover_letter=None, custom_offered_salary=None):
	"""Thêm ứng viên mới (đầy đủ fields + CV data)."""
	import json as _json
	doc = frappe.get_doc({
		"doctype": "Job Applicant",
		"job_title": job_title,
		"applicant_name": applicant_name,
		"email_id": email_id,
		"phone_number": phone_number,
		"source": _ensure_source(source_name),
		"resume_attachment": resume_attachment,
		"designation": designation,
		"country": country or "Vietnam",
		"lower_range": lower_range or 0,
		"upper_range": upper_range or 0,
		"custom_offered_salary": custom_offered_salary or 0,
		"cover_letter": cover_letter,
		"status": "Open",
	})
	
	# Tự động gán Recruiter của vị trí tuyển dụng nếu có
	if job_title:
		try:
			job_desc = frappe.db.get_value("Job Opening", job_title, "description") or ""
			import re as _re
			rec_match = _re.search(r'\[RECRUITER\]\s*(.*)', job_desc)
			if rec_match:
				recruiter_name = rec_match.group(1).strip()
				if recruiter_name:
					doc.notes = (doc.notes or "").strip() + f"\n[RECRUITER] {recruiter_name}"
					doc.notes = doc.notes.strip()
		except:
			pass

	doc.insert(ignore_permissions=True)

	# Lưu CV parsed data vào notes dưới dạng JSON
	if cv_data:
		try:
			if isinstance(cv_data, str):
				cv_data = _json.loads(cv_data)
			cv_json = _json.dumps(cv_data, ensure_ascii=False)
			doc.notes = (doc.notes or "").strip()
			doc.notes = doc.notes + "\n[CVDATA] " + cv_json
			doc.notes = doc.notes.strip()
			doc.save(ignore_permissions=True)
		except Exception as e:
			frappe.log_error(title="cv_data save failed", message=str(e)[:300])

	_log("Job Applicant", doc.name, "create_applicant", applicant_name)
	return doc.as_dict()


@frappe.whitelist()
def get_recruitment_dashboard():
	"""Tổng quan tuyển dụng — stats cho dashboard."""
	from frappe import db

	statuses = ["Open", "Shortlisted", "Replied", "Hold", "Accepted", "Rejected"]
	by_status = {}
	for s in statuses:
		by_status[s] = db.count("Job Applicant", {"status": s})

	# Nguồn ứng viên
	sources = db.get_all("Job Applicant", fields=["source_name"], group_by="source_name", pluck="source_name", limit=20)
	by_source = {}
	for src in sources:
		src_key = src or "Khác"
		by_source[src_key] = db.count("Job Applicant", {"source_name": src})

	return {
		"jobs_open": db.count("Job Opening", {"status": "Open"}),
		"jobs_total": db.count("Job Opening"),
		"applicants_total": db.count("Job Applicant"),
		"applicants_today": db.count("Job Applicant", {"creation": [">=", frappe.utils.today()]}),
		"by_status": by_status,
		"by_source": by_source,
	}


@frappe.whitelist()
def get_applicants_filtered(search="", status=None, job=None, source=None, page=1, page_length=50):
	"""Danh sách ứng viên có filter + search."""
	_ensure_applicant_fields()
	filters = {}
	if search:
		filters["applicant_name"] = ["like", f"%{search}%"]
	if status:
		filters["status"] = status
	if job:
		filters["job_title"] = job
	if source:
		filters["source_name"] = source

	return frappe.get_all(
		"Job Applicant",
		filters=filters,
		fields=["name", "applicant_name", "email_id", "phone_number", "job_title", "status", "source_name", "source", "creation", "custom_offered_salary", "lower_range", "upper_range"],
		order_by="creation desc",
		limit_page_length=page_length,
		start=(page - 1) * page_length,
	)


@frappe.whitelist()
def update_applicant_status(name, status):
	"""Cập nhật trạng thái ứng viên trong pipeline."""
	valid = ["Open", "Replied", "Hold", "Shortlisted", "Rejected", "Accepted"]
	if status not in valid:
		frappe.throw(f"Trạng thái không hợp lệ. Phải là: {', '.join(valid)}")
	frappe.db.set_value("Job Applicant", name, "status", status)
	_log("Job Applicant", name, "status_change", f"→ {status}")
	return {"ok": True, "status": status}


@frappe.whitelist()
def delete_job_applicant(name):
	"""Xoa ung vien."""
	frappe.delete_doc("Job Applicant", name, ignore_permissions=True)
	return {"ok": True}


@frappe.whitelist()
def delete_multiple_applicants(names):
	"""Xoá nhiều ứng viên cùng lúc."""
	import json as _json
	if isinstance(names, str):
		try: names = _json.loads(names)
		except: pass
	if not isinstance(names, list):
		names = [names]
	for name in names:
		if name:
			frappe.delete_doc("Job Applicant", name, ignore_permissions=True)
	return {"ok": True, "count": len(names)}


@frappe.whitelist()
def update_job_applicant(name, **kwargs):
	"""Cập nhật thông tin ứng viên."""
	doc = frappe.get_doc("Job Applicant", name)
	allowed_fields = [
		"applicant_name", "email_id", "phone_number", "job_title", 
		"designation", "country", "lower_range", "upper_range", "cover_letter", "status",
		"custom_offered_salary"
	]
	for field in allowed_fields:
		if field in kwargs:
			val = kwargs[field]
			if field in ("lower_range", "upper_range", "custom_offered_salary"):
				try: val = float(val) if val else 0
				except: val = 0
			doc.set(field, val)
	
	if "source_name" in kwargs:
		doc.source = _ensure_source(kwargs["source_name"])
		
	doc.save(ignore_permissions=True)
	return doc.as_dict()


@frappe.whitelist()
def save_applicant_avatar(name, avatar_base64):
	"""Luu anh dai dien cho ung vien vao CVDATA notes."""
	import json as _json
	doc = frappe.get_doc("Job Applicant", name)
	notes_text = doc.notes or ""
	cv_data = {}
	clean_lines = []

	for line in notes_text.split("\n"):
		line_s = line.strip()
		if line_s.startswith("[CVDATA] "):
			try: cv_data = _json.loads(line_s[8:])
			except: pass
		else:
			clean_lines.append(line_s)

	cv_data["avatar_base64"] = avatar_base64
	cv_json = _json.dumps(cv_data, ensure_ascii=False)
	clean_lines.append("[CVDATA] " + cv_json)
	doc.notes = "\n".join(clean_lines).strip()
	doc.save(ignore_permissions=True)
	_log("Job Applicant", name, "update_avatar", "Updated avatar")
	return {"ok": True}


@frappe.whitelist()
def save_checklist(name, checklist):
	"""Luu checklist ho so cua ung vien."""
	import json as _json
	doc = frappe.get_doc("Job Applicant", name)
	notes_text = doc.notes or ""
	clean_lines = []

	for line in notes_text.split("\n"):
		line_s = line.strip()
		if not line_s.startswith("[CHECKLIST]"):
			clean_lines.append(line_s)

	clean_lines.append("[CHECKLIST] " + (checklist if isinstance(checklist, str) else _json.dumps(checklist, ensure_ascii=False)))
	doc.notes = "\n".join(clean_lines).strip()
	doc.save(ignore_permissions=True)
	_log("Job Applicant", name, "checklist_update", "Updated checklist")
	return {"ok": True}


@frappe.whitelist()
def submit_interview_result(applicant, interview_id, passed=True, score=0, rating="", strengths=None, weaknesses=None, notes="", extra_notes=""):
	"""Nhap ket qua phong van — co them danh gia chung + y kien bo sung."""
	import json as _json
	doc = frappe.get_doc("Job Applicant", applicant)
	notes_text = doc.notes or ""
	updated = False
	lines = notes_text.split("\n")
	for i, line in enumerate(lines):
		line = line.strip()
		if line.startswith("[INTERVIEW] "):
			try:
				iv = _json.loads(line[12:])
				if iv.get("id") == interview_id:
					iv["status"] = "passed" if passed in (True, "true", "True", 1) else "failed"
					iv["score"] = int(score) if score else 0
					iv["rating"] = rating or ""
					iv["strengths"] = _json.loads(strengths) if isinstance(strengths, str) else (strengths or [])
					iv["weaknesses"] = _json.loads(weaknesses) if isinstance(weaknesses, str) else (weaknesses or [])
					iv["notes"] = notes
					iv["extra_notes"] = extra_notes or ""
					lines[i] = "[INTERVIEW] " + _json.dumps(iv, ensure_ascii=False)
					updated = True
					break
			except: pass
	if not updated:
		frappe.throw("Khong tim thay lich phong van")
	doc.notes = "\n".join(lines)
	if passed:
		doc.status = "Accepted"
	doc.save(ignore_permissions=True)
	_log("Job Applicant", applicant, "interview_result", f"{'Dat' if passed else 'Khong dat'} - Score: {score}")
	return {"ok": True}


@frappe.whitelist()
def reject_applicant(name, reason="", missing_requirements=None):
	"""Tu choi ung vien voi ly do."""
	import json as _json
	doc = frappe.get_doc("Job Applicant", name)
	doc.status = "Rejected"
	entry = {"reason": reason, "date": frappe.utils.today(), "missing": _json.loads(missing_requirements) if isinstance(missing_requirements, str) else (missing_requirements or [])}
	doc.notes = (doc.notes or "").strip() + "\n[REJECT] " + _json.dumps(entry, ensure_ascii=False)
	doc.save(ignore_permissions=True)
	_log("Job Applicant", name, "reject", reason[:100])
	return {"ok": True}


@frappe.whitelist()
def hold_applicant(name, reason="", missing_requirements=None):
	"""Can nhac ung vien - ghi nhan yeu cau con thieu."""
	import json as _json
	doc = frappe.get_doc("Job Applicant", name)
	doc.status = "Hold"
	entry = {"reason": reason, "date": frappe.utils.today(), "missing": _json.loads(missing_requirements) if isinstance(missing_requirements, str) else (missing_requirements or [])}
	doc.notes = (doc.notes or "").strip() + "\n[HOLD] " + _json.dumps(entry, ensure_ascii=False)
	doc.save(ignore_permissions=True)
	_log("Job Applicant", name, "hold", reason[:100])
	return {"ok": True}


@frappe.whitelist()
def get_applicant_detail(name):
	"""Chi tiet ung vien - CV data + interview history + clean notes."""
	_ensure_applicant_fields()
	import json as _json
	doc = frappe.get_doc("Job Applicant", name)
	result = doc.as_dict()

	notes = result.get("notes") or ""
	cv_data = {}
	interview_history = []
	clean_lines = []

	for line in notes.split("\n"):
		line_s = line.strip()
		if not line_s:
			continue
		if line_s.startswith("[CVDATA] "):
			try: cv_data = _json.loads(line_s[8:])
			except: pass
		elif line_s.startswith("[INTERVIEW] "):
			try: interview_history.append(_json.loads(line_s[12:]))
			except: pass
		elif line_s.startswith("[REJECT] "):
			try: result["reject_info"] = _json.loads(line_s[9:])
			except: pass
		elif line_s.startswith("[HOLD] "):
			try: result["hold_info"] = _json.loads(line_s[7:])
			except: pass
		elif not line_s.startswith("[LOG ") and not line_s.startswith("[DA TUYEN]") and not line_s.startswith("[CHECKLIST]"):
			clean_lines.append(line_s)

	result["cv_data"] = cv_data
	result["interview_history"] = interview_history
	result["checklist"] = []
	# Parse checklist from notes (not from clean_lines since we filter it above)
	for line in notes.split("\n"):
		line_s = line.strip()
		if line_s.startswith("[CHECKLIST] "):
			try: result["checklist"] = _json.loads(line_s[12:])
			except: pass
	result["clean_notes"] = "\n".join(clean_lines).strip()
	# Resolve actual Job Opening title (job_title field is the Link ID)
	if result.get("job_title"):
		try:
			real = frappe.db.get_value("Job Opening", result["job_title"], ["job_title", "description"], as_dict=True)
			if real:
				result["job_opening_title"] = real.job_title
				desc = real.description or ""
				import re
				sal_match = re.search(r'💰 Mức lương:\s*(.*)', desc)
				result["job_salary_range"] = sal_match.group(1).strip() if sal_match else ""
		except:
			pass
	
	# Resolve recruiter full name from owner
	if result.get("owner"):
		try:
			result["recruiter"] = frappe.db.get_value("User", result["owner"], "full_name") or result["owner"]
		except:
			result["recruiter"] = result["owner"]
			
	return result
@frappe.whitelist()
def get_all_interviews():
	"""Lấy tất cả lịch phỏng vấn từ tất cả ứng viên."""
	import json as _json
	applicants = frappe.get_all(
		"Job Applicant",
		fields=["name", "applicant_name", "job_title", "status", "email_id", "phone_number"]
	)
	
	# Resolve job titles
	jt_map = {}
	for a in applicants:
		if a.get("job_title") and a["job_title"] not in jt_map:
			try:
				real = frappe.db.get_value("Job Opening", a["job_title"], "job_title")
				jt_map[a["job_title"]] = real or a["job_title"]
			except:
				jt_map[a["job_title"]] = a["job_title"]
				
	interviews = []
	for app in applicants:
		notes = frappe.db.get_value("Job Applicant", app["name"], "notes") or ""
		is_converted = 1 if ("[ĐÃ TUYỂN]" in notes or "[DA TUYEN]" in notes) else 0
		cv_avatar = ""
		for line in notes.split("\n"):
			line_s = line.strip()
			if line_s.startswith("[CVDATA] "):
				try:
					cv_data = _json.loads(line_s[8:])
					cv_avatar = cv_data.get("avatar_base64") or ""
				except:
					pass
		for line in notes.split("\n"):
			line_s = line.strip()
			if line_s.startswith("[INTERVIEW] "):
				try:
					iv = _json.loads(line_s[12:])
					iv["applicant_id"] = app["name"]
					iv["applicant_name"] = app["applicant_name"]
					iv["job_opening_title"] = jt_map.get(app["job_title"], app["job_title"])
					iv["email_id"] = app["email_id"]
					iv["phone_number"] = app["phone_number"]
					iv["is_converted"] = is_converted
					iv["cv_avatar"] = cv_avatar
					interviews.append(iv)
				except:
					pass
					
	interviews.sort(key=lambda x: x.get("date", ""), reverse=True)
	return interviews


@frappe.whitelist()
def schedule_interview(applicant, round_name="Vòng 1", date=None, interviewer=None, interviewer_employee=None, notes=""):
	"""Len lich phong van - luu JSON structured. interviewer_employee la link den Employee doc."""
	import json as _json, datetime as _dt
	# Resolve interviewer name if employee link provided but name missing
	interviewer_name = interviewer or ""
	if interviewer_employee and not interviewer_name:
		try:
			interviewer_name = frappe.db.get_value("Employee", interviewer_employee, "employee_name") or interviewer_employee
		except:
			interviewer_name = interviewer_employee
	iv = {
		"id": _dt.datetime.now().strftime("%Y%m%d%H%M%S"),
		"round": round_name, "date": date or frappe.utils.today(),
		"interviewer": interviewer_name,
		"interviewer_employee": interviewer_employee or "",
		"notes": notes or "",
		"status": "scheduled", "score": None, "strengths": [], "weaknesses": []
	}
	doc = frappe.get_doc("Job Applicant", applicant)
	existing = (doc.notes or "").strip()
	doc.notes = existing + "\n[INTERVIEW] " + _json.dumps(iv, ensure_ascii=False)
	doc.status = "Replied"
	doc.save(ignore_permissions=True)
	_log("Job Applicant", applicant, "schedule_interview", f"{round_name} - {iv['date']}")
	return {"ok": True, "interview": iv}
	if interviewer:
		note += f" - Người PV: {interviewer}"
	if notes:
		note += f"\nGhi chú: {notes}"
	existing = doc.notes or ""
	doc.notes = (existing + "\n" + note).strip()
	doc.status = "Replied"  # Chuyển sang trạng thái Phỏng vấn
	doc.save(ignore_permissions=True)
	_log("Job Applicant", applicant, "schedule_interview", f"{round_name} - {interview_date}")
	return {"ok": True, "round": round_name, "date": interview_date}


# Marker lưu nguồn tuyển dụng trong field `bio` của Employee (Employee không có `notes`)
RECRUIT_TAG = "[NGUỒN_TUYỂN_DỤNG]"


@frappe.whitelist()
def convert_to_employee(applicant, first_name=None, last_name=None, gender=None, date_of_birth=None,
		date_of_joining=None, department=None, designation=None, personal_email=None, phone=None,
		location=None, company=None, salary=None):
	"""Tạo Employee từ ứng viên đã trúng tuyển — auto-fill từ CV + form."""
	app = frappe.get_doc("Job Applicant", applicant)
	# Parse name từ applicant name nếu chưa có
	if not first_name and not last_name:
		parts = app.applicant_name.strip().split(" ", 1)
		first_name = parts[0]
		last_name = parts[1] if len(parts) > 1 else ""
	if not first_name:
		first_name = app.applicant_name

	if frappe.db.exists("Employee", {"employee_name": f"{first_name} {last_name or ''}".strip()}):
		frappe.throw("Nhân viên đã tồn tại: " + f"{first_name} {last_name or ''}".strip())

	# Job Opening info
	job_dept = frappe.db.get_value("Job Opening", app.job_title, "department") if app.job_title else None
	job_label = (frappe.db.get_value("Job Opening", app.job_title, "job_title") if app.job_title else None) or app.job_title or ""
	applied = str(app.creation)[:10] if app.creation else ""

	src = f"{RECRUIT_TAG} applicant={app.name} | applicant_name={app.applicant_name} | job={job_label} | applied={applied}"

	# Parse dob: handle dd/mm/yyyy, dd-mm-yyyy, yyyy-mm-dd
	dob_parsed = None
	if date_of_birth:
		import re as _re2
		try:
			# Check format
			m = _re2.match(r'(\d{1,2})[/\-](\d{1,2})[/\-](\d{4})', date_of_birth)
			if m: dob_parsed = f"{m.group(3)}-{m.group(2).zfill(2)}-{m.group(1).zfill(2)}"
			else: dob_parsed = date_of_birth
		except: dob_parsed = date_of_birth

	salary_val = salary or getattr(app, "custom_offered_salary", 0) or 0
	emp = frappe.get_doc({
		"doctype": "Employee",
		"first_name": first_name,
		"last_name": last_name or "",
		"gender": gender or "Male",
		"date_of_birth": dob_parsed or "1990-01-01",
		"date_of_joining": date_of_joining or frappe.utils.today(),
		"company": company or _default_company(),
		"designation": designation or app.designation or None,
		"department": department or job_dept or None,
		"personal_email": personal_email or app.email_id or None,
		"cell_number": phone or getattr(app, "phone_number", None) or None,
		"current_address": location or "",
		"status": "Active",
		"bio": src,
		"custom_luong_co_ban": salary_val,
		"ctc": salary_val * 12,
	})
	emp.insert(ignore_permissions=True)

	# Copy avatar từ Job Applicant sang Employee (nếu có)
	try:
		cv_raw = app.get("custom_cv_data") or ""
		cv_data = {}
		try:
			cv_data = _json.loads(cv_raw) if isinstance(cv_raw, str) and cv_raw.strip() else {}
		except Exception:
			pass
		avatar_b64 = cv_data.get("avatar_base64") or ""
		if avatar_b64 and not emp.image:
			import base64 as _b64, io, os
			fname = f"avatar_{emp.name}.jpg"
			file_doc = frappe.get_doc({
				"doctype": "File", "file_name": fname, "is_private": 0,
				"attached_to_doctype": "Employee", "attached_to_name": emp.name,
				"content": avatar_b64, "decode": True,
			})
			file_doc.insert(ignore_permissions=True)
			frappe.db.set_value("Employee", emp.name, "image", file_doc.file_url)
	except Exception:
		pass

	# Liên kết ngược: ghi vào Job Applicant + chuyển status Accepted
	app.status = "Accepted"
	link_note = f"[ĐÃ TUYỂN] employee={emp.name} | employee_name={emp.employee_name} | date={frappe.utils.today()}"
	app.notes = ((app.notes or "") + "\n" + link_note).strip()
	app.save(ignore_permissions=True)
	_log("Job Applicant", applicant, "convert_employee", emp.employee_name)

	return {"ok": True, "employee": emp.name, "employee_name": emp.employee_name}


@frappe.whitelist()
def parse_cv(job_title=None):
	"""AI parse CV + danh gia muc do phu hop voi vi tri (DeepSeek)."""
	import re as _re, io, json as _json, os as _os
	from pypdf import PdfReader
	from PIL import Image as _PILImage

	files = frappe.request.files
	if not files:
		frappe.throw("Vui lòng upload file CV (PDF)")

	file_obj = list(files.values())[0]
	filename = file_obj.filename.lower()
	text = ""
	avatar_base64 = None

	if filename.endswith(".pdf"):
		import base64 as _b64
		reader = PdfReader(io.BytesIO(file_obj.read()))
		for i, page in enumerate(reader.pages):
			t = page.extract_text() or ""
			text += t + "\n"
			# Try to extract face photo from first page
			if i == 0 and not avatar_base64:
				candidates = []
				for img_key in list(page.images.keys()):
					try:
						img_data = page.images[img_key].data
						img = _PILImage.open(io.BytesIO(img_data))
						w, h = img.size
						# Collect all reasonable-sized images, pick best later
						if w > 40 and h > 40:
							candidates.append((w * h, w, h, img))
					except:
						continue
				if candidates:
					# Pick the largest image that's not full-page (face photo should be < 1/3 page area)
					candidates.sort(key=lambda x: x[0], reverse=True)
					for area, w, h, img in candidates:
						# Face photo typically 80-600px, portrait orientation, not too wide
						if w < 2000 and h < 2000:
							try:
								if img.mode in ('RGBA', 'P', 'CMYK'):
									img = img.convert('RGB')
								buf = io.BytesIO()
								img.save(buf, format="JPEG", quality=85)
								avatar_base64 = _b64.b64encode(buf.getvalue()).decode()
								break
							except:
								continue
	elif filename.endswith(".docx"):
		try:
			from docx import Document
			doc = Document(io.BytesIO(file_obj.read()))
			text = "\n".join(p.text for p in doc.paragraphs)
		except ImportError:
			frappe.throw("Chi ho tro PDF.")
	else:
		frappe.throw("Chi ho tro PDF hoac DOCX")

	if not text.strip():
		return {"error": "Khong doc duoc noi dung CV", "text": ""}

	# DeepSeek AI Parse + Job Fit
	api_key = _os.environ.get("DEEPSEEK_API_KEY", "")
	text_for_ai = text[:6000]

	if api_key:
		import requests as _http

		jd_text = ""
		if job_title:
			try:
				jd = frappe.db.get_value("Job Opening", job_title, "description")
				if jd:
					jd_text = "\n\nMO TA CONG VIEC:\n" + jd[:2000]
			except: pass

		prompt = """Ban la chuyen gia HR. Hay phan tich CV ung vien va danh gia muc do phu hop voi vi tri. LUON TRA LOI BANG TIENG VIET CO DAU DAY DU (a, a, e, e, o, o, u, u, i, y, d).

TRA VE JSON (khong markdown, khong giai thich):
{
  "name": "Ho ten",
  "email": "email",
  "phone": "so dien thoai",
  "location": "thanh pho",
  "dob": "ngay sinh neu co",
  "gender": "Nam hoac Nu (doan tu ten, anh)",
  "summary": "tom tat 2-3 cau tieng Viet",
  "education": ["- Truong A - Nganh B (2018-2022)", ...],
  "experience": ["- Vi tri tai Cong ty (2020-2023): mo ta", ...],
  "skills": ["Python", "React", ...],
  "languages": ["Tieng Anh - IELTS 7.0", ...],
  "links": ["linkedin.com/in/...", ...],
  "fit_score": 75,
  "fit_level": "Rat phu hop|Phu hop|Tam duoc|Chua phu hop",
  "fit_reason": "Danh gia 1-2 cau",
  "strengths": ["5 nam React", "Tieng Anh tot", ...],
  "gaps": ["Thieu AWS", "Chua co kinh nghiem quan ly", ...],
  "suggested_positions": ["Ten vi tri phu hop 1", "Ten vi tri 2", ...]
}

Trong "suggested_positions": dua ra 1-3 vi tri/ chuc danh ma ung vien nay phu hop nhat (vi du: "Lap trinh vien Python", "Truong phong Chuyen doi so", ...)
QUY TAC:
- fit_score: 0-100. Hãy chấm điểm RẤT RỘNG RÃI và NỚI LỎNG (lenient). Ưu tiên kinh nghiệm thực tế, khả năng thích ứng và kỹ năng có thể chuyển đổi hơn là bằng cấp hoặc sự trùng khớp 100% về từ khóa. Điểm số thông thường nên dao động từ 65 đến 95. Chỉ cho dưới 50 điểm nếu hồ sơ hoàn toàn không liên quan gì đến vị trí ứng tuyển.
  - Phân loại: >=80 là Rất phù hợp, 65-79 là Phù hợp, 45-64 là Tạm được, <45 là Chưa phù hợp.
- Neu khong co JD: danh gia dua tren kinh nghiem va ky nang chung, cho diem tu 70 den 90 tuy chat luong CV.

CV:
""" + text_for_ai + jd_text

		try:
			resp = _http.post(
				"https://api.deepseek.com/chat/completions",
				headers={"Authorization": "Bearer " + api_key, "Content-Type": "application/json"},
				json={
					"model": "deepseek-chat",
					"messages": [
						{"role": "system", "content": "Luon tra JSON thuan, khong markdown."},
						{"role": "user", "content": prompt},
					],
					"temperature": 0.2,
					"max_tokens": 3000,
				},
				timeout=45,
			)
			resp.raise_for_status()
			raw = resp.json()["choices"][0]["message"]["content"].strip()

			if raw.startswith("```"):
				raw = raw.split("\n", 1)[-1]
				if raw.endswith("```"):
					raw = raw[:-3]
				raw = raw.strip()
				if raw.startswith("json"):
					raw = raw[4:].strip()

			parsed = _json.loads(raw)

			return {
				"text": text[:3000],
				"name": parsed.get("name", ""),
				"email": parsed.get("email", ""),
				"phone": parsed.get("phone", ""),
				"location": parsed.get("location", ""),
				"dob": parsed.get("dob", ""),
				"gender": parsed.get("gender", ""),
				"summary": parsed.get("summary", ""),
				"education": parsed.get("education", []),
				"experience": parsed.get("experience", []),
				"skills": parsed.get("skills", []),
				"languages": parsed.get("languages", []),
				"links": parsed.get("links", []),
				"fit_score": parsed.get("fit_score", 50),
				"fit_level": parsed.get("fit_level", ""),
				"fit_reason": parsed.get("fit_reason", ""),
				"strengths": parsed.get("strengths", []),
				"gaps": parsed.get("gaps", []),
				"suggested_positions": parsed.get("suggested_positions", []),
				"avatar_base64": avatar_base64,
				"word_count": len(text.split()),
				"ai_model": "deepseek-chat",
			}
		except Exception as _e:
			pass  # fall through to regex

	# Regex Fallback
	lines = [l.strip() for l in text.split("\n") if l.strip()]
	full_text = " ".join(lines)
	emails = _re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", full_text, _re.I)
	phone_clean = full_text.replace(" ", "").replace(".", "").replace("-", "")
	phones = _re.findall(r"(0[3|5|7|8|9]\d{8})", phone_clean)

	skip_kw = ["cv", "resume", "curriculum", "profile", "ho so", "mobile", "phone",
		"email", "address", "github", "linkedin", "http",
		"thong tin", "hoc van", "kinh nghiem", "ky nang", "ngon ngu", "chung chi",
		"gioi thieu", "du an", "lien he", "so thich", "giai thuong", "ca nhan",
		"education", "experience", "skills", "language", "certificate"]
	name = ""
	for line in lines[:8]:
		cleaned = _re.sub(r"[^\w\s]", "", line).strip()
		words = cleaned.split()
		if (2 <= len(words) <= 5 and not any(kw in line.lower() for kw in skip_kw)
			and not _re.search(r"\d", line) and not _re.search(r"[@:/\]", line)
			and len(line) < 60):
			name = line
			break
	if not name and lines:
		name = lines[0][:50]

	return {
		"text": text[:3000], "name": name.strip(),
		"email": emails[0] if emails else "",
		"phone": phones[0] if phones else "",
		"location": "", "dob": "", "gender": "", "summary": "",
		"education": [], "experience": [], "skills": [],
		"languages": [], "links": [],
		"fit_score": 0, "fit_level": "", "fit_reason": "",
		"strengths": [], "gaps": [],
		"avatar_base64": avatar_base64,
		"word_count": len(text.split()), "ai_model": None,
	}

@frappe.whitelist()
def generate_jd(job_title, departments=None):
	"""AI tao Job Description day du + goi y phong ban."""
	import os as _os, json as _json, requests as _http
	api_key = _os.environ.get("DEEPSEEK_API_KEY", "")
	if not api_key:
		frappe.throw("Chua cau hinh DEEPSEEK_API_KEY")

	dept_list = []
	if departments:
		try:
			dept_list = _json.loads(departments) if isinstance(departments, str) else departments
		except: pass
	dept_hint = ""
	if dept_list:
		dept_hint = f'\\n- department: CHON 1 phong ban phu hop NHAT trong danh sach: {_json.dumps(dept_list, ensure_ascii=False)}'

	prompt = f"""Ban la chuyen gia HR gioi. Hay tao Job Description HOAN CHINH cho vi tri "{job_title}" tai mot cong ty cong nghe vua va nho o Viet Nam.

TRA VE JSON (khong markdown, khong giai thich):
{{
  "job_title": "ten vi tri (giu nguyen hoac chinh lai cho chuyen nghiep)",
  "description": "Mo ta cong viec 3-4 doan bang TIENG VIET CO DAU, markdown: gioi thieu cong ty, mo ta cong viec hang ngay, co hoi phat trien",
  "requirements": ["Yeu cau 1 - chi tiet, ro rang", "Yeu cau 2", ... toi thieu 5 yeu cau],
  "benefits": ["Quyen loi 1 - cu the (VD: Luong thang 13, BHXH day du)", "Quyen loi 2", ... toi thieu 5 quyen loi],
  "salary_range": "VD: 15-25 trieu VND (linh hoat theo nang luc)",
  "positions": "so luong can tuyen (VD: 2)",{dept_hint}
}}

LUU Y QUAN TRONG:
- TAT CA NOI DUNG PHAI BANG TIENG VIET CO DAU DAY DU
- description viet bang markdown co bold (**tu khoa**), bullet points (- item)
- requirements: moi muc la 1 yeu cau cu the, ro rang, co the do luong duoc
- benefits: moi muc la 1 quyen loi thuc te (luong, thuong, bao hiem, dao tao...)
- salary_range: neu ro rang, dung ghi "thoa thuan"
- Neu job_title khong ro rang, tu dong chuyen thanh ten vi tri phu hop"""

	try:
		resp = _http.post(
			"https://api.deepseek.com/chat/completions",
			headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
			json={
				"model": "deepseek-chat",
				"messages": [
					{"role": "system", "content": "Ban la chuyen gia HR. Luon tra JSON thuan, khong markdown."},
					{"role": "user", "content": prompt},
				],
				"temperature": 0.7,
				"max_tokens": 2000,
			},
			timeout=45,
		)
		resp.raise_for_status()
		raw = resp.json()["choices"][0]["message"]["content"].strip()
		if raw.startswith("```"):
			raw = raw.split("\n", 1)[-1]
			if raw.endswith("```"): raw = raw[:-3]
			raw = raw.strip()
			if raw.startswith("json"): raw = raw[4:].strip()
		return _json.loads(raw)
	except Exception as e:
		frappe.throw(f"Loi AI: {str(e)[:200]}")


@frappe.whitelist()
def get_attendance_dashboard(date=None):
	from frappe import db
	from datetime import date as _date, timedelta
	target = date or str(_date.today())
	prev = str(_date.today() - timedelta(days=1))

	emps = db.count("Employee", {"status": "Active"})
	present = db.count("Attendance", {"attendance_date": target, "docstatus": 1, "status": "Present"})
	absent = db.count("Attendance", {"attendance_date": target, "docstatus": 1, "status": "Absent"})
	half = db.count("Attendance", {"attendance_date": target, "docstatus": 1, "status": "Half Day"})
	leave = db.count("Attendance", {"attendance_date": target, "docstatus": 1, "status": "On Leave"})
	late = db.count("Attendance", {"attendance_date": target, "docstatus": 1, "late_entry": 1})
	wfh = db.count("Attendance", {"attendance_date": target, "docstatus": 1, "status": "Work From Home"})

	# Top late employees this month
	import datetime
	now = datetime.datetime.now()
	month_start = now.replace(day=1).strftime("%Y-%m-%d")
	late_records = db.get_all("Attendance",
		filters={"attendance_date": [">=", month_start], "late_entry": 1},
		fields=["employee", "employee_name", "attendance_date", "late_entry"],
		order_by="attendance_date desc", limit=10)

	return {
		"date": target, "total_employees": emps,
		"present": present, "absent": absent, "half_day": half,
		"on_leave": leave, "late": late, "wfh": wfh,
		"unmarked": max(0, emps - present - absent - half - leave - wfh),
		"recent_late": late_records,
	}


@frappe.whitelist()
def checkin(employee, log_type="IN"):
	from datetime import datetime
	doc = frappe.get_doc({
		"doctype": "Employee Checkin",
		"employee": employee,
		"log_type": log_type,
		"time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
	})
	doc.insert(ignore_permissions=True)

	# Auto-create/mark attendance + submit (để dashboard/báo cáo đếm được)
	today = frappe.utils.today()
	existing = frappe.db.exists("Attendance", {"employee": employee, "attendance_date": today})
	if not existing:
		att = frappe.get_doc({
			"doctype": "Attendance",
			"employee": employee,
			"attendance_date": today,
			"status": "Present",
		})
		att.insert(ignore_permissions=True)
		att.submit()
	else:
		att = frappe.get_doc("Attendance", existing)
		if att.status not in ("Present", "Half Day", "On Leave"):
			att.status = "Present"
			att.save(ignore_permissions=True)
		if att.docstatus == 0:
			att.submit()

	return {"ok": True, "log_type": log_type, "time": doc.time, "employee": employee}


@frappe.whitelist()
def mark_attendance(employee, attendance_date, status, late_entry=0):
	if frappe.db.exists("Attendance", {"employee": employee, "attendance_date": attendance_date}):
		att = frappe.get_doc("Attendance", {"employee": employee, "attendance_date": attendance_date})
		att.status = status
		att.late_entry = int(late_entry or 0)
		att.save(ignore_permissions=True)
		if att.docstatus == 0:
			att.submit()
	else:
		att = frappe.get_doc({
			"doctype": "Attendance",
			"employee": employee,
			"attendance_date": attendance_date,
			"status": status,
			"late_entry": int(late_entry or 0),
		})
		att.insert(ignore_permissions=True)
		att.submit()
	return {"ok": True}


@frappe.whitelist()
def get_attendance_records(employee=None, department=None, month=None, page=1, page_length=30):
	from datetime import date as _date
	filters = {"docstatus": 1}
	if employee: filters["employee"] = employee
	if department: filters["department"] = department
	if month:
		import calendar
		y, m = map(int, month.split("-"))
		last = calendar.monthrange(y, m)[1]
		filters["attendance_date"] = ["between", [f"{y}-{m:02d}-01", f"{y}-{m:02d}-{last}"]]
	else:
		filters["attendance_date"] = str(_date.today())

	records = frappe.get_all("Attendance", filters=filters,
		fields=["name", "employee", "employee_name", "attendance_date", "status", "late_entry", "working_hours"],
		order_by="attendance_date desc", limit_page_length=page_length, start=(page-1)*page_length)

	return records


@frappe.whitelist()
def get_attendance(employee=None, month=None):
    """Chấm công (Attendance) — lọc theo employee + tháng."""
    filters = {"docstatus": 1}
    if employee:
        filters["employee"] = employee
    if month:
        filters["attendance_date"] = ["between", [f"{month}-01", f"{month}-31"]]
    return frappe.get_all(
        "Attendance",
        filters=filters,
        fields=[
            "name", "employee", "employee_name",
            "attendance_date", "status", "working_hours",
        ],
        order_by="attendance_date desc",
        limit_page_length=100,
    )


# ════════════════════════════════════════════════════════════════════
#  QUẢN LÝ NHÂN SỰ — Hồ sơ nhân viên (CRUD + dashboard)
# ════════════════════════════════════════════════════════════════════

def _default_company():
	return (
		frappe.defaults.get_user_default("Company")
		or frappe.db.get_value("Company", {}, "name")
	)


@frappe.whitelist()
def get_hr_dashboard():
	"""Tổng quan nhân sự — stats cho dashboard Quản lý nhân sự."""
	from collections import Counter

	from frappe import db

	# Lấy 1 lần, đếm trong Python (tránh SQL-function string bị Frappe v16 chặn)
	emps = db.get_all(
		"Employee", filters={"status": "Active"},
		fields=["department", "gender", "designation"], limit_page_length=0,
	)

	dept_counter = Counter((e["department"] or "Chưa phân").split(" - ")[0] for e in emps)
	gender_counter = Counter(e["gender"] or "Khác" for e in emps)
	desig_counter = Counter(e["designation"] or "Khác" for e in emps)

	# Mới vào tháng này
	month_start = frappe.utils.today()[:8] + "01"
	new_this_month = db.count("Employee", {"status": "Active", "date_of_joining": [">=", month_start]})

	return {
		"total": len(emps),
		"inactive": db.count("Employee", {"status": ["!=", "Active"]}),
		"new_this_month": new_this_month,
		"departments": db.count("Department", {"is_group": 0}),
		"by_department": dict(dept_counter.most_common()),
		"by_gender": dict(gender_counter),
	}


@frappe.whitelist()
def get_hr_home_stats():
	"""Lấy số liệu thống kê tổng hợp cho trang chủ Nhân sự (Home.vue)."""
	from frappe import db

	today = frappe.utils.today()

	# Đi làm hôm nay (chỉ đếm attendance đã submit)
	present = db.count("Attendance", {"attendance_date": today, "docstatus": 1, "status": ["in", ["Present", "Work From Home", "Half Day"]]})

	# Đang nghỉ phép — đếm trực tiếp Leave Application (không phụ thuộc Attendance On Leave)
	on_leave = db.count("Leave Application", {"status": "Approved", "from_date": ["<=", today], "to_date": [">=", today]})

	return {
		"employees": db.count("Employee", {"status": "Active"}),
		"present": present,
		"on_leave": on_leave,
		"openings": db.count("Job Opening", {"status": "Open"}),
	}


_EMP_SORT_FIELDS = {"employee_name", "date_of_joining", "custom_luong_co_ban", "designation", "department", "name", "status"}


@frappe.whitelist()
def get_employees_filtered(search="", department=None, designation=None, status="Active",
		gender=None, employment_type=None, joined_from=None, joined_to=None,
		salary_min=None, salary_max=None, sort_field="employee_name", sort_dir="asc",
		page=1, page_length=30):
	"""Danh sách nhân viên: search + lọc nâng cao + sắp xếp + phân trang (kèm total)."""
	def _clean(v):
		# client gửi null/empty thành chuỗi "null"/"" → coi như không lọc
		return v if v not in (None, "", "null", "undefined") else None

	def _num(v):
		v = _clean(v)
		try:
			return float(v) if v is not None else None
		except (ValueError, TypeError):
			return None

	status, department, designation = _clean(status), _clean(department), _clean(designation)
	gender, employment_type = _clean(gender), _clean(employment_type)
	joined_from, joined_to = _clean(joined_from), _clean(joined_to)
	smin, smax = _num(salary_min), _num(salary_max)

	filters = {}
	if status:
		filters["status"] = status
	if department:
		filters["department"] = department
	if designation:
		filters["designation"] = designation
	if gender:
		filters["gender"] = gender
	if employment_type:
		filters["employment_type"] = employment_type
	if joined_from and joined_to:
		filters["date_of_joining"] = ["between", [joined_from, joined_to]]
	elif joined_from:
		filters["date_of_joining"] = [">=", joined_from]
	elif joined_to:
		filters["date_of_joining"] = ["<=", joined_to]
	if smin is not None and smax is not None:
		filters["custom_luong_co_ban"] = ["between", [smin, smax]]
	elif smin is not None:
		filters["custom_luong_co_ban"] = [">=", smin]
	elif smax is not None:
		filters["custom_luong_co_ban"] = ["<=", smax]

	or_filters = None
	if search:
		or_filters = [
			["employee_name", "like", f"%{search}%"],
			["name", "like", f"%{search}%"],
			["cell_number", "like", f"%{search}%"],
		]

	sf = sort_field if sort_field in _EMP_SORT_FIELDS else "employee_name"
	sd = "desc" if str(sort_dir).lower() == "desc" else "asc"

	page = int(page)
	page_length = int(page_length)
	total = len(frappe.get_all("Employee", filters=filters, or_filters=or_filters, pluck="name", limit_page_length=0))
	rows = frappe.get_all(
		"Employee",
		filters=filters,
		or_filters=or_filters,
		fields=[
			"name", "employee_name", "designation", "department",
			"company", "date_of_joining", "cell_number", "image",
			"gender", "status", "personal_email", "company_email",
			"employment_type", "custom_luong_co_ban",
		],
		order_by=f"{sf} {sd}",
		limit_page_length=page_length,
		start=(page - 1) * page_length,
	)
	return {
		"data": rows, "total": total, "page": page, "page_length": page_length,
		"has_more": page * page_length < total,
		"pages": max(1, (total + page_length - 1) // page_length),
	}


@frappe.whitelist()
def get_designation_department(designation):
	"""Tra phong ban phu hop nhat cho 1 chuc danh."""
	from frappe import db
	# 1. Check custom field default_department
	dept = db.get_value("Designation", designation, "default_department")
	if dept:
		return {"department": dept, "source": "default"}
	# 2. Look at existing employees
	emps = db.get_all("Employee", filters={"designation": designation, "status": "Active"}, fields=["department"], limit=50)
	if emps:
		from collections import Counter
		dept_counts = Counter(e["department"] for e in emps if e.get("department"))
		if dept_counts:
			return {"department": dept_counts.most_common(1)[0][0], "source": "employees"}
	# 3. AI fallback
	import os as _os, json as _json, requests as _http
	api_key = _os.environ.get("DEEPSEEK_API_KEY", "")
	if api_key:
		depts = db.get_all("Department", filters={"is_group": 0}, pluck="name", limit=30)
		try:
			prompt = f'Voi chuc danh "{designation}", phong ban nao trong danh sach sau la phu hop nhat? TRA VE JSON: {{"department": "ten phong ban"}}. Danh sach: {_json.dumps(depts, ensure_ascii=False)}. Chi chon 1 phong ban, khong giai thich.'
			resp = _http.post("https://api.deepseek.com/chat/completions",
				headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
				json={"model": "deepseek-chat", "messages": [{"role": "user", "content": prompt}], "temperature": 0.1, "max_tokens": 200}, timeout=15)
			resp.raise_for_status()
			raw = resp.json()["choices"][0]["message"]["content"].strip()
			if raw.startswith("```"): raw = raw.split("\n",1)[-1]; raw = raw[:-3] if raw.endswith("```") else raw
			raw = raw.strip(); raw = raw[4:].strip() if raw.startswith("json") else raw
			ai_dept = _json.loads(raw).get("department", "")
			if ai_dept and ai_dept in depts:
				return {"department": ai_dept, "source": "ai"}
		except: pass
	return {"department": None, "source": None}


@frappe.whitelist()
def get_designations():
	"""Danh sách chức vụ."""
	return frappe.get_all("Designation", pluck="name", limit=100, order_by="name asc")


@frappe.whitelist()
def fix_notes_field():
	"""One-time: change Job Applicant notes from Small Text to Text."""
	frappe.db.sql("""UPDATE `tabDocField` SET fieldtype='Text' WHERE parent='Job Applicant' AND fieldname='notes'""")
	frappe.db.commit()
	frappe.clear_cache(doctype="Job Applicant")
	return {"ok": True}


@frappe.whitelist()
def create_employee(first_name, last_name="", gender="Male", date_of_birth=None,
		date_of_joining=None, department=None, designation=None,
		cell_number=None, personal_email=None, company=None):
	"""Tạo hồ sơ nhân viên mới."""
	if not first_name or not first_name.strip():
		frappe.throw("Vui lòng nhập họ tên nhân viên")

	emp = frappe.get_doc({
		"doctype": "Employee",
		"first_name": first_name.strip(),
		"last_name": (last_name or "").strip(),
		"gender": gender or "Male",
		"date_of_birth": date_of_birth or "1990-01-01",
		"date_of_joining": date_of_joining or frappe.utils.today(),
		"company": company or _default_company(),
		"department": (department and frappe.db.exists("Department", department) and department) or None,
		"designation": (designation and frappe.db.exists("Designation", designation) and designation) or None,
		"cell_number": cell_number or None,
		"personal_email": personal_email or None,
		"status": "Active",
	})
	emp.insert(ignore_permissions=True)
	return {"ok": True, "name": emp.name, "employee_name": emp.employee_name}


# Field theo dõi lịch sử (đổi → ghi comment) + nhãn tiếng Việt
_TRACKED_FIELDS = {
	"designation": "Chức vụ", "department": "Phòng ban", "status": "Trạng thái",
	"employment_type": "Loại hợp đồng", "ctc": "Lương khoán/năm",
	"contract_end_date": "Ngày hết hạn HĐ", "reports_to": "Quản lý trực tiếp",
	"custom_luong_co_ban": "Lương cơ bản",
}


@frappe.whitelist()
def update_employee(name, **kwargs):
	"""Cập nhật thông tin nhân viên. Chỉ nhận field cho phép + ghi lịch sử thay đổi."""
	allowed = {
		"first_name", "last_name", "gender", "date_of_birth", "date_of_joining",
		"department", "designation", "cell_number", "personal_email",
		"company_email", "current_address", "status", "image",
		"employment_type", "ctc", "contract_end_date", "reports_to",
		"custom_luong_co_ban",
	}
	emp = frappe.get_doc("Employee", name)
	changed, history = [], []

	# If custom_luong_co_ban is modified, update ctc automatically
	if "custom_luong_co_ban" in kwargs and kwargs["custom_luong_co_ban"] is not None:
		try:
			val = float(kwargs["custom_luong_co_ban"])
		except:
			val = 0
		kwargs["ctc"] = val * 12

	for k, v in kwargs.items():
		if k in allowed and v is not None:
			if k in ("department", "designation", "employment_type", "reports_to") and v and not frappe.db.exists(_link_doctype(k), v):
				continue
			old = emp.get(k)
			if str(old or "") == str(v or ""):
				continue
			if k in ("ctc", "custom_luong_co_ban"):
				try: v = float(v) if v else 0
				except: v = 0
			emp.set(k, v)
			changed.append(k)
			if k in _TRACKED_FIELDS:
				history.append((k, old, v))
	emp.save(ignore_permissions=True)

	# Ghi lịch sử thay đổi qua Comment (Employee không có field notes)
	for k, old, new in history:
		emp.add_comment("Info", f"{_TRACKED_FIELDS[k]}: {old or '—'} → {new or '—'}")

	return {"ok": True, "name": emp.name, "changed": changed}


def _link_doctype(field):
	return {
		"department": "Department", "designation": "Designation",
		"employment_type": "Employment Type", "reports_to": "Employee",
	}.get(field, field)


@frappe.whitelist()
def get_employment_types():
	"""Danh sách loại hình hợp đồng/làm việc."""
	return frappe.get_all("Employment Type", pluck="name", limit=50)


@frappe.whitelist()
def get_employee_history(name):
	"""Lịch sử thay đổi hồ sơ nhân viên (từ Comment loại Info)."""
	rows = frappe.get_all(
		"Comment",
		filters={"reference_doctype": "Employee", "reference_name": name, "comment_type": "Info"},
		fields=["content", "creation", "comment_email"],
		order_by="creation desc", limit_page_length=40,
	)
	return [
		{"content": r["content"], "time": str(r["creation"])[:16], "user": r["comment_email"]}
		for r in rows
	]


@frappe.whitelist()
def set_employee_image(name, file_url):
	"""Gán ảnh đại diện cho nhân viên (sau khi upload_file)."""
	frappe.db.set_value("Employee", name, "image", file_url)
	return {"ok": True, "image": file_url}


def _parse_recruitment_source(bio):
	"""Tách marker [NGUỒN_TUYỂN_DỤNG] khỏi bio → trả (source_dict | None, bio_sạch)."""
	if not bio:
		return None, bio
	src, clean_lines = None, []
	for line in bio.split("\n"):
		if line.strip().startswith(RECRUIT_TAG):
			payload = line.strip()[len(RECRUIT_TAG):].strip()
			d = {}
			for part in payload.split(" | "):
				if "=" in part:
					k, v = part.split("=", 1)
					d[k.strip()] = v.strip()
			if d:
				src = d
		else:
			clean_lines.append(line)
	return src, "\n".join(clean_lines).strip()


@frappe.whitelist()
def get_employee_full(name):
	"""Chi tiết nhân viên + nghỉ phép + chấm công + lương + nguồn tuyển dụng (1 lần gọi)."""
	emp = frappe.get_doc("Employee", name).as_dict()

	# Nguồn tuyển dụng (parse từ bio) — liên kết Tuyển dụng ↔ Hồ sơ NV
	recruitment_source, bio_clean = _parse_recruitment_source(emp.get("bio"))
	emp["bio"] = bio_clean

	leaves = frappe.get_all(
		"Leave Application", filters={"employee": name},
		fields=["name", "leave_type", "from_date", "to_date", "status", "total_leave_days"],
		order_by="from_date desc", limit_page_length=10,
	)
	month = frappe.utils.today()[:7]
	attendance = frappe.get_all(
		"Attendance",
		filters={"employee": name, "attendance_date": ["between", [f"{month}-01", f"{month}-31"]]},
		fields=["name", "attendance_date", "status", "working_hours"],
		order_by="attendance_date desc", limit_page_length=31,
	)
	salary = frappe.get_all(
		"Salary Slip", filters={"employee": name},
		fields=["name", "start_date", "end_date", "gross_pay", "total_deduction", "net_pay"],
		order_by="start_date desc", limit_page_length=6,
	)
	history = get_employee_history(name)

	return {
		"employee": emp, "leaves": leaves, "attendance": attendance,
		"salary": salary, "recruitment_source": recruitment_source,
		"history": history,
	}


# ════════════════════════════════════════════════════════════════════
#  HIỆU SUẤT / KPI — đánh giá định kỳ (lưu dạng Comment có cấu trúc trên Employee)
# ════════════════════════════════════════════════════════════════════

KPI_TAG = "[KPI]"


def _kpi_band(score):
	"""Xếp loại theo điểm 0-100."""
	s = float(score or 0)
	if s >= 90:
		return "Xuất sắc"
	if s >= 75:
		return "Tốt"
	if s >= 60:
		return "Đạt"
	return "Cần cải thiện"


@frappe.whitelist()
def create_appraisal(employee, period, score, remarks="", reviewer=None, goals=None, start_date=None, end_date=None):
	"""Tạo đánh giá KPI cho nhân viên. score: 0-100 (tổng). goals: JSON [{"kra":"...","weight":30,"target":"...","result":"...","score":85}]."""
	if not frappe.db.exists("Employee", employee):
		frappe.throw("Không tìm thấy nhân viên: " + str(employee))
	try:
		score = max(0, min(100, float(score)))
	except (TypeError, ValueError):
		frappe.throw("Điểm phải là số 0-100")

	if isinstance(goals, str):
		try:
			goals = _json.loads(goals)
		except Exception:
			goals = [goals] if goals else []
	goals = goals or []

	payload = {
		"period": period or "",
		"start_date": start_date or "",
		"end_date": end_date or "",
		"score": score,
		"band": _kpi_band(score),
		"remarks": remarks or "",
		"reviewer": reviewer or frappe.session.user,
		"goals": goals,
		"date": frappe.utils.today(),
	}
	emp = frappe.get_doc("Employee", employee)
	emp.add_comment("Comment", KPI_TAG + _json.dumps(payload, ensure_ascii=False))
	return {"ok": True, "employee": employee, **payload}


@frappe.whitelist()
def delete_appraisal(comment_name):
	"""Xóa 1 đánh giá KPI (phải là Comment KPI)."""
	ct = frappe.db.get_value("Comment", comment_name, "content") or ""
	if not ct.startswith(KPI_TAG):
		frappe.throw("Không phải comment đánh giá KPI")
	frappe.delete_doc("Comment", comment_name, ignore_permissions=True)
	frappe.db.commit()
	return {"ok": True}


@frappe.whitelist()
def create_appraisal_cycle(period, start_date=None, end_date=None, ignore_existing=True):
	"""Tạo đánh giá KPI theo chu kỳ cho mọi NV Active (chưa có đánh giá trong kỳ nếu ignore_existing)."""
	emps = frappe.get_all("Employee", filters={"status": "Active"}, pluck="name", limit_page_length=0)
	created, skipped = 0, 0
	for emp in emps:
		if frappe.utils.cint(ignore_existing):
			existing = frappe.db.get_value("Comment", {
				"reference_doctype": "Employee", "reference_name": emp,
				"comment_type": "Comment", "content": ["like", f"{KPI_TAG}%{period}%"],
			}, "name")
			if existing:
				skipped += 1
				continue
		frappe.get_doc("Employee", emp).add_comment("Comment", KPI_TAG + _json.dumps({
			"period": period, "start_date": start_date or "", "end_date": end_date or "",
			"score": 0, "band": "Chưa đánh giá", "remarks": "", "reviewer": "",
			"goals": [], "date": frappe.utils.today(),
		}, ensure_ascii=False))
		created += 1
	frappe.db.commit()
	return {"created": created, "skipped": skipped}


def _parse_kpi_comments(rows):
	"""Parse list Comment → list đánh giá KPI."""
	import json

	out = []
	for r in rows:
		content = r.get("content") or ""
		if not content.startswith(KPI_TAG):
			continue
		try:
			d = json.loads(content[len(KPI_TAG):])
		except Exception:
			continue
		d["employee"] = r.get("reference_name")
		d["id"] = r.get("name")
		d["created"] = str(r.get("creation"))[:16]
		out.append(d)
	return out


@frappe.whitelist()
def get_appraisals(employee=None, limit=50):
	"""Danh sách đánh giá KPI — của 1 nhân viên hoặc toàn công ty."""
	filters = {"reference_doctype": "Employee", "comment_type": "Comment", "content": ["like", KPI_TAG + "%"]}
	if employee:
		filters["reference_name"] = employee
	rows = frappe.get_all(
		"Comment", filters=filters,
		fields=["name", "reference_name", "content", "creation"],
		order_by="creation desc", limit_page_length=int(limit),
	)
	apps = _parse_kpi_comments(rows)

	# Gắn tên nhân viên
	emp_names = {e["name"]: e["employee_name"] for e in frappe.get_all(
		"Employee", filters={"name": ["in", list({a["employee"] for a in apps})]},
		fields=["name", "employee_name"]) } if apps else {}
	for a in apps:
		a["employee_name"] = emp_names.get(a["employee"], a["employee"])
	return apps


@frappe.whitelist()
def get_performance_dashboard():
	"""Tổng quan hiệu suất — số đánh giá, điểm TB, phân bố xếp loại, top performers."""
	from collections import Counter

	apps = get_appraisals(limit=500)
	if not apps:
		return {"total": 0, "avg_score": 0, "by_band": {}, "top": [], "this_month": 0}

	scores = [a["score"] for a in apps]
	avg = round(sum(scores) / len(scores), 1)
	band_counter = Counter(a.get("band") or _kpi_band(a["score"]) for a in apps)

	# Top performers theo điểm cao nhất gần đây (mỗi NV lấy bản mới nhất)
	latest = {}
	for a in apps:  # apps đã sort theo creation desc
		latest.setdefault(a["employee"], a)
	top = sorted(latest.values(), key=lambda x: x["score"], reverse=True)[:5]

	month = frappe.utils.today()[:7]
	this_month = sum(1 for a in apps if (a.get("date") or "").startswith(month))

	return {
		"total": len(apps),
		"avg_score": avg,
		"by_band": dict(band_counter),
		"this_month": this_month,
		"top": [{"employee": a["employee"], "employee_name": a["employee_name"], "score": a["score"], "band": a.get("band"), "period": a.get("period")} for a in top],
	}


# ════════════════════════════════════════════════════════════════════
#  CHI PHÍ — Đề nghị thanh toán / hoàn ứng (reuse Expense Claim của HRMS)
# ════════════════════════════════════════════════════════════════════

@frappe.whitelist()
def get_expense_claim_types():
	"""Danh sách loại chi phí."""
	return frappe.get_all("Expense Claim Type", pluck="name", limit=50)


@frappe.whitelist()
def create_expense_claim(employee, expense_type, amount, description="", expense_date=None, company=None):
	"""Tạo đề nghị thanh toán/hoàn ứng (Expense Claim, trạng thái Draft chờ duyệt)."""
	if not frappe.db.exists("Employee", employee):
		frappe.throw("Không tìm thấy nhân viên: " + str(employee))
	try:
		amount = float(amount)
	except (TypeError, ValueError):
		frappe.throw("Số tiền không hợp lệ")
	if amount <= 0:
		frappe.throw("Số tiền phải lớn hơn 0")

	company = company or frappe.db.get_value("Employee", employee, "company") or _default_company()
	currency = frappe.db.get_value("Company", company, "default_currency") or "VND"

	# Tài khoản chi phí mặc định cho dòng (Expense Claim Type chưa cấu hình account theo company)
	default_account = (
		frappe.db.get_value("Expense Claim Account", {"parent": expense_type, "company": company}, "default_account")
		or frappe.db.get_value("Account", {"company": company, "root_type": "Expense", "is_group": 0}, "name")
	)

	doc = frappe.get_doc({
		"doctype": "Expense Claim",
		"employee": employee,
		"company": company,
		"currency": currency,
		"exchange_rate": 1,
		"posting_date": expense_date or frappe.utils.today(),
		"approval_status": "Draft",
		"expenses": [{
			"expense_date": expense_date or frappe.utils.today(),
			"expense_type": expense_type,
			"description": description or "",
		"no_of_positions": frappe.form_dict.get("positions") or 1,
			"amount": amount,
			"sanctioned_amount": amount,
			"default_account": default_account,
		}],
	})
	doc.insert(ignore_permissions=True)
	return {"ok": True, "name": doc.name, "amount": amount}


def _claim_state(d):
	"""Trạng thái rút gọn tiếng Việt từ approval_status + docstatus."""
	if d.get("docstatus") == 2:
		return "Đã hủy"
	st = d.get("approval_status")
	return {"Draft": "Chờ duyệt", "Approved": "Đã duyệt", "Rejected": "Từ chối"}.get(st, st or "Chờ duyệt")


@frappe.whitelist()
def get_expense_claims(employee=None, status=None, limit=100):
	"""Danh sách đề nghị chi phí."""
	filters = {}
	if employee:
		filters["employee"] = employee
	if status:
		filters["approval_status"] = status
	rows = frappe.get_all(
		"Expense Claim", filters=filters,
		fields=[
			"name", "employee", "employee_name", "posting_date",
			"total_claimed_amount", "total_sanctioned_amount",
			"approval_status", "docstatus", "company",
		],
		order_by="posting_date desc, creation desc", limit_page_length=int(limit),
	)
	for r in rows:
		r["state"] = _claim_state(r)
	return rows


@frappe.whitelist()
def get_expense_claim_detail(name):
	"""Chi tiết 1 đề nghị chi phí + các dòng chi phí."""
	doc = frappe.get_doc("Expense Claim", name)
	d = doc.as_dict()
	d["state"] = _claim_state(d)
	return d


@frappe.whitelist()
def approve_expense_claim(name, approve=1, remark=""):
	"""Duyệt hoặc từ chối đề nghị chi phí (đổi approval_status)."""
	approve = str(approve) in ("1", "true", "True")
	doc = frappe.get_doc("Expense Claim", name)
	doc.approval_status = "Approved" if approve else "Rejected"
	if approve:
		# Duyệt full số tiền đề nghị
		for row in doc.expenses:
			row.sanctioned_amount = row.amount
	doc.save(ignore_permissions=True)
	frappe.get_doc("Expense Claim", name).add_comment(
		"Comment", ("✅ Duyệt" if approve else "❌ Từ chối") + (f": {remark}" if remark else "")
	)
	return {"ok": True, "name": name, "approval_status": doc.approval_status}


@frappe.whitelist()
def get_expense_dashboard():
	"""Tổng quan chi phí — số đề nghị theo trạng thái + tổng tiền."""
	from frappe import db

	rows = db.get_all(
		"Expense Claim",
		fields=["approval_status", "docstatus", "total_claimed_amount", "total_sanctioned_amount", "posting_date"],
		limit_page_length=0,
	)
	pending = sum(1 for r in rows if r["approval_status"] == "Draft" and r["docstatus"] != 2)
	approved = sum(1 for r in rows if r["approval_status"] == "Approved")
	rejected = sum(1 for r in rows if r["approval_status"] == "Rejected")
	total_pending_amount = sum((r["total_claimed_amount"] or 0) for r in rows if r["approval_status"] == "Draft")
	total_approved_amount = sum((r["total_sanctioned_amount"] or 0) for r in rows if r["approval_status"] == "Approved")

	month = frappe.utils.today()[:7]
	this_month_amount = sum(
		(r["total_sanctioned_amount"] or r["total_claimed_amount"] or 0)
		for r in rows if (str(r["posting_date"]) or "").startswith(month)
	)

	return {
		"total": len(rows),
		"pending": pending,
		"approved": approved,
		"rejected": rejected,
		"total_pending_amount": total_pending_amount,
		"total_approved_amount": total_approved_amount,
		"this_month_amount": this_month_amount,
	}


# ════════════════════════════════════════════════════════════════════
#  TẠM ỨNG (Employee Advance) — reuse HRMS doctype, submit tự cập nhật
# ════════════════════════════════════════════════════════════════════

@frappe.whitelist()
def create_advance(employee, amount, purpose, advance_account=None, mode_of_payment=None, date=None):
	"""Tạo đề nghị tạm ứng (Draft). Có thể submit luôn để kế toán chi."""
	from frappe import db
	if not db.exists("Employee", employee):
		frappe.throw("Không tìm thấy nhân viên")
	amount = float(amount or 0)
	if amount <= 0:
		frappe.throw("Số tiền phải > 0")
	company = db.get_value("Employee", employee, "company") or _default_company()
	doc = frappe.new_doc("Employee Advance")
	doc.employee = employee
	doc.purpose = purpose or "Tạm ứng"
	doc.advance_amount = amount
	doc.company = company
	doc.posting_date = date or frappe.utils.today()
	# auto-pick cash advance account (find Cash type)
	if not advance_account:
		acct = db.get_value("Account", {"company": company, "account_type": "Cash", "is_group": 0}, "name")
		advance_account = acct
	if advance_account:
		doc.advance_account = advance_account
	doc.insert(ignore_permissions=True)
	doc.submit()
	frappe.db.commit()
	return {"ok": True, "name": doc.name, "status": doc.status, "amount": doc.advance_amount}


@frappe.whitelist()
def get_advances(employee=None, status=None, limit=100):
	"""Danh sách tạm ứng."""
	filters = {}
	if employee:
		filters["employee"] = employee
	if status:
		filters["status"] = status
	return frappe.get_all("Employee Advance", filters=filters,
		fields=["name", "employee", "employee_name", "posting_date", "advance_amount",
			"paid_amount", "claimed_amount", "purpose", "status"],
		order_by="posting_date desc", limit_page_length=int(limit))


@frappe.whitelist()
def get_advance_dashboard():
	"""Tổng quan tạm ứng — tổng tiền tạm ứng, chưa hoàn, đã hoàn."""
	rows = frappe.get_all("Employee Advance", fields=["advance_amount", "status", "paid_amount", "claimed_amount"], limit_page_length=0)
	total, pending, cleared, paid = 0, 0, 0, 0
	for r in rows:
		total += r["advance_amount"] or 0
		if r["status"] == "Draft" or r["status"] == "Paid":
			pending += (r["advance_amount"] or 0) - (r["claimed_amount"] or 0)
		elif r["status"] == "Claimed":
			cleared += r["advance_amount"] or 0
		paid += r["paid_amount"] or 0
	return {
		"count": len(rows), "total": round(total), "pending": round(max(0, pending)),
		"cleared": round(cleared), "paid": round(paid),
	}


@frappe.whitelist()
def settle_advance(name):
	"""Đánh dấu tạm ứng đã quyết toán (status='Claimed')."""
	doc = frappe.get_doc("Employee Advance", name)
	doc.status = "Claimed"
	doc.save()
	return {"ok": True, "name": name, "status": doc.status}


_BADGE_HTML = """<!doctype html><html><head><meta charset="utf-8"><title>Thẻ NV - __EMP_NAME__</title>
<style>
body{font-family:sans-serif;margin:0;padding:20px;display:flex;flex-wrap:wrap;gap:16px;justify-content:center}
.card{width:320px;border-radius:16px;overflow:hidden;box-shadow:0 4px 16px rgba(0,0,0,.12);background:#fff;break-inside:avoid;page-break-inside:avoid}
.card-header{background:linear-gradient(135deg,#4f46e5,#7c3aed);color:#fff;padding:20px;text-align:center}
.card-avatar{width:72px;height:72px;border-radius:50%;border:3px solid #fff;object-fit:cover;margin-bottom:8px;background:#e0e7ff;display:flex;align-items:center;justify-content:center;font-size:28px;font-weight:bold;color:#4f46e5}
.avatar-placeholder{background:#e0e7ff;border-radius:50%}
.card-body{padding:16px;font-size:13px;line-height:1.7}
.card-row{display:flex;justify-content:space-between;padding:4px 0;border-bottom:1px solid #f3f4f6}
.card-row .label{color:#6b7280}.card-row .value{font-weight:600;color:#1f2937}
.qr-box{text-align:center;padding:10px 0;margin-top:8px;border-top:1px solid #e5e7eb}
.qr-box .qr{width:80px;height:80px;background:#f3f4f6;display:inline-flex;align-items:center;justify-content:center;font-size:10px;color:#9ca3af;border-radius:8px}
.toolbar{text-align:center;margin:20px;break-before:page}
button{font-family:sans-serif;padding:10px 24px;border:none;background:#4f46e5;color:#fff;border-radius:8px;cursor:pointer;font-size:14px}
@media print{.toolbar{display:none};body{padding:0;gap:0}.card{box-shadow:none;break-inside:avoid}}
</style></head><body>
<div id="cards"></div>
<div class="toolbar"><button onclick="window.print()">🖨 In thẻ (__COUNT__ NV)</button></div>
</body></html>"""

_CARD_HTML = """<div class="card">
<div class="card-header">__AVATAR__<h2 style="margin:8px 0 2px;font-size:16px">__EMP_NAME__</h2><div style="font-size:12px;opacity:.85">__DESIGNATION__</div></div>
<div class="card-body">
<div class="card-row"><span class="label">Mã NV</span><span class="value">__CODE__</span></div>
<div class="card-row"><span class="label">Phòng ban</span><span class="value">__DEPT__</span></div>
<div class="card-row"><span class="label">Ngày vào làm</span><span class="value">__JOIN__</span></div>
<div class="card-row"><span class="label">SĐT</span><span class="value">__PHONE__</span></div>
<div class="qr-box"><div class="qr">QR: __CODE__</div></div>
</div></div>"""


@frappe.whitelist()
def get_employee_badge(name):
	"""HTML thẻ nhân viên (1 người) để in."""
	emp = frappe.get_doc("Employee", name)
	avatar = ""
	if emp.image:
		avatar = f'<img class="card-avatar" src="{emp.image}" />'
	else:
		initials = "".join((emp.employee_name or "?").split()[:2])[:2].upper()
		avatar = f'<div class="card-avatar avatar-placeholder">{initials}</div>'
	html = _BADGE_HTML
	html = html.replace("__EMP_NAME__", emp.employee_name or "")
	html = html.replace("__COUNT__", "1")
	cards = (_CARD_HTML
		.replace("__AVATAR__", avatar)
		.replace("__EMP_NAME__", emp.employee_name or "")
		.replace("__DESIGNATION__", emp.designation or "—")
		.replace("__CODE__", emp.name)
		.replace("__DEPT__", (emp.department or "—").split(" - ")[0])
		.replace("__JOIN__", str(emp.date_of_joining or "—"))
		.replace("__PHONE__", emp.cell_number or "—"))
	html = html.replace('<div id="cards"></div>', f'<div id="cards">{cards}</div>')
	return {"html": html, "name": emp.name, "employee_name": emp.employee_name}


@frappe.whitelist()
def get_employee_badges_batch(names=None):
	"""HTML thẻ NV hàng loạt (names: JSON list, hoặc None = tất cả Active)."""
	sel = _json.loads(names) if isinstance(names, str) else names
	if sel:
		emps = frappe.get_all("Employee", filters={"name": ["in", sel]}, fields=["name", "employee_name", "designation", "department", "date_of_joining", "cell_number", "image"], order_by="employee_name asc", limit_page_length=0)
	else:
		emps = frappe.get_all("Employee", filters={"status": "Active"}, fields=["name", "employee_name", "designation", "department", "date_of_joining", "cell_number", "image"], order_by="employee_name asc", limit_page_length=0)
	cards = ""
	for e in emps:
		avatar = ""
		if e.get("image"):
			avatar = f'<img class="card-avatar" src="{e["image"]}" />'
		else:
			initials = "".join((e["employee_name"] or "?").split()[:2])[:2].upper()
			avatar = f'<div class="card-avatar avatar-placeholder">{initials}</div>'
		cards += (_CARD_HTML
			.replace("__AVATAR__", avatar)
			.replace("__EMP_NAME__", e["employee_name"] or "")
			.replace("__DESIGNATION__", e.get("designation") or "—")
			.replace("__CODE__", e["name"])
			.replace("__DEPT__", (e.get("department") or "—").split(" - ")[0])
			.replace("__JOIN__", str(e.get("date_of_joining") or "—"))
			.replace("__PHONE__", e.get("cell_number") or "—"))
	html = _BADGE_HTML
	html = html.replace("__EMP_NAME__", f"{len(emps)} nhân viên")
	html = html.replace("__COUNT__", str(len(emps)))
	html = html.replace('<div id="cards"></div>', f'<div id="cards">{cards}</div>')
	return {"html": html, "count": len(emps)}


@frappe.whitelist()


def upload_employee_avatar(employee):
	"""Nhận file upload ảnh và gán cho Employee. Trả url."""
	if not frappe.request.files:
		frappe.throw("Chưa chọn file")
	file_obj = list(frappe.request.files.values())[0]
	from frappe.handler import upload_file as _upload
	frappe.form_dict = frappe._dict({
		"file": file_obj, "is_private": 0, "doctype": "Employee", "docname": employee, "fieldname": "image",
	})
	ret = _upload()
	url = ret.get("file_url") if isinstance(ret, dict) else (ret.message.get("file_url") if hasattr(ret, "message") else None)
	if url:
		frappe.db.set_value("Employee", employee, "image", url)
		frappe.db.commit()
	return {"file_url": url, "employee": employee}


# ════════════════════════════════════════════════════════════════════
#  TIỆN ÍCH — cảnh báo (sinh nhật / hết hạn HĐ / thâm niên) + export CSV
# ════════════════════════════════════════════════════════════════════

@frappe.whitelist()
def get_hr_alerts():
	"""Cảnh báo nhân sự: sinh nhật 7 ngày tới, HĐ hết hạn ±30 ngày, kỷ niệm thâm niên tháng này."""
	today = frappe.utils.getdate()
	emps = frappe.get_all(
		"Employee", filters={"status": "Active"},
		fields=["name", "employee_name", "date_of_birth", "date_of_joining", "contract_end_date", "designation", "department"],
		limit_page_length=0,
	)

	def _next_occurrence(d):
		"""Lần kế tiếp của ngày-tháng d so với hôm nay (số ngày tới)."""
		try:
			nxt = d.replace(year=today.year)
		except ValueError:  # 29/2
			nxt = d.replace(year=today.year, day=28)
		if nxt < today:
			try:
				nxt = d.replace(year=today.year + 1)
			except ValueError:
				nxt = d.replace(year=today.year + 1, day=28)
		return (nxt - today).days

	birthdays, contracts, anniversaries = [], [], []
	for e in emps:
		if e.get("date_of_birth"):
			days = _next_occurrence(frappe.utils.getdate(e["date_of_birth"]))
			if 0 <= days <= 7:
				birthdays.append({"name": e["name"], "employee_name": e["employee_name"], "days": days, "date": str(e["date_of_birth"])[5:]})

		if e.get("contract_end_date"):
			d = frappe.utils.getdate(e["contract_end_date"])
			days = (d - today).days
			if -30 <= days <= 30:
				contracts.append({"name": e["name"], "employee_name": e["employee_name"], "days": days, "date": str(e["contract_end_date"])})

		if e.get("date_of_joining"):
			d = frappe.utils.getdate(e["date_of_joining"])
			if d.month == today.month and today.year > d.year:
				anniversaries.append({"name": e["name"], "employee_name": e["employee_name"], "years": today.year - d.year, "date": str(e["date_of_joining"])})

	birthdays.sort(key=lambda x: x["days"])
	contracts.sort(key=lambda x: x["days"])
	anniversaries.sort(key=lambda x: -x["years"])
	return {
		"birthdays": birthdays,
		"contracts_expiring": contracts,
		"anniversaries": anniversaries,
		"count": len(birthdays) + len(contracts) + len(anniversaries),
	}


@frappe.whitelist()
def export_employees_csv(department=None, status="Active", names=None):
	"""Xuất danh sách nhân viên ra CSV (UTF-8 BOM cho Excel). names = chỉ xuất NV đã chọn."""
	import csv
	import io

	filters = {}
	sel = (_json.loads(names) if isinstance(names, str) else names) if names else None
	if sel:
		filters["name"] = ["in", sel]
	else:
		if status:
			filters["status"] = status
		if department:
			filters["department"] = department
	rows = frappe.get_all(
		"Employee", filters=filters,
		fields=[
			"name", "employee_name", "gender", "date_of_birth", "date_of_joining",
			"designation", "department", "employment_type", "contract_end_date",
			"cell_number", "personal_email", "status",
		],
		order_by="employee_name asc", limit_page_length=0,
	)
	headers = [
		("name", "Mã NV"), ("employee_name", "Họ tên"), ("gender", "Giới tính"),
		("date_of_birth", "Ngày sinh"), ("date_of_joining", "Ngày vào làm"),
		("designation", "Chức vụ"), ("department", "Phòng ban"),
		("employment_type", "Loại HĐ"), ("contract_end_date", "Hết hạn HĐ"),
		("cell_number", "SĐT"), ("personal_email", "Email"), ("status", "Trạng thái"),
	]
	buf = io.StringIO()
	w = csv.writer(buf)
	w.writerow([h[1] for h in headers])
	for r in rows:
		w.writerow([r.get(h[0]) or "" for h in headers])

	return {"filename": f"nhan_vien_{frappe.utils.today()}.csv", "content": buf.getvalue(), "count": len(rows)}


_BULK_FIELDS = {"status": "Trạng thái", "department": "Phòng ban", "designation": "Chức vụ"}


@frappe.whitelist()
def bulk_update_employees(names, field, value):
	"""Cập nhật hàng loạt 1 trường (status/department/designation) cho nhiều NV + ghi lịch sử."""
	if field not in _BULK_FIELDS:
		frappe.throw("Trường không hợp lệ")
	sel = _json.loads(names) if isinstance(names, str) else (names or [])
	updated, errors = 0, []
	for n in sel:
		try:
			old = frappe.db.get_value("Employee", n, field)
			if str(old or "") == str(value or ""):
				continue
			frappe.db.set_value("Employee", n, field, value or None)
			frappe.get_doc("Employee", n).add_comment("Info", f"{_BULK_FIELDS[field]}: {old or '—'} → {value or '—'}")
			updated += 1
		except Exception as e:
			errors.append({"name": n, "error": str(e)[:120]})
	frappe.db.commit()
	return {"updated": updated, "errors": errors}


@frappe.whitelist()
def bulk_delete_employees(names):
	"""Xóa nhiều NV (an toàn — NV có liên kết submit sẽ bị bỏ qua + báo lý do)."""
	sel = _json.loads(names) if isinstance(names, str) else (names or [])
	deleted, skipped = 0, []
	for n in sel:
		nm = frappe.db.get_value("Employee", n, "employee_name") or n
		try:
			frappe.delete_doc("Employee", n, ignore_permissions=True)
			deleted += 1
		except Exception as e:
			skipped.append({"name": nm, "reason": str(e)[:120]})
	frappe.db.commit()
	return {"deleted": deleted, "skipped": skipped}


# ════════════════════════════════════════════════════════════════════
#  THÂM NIÊN — số năm công tác, phân nhóm, kỷ niệm, khen thưởng
# ════════════════════════════════════════════════════════════════════

@frappe.whitelist()
def get_seniority():
	"""Thống kê thâm niên: số năm công tác từng NV, phân nhóm, kỷ niệm tháng này."""
	today = frappe.utils.getdate()
	emps = frappe.get_all(
		"Employee", filters={"status": "Active"},
		fields=["name", "employee_name", "date_of_joining", "designation", "department", "image"],
		limit_page_length=0,
	)
	bands = {"< 1 năm": 0, "1-3 năm": 0, "3-5 năm": 0, "5-10 năm": 0, "10+ năm": 0}
	ranking, anniversaries = [], []
	for e in emps:
		doj = e.get("date_of_joining")
		if not doj:
			continue
		d = frappe.utils.getdate(doj)
		years = round((today - d).days / 365.25, 1)
		if years < 1:
			bands["< 1 năm"] += 1
		elif years < 3:
			bands["1-3 năm"] += 1
		elif years < 5:
			bands["3-5 năm"] += 1
		elif years < 10:
			bands["5-10 năm"] += 1
		else:
			bands["10+ năm"] += 1
		ranking.append({
			"name": e["name"], "employee_name": e["employee_name"],
			"designation": e.get("designation"), "department": e.get("department"),
			"image": e.get("image"), "years": years, "date_of_joining": str(doj),
		})
		# Kỷ niệm tháng này (tròn năm)
		if d.month == today.month and today.year > d.year:
			anniversaries.append({
				"name": e["name"], "employee_name": e["employee_name"],
				"years": today.year - d.year, "day": d.day,
			})

	ranking.sort(key=lambda x: x["years"], reverse=True)
	anniversaries.sort(key=lambda x: x["day"])
	return {
		"total": len(ranking),
		"avg_years": round(sum(r["years"] for r in ranking) / len(ranking), 1) if ranking else 0,
		"bands": bands,
		"ranking": ranking,
		"anniversaries": anniversaries,
	}


@frappe.whitelist()
def add_award(employee, title, note=""):
	"""Ghi nhận khen thưởng cho nhân viên (lưu qua Comment)."""
	if not frappe.db.exists("Employee", employee):
		frappe.throw("Không tìm thấy nhân viên")
	frappe.get_doc("Employee", employee).add_comment(
		"Comment", f"🏆 [KHEN THƯỞNG] {title}" + (f" — {note}" if note else "")
	)
	return {"ok": True}


# ════════════════════════════════════════════════════════════════════
#  THUẾ & PHÚC LỢI — bảo hiểm bắt buộc + thuế TNCN (ước tính theo lương)
# ════════════════════════════════════════════════════════════════════

# Tỉ lệ bảo hiểm bắt buộc VN — phần người lao động đóng
_INS_EMP = {"BHXH": 0.08, "BHYT": 0.015, "BHTN": 0.01}      # = 10.5%
_INS_COMPANY = {"BHXH": 0.175, "BHYT": 0.03, "BHTN": 0.01}  # = 21.5%
_PERSONAL_DEDUCTION = 11_000_000  # giảm trừ bản thân/tháng


def _est_pit(taxable_monthly):
	"""Thuế TNCN lũy tiến từng phần (biểu thuế VN), thu nhập tính thuế/tháng."""
	if taxable_monthly <= 0:
		return 0
	brackets = [
		(5_000_000, 0.05), (10_000_000, 0.10), (18_000_000, 0.15),
		(32_000_000, 0.20), (52_000_000, 0.25), (80_000_000, 0.30),
		(float("inf"), 0.35),
	]
	tax, lower = 0, 0
	for upper, rate in brackets:
		if taxable_monthly > lower:
			tax += (min(taxable_monthly, upper) - lower) * rate
			lower = upper
		else:
			break
	return round(tax)


@frappe.whitelist()
def get_salary_components():
	"""Danh sách thành phần lương (Earning/Deduction)."""
	return frappe.get_all("Salary Component", fields=["name", "type"], order_by="type, name", limit_page_length=0)


@frappe.whitelist()
def get_benefits_dashboard():
	"""Tổng quan thuế & phúc lợi — tính chính xác qua compute_payroll (phụ cấp, lương đóng BH có trần, NPT)."""
	cfg = _load_vn_config()
	emps = frappe.get_all(
		"Employee", filters={"status": "Active"},
		fields=["name", "employee_name", "designation", "department"],
		limit_page_length=0,
	)
	rows = []
	tot = {"salary": 0, "ins_emp": 0, "ins_company": 0, "tax": 0, "net": 0}
	for e in emps:
		c = compute_payroll(e["name"], cfg)
		rows.append({
			"name": e["name"], "employee_name": e["employee_name"],
			"designation": e.get("designation"),
			"monthly": c["gross"], "bh_base": c["bh_base"],
			"bhxh": c["bhxh"], "bhyt": c["bhyt"], "bhtn": c["bhtn"],
			"ins_emp": c["bh_nld"], "ins_company": c["bh_dn"], "tax": c["pit"], "net": c["net"],
			"npt": c["npt_count"], "has_salary": c["gross"] > 0,
		})
		tot["salary"] += c["gross"]
		tot["ins_emp"] += c["bh_nld"]
		tot["ins_company"] += c["bh_dn"]
		tot["tax"] += c["pit"]
		tot["net"] += c["net"]

	rows.sort(key=lambda x: x["monthly"], reverse=True)
	return {
		"employees": len(rows),
		"with_salary": sum(1 for r in rows if r["has_salary"]),
		"totals": tot,
		"rates": {"emp": cfg["ty_le_bh_nld"], "company": cfg["ty_le_bh_dn"], "personal_deduction": cfg["giam_tru_ban_than"]},
		"rows": rows,
	}


# ════════════════════════════════════════════════════════════════════
#  BẢNG LƯƠNG — chạy lương tháng (Salary Slip), tái dùng công thức BH + thuế TNCN
# ════════════════════════════════════════════════════════════════════

_SALARY_STRUCTURE = "GPC Co ban"  # cấu trúc lương: 1 earning Basic = base (lương khoán/tháng)

# Thành phần khấu trừ (Deduction) — nhãn hiển thị + viết tắt; tỉ lệ khớp module Thuế & Phúc lợi
_DEDUCTION_COMPONENTS = [
	("BHXH (8%)", "BHXH", _INS_EMP["BHXH"]),
	("BHYT (1.5%)", "BHYT", _INS_EMP["BHYT"]),
	("BHTN (1%)", "BHTN", _INS_EMP["BHTN"]),
	("Thuế TNCN", "TNCN", None),
]


def _ensure_salary_components():
	"""Tạo các Salary Component khấu trừ nếu chưa có (idempotent). depends_on_payment_days=0 → không prorate."""
	for label, abbr, _rate in _DEDUCTION_COMPONENTS:
		if not frappe.db.exists("Salary Component", label):
			doc = frappe.new_doc("Salary Component")
			doc.salary_component = label
			doc.salary_component_abbr = abbr
			doc.type = "Deduction"
			doc.depends_on_payment_days = 0
			doc.do_not_include_in_total = 0
			doc.insert(ignore_permissions=True)


def _ensure_structure(company):
	"""Đảm bảo Salary Structure mặc định tồn tại + active (earning Basic = base)."""
	if frappe.db.exists("Salary Structure", _SALARY_STRUCTURE):
		return _SALARY_STRUCTURE
	doc = frappe.new_doc("Salary Structure")
	doc.name = _SALARY_STRUCTURE
	doc.company = company
	doc.is_active = "Yes"
	doc.payroll_frequency = "Monthly"
	doc.append("earnings", {"salary_component": "Basic", "amount_based_on_formula": 1, "formula": "base"})
	doc.insert(ignore_permissions=True)
	doc.submit()
	return _SALARY_STRUCTURE


def _ensure_assignment(employee, base, from_date, company):
	"""Tạo + submit Salary Structure Assignment nếu NV chưa có assignment active. Nếu có rồi nhưng base khác → cập nhật. Trả tên assignment."""
	existing = frappe.db.exists("Salary Structure Assignment", {
		"employee": employee, "salary_structure": _SALARY_STRUCTURE, "docstatus": 1,
	})
	if existing:
		cur = frappe.db.get_value("Salary Structure Assignment", existing, "base")
		if abs(float(cur or 0) - float(base)) > 1:
			doc = frappe.get_doc("Salary Structure Assignment", existing)
			doc.cancel()
			frappe.delete_doc("Salary Structure Assignment", existing, ignore_permissions=True)
			# fall through → tạo mới
		else:
			return existing
	doc = frappe.new_doc("Salary Structure Assignment")
	doc.employee = employee
	doc.salary_structure = _SALARY_STRUCTURE
	doc.company = company
	doc.from_date = from_date
	doc.base = base
	doc.insert(ignore_permissions=True)
	doc.submit()
	return doc.name


def _ensure_holiday_list(company, year):
	"""Trả về Holiday List phủ kỳ lương + đảm bảo có Holiday List Assignment cấp Công ty.
	HRMS 16 tra holiday qua doctype Holiday List Assignment (KHÔNG dùng employee.holiday_list /
	default công ty) → tạo HLA cấp Công ty để mọi NV chưa có HLA riêng đều kế thừa."""
	hl = frappe.db.get_value("Company", company, "default_holiday_list")
	if not (hl and frappe.db.exists("Holiday List", hl)):
		hl = f"Lịch nghỉ {year}"
		if not frappe.db.exists("Holiday List", hl):
			doc = frappe.new_doc("Holiday List")
			doc.holiday_list_name = hl
			doc.from_date = f"{year}-01-01"
			doc.to_date = f"{year}-12-31"
			doc.weekly_off = "Sunday"
			try:
				doc.get_weekly_off_dates()   # điền các ngày Chủ nhật
			except Exception:
				pass
			doc.insert(ignore_permissions=True)
		frappe.db.set_value("Company", company, "default_holiday_list", hl)
	if not frappe.db.exists("Holiday List Assignment", {"applicable_for": "Company", "assigned_to": company, "docstatus": 1}):
		hla = frappe.new_doc("Holiday List Assignment")
		hla.applicable_for = "Company"
		hla.assigned_to = company
		hla.holiday_list = hl
		hla.from_date = f"{year}-01-01"
		hla.insert(ignore_permissions=True)
		hla.submit()
	return hl


@frappe.whitelist()
def run_payroll(month=None, year=None, working_days=None):
	"""Chạy bảng lương tháng: sinh Salary Slip (Draft) cho NV Active có lương khoán.
	Khấu trừ BHXH/BHYT/BHTN (10.5%) + thuế TNCN lũy tiến — khớp module Thuế & Phúc lợi.
	Bỏ qua NV chưa có lương, vào làm sau kỳ, hoặc đã có phiếu lương kỳ này (idempotent).

	working_days (optional): JSON dict {employee_name: days_actual}. Nếu có → prorate
	lương/phụ cấp/thuế theo ngày công thực / ngày công chuẩn. BHXH/BHYT/BHTN KHÔNG prorate
	(luật VN: đóng trên mức lương HĐ, không theo ngày công)."""
	from hrms.payroll.doctype.salary_structure.salary_structure import make_salary_slip
	import calendar as _cal
	from datetime import date as _date, timedelta

	today = frappe.utils.getdate()
	year = int(year) if year else today.year
	month = int(month) if month else today.month
	last_day = _cal.monthrange(year, month)[1]
	start = _date(year, month, 1)
	end = _date(year, month, last_day)
	company = _default_company()
	cfg = _load_vn_config()

	# Parse working_days map
	wd_map = (working_days and _json.loads(working_days)) if isinstance(working_days, str) else (working_days or {})
	# Tổng ngày công chuẩn = số ngày trong tháng trừ CN + lễ
	total_wd = 0
	hl_name = _ensure_holiday_list(company, year)
	holidays = {frappe.utils.getdate(h.holiday_date) for h in frappe.get_all("Holiday", filters={"parent": hl_name}, fields=["holiday_date"], limit_page_length=0)}
	d = start
	while d <= end:
		if d.weekday() != 6 and d not in holidays:  # không phải Chủ nhật và không phải lễ
			total_wd += 1
		d += timedelta(days=1)

	_ensure_salary_components()
	_ensure_structure(company)
	_ensure_earning_component("Lương cơ bản")

	if _is_payroll_locked(year, month):
		return {"period": f"{month:02d}/{year}", "locked": True, "created": [], "skipped": [], "errors": [{"lock": "Kỳ lương này đã được khóa — không thể chạy lại"}]}

	emps = frappe.get_all(
		"Employee", filters={"status": "Active"},
		fields=["name", "employee_name", "date_of_joining"], limit_page_length=0,
	)

	created, skipped, errors = [], [], []
	totals = {"gross": 0, "ins": 0, "tax": 0, "net": 0, "count": 0, "total_wd": total_wd}

	for e in emps:
		label = e.get("employee_name")
		emp = frappe.get_doc("Employee", e["name"])
		calc = compute_payroll(emp, cfg)
		if calc["gross"] <= 0:
			skipped.append({"employee": e["name"], "name": label, "reason": "Chưa có lương"})
			continue
		doj = frappe.utils.getdate(e.get("date_of_joining")) if e.get("date_of_joining") else start
		if doj > end:
			skipped.append({"employee": e["name"], "name": label, "reason": "Vào làm sau kỳ lương"})
			continue
		if frappe.db.exists("Salary Slip", {"employee": e["name"], "start_date": start, "end_date": end}):
			skipped.append({"employee": e["name"], "name": label, "reason": "Đã có phiếu lương"})
			continue
		try:
			if not emp.get("holiday_list"):
				frappe.db.set_value("Employee", e["name"], "holiday_list", hl_name)

			luong_cb_full = calc["earnings"][0]["so_tien"]    # lương HĐ (gốc, chưa prorate)
			_ensure_assignment(e["name"], luong_cb_full, min(doj, start), company)

			# Ngày công thực → prorate nếu có khai
			actual_days = int(wd_map.get(e["name"], 0))
			if actual_days > 0 and total_wd > 0:
				factor = actual_days / total_wd
				# Prorate lương + phụ cấp
				for a in calc["earnings"]:
					a["so_tien"] = round(a["so_tien"] * factor)
				calc["gross"] = round(calc["gross"] * factor)
				calc["taxable_earn"] = round(calc["taxable_earn"] * factor)
				calc["bh_base"] = round(calc["bh_base"] * factor)
				# Recalc PIT (BH giữ full — luật VN)
				calc["assessable"] = max(0, calc["taxable_earn"] - calc["giam_tru"])
				calc["pit"] = _pit(calc["assessable"], cfg["pit_brackets"])
				calc["net"] = max(0, calc["gross"] - calc["bh_nld"] - calc["pit"])
				calc["_prorated"] = True
				calc["_actual_days"] = actual_days
				calc["_total_days"] = total_wd
			else:
				factor = 1.0
				calc["_prorated"] = False
				calc["_actual_days"] = total_wd
				calc["_total_days"] = total_wd

			slip = make_salary_slip(_SALARY_STRUCTURE, employee=e["name"])
			slip.start_date = start
			slip.end_date = end
			slip.posting_date = end
			slip.default_series = f"Sal Slip/{slip.employee}/.#####"
			slip.insert(ignore_permissions=True)
			frappe.db.set_value("Salary Slip", slip.name, "payment_days", calc["_actual_days"])
			frappe.db.set_value("Salary Slip", slip.name, "total_working_days", total_wd)
			for a in calc["earnings"]:
				if (a["so_tien"] or 0) > 0:
					_ensure_earning_component(a["ten"])
					frappe.get_doc({"doctype": "Salary Detail", "parent": slip.name, "parenttype": "Salary Slip",
						"salary_component": a["ten"], "amount": a["so_tien"], "amount_based_on_formula": 0}).insert(ignore_permissions=True)
			for comp, amt in (("BHXH (8%)", calc["bhxh"]), ("BHYT (1.5%)", calc["bhyt"]),
					("BHTN (1%)", calc["bhtn"]), ("Thuế TNCN", calc["pit"])):
				if amt > 0:
					frappe.get_doc({"doctype": "Salary Detail", "parent": slip.name, "parenttype": "Salary Slip",
						"salary_component": comp, "amount": amt, "amount_based_on_formula": 0}).insert(ignore_permissions=True)
			frappe.db.set_value("Salary Slip", slip.name, "gross_pay", calc["gross"])
			frappe.db.set_value("Salary Slip", slip.name, "total_deduction", calc["bh_nld"] + calc["pit"])
			frappe.db.set_value("Salary Slip", slip.name, "net_pay", calc["net"])
			frappe.db.commit()

			created.append({
				"employee": e["name"], "name": label, "slip": slip.name,
				"gross": slip.gross_pay, "deduction": slip.total_deduction, "net": slip.net_pay,
				"days": calc["_actual_days"], "total_days": total_wd,
			})
			totals["gross"] += slip.gross_pay or 0
			totals["ins"] += calc["bh_nld"]
			totals["tax"] += calc["pit"]
			totals["net"] += slip.net_pay or 0
			totals["count"] += 1
		except Exception as ex:
			errors.append({"employee": e["name"], "name": label, "error": str(ex)[:200]})

	frappe.db.commit()
	return {
		"period": f"{month:02d}/{year}",
		"start": str(start), "end": str(end),
		"created": created, "skipped": skipped, "errors": errors, "totals": totals,
	}


@frappe.whitelist()
def get_salary_slip_detail(name):
	"""Chi tiết 1 phiếu lương: thành phần thu nhập + khấu trừ."""
	doc = frappe.get_doc("Salary Slip", name)
	return {
		"name": doc.name,
		"employee": doc.employee,
		"employee_name": doc.employee_name,
		"designation": doc.designation,
		"start_date": str(doc.start_date),
		"end_date": str(doc.end_date),
		"total_working_days": doc.total_working_days,
		"payment_days": doc.payment_days,
		"gross_pay": doc.gross_pay,
		"total_deduction": doc.total_deduction,
		"net_pay": doc.net_pay,
		"docstatus": doc.docstatus,
		"earnings": [{"component": x.salary_component, "amount": x.amount} for x in doc.earnings],
		"deductions": [{"component": x.salary_component, "amount": x.amount} for x in doc.deductions],
	}


@frappe.whitelist()
def get_working_days_info(month=None, year=None):
	"""Trả về tổng ngày công chuẩn của tháng + danh sách NV Active để điền ngày công khi chạy lương."""
	import calendar as _cal
	from datetime import date as _date, timedelta
	today = frappe.utils.getdate()
	year = int(year) if year else today.year
	month = int(month) if month else today.month
	last_day = _cal.monthrange(year, month)[1]
	start = _date(year, month, 1)
	end = _date(year, month, last_day)
	company = _default_company()
	hl_name = _ensure_holiday_list(company, year)
	holidays = {frappe.utils.getdate(h.holiday_date) for h in frappe.get_all("Holiday", filters={"parent": hl_name}, fields=["holiday_date"], limit_page_length=0)}
	total = 0
	d = start
	while d <= end:
		if d.weekday() != 6 and d not in holidays:
			total += 1
		d += timedelta(days=1)
	emps = frappe.get_all("Employee", filters={"status": "Active"}, fields=["name", "employee_name", "custom_luong_co_ban"], order_by="employee_name asc", limit_page_length=0)
	return {"month": month, "year": year, "total_working_days": total, "employees": [{"name": e["name"], "employee_name": e["employee_name"], "luong_co_ban": e.get("custom_luong_co_ban") or 0} for e in emps]}


@frappe.whitelist()
def submit_salary_slip(name):
	"""Chốt (submit) 1 phiếu lương Nháp."""
	doc = frappe.get_doc("Salary Slip", name)
	if doc.docstatus == 0:
		doc.submit()
		frappe.db.commit()
	return {"ok": True, "docstatus": doc.docstatus}


@frappe.whitelist()
def delete_salary_slip(name):
	"""Xóa phiếu lương (cancel nếu đã submit)."""
	doc = frappe.get_doc("Salary Slip", name)
	if doc.docstatus == 1:
		doc.cancel()
	frappe.delete_doc("Salary Slip", name, ignore_permissions=True)
	frappe.db.commit()
	return {"ok": True}


@frappe.whitelist()
def submit_all_salary_slips(month=None, year=None):
	"""Chốt toàn bộ phiếu lương Nháp của 1 kỳ."""
	import calendar as _cal
	today = frappe.utils.getdate()
	year = int(year) if year else today.year
	month = int(month) if month else today.month
	last = _cal.monthrange(year, month)[1]
	start, end = f"{year}-{month:02d}-01", f"{year}-{month:02d}-{last}"
	slips = frappe.get_all("Salary Slip", filters={
		"start_date": start, "end_date": end, "docstatus": 0,
	}, pluck="name", limit_page_length=0)
	submitted, errors = 0, []
	for name in slips:
		try:
			frappe.get_doc("Salary Slip", name).submit()
			submitted += 1
		except Exception as e:
			errors.append({"name": name, "error": str(e)[:120]})
	frappe.db.commit()
	return {"submitted": submitted, "errors": errors, "total": len(slips)}


_PAYROLL_LOCKS = {}  # cache in-memory cho nhanh trong cùng request

def _payroll_lock_key(year, month):
	return f"{int(year)}-{int(month):02d}"

def _is_payroll_locked(year, month):
	"""Kiểm tra kỳ lương đã khóa chưa (lưu trong HR Settings JSON). Trả False nếu field chưa tạo."""
	try:
		raw = frappe.db.get_single_value("HR Settings", "custom_payroll_locks")
	except Exception:
		return False
	if not raw:
		return False
	try:
		return _payroll_lock_key(year, month) in _json.loads(raw)
	except Exception:
		return False


@frappe.whitelist()
def get_payroll_period_status(month=None, year=None):
	"""Trạng thái kỳ lương: số phiếu Nháp/Đã chốt + khóa."""
	import calendar as _cal
	today = frappe.utils.getdate()
	year = int(year) if year else today.year
	month = int(month) if month else today.month
	last = _cal.monthrange(year, month)[1]
	start, end = f"{year}-{month:02d}-01", f"{year}-{month:02d}-{last}"
	locked = _is_payroll_locked(year, month)
	draft = frappe.db.count("Salary Slip", {"start_date": start, "end_date": end, "docstatus": 0})
	submitted = frappe.db.count("Salary Slip", {"start_date": start, "end_date": end, "docstatus": 1})
	return {"period": _payroll_lock_key(year, month), "draft": draft, "submitted": submitted,
		"locked": locked, "total": draft + submitted}


@frappe.whitelist()
def lock_payroll_period(month, year, unlock=0):
	"""Khóa / mở khóa kỳ lương (ngăn chạy lại). Lưu JSON trong HR Settings."""
	_ensure_custom_field("HR Settings", "custom_payroll_locks", {"label": "Khóa kỳ lương (JSON)", "fieldtype": "Long Text"})
	raw = frappe.db.get_single_value("HR Settings", "custom_payroll_locks")
	locks = _json.loads(raw) if raw else {}
	key = _payroll_lock_key(year, month)
	unlock = str(unlock) in ("1", "true", "True")
	if unlock:
		locks.pop(key, None)
	else:
		locks[key] = True
	frappe.db.set_single_value("HR Settings", "custom_payroll_locks", _json.dumps(locks, ensure_ascii=False))
	frappe.db.commit()
	return {"locked": not unlock, "period": key}


_WAGE_SLIP_HTML = """<html><head><meta charset="utf-8"><title>Phiếu lương __PERIOD__</title>
<style>
body{font-family:sans-serif;max-width:480px;margin:20px auto;line-height:1.6;color:#1f2937}
h2{text-align:center;margin-bottom:4px}.sub{text-align:center;font-size:12px;color:#6b7280;margin-bottom:16px}
.row{display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px solid #e5e7eb;font-size:14px}
.gross{font-weight:bold;border-top:2px solid #1f2937;margin-top:8px;padding-top:8px}
.net{font-size:18px;font-weight:bold;color:#059669;border-top:2px solid #059669;margin-top:8px;padding-top:8px}
.payee{font-size:12px;color:#6b7280}.toolbar{text-align:center;margin-top:20px}
button{font-family:sans-serif;padding:8px 18px;background:#2563eb;color:#fff;border:none;border-radius:6px;cursor:pointer}
@media print{.toolbar{display:none}}
</style></head><body>
<h2>PHIẾU LƯƠNG</h2>
<div class="sub">__PERIOD__</div>
<div class="row payee"><strong>__EMP_NAME__</strong><span>__EMP_CODE__</span></div>
<div class="row payee">__DESIGNATION__<span>__DEPARTMENT__</span></div>
__EARNINGS_ROWS__
<div class="row gross"><strong>Tổng thu nhập (Gross)</strong><strong>__GROSS__</strong></div>
__DEDUCTION_ROWS__
<div class="row"><strong>Tổng khấu trừ</strong><strong>-__TOTAL_DED__</strong></div>
<div class="row net"><strong>💰 Thực lãnh (Net)</strong><strong>__NET__</strong></div>
<div class="payee" style="margin-top:12px">Ngày công: __PAYMENT_DAYS__ / __TOTAL_WD__ ngày</div>
<div class="toolbar"><button onclick="window.print()">🖨 In / Lưu PDF</button></div>
</body></html>"""


@frappe.whitelist()
def print_salary_slip(name):
	"""HTML phiếu lương để in/lưu PDF."""
	doc = frappe.get_doc("Salary Slip", name)
	money = lambda v: f"{int(v or 0):,} ₫"
	html = _WAGE_SLIP_HTML
	html = html.replace("__PERIOD__", f"{doc.start_date} → {doc.end_date}")
	html = html.replace("__EMP_NAME__", doc.employee_name or "")
	html = html.replace("__EMP_CODE__", doc.employee or "")
	html = html.replace("__DESIGNATION__", doc.designation or "")
	html = html.replace("__DEPARTMENT__", doc.department or "")
	html = html.replace("__GROSS__", money(doc.gross_pay))
	html = html.replace("__NET__", money(doc.net_pay))
	html = html.replace("__TOTAL_DED__", money(doc.total_deduction))
	html = html.replace("__PAYMENT_DAYS__", str(doc.payment_days or doc.total_working_days or ""))
	html = html.replace("__TOTAL_WD__", str(doc.total_working_days or ""))
	e_rows = ""
	for e in doc.earnings:
		if e.amount:
			label = (e.salary_component or "").replace("Basic", "Lương cơ bản")
			e_rows += f'<div class="row"><span>{label}</span><span>{money(e.amount)}</span></div>\n'
	html = html.replace("__EARNINGS_ROWS__", e_rows)
	d_rows = ""
	for d in doc.deductions:
		if d.amount:
			d_rows += f'<div class="row"><span>{d.salary_component}</span><span style="color:#dc2626">-{money(d.amount)}</span></div>\n'
	html = html.replace("__DEDUCTION_ROWS__", d_rows)
	return {"html": html, "name": doc.name, "employee_name": doc.employee_name}
	doc = frappe.get_doc("Salary Slip", name)
	if doc.docstatus == 1:
		doc.cancel()
	frappe.delete_doc("Salary Slip", name, ignore_permissions=True)
	frappe.db.commit()
	return {"ok": True}


# ════════════════════════════════════════════════════════════════════
#  LƯƠNG VN FULL CHUẨN — gross/net, phụ cấp, lương đóng BHXH (trần), NPT, gross-up
#  Engine compute_payroll() dùng chung cho Bảng lương + Thuế & Phúc lợi.
# ════════════════════════════════════════════════════════════════════
import json as _json

# Cấu hình mặc định (lưu JSON trong HR Settings.custom_vn_payroll_config, chỉnh trên UI)
_VN_DEFAULT_CFG = {
	"luong_co_so": 2_340_000,
	"luong_toi_thieu_vung": {"I": 4_960_000, "II": 4_410_000, "III": 3_860_000, "IV": 3_450_000},
	"he_so_tran": 20,
	"giam_tru_ban_than": 11_000_000,
	"giam_tru_nguoi_phu_thuoc": 4_400_000,
	"ty_le_bh_nld": {"bhxh": 0.08, "bhyt": 0.015, "bhtn": 0.01},
	"ty_le_bh_dn": {"bhxh": 0.175, "bhyt": 0.03, "bhtn": 0.01},
	# [đến_mức, thuế_suất]; mức cuối null = vô cực
	"pit_brackets": [[5_000_000, 0.05], [10_000_000, 0.10], [18_000_000, 0.15],
		[32_000_000, 0.20], [52_000_000, 0.25], [80_000_000, 0.30], [None, 0.35]],
	# Catalog phụ cấp gợi ý (mỗi NV copy ra rồi sửa số tiền)
	"allowance_catalog": [
		{"ten": "Phụ cấp chức vụ", "chiu_thue": True, "dong_bh": True, "tran_mien": 0},
		{"ten": "Phụ cấp trách nhiệm", "chiu_thue": True, "dong_bh": True, "tran_mien": 0},
		{"ten": "Phụ cấp ăn ca", "chiu_thue": True, "dong_bh": False, "tran_mien": 730_000},
		{"ten": "Phụ cấp xăng xe", "chiu_thue": True, "dong_bh": False, "tran_mien": 0},
		{"ten": "Phụ cấp điện thoại", "chiu_thue": False, "dong_bh": False, "tran_mien": 0},
		{"ten": "Thưởng", "chiu_thue": True, "dong_bh": False, "tran_mien": 0},
	],
}

# Custom Field cần tạo trên Employee
_EMP_CUSTOM_FIELDS = [
	("custom_loai_luong", {"label": "Loại lương (Gross/Net)", "fieldtype": "Select", "options": "Gross\nNet", "default": "Gross"}),
	("custom_luong_co_ban", {"label": "Lương cơ bản (đóng BH)", "fieldtype": "Currency"}),
	("custom_luong_dong_bhxh", {"label": "Lương đóng BHXH (nếu khác lương cơ bản)", "fieldtype": "Currency"}),
	("custom_vung_luong", {"label": "Vùng lương tối thiểu", "fieldtype": "Select", "options": "I\nII\nIII\nIV", "default": "I"}),
	("custom_phu_cap", {"label": "Phụ cấp (JSON)", "fieldtype": "Long Text"}),
	("custom_nguoi_phu_thuoc", {"label": "Người phụ thuộc (JSON)", "fieldtype": "Long Text"}),
]


def _ensure_custom_field(dt, fieldname, props):
	if frappe.db.exists("Custom Field", f"{dt}-{fieldname}"):
		return
	props = dict(props)
	frappe.get_doc({"doctype": "Custom Field", "dt": dt, "fieldname": fieldname,
		"insert_after": props.pop("insert_after", "ctc" if dt == "Employee" else None), **props}).insert(ignore_permissions=True)


def _ensure_applicant_fields():
	_ensure_custom_field("Job Applicant", "custom_offered_salary", {"label": "Lương offer", "fieldtype": "Currency", "insert_after": "upper_range"})


def _ensure_earning_component(name):
	if not frappe.db.exists("Salary Component", name):
		frappe.get_doc({"doctype": "Salary Component", "salary_component": name,
			"type": "Earning", "depends_on_payment_days": 0, "is_tax_applicable": 1}).insert(ignore_permissions=True)


@frappe.whitelist()
def setup_vn_payroll():
	"""Cài đặt 1 lần (idempotent): custom field Employee + HR Settings, cấu hình mặc định, salary component."""
	for fn, props in _EMP_CUSTOM_FIELDS:
		_ensure_custom_field("Employee", fn, props)
	_ensure_custom_field("HR Settings", "custom_vn_payroll_config", {"label": "Cấu hình lương VN (JSON)", "fieldtype": "Long Text"})

	if not (frappe.db.get_single_value("HR Settings", "custom_vn_payroll_config") or "").strip():
		frappe.db.set_single_value("HR Settings", "custom_vn_payroll_config", _json.dumps(_VN_DEFAULT_CFG, ensure_ascii=False))

	_ensure_earning_component("Lương cơ bản")
	for a in _VN_DEFAULT_CFG["allowance_catalog"]:
		_ensure_earning_component(a["ten"])
	_ensure_salary_components()
	frappe.db.commit()
	frappe.clear_cache(doctype="Employee")
	return {"ok": True, "fields": [f for f, _ in _EMP_CUSTOM_FIELDS]}


def _load_vn_config():
	"""Đọc cấu hình lương VN (merge default để an toàn nếu thiếu khóa)."""
	raw = frappe.db.get_single_value("HR Settings", "custom_vn_payroll_config")
	cfg = dict(_VN_DEFAULT_CFG)
	if raw:
		try:
			cfg.update(_json.loads(raw))
		except Exception:
			pass
	return cfg


def _pit(taxable, brackets):
	"""Thuế TNCN lũy tiến từng phần. brackets = [[đến_mức|None, suất], ...]."""
	if taxable <= 0:
		return 0
	tax, lower = 0, 0
	for upper, rate in brackets:
		cap = taxable if upper is None else upper
		if taxable > lower:
			tax += (min(taxable, cap) - lower) * rate
			lower = cap
		else:
			break
	return round(tax)


def _compute(p, cfg):
	"""Lõi tính lương VN (chạy xuôi từ gross). p = dict tham số NV."""
	lcb = float(p.get("luong_co_ban") or 0)
	phu_cap = p.get("phu_cap") or []
	npt_count = int(p.get("npt_count") or 0)
	vung = p.get("vung") or "I"
	override_bh = float(p.get("luong_dong_bhxh") or 0)

	earnings = [{"ten": "Lương cơ bản", "so_tien": lcb, "chiu_thue": True, "dong_bh": True, "tran_mien": 0}]
	for a in phu_cap:
		earnings.append({"ten": a.get("ten") or "Phụ cấp", "so_tien": float(a.get("so_tien") or 0),
			"chiu_thue": bool(a.get("chiu_thue", True)), "dong_bh": bool(a.get("dong_bh", False)),
			"tran_mien": float(a.get("tran_mien") or 0)})
	gross = sum(e["so_tien"] for e in earnings)

	if override_bh > 0:
		bh_base = override_bh
	else:
		bh_base = sum(e["so_tien"] for e in earnings if e["dong_bh"])
	cap_xhyt = cfg["he_so_tran"] * cfg["luong_co_so"]
	cap_tn = cfg["he_so_tran"] * cfg["luong_toi_thieu_vung"].get(vung, cfg["luong_toi_thieu_vung"]["I"])
	r = cfg["ty_le_bh_nld"]
	bhxh = round(min(bh_base, cap_xhyt) * r["bhxh"])
	bhyt = round(min(bh_base, cap_xhyt) * r["bhyt"])
	bhtn = round(min(bh_base, cap_tn) * r["bhtn"])
	bh_nld = bhxh + bhyt + bhtn

	taxable_earn = 0
	for e in earnings:
		if e["chiu_thue"]:
			taxable_earn += max(0, e["so_tien"] - e["tran_mien"])
	giam_tru = cfg["giam_tru_ban_than"] + cfg["giam_tru_nguoi_phu_thuoc"] * npt_count
	assessable = taxable_earn - bh_nld - giam_tru
	pit = _pit(max(0, assessable), cfg["pit_brackets"])

	net = round(gross - bh_nld - pit)
	rd = cfg["ty_le_bh_dn"]
	bh_dn = round(min(bh_base, cap_xhyt) * rd["bhxh"]) + round(min(bh_base, cap_xhyt) * rd["bhyt"]) + round(min(bh_base, cap_tn) * rd["bhtn"])

	return {
		"gross": round(gross), "earnings": earnings,
		"bh_base": round(bh_base), "bh_capped_xhyt": round(min(bh_base, cap_xhyt)), "bh_capped_tn": round(min(bh_base, cap_tn)),
		"bhxh": bhxh, "bhyt": bhyt, "bhtn": bhtn, "bh_nld": bh_nld, "bh_dn": bh_dn,
		"taxable_earn": round(taxable_earn), "giam_tru": giam_tru, "npt_count": npt_count,
		"assessable": round(max(0, assessable)), "pit": pit, "net": net,
	}


def _emp_params(emp):
	"""Trích tham số lương từ Employee doc."""
	def _arr(field):
		try:
			return _json.loads(emp.get(field) or "[]")
		except Exception:
			return []
	npt = _arr("custom_nguoi_phu_thuoc")
	return {
		# fallback ctc/12 cho NV chưa cấu hình lương cơ bản (tương thích dữ liệu cũ)
		"luong_co_ban": emp.get("custom_luong_co_ban") or ((emp.get("ctc") or 0) / 12),
		"luong_dong_bhxh": emp.get("custom_luong_dong_bhxh") or 0,
		"vung": emp.get("custom_vung_luong") or "I",
		"loai_luong": emp.get("custom_loai_luong") or "Gross",
		"phu_cap": _arr("custom_phu_cap"),
		"npt_count": sum(1 for d in npt if d.get("active", True)),
	}


def compute_payroll(emp, cfg=None):
	"""Tính lương cho 1 Employee (doc hoặc name)."""
	if isinstance(emp, str):
		emp = frappe.get_doc("Employee", emp)
	cfg = cfg or _load_vn_config()
	return _compute(_emp_params(emp), cfg)


@frappe.whitelist()
def compute_payroll_preview(employee):
	"""Xem trước bảng tính lương realtime cho form NV (không lưu)."""
	res = compute_payroll(employee)
	res["loai_luong"] = (frappe.db.get_value("Employee", employee, "custom_loai_luong") or "Gross")
	return res


@frappe.whitelist()
def preview_salary(luong_co_ban=0, luong_dong_bhxh=0, vung="I", phu_cap=None, npt_count=0):
	"""Xem trước bảng tính lương từ tham số form (KHÔNG cần lưu) — cho preview realtime."""
	p = {
		"luong_co_ban": float(luong_co_ban or 0),
		"luong_dong_bhxh": float(luong_dong_bhxh or 0),
		"vung": vung or "I",
		"phu_cap": _json.loads(phu_cap) if isinstance(phu_cap, str) else (phu_cap or []),
		"npt_count": int(npt_count or 0),
	}
	return _compute(p, _load_vn_config())


@frappe.whitelist()
def gross_up_basic(net_target, employee=None, phu_cap=None, npt_count=0, vung="I", luong_dong_bhxh=0):
	"""HĐ Net: tìm Lương cơ bản gross sao cho net == net_target (binary search)."""
	net_target = float(net_target)
	cfg = _load_vn_config()
	if employee:
		base = _emp_params(frappe.get_doc("Employee", employee))
	else:
		base = {"phu_cap": _json.loads(phu_cap) if isinstance(phu_cap, str) else (phu_cap or []),
			"npt_count": int(npt_count), "vung": vung, "luong_dong_bhxh": float(luong_dong_bhxh or 0)}
	lo, hi = 0.0, max(net_target * 3, 10_000_000)
	for _ in range(40):
		base["luong_co_ban"] = hi
		if _compute(base, cfg)["net"] >= net_target:
			break
		hi *= 1.5
	mid = hi
	for _ in range(60):
		mid = (lo + hi) / 2
		base["luong_co_ban"] = mid
		net = _compute(base, cfg)["net"]
		if abs(net - net_target) <= 500:
			break
		if net < net_target:
			lo = mid
		else:
			hi = mid
	base["luong_co_ban"] = round(mid)
	return {"luong_co_ban": round(mid), "result": _compute(base, cfg)}


@frappe.whitelist()
def get_allowance_catalog():
	"""Danh mục phụ cấp gợi ý (để dropdown thêm phụ cấp trên form NV)."""
	return _load_vn_config().get("allowance_catalog", [])


@frappe.whitelist()
def get_vn_payroll_config():
	return _load_vn_config()


@frappe.whitelist()
def save_vn_payroll_config(config):
	"""Lưu cấu hình lương VN (JSON từ trang cấu hình)."""
	cfg = _json.loads(config) if isinstance(config, str) else config
	frappe.db.set_single_value("HR Settings", "custom_vn_payroll_config", _json.dumps(cfg, ensure_ascii=False))
	frappe.db.commit()
	return {"ok": True}


@frappe.whitelist()
def get_employee_salary(name):
	"""Cấu hình lương + phụ cấp + NPT của 1 NV (cho form sửa)."""
	emp = frappe.get_doc("Employee", name)
	p = _emp_params(emp)
	return {
		"employee": name, "employee_name": emp.employee_name,
		"loai_luong": emp.get("custom_loai_luong") or "Gross",
		"luong_co_ban": emp.get("custom_luong_co_ban") or 0,
		"luong_dong_bhxh": emp.get("custom_luong_dong_bhxh") or 0,
		"vung": emp.get("custom_vung_luong") or "I",
		"phu_cap": p["phu_cap"],
		"nguoi_phu_thuoc": _json.loads(emp.get("custom_nguoi_phu_thuoc") or "[]"),
		"preview": _compute(p, _load_vn_config()),
	}


@frappe.whitelist()
def save_employee_salary(name, loai_luong="Gross", luong_co_ban=0, luong_dong_bhxh=0, vung="I", phu_cap=None, nguoi_phu_thuoc=None):
	"""Lưu cấu hình lương NV. phu_cap/nguoi_phu_thuoc là JSON string hoặc list."""
	emp = frappe.get_doc("Employee", name)
	pc = phu_cap if isinstance(phu_cap, str) else _json.dumps(phu_cap or [], ensure_ascii=False)
	npt = nguoi_phu_thuoc if isinstance(nguoi_phu_thuoc, str) else _json.dumps(nguoi_phu_thuoc or [], ensure_ascii=False)
	emp.db_set("custom_loai_luong", loai_luong)
	emp.db_set("custom_luong_co_ban", float(luong_co_ban or 0))
	emp.db_set("custom_luong_dong_bhxh", float(luong_dong_bhxh or 0))
	emp.db_set("custom_vung_luong", vung or "I")
	emp.db_set("custom_phu_cap", pc)
	emp.db_set("custom_nguoi_phu_thuoc", npt)
	gross = _compute(_emp_params(frappe.get_doc("Employee", name)), _load_vn_config())["gross"]
	emp.db_set("ctc", gross * 12)
	frappe.db.commit()
	return {"ok": True, "gross": gross}


# ════════════════════════════════════════════════════════════════════
#  QUYẾT ĐỊNH NHÂN SỰ — bổ nhiệm/thăng chức, điều chuyển, khen thưởng/kỷ luật, thôi việc
#  Tái dùng doctype HRMS (submit tự cập nhật hồ sơ NV).
# ════════════════════════════════════════════════════════════════════

def _prop_history(parent, parenttype):
	rows = frappe.get_all("Employee Property History",
		filters={"parent": parent, "parenttype": parenttype},
		fields=["property", "current", "new"])
	return "; ".join(f"{r.property}: {r.current or '—'} → {r.new}" for r in rows)


def _eff_date(d):
	"""Ngày hiệu lực hợp lệ để submit: không vượt quá hôm nay (theo giờ server).
	Tránh lỗi 'cannot be submitted before ... Date' khi client gửi ngày tương lai (lệch múi giờ)."""
	today = frappe.utils.getdate()
	d = frappe.utils.getdate(d) if d else today
	return d if d <= today else today


@frappe.whitelist()
def create_promotion(employee, new_designation=None, new_luong_co_ban=None, promotion_date=None, reason=""):
	"""Quyết định bổ nhiệm/thăng chức (+ điều chỉnh lương). Submit → tự cập nhật hồ sơ NV."""
	emp = frappe.get_doc("Employee", employee)
	doc = frappe.new_doc("Employee Promotion")
	doc.employee = employee
	doc.promotion_date = _eff_date(promotion_date)
	doc.company = emp.company
	changed_salary = False
	if new_designation and new_designation != emp.designation:
		doc.append("promotion_details", {"property": "Chức vụ", "fieldname": "designation",
			"current": emp.designation or "", "new": new_designation})
	if new_luong_co_ban and float(new_luong_co_ban) != float(emp.get("custom_luong_co_ban") or 0):
		old_lcb = float(emp.get("custom_luong_co_ban") or 0)
		doc.append("promotion_details", {"property": "Lương cơ bản", "fieldname": "custom_luong_co_ban",
			"current": str(int(old_lcb)), "new": str(int(float(new_luong_co_ban)))})
		doc.current_ctc = old_lcb * 12
		doc.revised_ctc = float(new_luong_co_ban) * 12
		changed_salary = True
	if not doc.promotion_details:
		frappe.throw("Chưa có thay đổi nào (chức vụ/lương) để bổ nhiệm.")
	doc.insert(ignore_permissions=True)
	doc.submit()
	if changed_salary:
		frappe.db.set_value("Employee", employee, "ctc", float(new_luong_co_ban) * 12)
	if reason:
		frappe.get_doc("Employee", employee).add_comment("Info", f"[BỔ NHIỆM] {reason}")
	frappe.db.commit()
	return {"ok": True, "name": doc.name}


@frappe.whitelist()
def create_transfer(employee, new_department=None, new_company=None, transfer_date=None, reason=""):
	"""Quyết định điều chuyển phòng ban/công ty. Submit → tự cập nhật hồ sơ NV."""
	emp = frappe.get_doc("Employee", employee)
	doc = frappe.new_doc("Employee Transfer")
	doc.employee = employee
	doc.transfer_date = _eff_date(transfer_date)
	doc.company = emp.company
	doc.create_new_employee_id = 0
	if new_department and new_department != emp.department:
		doc.append("transfer_details", {"property": "Phòng ban", "fieldname": "department",
			"current": emp.department or "", "new": new_department})
	if new_company and new_company != emp.company:
		doc.new_company = new_company
		doc.append("transfer_details", {"property": "Công ty", "fieldname": "company",
			"current": emp.company or "", "new": new_company})
	if not doc.transfer_details:
		frappe.throw("Chưa có thay đổi phòng ban/công ty để điều chuyển.")
	doc.insert(ignore_permissions=True)
	doc.submit()
	if reason:
		frappe.get_doc("Employee", employee).add_comment("Info", f"[ĐIỀU CHUYỂN] {reason}")
	frappe.db.commit()
	return {"ok": True, "name": doc.name}


@frappe.whitelist()
def create_separation(employee, separation_date=None, reason="", exit_interview=""):
	"""Quyết định thôi việc/chấm dứt HĐ. Đánh dấu NV nghỉ việc + tạo Employee Separation (checklist offboarding)."""
	emp = frappe.get_doc("Employee", employee)
	rdate = _eff_date(separation_date)
	doc = frappe.new_doc("Employee Separation")
	doc.employee = employee
	doc.company = emp.company
	doc.boarding_begins_on = rdate
	doc.resignation_letter_date = rdate
	doc.boarding_status = "Pending"
	if exit_interview:
		doc.exit_interview = exit_interview
	doc.insert(ignore_permissions=True)
	doc.submit()
	emp.status = "Left"
	emp.relieving_date = rdate
	emp.save(ignore_permissions=True)
	emp.add_comment("Info", f"[THÔI VIỆC] {reason or 'Chấm dứt hợp đồng lao động'}")
	frappe.db.commit()
	return {"ok": True, "name": doc.name}


@frappe.whitelist()
def create_reward_discipline(employee, kind="reward", title="", amount=0, note="", date=None):
	"""Quyết định khen thưởng (reward) / kỷ luật (discipline) — lưu Comment có cấu trúc trên hồ sơ NV."""
	marker = "KHEN_THUONG" if kind == "reward" else "KY_LUAT"
	data = {"title": title, "amount": float(amount or 0), "note": note, "date": date or frappe.utils.today()}
	frappe.get_doc("Employee", employee).add_comment("Info", f"[{marker}]{_json.dumps(data, ensure_ascii=False)}")
	frappe.db.commit()
	return {"ok": True}


@frappe.whitelist()
def get_decisions(employee):
	"""Gộp mọi quyết định nhân sự của 1 NV (mới nhất trước)."""
	out = []
	for p in frappe.get_all("Employee Promotion", filters={"employee": employee, "docstatus": 1},
			fields=["name", "promotion_date"]):
		out.append({"kind": "promotion", "label": "Bổ nhiệm / Thăng chức", "doctype": "Employee Promotion",
			"name": p.name, "date": str(p.promotion_date), "detail": _prop_history(p.name, "Employee Promotion")})
	for t in frappe.get_all("Employee Transfer", filters={"employee": employee, "docstatus": 1},
			fields=["name", "transfer_date"]):
		out.append({"kind": "transfer", "label": "Điều chuyển", "doctype": "Employee Transfer",
			"name": t.name, "date": str(t.transfer_date), "detail": _prop_history(t.name, "Employee Transfer")})
	for s in frappe.get_all("Employee Separation", filters={"employee": employee, "docstatus": 1},
			fields=["name", "boarding_begins_on"]):
		out.append({"kind": "separation", "label": "Thôi việc", "doctype": "Employee Separation",
			"name": s.name, "date": str(s.boarding_begins_on), "detail": "Chấm dứt hợp đồng lao động"})
	for c in frappe.get_all("Comment",
			filters={"reference_doctype": "Employee", "reference_name": employee, "comment_type": "Info"},
			fields=["content", "creation"], order_by="creation desc"):
		for marker, kind, label in (("[KHEN_THUONG]", "reward", "Khen thưởng"), ("[KY_LUAT]", "discipline", "Kỷ luật")):
			if marker in (c.content or ""):
				try:
					d = _json.loads(c.content.split(marker, 1)[1])
				except Exception:
					d = {}
				out.append({"kind": kind, "label": label, "doctype": "Comment", "name": None,
					"date": d.get("date") or str(c.creation)[:10],
					"detail": d.get("title", "") + (f" ({int(d['amount']):,}₫)" if d.get("amount") else ""), "data": d})
	out.sort(key=lambda x: x["date"], reverse=True)
	return out


def _vn_date(d):
	d = frappe.utils.getdate(d)
	return f"ngày {d.day:02d} tháng {d.month:02d} năm {d.year}"


_DECISION_TPL = """<!doctype html><html><head><meta charset="utf-8"><title>Quyết định</title>
<style>
body{font-family:'Times New Roman',serif;font-size:14.5px;max-width:760px;margin:24px auto;line-height:1.55;color:#000;padding:0 16px}
.row{display:flex;justify-content:space-between;text-align:center;gap:16px}.row>div{flex:1}
.center{text-align:center}.b{font-weight:bold}.mt{margin-top:14px}.sign{margin-top:36px;align-items:flex-start}
hr.s{width:150px;border:none;border-top:1px solid #000;margin:5px auto}
.title{font-size:18px;letter-spacing:1px}.toolbar{text-align:center;margin-top:28px}
button{font-family:sans-serif;padding:8px 18px;border:1px solid #2563eb;background:#2563eb;color:#fff;border-radius:6px;cursor:pointer}
@media print{.toolbar{display:none}}
</style></head><body>
<div class="row">
<div><div class="b">__CNAME__</div><div>Số: ......./QĐ-__SO__</div></div>
<div><div class="b">CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM</div><div class="b">Độc lập - Tự do - Hạnh phúc</div><hr class="s"/><div><i>__DATE__</i></div></div>
</div>
<div class="center mt"><div class="b title">QUYẾT ĐỊNH</div><div>V/v __TITLE_LOWER__ đối với ông/bà __EMP__</div></div>
<div class="center b mt">GIÁM ĐỐC CÔNG TY</div>
<div class="mt">- Căn cứ Bộ luật Lao động hiện hành;</div>
<div>- Căn cứ Điều lệ tổ chức và hoạt động của Công ty;</div>
<div>- Xét năng lực, phẩm chất và nhu cầu công tác,</div>
<div class="center b mt">QUYẾT ĐỊNH:</div>
<div class="mt"><b>Điều 1.</b> __DIEU1__</div>
<div class="mt"><b>Điều 2.</b> Quyết định có hiệu lực kể từ __DATE__.__NOTE__</div>
<div class="mt"><b>Điều 3.</b> Các phòng/ban liên quan và ông/bà có tên tại Điều 1 chịu trách nhiệm thi hành quyết định này.</div>
<div class="row sign">
<div style="text-align:left"><i>Nơi nhận:</i><div>- Như Điều 3;<br/>- Lưu VT.</div></div>
<div><div class="b">GIÁM ĐỐC</div><div><i>(Ký, ghi rõ họ tên)</i></div></div>
</div>
<div class="toolbar"><button onclick="window.print()">🖨 In / Lưu PDF</button></div>
</body></html>"""


@frappe.whitelist()
def get_decision_print(kind, name=None, employee=None, payload=None):
	"""HTML quyết định nhân sự mẫu VN để in/lưu PDF."""
	data = _json.loads(payload) if (payload and isinstance(payload, str)) else (payload or {})
	if kind == "promotion":
		doc = frappe.get_doc("Employee Promotion", name)
		emp_name, company, ddate = doc.employee_name, doc.company, doc.promotion_date
		so, title = "BN", "bổ nhiệm / điều chỉnh công tác"
		dieu1 = f"Bổ nhiệm/điều chỉnh đối với ông/bà <b>{emp_name}</b> với nội dung: {_prop_history(doc.name, 'Employee Promotion')}."
	elif kind == "transfer":
		doc = frappe.get_doc("Employee Transfer", name)
		emp_name, company, ddate = doc.employee_name, doc.company, doc.transfer_date
		so, title = "DC", "điều chuyển công tác"
		dieu1 = f"Điều chuyển công tác đối với ông/bà <b>{emp_name}</b>: {_prop_history(doc.name, 'Employee Transfer')}."
	elif kind == "separation":
		doc = frappe.get_doc("Employee Separation", name)
		emp_name, company, ddate = doc.employee_name, doc.company, doc.boarding_begins_on
		so, title = "TV", "chấm dứt hợp đồng lao động"
		dieu1 = f"Chấm dứt hợp đồng lao động đối với ông/bà <b>{emp_name}</b> kể từ {_vn_date(ddate)}."
	else:  # reward / discipline (từ payload)
		company = frappe.db.get_value("Employee", employee, "company")
		emp_name = frappe.db.get_value("Employee", employee, "employee_name")
		ddate = data.get("date") or frappe.utils.today()
		if kind == "reward":
			so, title = "KT", "khen thưởng"
			amt = f" Mức thưởng: {int(data.get('amount') or 0):,} đồng." if data.get("amount") else ""
			dieu1 = f"Khen thưởng đối với ông/bà <b>{emp_name}</b> — {data.get('title','')}.{amt}"
		else:
			so, title = "KL", "kỷ luật"
			dieu1 = f"Thi hành kỷ luật đối với ông/bà <b>{emp_name}</b> — hình thức: {data.get('title','')}."
	cname = (frappe.db.get_value("Company", company, "company_name") or company or "CÔNG TY").upper()
	note = (" " + data.get("note")) if data.get("note") else ""
	html_doc = (_DECISION_TPL
		.replace("__CNAME__", cname).replace("__SO__", so)
		.replace("__TITLE_LOWER__", title).replace("__EMP__", emp_name or "")
		.replace("__DIEU1__", dieu1).replace("__NOTE__", note)
		.replace("__DATE__", _vn_date(ddate)))
	return {"html": html_doc, "title": title, "employee_name": emp_name}


def _decision_icon(kind):
	return {"promotion": "trending-up", "transfer": "shuffle", "separation": "log-out",
		"reward": "award", "discipline": "alert-triangle", "join": "log-in", "update": "edit-2"}.get(kind, "file-text")


@frappe.whitelist()
def get_employee_timeline(employee):
	"""Dòng thời gian công tác: vào làm + mọi quyết định + thay đổi thông tin."""
	emp = frappe.get_doc("Employee", employee)
	items = []
	if emp.date_of_joining:
		items.append({"date": str(emp.date_of_joining), "kind": "join", "icon": "log-in",
			"title": "Vào làm", "detail": emp.designation or ""})
	for d in get_decisions(employee):
		items.append({"date": d["date"], "kind": d["kind"], "icon": _decision_icon(d["kind"]),
			"title": d["label"], "detail": d.get("detail", "")})
	for c in frappe.get_all("Comment",
			filters={"reference_doctype": "Employee", "reference_name": employee, "comment_type": "Info"},
			fields=["content", "creation"], order_by="creation desc"):
		ct = c.content or ""
		if ct[:1] != "[" and "→" in ct:
			items.append({"date": str(c.creation)[:10], "kind": "update", "icon": "edit-2",
				"title": "Cập nhật thông tin", "detail": ct})
	items.sort(key=lambda x: x["date"], reverse=True)
	return items


# ════════════════════════════════════════════════════════════════════
#  HỒ SƠ NV ĐẦY ĐỦ + DASHBOARD BIẾN ĐỘNG NHÂN SỰ
# ════════════════════════════════════════════════════════════════════

_PROFILE_FIELDS = [
	("custom_cccd", {"label": "CCCD/CMND", "fieldtype": "Data"}),
	("custom_mst_tncn", {"label": "Mã số thuế TNCN", "fieldtype": "Data"}),
	("custom_so_bhxh", {"label": "Số sổ BHXH", "fieldtype": "Data"}),
	("custom_hoc_van", {"label": "Học vấn (JSON)", "fieldtype": "Long Text"}),
	("custom_kinh_nghiem", {"label": "Kinh nghiệm (JSON)", "fieldtype": "Long Text"}),
	("custom_onboarding", {"label": "Onboarding checklist (JSON)", "fieldtype": "Long Text"}),
	("custom_offboarding", {"label": "Offboarding checklist (JSON)", "fieldtype": "Long Text"}),
]

_CHECKLIST_DEFAULT = {
	"onboarding": ["Ký hợp đồng lao động", "Khai báo thông tin cá nhân", "Cấp tài khoản & email",
		"Bàn giao thiết bị làm việc", "Đào tạo hội nhập", "Đăng ký BHXH/BHYT"],
	"offboarding": ["Bàn giao công việc", "Thu hồi thiết bị", "Thu hồi tài khoản & email",
		"Thanh toán lương & công nợ", "Chốt sổ BHXH", "Phỏng vấn thôi việc"],
}


@frappe.whitelist()
def get_checklist(employee, kind="onboarding"):
	"""Checklist onboarding/offboarding (seed mặc định nếu trống)."""
	field = "custom_onboarding" if kind == "onboarding" else "custom_offboarding"
	raw = frappe.db.get_value("Employee", employee, field)
	try:
		items = _json.loads(raw) if raw else []
	except Exception:
		items = []
	if not items:
		items = [{"task": t, "done": False} for t in _CHECKLIST_DEFAULT[kind]]
	return items


@frappe.whitelist()
def save_checklist_tasks(employee, kind, items):
	field = "custom_onboarding" if kind == "onboarding" else "custom_offboarding"
	data = items if isinstance(items, str) else _json.dumps(items or [], ensure_ascii=False)
	frappe.db.set_value("Employee", employee, field, data)
	frappe.db.commit()
	return {"ok": True}


@frappe.whitelist()
def setup_hr_profile():
	"""Tạo custom field hồ sơ NV (idempotent)."""
	for fn, props in _PROFILE_FIELDS:
		_ensure_custom_field("Employee", fn, props)
	frappe.clear_cache(doctype="Employee")
	return {"ok": True}


@frappe.whitelist()
def get_employee_profile(name):
	"""Hồ sơ chi tiết NV: giấy tờ, học vấn, kinh nghiệm, ngân hàng, liên hệ khẩn."""
	emp = frappe.get_doc("Employee", name)
	def arr(f):
		try:
			return _json.loads(emp.get(f) or "[]")
		except Exception:
			return []
	return {
		"cccd": emp.get("custom_cccd") or "", "mst": emp.get("custom_mst_tncn") or "",
		"so_bhxh": emp.get("custom_so_bhxh") or "",
		"bank_name": emp.get("bank_name") or "", "bank_ac_no": emp.get("bank_ac_no") or "",
		"emergency_contact": emp.get("person_to_be_contacted") or "", "emergency_phone": emp.get("emergency_phone_number") or "",
		"marital_status": emp.get("marital_status") or "", "current_address": emp.get("current_address") or "",
		"hoc_van": arr("custom_hoc_van"), "kinh_nghiem": arr("custom_kinh_nghiem"),
	}


@frappe.whitelist()
def save_employee_profile(name, cccd="", mst="", so_bhxh="", bank_name="", bank_ac_no="",
		emergency_contact="", emergency_phone="", marital_status="", current_address="", hoc_van=None, kinh_nghiem=None):
	emp = frappe.get_doc("Employee", name)
	emp.db_set("custom_cccd", cccd or None)
	emp.db_set("custom_mst_tncn", mst or None)
	emp.db_set("custom_so_bhxh", so_bhxh or None)
	emp.db_set("bank_name", bank_name or None)
	emp.db_set("bank_ac_no", bank_ac_no or None)
	emp.db_set("person_to_be_contacted", emergency_contact or None)
	emp.db_set("emergency_phone_number", emergency_phone or None)
	if marital_status:
		emp.db_set("marital_status", marital_status)
	emp.db_set("current_address", current_address or None)
	emp.db_set("custom_hoc_van", hoc_van if isinstance(hoc_van, str) else _json.dumps(hoc_van or [], ensure_ascii=False))
	emp.db_set("custom_kinh_nghiem", kinh_nghiem if isinstance(kinh_nghiem, str) else _json.dumps(kinh_nghiem or [], ensure_ascii=False))
	frappe.db.commit()
	return {"ok": True}


@frappe.whitelist()
def get_hr_movement_dashboard(year=None):
	"""Biến động nhân sự theo tháng + tỷ lệ nghỉ việc + phân bổ thâm niên."""
	year = int(year) if year else frappe.utils.getdate().year
	months = [{"m": m, "label": f"T{m}", "join": 0, "leave": 0, "promotion": 0, "transfer": 0} for m in range(1, 13)]

	def bump(key, datestr):
		if not datestr:
			return
		d = frappe.utils.getdate(datestr)
		if d.year == year:
			months[d.month - 1][key] += 1

	for e in frappe.get_all("Employee", fields=["date_of_joining"], limit_page_length=0):
		bump("join", e.date_of_joining)
	for s in frappe.get_all("Employee Separation", filters={"docstatus": 1}, fields=["boarding_begins_on"], limit_page_length=0):
		bump("leave", s.boarding_begins_on)
	for p in frappe.get_all("Employee Promotion", filters={"docstatus": 1}, fields=["promotion_date"], limit_page_length=0):
		bump("promotion", p.promotion_date)
	for t in frappe.get_all("Employee Transfer", filters={"docstatus": 1}, fields=["transfer_date"], limit_page_length=0):
		bump("transfer", t.transfer_date)

	active = frappe.db.count("Employee", {"status": "Active"})
	left_year = sum(m["leave"] for m in months)
	join_year = sum(m["join"] for m in months)
	turnover = round(left_year / active * 100, 1) if active else 0

	today = frappe.utils.getdate()
	tenure = {"<1 năm": 0, "1-3 năm": 0, "3-5 năm": 0, ">5 năm": 0}
	for e in frappe.get_all("Employee", filters={"status": "Active"}, fields=["date_of_joining"], limit_page_length=0):
		if not e.date_of_joining:
			continue
		yrs = (today - frappe.utils.getdate(e.date_of_joining)).days / 365.0
		if yrs < 1:
			tenure["<1 năm"] += 1
		elif yrs < 3:
			tenure["1-3 năm"] += 1
		elif yrs < 5:
			tenure["3-5 năm"] += 1
		else:
			tenure[">5 năm"] += 1

	return {"year": year, "months": months, "active": active, "joined": join_year,
		"left": left_year, "promotions": sum(m["promotion"] for m in months),
		"transfers": sum(m["transfer"] for m in months), "turnover": turnover, "tenure": tenure}


# ════════════════════════════════════════════════════════════════════
#  JOB OFFER & THƯ MỜI — tái dùng HRMS Job Offer + in mẫu VN
# ════════════════════════════════════════════════════════════════════

@frappe.whitelist()
def create_job_offer(applicant, designation=None, offer_date=None, salary=0,
		allowances=None, bonus=0, valid_till=None, note=""):
	"""Tạo Job Offer cho ứng viên. Khi accept → tự tạo Employee."""
	app = frappe.get_doc("Job Applicant", applicant)
	doc = frappe.new_doc("Job Offer")
	doc.job_applicant = applicant
	doc.applicant_name = app.applicant_name
	doc.applicant_email = app.get("email_id") or ""
	doc.designation = designation or app.designation or ""
	doc.company = _default_company()
	doc.offer_date = offer_date or frappe.utils.today()
	doc.status = "Awaiting Response"
	# Ensure Offer Term records exist (idempotent)
	def _ensure_term(tname):
		if not frappe.db.exists("Offer Term", tname):
			frappe.get_doc({"doctype": "Offer Term", "offer_term": tname}).insert(ignore_permissions=True)
	# Offer Terms (child table) — convert salary/allowances/bonus to rows
	_ensure_term("Lương cơ bản"); _ensure_term("Phụ cấp"); _ensure_term("Thưởng (dự kiến)"); _ensure_term("Ngày hết hạn")
	terms = [{"offer_term": "Lương cơ bản", "value": f"{int(salary or 0):,} ₫/tháng"}]
	allow = _json.loads(allowances) if isinstance(allowances, str) else (allowances or [])
	for a in allow:
		tname = a.get("ten") or "Phụ cấp"
		_ensure_term(tname)
		terms.append({"offer_term": tname, "value": f"{int(a.get('so_tien') or 0):,} ₫"})
	if float(bonus or 0) > 0:
		terms.append({"offer_term": "Thưởng (dự kiến)", "value": f"{int(float(bonus)):,} ₫"})
	if valid_till:
		terms.append({"offer_term": "Ngày hết hạn", "value": str(valid_till)})
	for t in terms:
		doc.append("offer_terms", t)
	doc.terms = (f"<b>THƯ MỜI LÀM VIỆC</b><br><br>Kính gửi Ông/Bà <b>{app.applicant_name}</b>,<br><br>"
		f"Công ty {frappe.db.get_value('Company', doc.company, 'company_name') or doc.company} trân trọng mời Ông/Bà đảm nhận vị trí <b>{doc.designation}</b> "
		f"với mức lương cơ bản <b>{int(salary or 0):,} ₫/tháng</b> cùng các phúc lợi theo chính sách Công ty."
		f"{'<br><br>Ghi chú: ' + note if note else ''}"
		f"<br><br>Chúng tôi hy vọng Ông/Bà sẽ sớm nhận lời và gia nhập đội ngũ.")
	doc.insert(ignore_permissions=True)
	doc.submit()
	_applicant_log(applicant, "offer_created", f"Job Offer #{doc.name} — {doc.designation}")
	return {"ok": True, "name": doc.name, "status": doc.status}


def _applicant_log(applicant, action, detail=""):
	"""Ghi log lên ứng viên (tái dùng pattern _log ở đầu file)."""
	try:
		frappe.get_doc("Job Applicant", applicant).add_comment("Info",
			f"[{frappe.utils.today()}] {action.upper()}: {detail}")
	except Exception:
		pass


@frappe.whitelist()
def get_job_offers(applicant):
	"""Danh sách Job Offer của 1 ứng viên."""
	offers = frappe.get_all("Job Offer",
		filters={"job_applicant": applicant},
		fields=["name", "offer_date", "designation", "status", "terms"],
		order_by="creation desc", limit_page_length=20)
	for o in offers:
		o["offer_terms"] = [{"offer_term": t.offer_term, "value": t.value}
			for t in frappe.get_doc("Job Offer", o["name"]).offer_terms]
	return offers


@frappe.whitelist()
def accept_job_offer(name, employee_name=None, gender="Male", date_of_birth=None, cell_number=None):
	"""Ứng viên chấp nhận Job Offer → tạo Employee (tái dùng convert_to_employee pattern)."""
	offer = frappe.get_doc("Job Offer", name)
	if offer.status != "Awaiting Response":
		frappe.throw("Offer này không còn ở trạng thái chờ phản hồi")
	offer.status = "Accepted"
	offer.save()
	app = frappe.get_doc("Job Applicant", offer.job_applicant)
	# Tự tạo Employee
	full = employee_name or app.applicant_name
	parts = full.strip().split(" ", 1)
	emp = frappe.get_doc({
		"doctype": "Employee", "first_name": parts[0], "last_name": parts[1] if len(parts) > 1 else "",
		"gender": gender, "date_of_birth": date_of_birth or "1990-01-01",
		"date_of_joining": frappe.utils.today(), "designation": offer.designation,
		"company": offer.company, "cell_number": cell_number or app.get("phone_number") or "",
		"personal_email": offer.applicant_email or "",
	})
	emp.insert(ignore_permissions=True)
	_applicant_log(offer.job_applicant, "offer_accepted", f"Offer #{offer.name} → Employee {emp.name}")
	return {"ok": True, "offer": offer.name, "employee": emp.name, "employee_name": emp.employee_name}


@frappe.whitelist()
def reject_job_offer(name, reason=""):
	offer = frappe.get_doc("Job Offer", name)
	offer.status = "Rejected"
	offer.save()
	if reason:
		offer.add_comment("Comment", f"Lý do từ chối: {reason}")
	_applicant_log(offer.job_applicant, "offer_rejected", f"Offer #{offer.name}: {reason}")
	return {"ok": True, "name": name}


_APPOINTMENT_HTML = """<html><head><meta charset="utf-8"><title>Thư mời làm việc</title>
<style>
body{font-family:'Times New Roman',serif;font-size:15px;max-width:720px;margin:24px auto;line-height:1.6;color:#000;padding:0 16px}
.row{display:flex;justify-content:space-between;text-align:center;gap:16px}.row>div{flex:1}
.center{text-align:center}.b{font-weight:bold}.mt{margin-top:16px}.sign{margin-top:40px;align-items:flex-start}
hr.s{width:150px;border:none;border-top:1px solid #000;margin:5px auto}
.title{font-size:20px;letter-spacing:1px}.tbl{width:100%;border-collapse:collapse;margin:16px 0}
.tbl td,.tbl th{border:1px solid #ccc;padding:6px 10px;font-size:14px;text-align:left}
.toolbar{text-align:center;margin-top:28px}
button{font-family:sans-serif;padding:8px 18px;border:none;background:#2563eb;color:#fff;border-radius:6px;cursor:pointer}
@media print{.toolbar{display:none}}
</style></head><body>
<div class="row">
<div><div class="b">__CNAME__</div><div>Số: ......./TL-__SO__</div></div>
<div><div class="b">CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM</div><div class="b">Độc lập - Tự do - Hạnh phúc</div><hr class="s"/><div><i>__DATE__</i></div></div>
</div>
<div class="center mt"><div class="b title">THƯ MỜI LÀM VIỆC</div></div>
<div class="mt">Kính gửi: Ông/Bà <b>__EMP__</b></div>
<div class="mt">Công ty <b>__CNAME__</b> trân trọng mời Ông/Bà đến làm việc tại Công ty với các điều khoản sau:</div>
<table class="tbl">
<tr><td style="width:30%"><b>Vị trí</b></td><td>__DESIGNATION__</td></tr>
<tr><td><b>Ngày làm việc đầu tiên</b></td><td>__JOIN__</td></tr>
__TERM_ROWS__
</table>
<div class="mt">Nếu Ông/Bà đồng ý, vui lòng ký xác nhận và gửi lại bản scan trước ngày <b>__VALID__</b>.</div>
<div class="mt">Chúng tôi rất mong được chào đón Ông/Bà gia nhập đội ngũ.</div>
<div class="row sign">
<div><i>Đã đọc và đồng ý</i><br/>(Ký, ghi rõ họ tên)</div>
<div style="text-align:right"><div class="b">GIÁM ĐỐC</div><div><i>(Ký, ghi rõ họ tên, đóng dấu)</i></div></div>
</div>
<div class="toolbar"><button onclick="window.print()">🖨 In / Lưu PDF</button></div>
</body></html>"""


@frappe.whitelist()
def print_appointment_letter(name):
	"""HTML thư mời làm việc mẫu VN để in."""
	offer = frappe.get_doc("Job Offer", name)
	company = offer.company or _default_company()
	cname = (frappe.db.get_value("Company", company, "company_name") or company or "CÔNG TY").upper()
	html = (_APPOINTMENT_HTML
		.replace("__CNAME__", cname).replace("__SO__", offer.name[-8:] if len(offer.name) >= 8 else offer.name)
		.replace("__DATE__", _vn_date(offer.offer_date))
		.replace("__EMP__", offer.applicant_name).replace("__DESIGNATION__", offer.designation)
		.replace("__JOIN__", _vn_date(offer.offer_date)).replace("__VALID__", _vn_date(offer.offer_date)))
	trows = ""
	for t in offer.offer_terms:
		trows += f'<tr><td><b>{t.offer_term}</b></td><td>{t.value}</td></tr>\n'
	html = html.replace("__TERM_ROWS__", trows)
	return {"html": html, "name": offer.name, "applicant_name": offer.applicant_name}


# ════════════════════════════════════════════════════════════════════
#  HR SETUP — quản lý master data (phòng ban / chức vụ / loại NP / HĐ / chi phí)
# ════════════════════════════════════════════════════════════════════

# key → (doctype, field tên, nhãn tiếng Việt)
_MASTER_MAP = {
	"department": ("Department", "department_name", "Phòng ban"),
	"designation": ("Designation", "designation_name", "Chức vụ"),
	"leave_type": ("Leave Type", "leave_type_name", "Loại nghỉ phép"),
	"employment_type": ("Employment Type", "employee_type_name", "Loại hợp đồng"),
	"expense_claim_type": ("Expense Claim Type", "expense_type", "Loại chi phí"),
}


@frappe.whitelist()
def get_setup_data():
	"""Lấy toàn bộ master data của HR Setup."""
	out = {}
	for key, (doctype, field, label) in _MASTER_MAP.items():
		if doctype == "Department":
			items = frappe.get_all("Department", filters={"is_group": 0}, pluck="name", order_by="name")
		else:
			items = frappe.get_all(doctype, pluck="name", order_by="name", limit_page_length=0)
		out[key] = {"label": label, "doctype": doctype, "items": items, "count": len(items)}
	return out


@frappe.whitelist()
def create_master(key, name):
	"""Tạo bản ghi master mới theo key (department/designation/leave_type/...)."""
	if key not in _MASTER_MAP:
		frappe.throw("Loại master không hợp lệ")
	if not name or not name.strip():
		frappe.throw("Vui lòng nhập tên")
	doctype, field, label = _MASTER_MAP[key]
	name = name.strip()

	doc = {"doctype": doctype, field: name}
	if doctype == "Department":
		doc["company"] = _default_company()
	if frappe.db.exists(doctype, name):
		frappe.throw(f"{label} '{name}' đã tồn tại")
	d = frappe.get_doc(doc)
	d.insert(ignore_permissions=True)
	return {"ok": True, "name": d.name, "key": key}


# ════════════════════════════════════════════════════════════════════
#  NGHỈ PHÉP — tạo đơn + duyệt/từ chối (reuse Leave Application)
# ════════════════════════════════════════════════════════════════════

@frappe.whitelist()
def get_leave_types():
	"""Danh sách loại nghỉ phép."""
	return frappe.get_all("Leave Type", pluck="name", limit=50, order_by="name")


def _ensure_leave_allocation(employee, leave_type, on_date, company):
	"""Đảm bảo có phân bổ nghỉ phép (Leave Allocation) bao trùm ngày — tự cấp 12 ngày/năm nếu chưa, prorate theo ngày vào làm."""
	if frappe.db.get_value("Leave Type", leave_type, "is_lwp"):
		return  # Nghỉ không lương không cần phân bổ
	on = frappe.utils.getdate(on_date)
	year = str(on.year)
	covered = frappe.db.get_value("Leave Allocation", {
		"employee": employee, "leave_type": leave_type, "docstatus": 1,
		"from_date": ["<=", on], "to_date": [">=", on],
	}, "name")
	if covered:
		return covered
	# Prorate: nếu join sau đầu năm → tỉ lệ theo số tháng còn lại
	doj = frappe.db.get_value("Employee", employee, "date_of_joining")
	start = on.replace(month=1, day=1)
	if doj and frappe.utils.getdate(doj) > start:
		start = frappe.utils.getdate(doj)
	months = max(1, 12 - start.month + 1)
	days = max(1, round(12 * months / 12))
	la = frappe.get_doc({
		"doctype": "Leave Allocation", "employee": employee, "company": company,
		"leave_type": leave_type, "from_date": start, "to_date": f"{year}-12-31",
		"new_leaves_allocated": days,
	})
	la.insert(ignore_permissions=True)
	la.submit()
	return la.name


def _leave_balance(employee, leave_type, year=None):
	"""Số ngày phép còn lại = allocated - approved."""
	import calendar as _cal
	today = frappe.utils.getdate()
	y = str(year or today.year)
	alloc = frappe.get_all("Leave Allocation", filters={
		"employee": employee, "leave_type": leave_type, "docstatus": 1,
		"from_date": ["<=", today], "to_date": [">=", today],
	}, fields=["total_leaves_allocated", "new_leaves_allocated"])
	allocated = sum(a.get("total_leaves_allocated") or a.get("new_leaves_allocated") or 0 for a in alloc)
	used_days = frappe.db.sql("""
		SELECT IFNULL(SUM(total_leave_days), 0) FROM `tabLeave Application`
		WHERE employee=%s AND leave_type=%s AND status='Approved'
		AND from_date >= %s AND to_date <= %s
	""", (employee, leave_type, f"{y}-01-01", f"{y}-12-31"))[0][0] or 0
	return {"leave_type": leave_type, "allocated": allocated, "used": round(float(used_days), 1), "remaining": round(allocated - float(used_days), 1), "year": y}


@frappe.whitelist()
def get_leave_balance(employee, year=None):
	"""Số dư ngày phép các loại của nhân viên (tự cấp phân bổ nếu thiếu)."""
	company = frappe.db.get_value("Employee", employee, "company") or _default_company()
	today = frappe.utils.getdate()
	y = str(year or today.year)
	result = []
	for lt in frappe.get_all("Leave Type", pluck="name", order_by="name"):
		if frappe.db.get_value("Leave Type", lt, "is_lwp"):
			continue
		# ensure allocation exists for this year
		_ensure_leave_allocation(employee, lt, f"{y}-01-01", company)
		result.append(_leave_balance(employee, lt, int(y)))
	return result


@frappe.whitelist()
def auto_allocate_all(year=None):
	"""Phân bổ 12 ngày phép năm cho mọi NV Active chưa có phân bổ."""
	from datetime import date as _date
	today = frappe.utils.getdate()
	y = str(year or today.year)
	company = _default_company()
	emps = frappe.get_all("Employee", filters={"status": "Active"}, fields=["name", "employee_name", "date_of_joining"], limit_page_length=0)
	results = []
	for e in emps:
		try:
			la = _ensure_leave_allocation(e["name"], "Nghỉ phép năm", f"{y}-01-01", company)
			if la:
				b = _leave_balance(e["name"], "Nghỉ phép năm", int(y))
				results.append({"employee": e["name"], "name": e["employee_name"], "allocated": b["allocated"], "name_ref": la[:20] if la else ""})
		except Exception as ex:
			results.append({"employee": e["name"], "name": e["employee_name"], "error": str(ex)[:120]})
	return {"year": y, "results": results, "count": len([r for r in results if not r.get("error")])}


@frappe.whitelist()
def set_leave_balance(employee, leave_type, days, year=None):
	"""Ghi đè số ngày phép được cấp (tạo mới hoặc cập nhật phân bổ hiện tại)."""
	today = frappe.utils.getdate()
	y = str(year or today.year)
	company = frappe.db.get_value("Employee", employee, "company") or _default_company()
	existing = frappe.db.get_value("Leave Allocation", {
		"employee": employee, "leave_type": leave_type, "docstatus": 1,
		"from_date": ["<=", f"{y}-01-01"], "to_date": [">=", f"{y}-12-31"],
	}, "name")
	if existing:
		doc = frappe.get_doc("Leave Allocation", existing)
		doc.cancel()
		frappe.delete_doc("Leave Allocation", existing, ignore_permissions=True)
	doj = frappe.db.get_value("Employee", employee, "date_of_joining")
	start = frappe.utils.getdate(f"{y}-01-01")
	if doj and frappe.utils.getdate(doj) > start:
		start = frappe.utils.getdate(doj)
	la = frappe.get_doc({
		"doctype": "Leave Allocation", "employee": employee, "company": company,
		"leave_type": leave_type, "from_date": start, "to_date": f"{y}-12-31",
		"new_leaves_allocated": days,
	})
	la.insert(ignore_permissions=True)
	la.submit()
	frappe.db.commit()
	return _leave_balance(employee, leave_type, int(y))


@frappe.whitelist()
def get_all_leave_balances(search="", department=None, page=1, page_length=50):
	"""Bảng tổng số dư phép toàn NV (có search + filter + phân trang)."""
	from collections import defaultdict
	import calendar as _cal
	today = frappe.utils.getdate()
	y = str(today.year)
	company = _default_company()
	filters = {"status": "Active"}
	if department:
		filters["department"] = department
	or_filters = None
	if search:
		or_filters = [["employee_name", "like", f"%{search}%"], ["name", "like", f"%{search}%"]]
	emps = frappe.get_all("Employee", filters=filters, or_filters=or_filters,
		fields=["name", "employee_name", "department", "designation"],
		order_by="employee_name asc", limit_page_length=0)
	leave_types = [lt for lt in frappe.get_all("Leave Type", pluck="name", order_by="name") if not frappe.db.get_value("Leave Type", lt, "is_lwp")]
	total = len(emps)
	page = int(page); page_length = int(page_length)
	emps_page = emps[(page - 1) * page_length : page * page_length]
	rows = []
	for e in emps_page:
		row = {"name": e["name"], "employee_name": e["employee_name"], "department": e.get("department") or "", "designation": e.get("designation") or ""}
		for lt in leave_types:
			_ensure_leave_allocation(e["name"], lt, f"{y}-01-01", company)
			b = _leave_balance(e["name"], lt, int(y))
			row[f"bal_{lt}"] = b["remaining"]
			row[f"used_{lt}"] = b["used"]
			row[f"alloc_{lt}"] = b["allocated"]
		rows.append(row)
	return {
		"data": rows, "leave_types": leave_types, "total": total,
		"page": page, "page_length": page_length,
		"pages": max(1, (total + page_length - 1) // page_length),
		"has_more": page * page_length < total,
	}


@frappe.whitelist()
def create_leave_application(employee, leave_type, from_date, to_date, reason=""):
	"""Tạo đơn nghỉ phép (trạng thái Open chờ duyệt). Tự cấp phân bổ nếu chưa có."""
	if not frappe.db.exists("Employee", employee):
		frappe.throw("Không tìm thấy nhân viên")
	if frappe.utils.getdate(to_date) < frappe.utils.getdate(from_date):
		frappe.throw("Ngày kết thúc phải sau ngày bắt đầu")
	company = frappe.db.get_value("Employee", employee, "company") or _default_company()
	_ensure_leave_allocation(employee, leave_type, from_date, company)
	doc = frappe.get_doc({
		"doctype": "Leave Application",
		"employee": employee,
		"leave_type": leave_type,
		"company": company,
		"from_date": from_date,
		"to_date": to_date,
		"posting_date": frappe.utils.today(),
		"description": reason or "",
		"status": "Open",
	})
	doc.insert(ignore_permissions=True)
	return {"ok": True, "name": doc.name, "days": doc.total_leave_days}


@frappe.whitelist()
def approve_leave(name, approve=1, comment=""):
	"""Duyệt / từ chối đơn nghỉ phép (đổi status, không submit để tránh vướng số dư)."""
	approve = str(approve) in ("1", "true", "True")
	status = "Approved" if approve else "Rejected"
	frappe.db.set_value("Leave Application", name, "status", status)
	if comment:
		frappe.get_doc("Leave Application", name).add_comment("Comment", ("✅ Duyệt: " if approve else "❌ Từ chối: ") + comment)
	return {"ok": True, "name": name, "status": status}


@frappe.whitelist()
def get_leave_applications(employee=None, status=None, limit=100):
	"""Danh sách đơn nghỉ phép."""
	filters = {}
	if employee:
		filters["employee"] = employee
	if status:
		filters["status"] = status
	rows = frappe.get_all(
		"Leave Application", filters=filters,
		fields=[
			"name", "employee", "employee_name", "leave_type",
			"from_date", "to_date", "total_leave_days", "status", "description",
		],
		order_by="from_date desc", limit_page_length=int(limit),
	)
	return rows


@frappe.whitelist()
def get_leave_dashboard():
	"""Tổng quan nghỉ phép — đơn theo trạng thái + ngày nghỉ theo loại (năm hiện tại)."""
	from collections import Counter

	year = frappe.utils.today()[:4]
	rows = frappe.get_all(
		"Leave Application",
		filters={"from_date": [">=", f"{year}-01-01"]},
		fields=["status", "leave_type", "total_leave_days"], limit_page_length=0,
	)
	by_status = Counter(r["status"] or "Open" for r in rows)
	by_type = Counter()
	for r in rows:
		if r["status"] == "Approved":
			by_type[r["leave_type"]] += (r["total_leave_days"] or 0)
	return {
		"total": len(rows),
		"pending": by_status.get("Open", 0),
		"approved": by_status.get("Approved", 0),
		"rejected": by_status.get("Rejected", 0),
		"days_approved": round(sum(by_type.values()), 1),
		"by_type": dict(by_type),
	}


@frappe.whitelist()
@frappe.whitelist()
def close_job_opening(name):
	"""Dong tin tuyen dung."""
	frappe.db.set_value('Job Opening', name, 'status', 'Closed')
	return {'ok': True, 'name': name}


@frappe.whitelist()
def get_attendance_monthly_grid(month=None, year=None, department=None):
	"""Bang cong thang dang luoi."""
	import calendar as _cal
	from datetime import date as _date, timedelta
	from collections import defaultdict
	today = frappe.utils.getdate()
	year = int(year) if year else today.year
	month = int(month) if month else today.month
	last = _cal.monthrange(year, month)[1]
	start = _date(year, month, 1)
	end = _date(year, month, last)
	filters = {'status': 'Active'}
	if department: filters['department'] = department
	emps = frappe.get_all('Employee', filters=filters, fields=['name','employee_name','department','designation'], order_by='employee_name asc', limit_page_length=0)
	att_map = {}
	for a in frappe.get_all('Attendance', filters={'docstatus':1,'attendance_date':['between',[str(start),str(end)]]}, fields=['employee','attendance_date','status','late_entry','working_hours'], limit_page_length=0):
		att_map[(a['employee'], str(a['attendance_date']))] = a
	cin_map = defaultdict(list)
	for c in frappe.get_all('Employee Checkin', filters={'time':['>=',str(start)+' 00:00:00'],'time':['<=',str(end)+' 23:59:59']}, fields=['employee','time','log_type'], order_by='time asc', limit_page_length=0):
		cin_map[(c['employee'], str(c['time'])[:10])].append(str(c['time'])[11:16])
	days = [_date(year, month, d) for d in range(1, last+1)]
	rows = []
	for e in emps:
		row = {'name':e['name'],'employee_name':e['employee_name'],'department':e.get('department') or '','designation':e.get('designation') or ''}
		p, ab, lt, hr = 0, 0, 0, 0.0
		for d in days:
			ds = str(d)
			a = att_map.get((e['name'], ds))
			ci = cin_map.get((e['name'], ds), [])
			row['a_%d'%d.day] = {'s': a['status'] if a else '', 'l': 1 if a and a.get('late_entry') else 0, 'h': a.get('working_hours',0) if a else 0, 'in': ci[0] if ci else '', 'out': ci[-1] if len(ci)>1 else ''}
			if a:
				if a['status'] in ('Present','Work From Home','Half Day'): p += 1
				elif a['status'] == 'Absent': ab += 1
				if a.get('late_entry'): lt += 1
				hr += a.get('working_hours') or 0
		row['present'] = p; row['absent'] = ab; row['late'] = lt; row['total_hours'] = round(hr, 1)
		rows.append(row)
	return {'data': rows, 'days': [str(d.day) for d in days], 'month': '%02d/%d'%(month,year), 'total': len(emps)}


@frappe.whitelist()
def export_attendance_csv(month=None, year=None, department=None):
	"""Xuat bang cong CSV."""
	import csv, io
	grid = get_attendance_monthly_grid(month=month, year=year, department=department)
	buf = io.StringIO()
	w = csv.writer(buf)
	w.writerow(['Ma NV','Ho ten','Phong ban','Chuc vu'] + grid['days'] + ['Di lam','Vang','Di muon','Gio'])
	for r in grid['data']:
		row = [r['name'], r['employee_name'], r['department'], r.get('designation','')]
		for d in grid['days']:
			c = r.get('a_'+d, {})
			row.append(c.get('s','') if isinstance(c,dict) else '')
		row.extend([r['present'], r['absent'], r['late'], r['total_hours']])
		w.writerow(row)
	return {'filename': 'bang_cong_%s.csv'%grid['month'].replace('/','_'), 'content': buf.getvalue(), 'count': len(grid['data'])}


@frappe.whitelist()
def get_ai_suggested_questions(applicant):
	"""AI gợi ý câu hỏi phỏng vấn dựa trên CV và vị trí ứng tuyển."""
	import os as _os, json as _json, requests as _http, re as _re
	api_key = _os.environ.get("DEEPSEEK_API_KEY", "")
	if not api_key:
		return {"error": "Chưa cấu hình DEEPSEEK_API_KEY"}
		
	app_detail = get_applicant_detail(applicant)
	cv_data = app_detail.get("cv_data") or {}
	
	applicant_name = app_detail.get("applicant_name") or "Ứng viên"
	job_title = app_detail.get("job_opening_title") or app_detail.get("job_title") or "Vị trí tuyển"
	
	cv_summary = cv_data.get("summary") or ""
	cv_strengths = ", ".join(cv_data.get("strengths") or [])
	cv_gaps = ", ".join(cv_data.get("gaps") or [])
	cv_skills = ", ".join(cv_data.get("skills") or [])
	
	prompt = f"""Ban la chuyen gia HR va phong van vien chuyên nghiệp. Hay goi y 5 cau hoi phong van sac ben danh cho ung vien "{applicant_name}" ung tuyen vao vi tri "{job_title}".
	
NOI DUNG CV:
- Tom tat: {cv_summary}
- Ky nang: {cv_skills}
- Diem manh: {cv_strengths}
- Lỗ hổng/Diem can bo sung: {cv_gaps}

QUY TAC:
- Cac cau hoi phai sac ben, thuc te, nham kiem chung kinh nghiem trong CV va lam ro cac diem can bo sung (gaps).
- Tra ve JSON danh sach cac cau hoi kem muc dich hoi bang TIENG VIET CO DAU.
- Khong tra ve markdown, khong giai thich ngoai JSON.

JSON FORMAT:
[
  {{"question": "Noi dung cau hoi 1", "purpose": "Muc dich hoi (VD: Kiem tra kha nang AWS, lam ro ly do nghi viec...)"}},
  ...
]"""

	try:
		resp = _http.post(
			"https://api.deepseek.com/chat/completions",
			headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
			json={
				"model": "deepseek-chat",
				"messages": [
					{"role": "system", "content": "Ban la chuyen gia HR. Luon tra JSON thuan, khong markdown."},
					{"role": "user", "content": prompt},
				],
				"temperature": 0.5,
				"max_tokens": 1000,
			},
			timeout=30,
		)
		resp.raise_for_status()
		raw = resp.json()["choices"][0]["message"]["content"].strip()
		if raw.startswith("```"):
			raw = raw.split("\n", 1)[-1]
			if raw.endswith("```"): raw = raw[:-3]
			raw = raw.strip()
			if raw.startswith("json"): raw = raw[4:].strip()
		return _json.loads(raw)
	except Exception as e:
		return {"error": f"Lỗi AI: {str(e)[:200]}"}


@frappe.whitelist()
def chat_recruitment_helper(message, history=None):
	"""Bóng chat trợ lý AI hỏi đáp hướng dẫn nghiệp vụ Tuyển dụng."""
	import os as _os, json as _json, requests as _http
	api_key = _os.environ.get("DEEPSEEK_API_KEY", "")
	if not api_key:
		return {"response": "Xin lỗi, hệ thống chưa được cấu hình DEEPSEEK_API_KEY để trò chuyện."}
		
	chat_history = []
	if history:
		try:
			chat_history = _json.loads(history) if isinstance(history, str) else history
		except:
			pass
			
	messages = [
		{"role": "system", "content": "Bạn là Trợ lý Tuyển dụng AI (AI Recruitment Assistant) của hệ thống GPC ERP. Hãy trả lời ngắn gọn, thân thiện, sử dụng tiếng Việt có dấu chuẩn, tập trung hướng dẫn người dùng các nghiệp vụ tuyển dụng như: tạo tin tuyển dụng, tải CV và parse bằng AI, lọc danh sách phỏng vấn, lên lịch phỏng vấn, tạo hồ sơ nhân sự, xem biểu đồ phễu tuyển dụng trên dashboard, xuất danh sách CSV. Bạn chỉ trả lời các câu hỏi liên quan đến tuyển dụng và quản lý nhân sự GPC."}
	]
	
	for h in chat_history:
		messages.append({"role": "user" if h.get("sender") == "user" else "assistant", "content": h.get("text", "")})
		
	messages.append({"role": "user", "content": message})
	
	try:
		resp = _http.post(
			"https://api.deepseek.com/chat/completions",
			headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
			json={
				"model": "deepseek-chat",
				"messages": messages,
				"temperature": 0.4,
				"max_tokens": 1000,
			},
			timeout=30,
		)
		resp.raise_for_status()
		ai_response = resp.json()["choices"][0]["message"]["content"].strip()
		return {"response": ai_response}
	except Exception as e:
		return {"response": f"Xin lỗi, có lỗi kết nối trợ lý AI: {str(e)[:150]}"}


@frappe.whitelist()
def get_current_user():
	"""Lấy thông tin người dùng đăng nhập hiện tại."""
	user = frappe.session.user
	if not user or user == "Guest":
		return {
			"email": "guest@example.com",
			"fullName": "Guest User",
			"image": None
		}
	try:
		user_doc = frappe.get_doc("User", user)
		return {
			"email": user_doc.email,
			"fullName": user_doc.full_name or user_doc.name,
			"image": user_doc.user_image
		}
	except Exception:
		return {
			"email": user,
			"fullName": user,
			"image": None
		}


@frappe.whitelist()
def send_offer_letter(applicant, subject, content, email_id=None, attach_pdf=False, contract_type="thu_viec", include_onboarding=False):
	"""Gửi email thư mời nhận việc cho ứng viên (hỗ trợ đính kèm PDF hợp đồng và link onboarding)."""
	_ensure_applicant_fields()
	_ensure_onboarding_fields()
	app = frappe.get_doc("Job Applicant", applicant)
	recipient = email_id or app.email_id
	if not recipient:
		frappe.throw("Ứng viên không có địa chỉ email")

	email_content = content

	# Thêm link onboarding nếu được yêu cầu
	onboarding_url = None
	if include_onboarding and frappe.utils.cstr(include_onboarding) in ("1", "true", "True"):
		token = _get_or_create_onboarding_token(app)
		site_url = frappe.utils.get_url()
		onboarding_url = f"{site_url}/hr_app/onboarding?token={token}"
		email_content += f"\n\n---\n📋 Vui lòng điền thông tin hồ sơ tại đây (trước ngày nhận việc):\n{onboarding_url}"

	attachments = []
	if attach_pdf and frappe.utils.cstr(attach_pdf) in ("1", "true", "True"):
		try:
			pdf_bytes = _generate_contract_pdf(app, contract_type)
			attachments = [{
				"fname": f"hop_dong_{contract_type}_{app.applicant_name or app.name}.pdf",
				"fcontent": pdf_bytes
			}]
		except Exception as e:
			frappe.log_error(f"Lỗi tạo PDF hợp đồng: {e}", "generate_contract_pdf")

	frappe.sendmail(
		recipients=recipient,
		subject=subject,
		content=email_content,
		attachments=attachments if attachments else None,
		now=True
	)

	_log("Job Applicant", applicant, "send_offer", f"Thư mời nhận việc: {subject}")

	note_extra = f"\n  PDF: {contract_type}" if attachments else ""
	note_extra += f"\n  Onboarding: {onboarding_url}" if onboarding_url else ""
	app.notes = ((app.notes or "") + f"\n[OFFER_LETTER] Gửi ngày {frappe.utils.today()}:{note_extra}\n{content}").strip()
	app.save(ignore_permissions=True)

	return {"ok": True, "onboarding_url": onboarding_url}


# ─────────────────────────────────────────────────────────
#  OFFER LETTER TEMPLATES
# ─────────────────────────────────────────────────────────

OFFER_TEMPLATES = {
	"chung": {
		"label": "Mẫu chung",
		"subject": "[{company}] Thư mời nhận việc - Vị trí {designation}",
		"content": """Kính gửi {title} {name},

Thay mặt Ban lãnh đạo Công ty {company}, chúng tôi trân trọng kính mời {title} tham gia làm việc tại công ty với thông tin như sau:

• Vị trí công việc  : {designation}
• Phòng ban          : {department}
• Mức lương đề nghị : {salary}
• Ngày bắt đầu      : [Điền ngày bắt đầu]
• Địa điểm làm việc : [Điền địa điểm]

Vui lòng xác nhận nhận lời mời này trước ngày [Điền hạn xác nhận] bằng cách trả lời email này.

Trân trọng,
Phòng Nhân sự — {company}"""
	},
	"ky_thuat": {
		"label": "Kỹ thuật / IT",
		"subject": "[{company}] Thư mời nhận việc — {designation} (Kỹ thuật)",
		"content": """Kính gửi {title} {name},

Chúng tôi rất vui được thông báo rằng {title} đã vượt qua thành công quy trình tuyển chọn của chúng tôi.

Chúng tôi trân trọng mời {title} tham gia đội ngũ Kỹ thuật của Công ty {company}:

• Vị trí             : {designation} — Bộ phận Kỹ thuật
• Phòng ban          : {department}
• Mức lương cứng     : {salary}/tháng
• Thưởng hiệu suất   : Theo KPI hàng quý
• Ngày bắt đầu      : [Điền ngày bắt đầu]

Môi trường làm việc: Agile/Scrum, remote một phần, trang bị laptop theo yêu cầu.

Xác nhận nhận lời trước: [Điền hạn xác nhận]

Trân trọng,
Phòng Nhân sự — {company}"""
	},
	"kinh_doanh": {
		"label": "Kinh doanh / Sales",
		"subject": "[{company}] Thư mời nhận việc — {designation} (Kinh doanh)",
		"content": """Kính gửi {title} {name},

Sau quá trình đánh giá kỹ lưỡng, chúng tôi rất vui được mời {title} gia nhập đội ngũ Kinh doanh năng động của Công ty {company}.

• Vị trí             : {designation} — Phòng Kinh doanh
• Phòng ban          : {department}
• Lương cơ bản       : {salary}/tháng
• Hoa hồng doanh số  : Theo bảng lương thương mại (trao đổi thêm khi nhận việc)
• Chính sách phúc lợi: BHXH/BHYT/BHTN đầy đủ, phụ cấp công tác, điện thoại
• Ngày bắt đầu      : [Điền ngày bắt đầu]

Xác nhận nhận lời trước: [Điền hạn xác nhận]

Trân trọng,
Phòng Nhân sự — {company}"""
	},
	"ke_toan": {
		"label": "Kế toán / Tài chính",
		"subject": "[{company}] Thư mời nhận việc — {designation} (Kế toán)",
		"content": """Kính gửi {title} {name},

Công ty {company} trân trọng kính mời {title} đảm nhiệm vị trí {designation} tại Phòng Tài chính – Kế toán.

• Vị trí             : {designation}
• Phòng ban          : {department}
• Mức lương          : {salary}/tháng (cộng thêm thưởng cuối năm theo quy định)
• Giờ làm việc       : Thứ 2 – Thứ 6, 08:00 – 17:30
• Ngày bắt đầu      : [Điền ngày bắt đầu]
• Hồ sơ cần mang    : CCCD, bằng cấp, giấy khám sức khỏe (6 tháng gần nhất)

Xác nhận nhận lời trước: [Điền hạn xác nhận]

Trân trọng,
Phòng Nhân sự — {company}"""
	},
}

CONTRACT_TEMPLATES = {
	"thu_viec": {
		"label": "Thử việc 2 tháng",
		"content": """CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM
Độc lập - Tự do - Hạnh phúc
---
HỢP ĐỒNG THỬ VIỆC

Chúng tôi gồm:
BÊN A: {company}
- Đại diện: Ban Giám đốc
- Chức vụ: Đại diện ủy quyền

BÊN B: {name}
- Vị trí: {designation}
- Phòng ban: {department}
- Email: {email}

Hai bên thống nhất thỏa thuận các điều khoản sau:
Điều 1: Thời gian thử việc là 02 tháng, bắt đầu từ ngày [Điền ngày bắt đầu] đến ngày [Điền ngày kết thúc].
Điều 2: Địa điểm làm việc tại văn phòng công ty. Vị trí công việc là {designation}.
Điều 3: Mức lương thử việc là {salary}/tháng (bằng 85% mức lương chính thức hoặc thỏa thuận). Hình thức thanh toán chuyển khoản ngân hàng.
Điều 4: Thời gian làm việc 8 giờ/ngày, từ thứ Hai đến thứ Sáu hàng tuần.
Điều 5: Hai bên cam kết thực hiện đúng các điều khoản thử việc và quy định lao động hiện hành."""
	},
	"thu_viec_1": {
		"label": "Thử việc 1 tháng",
		"content": """CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM
Độc lập - Tự do - Hạnh phúc
---
HỢP ĐỒNG THỬ VIỆC

Chúng tôi gồm:
BÊN A: {company}
- Đại diện: Ban Giám đốc
- Chức vụ: Đại diện ủy quyền

BÊN B: {name}
- Vị trí: {designation}
- Phòng ban: {department}
- Email: {email}

Hai bên thống nhất thỏa thuận các điều khoản sau:
Điều 1: Thời gian thử việc là 01 tháng, bắt đầu từ ngày [Điền ngày bắt đầu] đến ngày [Điền ngày kết thúc].
Điều 2: Địa điểm làm việc tại văn phòng công ty. Vị trí công việc là {designation}.
Điều 3: Mức lương thử việc là {salary}/tháng. Hình thức thanh toán chuyển khoản ngân hàng.
Điều 4: Thời gian làm việc 8 giờ/ngày, từ thứ Hai đến thứ Sáu hàng tuần.
Điều 5: Hai bên cam kết thực hiện đúng các điều khoản thử việc và quy định lao động hiện hành."""
	},
	"toan_thoi_gian": {
		"label": "Hợp đồng toàn thời gian",
		"content": """CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM
Độc lập - Tự do - Hạnh phúc
---
HỢP ĐỒNG LAO ĐỘNG

Chúng tôi gồm:
BÊN A: {company}
- Đại diện: Ban Giám đốc
- Chức vụ: Đại diện ủy quyền

BÊN B: {name}
- Vị trí: {designation}
- Phòng ban: {department}
- Email: {email}

Hai bên thống nhất thỏa thuận các điều khoản sau:
Điều 1: Loại hợp đồng lao động không xác định thời hạn. Ngày bắt đầu làm việc từ ngày [Điền ngày].
Điều 2: Công việc chính theo mô tả công việc của vị trí {designation}.
Điều 3: Mức lương chính thức là {salary}/tháng. Đóng BHXH, BHYT theo quy định pháp luật.
Điều 4: Thời gian làm việc 8 giờ/ngày, từ thứ Hai đến thứ Sáu hàng tuần.
Điều 5: Quyền lợi và nghĩa vụ khác của người lao động thực hiện theo quy chế công ty và Bộ luật Lao động."""
	}
}


@frappe.whitelist()
def get_offer_templates():
	"""Trả về danh sách mẫu thư mời nhận việc."""
	return [{"key": k, "label": v["label"]} for k, v in OFFER_TEMPLATES.items()]


@frappe.whitelist()
def get_offer_template(template_key, applicant):
	"""Render mẫu thư mời với thông tin ứng viên thực tế."""
	_ensure_applicant_fields()
	tpl = OFFER_TEMPLATES.get(template_key)
	if not tpl:
		frappe.throw(f"Mẫu thư không tồn tại: {template_key}")

	app = frappe.get_doc("Job Applicant", applicant)
	salary_val = getattr(app, "custom_offered_salary", 0) or 0

	def fmt_money(v):
		try:
			return f"{int(float(v)):,} VNĐ".replace(",", ".")
		except Exception:
			return str(v)

	ctx = {
		"name": app.get("applicant_name") or "",
		"title": "Anh/Chị",
		"designation": app.get("designation") or app.get("job_title") or "Nhân viên",
		"department": app.get("department") or "",
		"salary": fmt_money(salary_val) if salary_val else "[Thỏa thuận]",
		"company": frappe.defaults.get_global_default("company") or "Công ty",
	}

	subject = tpl["subject"].format(**ctx)
	content = tpl["content"].format(**ctx)
	return {"subject": subject, "content": content}


@frappe.whitelist()
def get_contract_types():
	"""Trả về danh sách loại hợp đồng để đính kèm PDF."""
	return [{"key": k, "label": v["label"]} for k, v in CONTRACT_TEMPLATES.items()]


@frappe.whitelist()
def get_contract_template(template_key, applicant):
	"""Render mẫu hợp đồng với thông tin ứng viên thực tế."""
	_ensure_applicant_fields()
	tpl = CONTRACT_TEMPLATES.get(template_key)
	if not tpl:
		frappe.throw(f"Mẫu hợp đồng không tồn tại: {template_key}")

	app = frappe.get_doc("Job Applicant", applicant)
	salary_val = getattr(app, "custom_offered_salary", 0) or 0

	def fmt_money(v):
		try:
			return f"{int(float(v)):,} VNĐ".replace(",", ".")
		except Exception:
			return str(v)

	ctx = {
		"name": app.get("applicant_name") or "",
		"designation": app.get("designation") or app.get("job_title") or "Nhân viên",
		"department": app.get("department") or "",
		"email": app.get("email_id") or "",
		"salary": fmt_money(salary_val) if salary_val else "[Thỏa thuận]",
		"company": frappe.defaults.get_global_default("company") or "Công ty",
	}

	content = tpl["content"].format(**ctx)
	return {"content": content}


# ─────────────────────────────────────────────────────────
#  ONBOARDING FORM (Public — không cần đăng nhập)
# ─────────────────────────────────────────────────────────

def _ensure_onboarding_fields():
	_ensure_custom_field("Job Applicant", "custom_onboarding_token", {
		"label": "Onboarding Token", "fieldtype": "Data", "insert_after": "custom_offered_salary", "read_only": 1
	})
	_ensure_custom_field("Job Applicant", "custom_onboarding_done", {
		"label": "Onboarding Done", "fieldtype": "Check", "insert_after": "custom_onboarding_token", "read_only": 1
	})
	_ensure_custom_field("Job Applicant", "custom_onboarding_data", {
		"label": "Onboarding Data (JSON)", "fieldtype": "Long Text", "insert_after": "custom_onboarding_done", "read_only": 1
	})


def _get_or_create_onboarding_token(app):
	"""Tạo hoặc lấy token onboarding của ứng viên."""
	token = app.get("custom_onboarding_token")
	if not token:
		import uuid
		token = uuid.uuid4().hex
		frappe.db.set_value("Job Applicant", app.name, "custom_onboarding_token", token, update_modified=False)
		app.custom_onboarding_token = token
	return token



@frappe.whitelist(allow_guest=True)
def get_onboarding_form(token):
	"""Trả về dữ liệu form onboarding theo token (không cần đăng nhập)."""
	if not token:
		frappe.throw("Token không hợp lệ")
	results = frappe.get_all(
		"Job Applicant",
		filters={"custom_onboarding_token": token},
		fields=["name", "applicant_name", "email_id", "phone_number", "designation", "job_title",
		        "custom_onboarding_done", "custom_onboarding_data"]
	)
	if not results:
		return {"error": "Link không hợp lệ hoặc đã hết hạn"}
	r = results[0]
	existing_data = {}
	if r.get("custom_onboarding_data"):
		try:
			import json
			existing_data = json.loads(r["custom_onboarding_data"])
		except Exception:
			pass
	return {
		"applicant_name": r["applicant_name"],
		"email_id": r["email_id"],
		"phone_number": r["phone_number"],
		"designation": r.get("designation") or r.get("job_title") or "",
		"department": "",
		"already_done": bool(r.get("custom_onboarding_done")),
		"existing_data": existing_data
	}


@frappe.whitelist(allow_guest=True)
def submit_onboarding_form(token, data):
	"""Ứng viên tự điền thông tin onboarding (không cần đăng nhập)."""
	import json
	if not token:
		frappe.throw("Token không hợp lệ")
	results = frappe.get_all("Job Applicant",
		filters={"custom_onboarding_token": token},
		fields=["name", "custom_onboarding_done"]
	)
	if not results:
		return {"error": "Token không tồn tại"}
	r = results[0]
	if r.get("custom_onboarding_done"):
		return {"error": "Bạn đã hoàn thành điền thông tin trước đó. Vui lòng liên hệ HR nếu cần cập nhật."}

	parsed = data if isinstance(data, dict) else json.loads(data)
	app = frappe.get_doc("Job Applicant", r["name"])
	app.custom_onboarding_data = json.dumps(parsed, ensure_ascii=False)
	app.custom_onboarding_done = 1
	app.save(ignore_permissions=True)
	_log("Job Applicant", r["name"], "onboarding_submit", "Ứng viên đã điền form onboarding")
	return {"ok": True}


# ─────────────────────────────────────────────────────────
#  PDF CONTRACT GENERATOR
# ─────────────────────────────────────────────────────────

def _generate_contract_pdf(app, contract_type="thu_viec", contract_content=None):
	"""Tạo PDF hợp đồng thử việc bằng reportlab từ nội dung tùy chỉnh."""
	try:
		from reportlab.lib.pagesizes import A4
		from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
		from reportlab.lib.units import cm
		from reportlab.lib import colors
		from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
		from reportlab.pdfbase import pdfmetrics
		from reportlab.pdfbase.ttfonts import TTFont
		import io, os

		# Thử đăng ký font hỗ trợ Unicode tiếng Việt (cả Regular và Bold)
		try:
			font_paths = [
				(
					"/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
					"/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
				),
				(
					"/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
					"/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
				),
			]
			font_registered = False
			for fp_norm, fp_bold in font_paths:
				if os.path.exists(fp_norm) and os.path.exists(fp_bold):
					pdfmetrics.registerFont(TTFont("VietFont", fp_norm))
					pdfmetrics.registerFont(TTFont("VietFont-Bold", fp_bold))
					from reportlab.pdfbase.pdfmetrics import registerFontFamily
					registerFontFamily("VietFont", normal="VietFont", bold="VietFont-Bold", italic="VietFont", boldItalic="VietFont-Bold")
					font_registered = True
					break
			base_font = "VietFont" if font_registered else "Helvetica"
		except Exception:
			base_font = "Helvetica"

		buffer = io.BytesIO()
		doc = SimpleDocTemplate(buffer, pagesize=A4,
			rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)

		styles = getSampleStyleSheet()
		normal_style = ParagraphStyle("normal", parent=styles["Normal"], fontName=base_font,
			fontSize=10, leading=16, spaceAfter=8)
		title_style = ParagraphStyle("title", parent=styles["Normal"], fontName=base_font,
			fontSize=14, alignment=1, spaceAfter=12, leading=20, textColor=colors.HexColor("#1e3a5f"))
		bold_style = ParagraphStyle("bold", parent=styles["Normal"], fontName=base_font,
			fontSize=10, leading=16, spaceAfter=4)

		elements = []

		if not contract_content:
			# Fallback default template if no custom content
			company = frappe.defaults.get_global_default("company") or "Công ty"
			salary_val = getattr(app, "custom_offered_salary", 0) or 0
			fmt_money = lambda v: f"{int(float(v)):,} VNĐ".replace(",", ".") if v else "[Thỏa thuận]"
			contract_content = f"""CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM
Độc lập - Tự do - Hạnh phúc
---
HỢP ĐỒNG THỬ VIỆC

BÊN A: {company}
BÊN B: {app.get("applicant_name") or ""}
- Vị trí: {app.get("designation") or app.get("job_title") or "Nhân viên"}
- Mức lương thử việc: {fmt_money(salary_val)}/tháng

Điều 1: Thời gian thử việc là 2 tháng.
Điều 2: Công việc chính theo mô tả của vị trí ứng tuyển.
Điều 3: Thời gian làm việc 8 giờ/ngày, từ thứ Hai đến thứ Sáu."""

		# Convert content text into Paragraphs
		lines = contract_content.split("\n")
		for line in lines:
			line_str = line.strip()
			if not line_str:
				elements.append(Spacer(1, 0.2*cm))
				continue
			
			if line_str.startswith("CỘNG HÒA") or line_str.startswith("HỢP ĐỒNG") or line_str.startswith("Độc lập"):
				elements.append(Paragraph(f"<b>{line_str}</b>", title_style))
			elif line_str.startswith("Điều ") or line_str.startswith("BÊN "):
				elements.append(Paragraph(f"<b>{line_str}</b>", normal_style))
			else:
				elements.append(Paragraph(line_str, normal_style))

		# Signatures
		elements.append(Spacer(1, 0.6*cm))
		sig_data = [
			[Paragraph("<b>ĐẠI DIỆN BÊN A</b>", bold_style), Paragraph("<b>BÊN B</b>", bold_style)],
			[Paragraph("(Ký, đóng dấu và ghi rõ họ tên)", normal_style), Paragraph("(Ký và ghi rõ họ tên)", normal_style)],
			["", ""],
			["", ""],
			[Paragraph("[Đại diện Công ty]", normal_style), Paragraph(app.get("applicant_name") or "", normal_style)],
		]
		sig_table = Table(sig_data, colWidths=[9*cm, 9*cm])
		sig_table.setStyle(TableStyle([
			("FONTNAME", (0,0), (-1,-1), base_font),
			("ALIGN", (0,0), (-1,-1), "CENTER"),
			("TOPPADDING", (0,2), (-1,3), 20),
		]))
		elements.append(sig_table)

		doc.build(elements)
		return buffer.getvalue()

	except ImportError:
		# Fallback nếu không có reportlab: trả về PDF đơn giản
		return _generate_simple_pdf_fallback(app, contract_type)


def _generate_simple_pdf_fallback(app, contract_type):
	"""PDF fallback cực kỳ đơn giản nếu không có reportlab."""
	content = f"""%PDF-1.4
1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj
2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj
3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R/Contents 4 0 R/Resources<</Font<</F1 5 0 R>>>>>>endobj
4 0 obj<</Length 200>>
stream
BT /F1 12 Tf 72 720 Td (HOP DONG LAO DONG) Tj 0 -30 Td (Ben B: {(app.applicant_name or '').encode('ascii', 'replace').decode()}) Tj 0 -20 Td (Vi tri: {(app.designation or '').encode('ascii', 'replace').decode()}) Tj ET
endstream
endobj
5 0 obj<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>endobj
xref
0 6
0000000000 65535 f
0000000009 00000 n
0000000058 00000 n
0000000115 00000 n
0000000266 00000 n
0000000516 00000 n
trailer<</Size 6/Root 1 0 R>>
startxref
600
%%EOF"""
	return content.encode("latin-1", errors="replace")


# ═════════════════════════════════════════════════════════
#  RESEND EMAIL HELPER
# ═════════════════════════════════════════════════════════

RESEND_API_KEY = "re_aYc6fb9V_NvkMFUGZL2WqyxKMnuw6GmTz"
RESEND_FROM    = "HR System <onboarding@resend.dev>"   # Thay bằng domain đã verify khi dùng thật


def _send_via_resend(to, subject, html_body, text_body=None, attachments=None):
	"""Gửi email qua Resend API (https://resend.com).
	Fallback về frappe.sendmail nếu lỗi.
	"""
	import requests as _http
	import base64

	payload = {
		"from": RESEND_FROM,
		"to": [to] if isinstance(to, str) else to,
		"subject": subject,
		"html": html_body,
	}
	if text_body:
		payload["text"] = text_body

	if attachments:
		payload["attachments"] = []
		for att in attachments:
			fname = att.get("fname", "attachment")
			fcontent = att.get("fcontent", b"")
			if isinstance(fcontent, str):
				fcontent = fcontent.encode("latin-1", errors="replace")
			payload["attachments"].append({
				"filename": fname,
				"content": base64.b64encode(fcontent).decode("ascii"),
			})

	try:
		resp = _http.post(
			"https://api.resend.com/emails",
			headers={
				"Authorization": f"Bearer {RESEND_API_KEY}",
				"Content-Type": "application/json",
			},
			json=payload,
			timeout=20,
		)
		resp.raise_for_status()
		return resp.json()
	except Exception as e:
		frappe.log_error(f"Resend error: {e}", "resend_send")
		# Fallback sang frappe sendmail
		frappe.sendmail(
			recipients=to,
			subject=subject,
			content=html_body,
			now=True,
		)
		return {"fallback": True}


def _text_to_html(text):
	"""Chuyển plain-text có xuống dòng thành HTML đẹp cho email."""
	import html as _html
	lines = _html.escape(text).split("\n")
	html_lines = []
	for line in lines:
		stripped = line.strip()
		if stripped.startswith("•") or stripped.startswith("-"):
			html_lines.append(f"<li style='margin:2px 0'>{stripped.lstrip('•- ').strip()}</li>")
		elif stripped == "":
			html_lines.append("<br>")
		else:
			html_lines.append(f"<p style='margin:4px 0'>{line}</p>")
	body = "\n".join(html_lines)
	return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
  body{{font-family:'Segoe UI',Arial,sans-serif;font-size:14px;color:#1f2937;line-height:1.7;background:#f9fafb}}
  .wrap{{max-width:620px;margin:30px auto;background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 2px 12px rgba(0,0,0,.08)}}
  .hdr{{background:linear-gradient(135deg,#4f46e5,#7c3aed);color:#fff;padding:28px 32px}}
  .hdr h1{{margin:0;font-size:20px;font-weight:700}}
  .hdr p{{margin:6px 0 0;opacity:.85;font-size:13px}}
  .body{{padding:28px 32px}}
  li{{margin-left:20px}}
  .footer{{background:#f3f4f6;padding:16px 32px;font-size:12px;color:#6b7280;text-align:center;border-top:1px solid #e5e7eb}}
</style></head>
<body><div class="wrap">
  <div class="hdr"><h1>✉️ Thư mời nhận việc</h1><p>Kính gửi Ứng viên</p></div>
  <div class="body">{body}</div>
  <div class="footer">Email này được gửi tự động từ Hệ thống Tuyển dụng HR. Vui lòng không trả lời trực tiếp.</div>
</div></body></html>"""


# ═════════════════════════════════════════════════════════
#  AI RENDER — OFFER LETTER (DeepSeek tự động sinh thư mời)
# ═════════════════════════════════════════════════════════

@frappe.whitelist()
def ai_render_offer_letter(applicant, template_type="chung"):
	"""Dùng DeepSeek AI tự động sinh nội dung thư mời nhận việc cá nhân hóa.
	
	template_type: chung | ky_thuat | kinh_doanh | ke_toan
	Trả về: { subject, content, html }
	"""
	import requests as _http
	import os as _os

	_ensure_applicant_fields()
	app = frappe.get_doc("Job Applicant", applicant)

	api_key = _os.environ.get("DEEPSEEK_API_KEY", "")
	if not api_key:
		frappe.throw("Chưa cấu hình DEEPSEEK_API_KEY trong môi trường server")

	# Thu thập dữ liệu ứng viên
	salary_val = getattr(app, "custom_offered_salary", 0) or 0
	def fmt_money(v):
		try:
			return f"{int(float(v)):,} VNĐ".replace(",", ".")
		except Exception:
			return str(v)

	company = frappe.defaults.get_global_default("company") or "Công ty"
	today_str = frappe.utils.formatdate(frappe.utils.today(), "dd/MM/yyyy")

	template_hints = {
		"chung": "thư mời nhận việc chuyên nghiệp, lịch sự, phù hợp mọi ngành",
		"ky_thuat": "thư mời nhận việc cho vị trí kỹ thuật/IT, nhấn mạnh môi trường tech, Agile, học hỏi liên tục",
		"kinh_doanh": "thư mời nhận việc cho vị trí kinh doanh/sales, nhấn mạnh cơ hội thu nhập, hoa hồng, thăng tiến",
		"ke_toan": "thư mời nhận việc cho vị trí kế toán/tài chính, nhấn mạnh sự ổn định, phúc lợi, quy trình chuẩn",
	}
	tone_hint = template_hints.get(template_type, template_hints["chung"])

	cv_summary = ""
	try:
		cv_raw = None
		for _field in ["custom_cv_data", "cv_ai_data", "cv_data"]:
			try:
				cv_raw = frappe.db.get_value("Job Applicant", applicant, _field)
				if cv_raw:
					break
			except Exception:
				continue
		if cv_raw and isinstance(cv_raw, str) and cv_raw.strip().startswith("{"):
			import json as _cvj
			_cv = _cvj.loads(cv_raw)
			cv_summary = (
				f"\nThông tin từ CV phân tích AI:"
				f"\n- Tóm tắt: {_cv.get('summary', '')}"
				f"\n- Điểm mạnh: {', '.join((_cv.get('strengths') or [])[:3])}"
				f"\n- Kỹ năng: {', '.join((_cv.get('skills') or [])[:5])}"
				f"\n- Phù hợp: {_cv.get('fit_score', '')}/100 ({_cv.get('fit_level', '')})"
			)
	except Exception:
		pass  # CV data không bắt buộc


	prompt = f"""Bạn là chuyên gia HR cao cấp, đang viết {tone_hint}.

THÔNG TIN ỨNG VIÊN:
- Họ tên: {app.get('applicant_name') or ''}
- Email: {app.get('email_id') or ''}
- Vị trí ứng tuyển: {app.get('designation') or app.get('job_title') or 'Nhân viên'}
- Phòng ban: {app.get('department') or ''}
- Mức lương offer: {fmt_money(salary_val) if salary_val else '[Thỏa thuận]'}
- Ngày hôm nay: {today_str}
- Công ty: {company}
{cv_summary}

YÊU CẦU:
1. Viết thư mời nhận việc bằng TIẾNG VIỆT CÓ DẤU ĐẦY ĐỦ, trang trọng, ấm áp, cá nhân hóa cho ứng viên này.
2. Thư phải có: lời chào tên ứng viên, thông báo trúng tuyển, thông tin vị trí + lương + ngày bắt đầu (để [Điền ngày]), yêu cầu xác nhận trước [Điền ngày], lời kết trang trọng.
3. Độ dài: 200-350 từ. KHÔNG markdown, KHÔNG bullet point thừa, KHÔNG giải thích thêm.
4. Cuối cùng trả về ĐÚNG FORMAT JSON sau (không gì khác):
{{
  "subject": "Tiêu đề email (ngắn gọn, chuyên nghiệp)",
  "content": "Toàn bộ nội dung thư (plain text, xuống dòng bình thường)"
}}"""

	try:
		resp = _http.post(
			"https://api.deepseek.com/chat/completions",
			headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
			json={
				"model": "deepseek-chat",
				"messages": [
					{"role": "system", "content": "Chỉ trả về JSON thuần, không markdown, không giải thích."},
					{"role": "user", "content": prompt},
				],
				"temperature": 0.4,
				"max_tokens": 1500,
			},
			timeout=30,
		)
		resp.raise_for_status()
		raw = resp.json()["choices"][0]["message"]["content"].strip()
		import re as _re, json as _json
		json_match = _re.search(r"\{.*\}", raw, _re.DOTALL)
		if json_match:
			raw = json_match.group(0)
		result = _json.loads(raw, strict=False)
		subject = result.get("subject", "")
		content = result.get("content", "")
		return {
			"subject": subject,
			"content": content,
			"html": _text_to_html(content),
			"ai": True,
		}
	except Exception as e:
		frappe.log_error(f"AI render offer error: {e}", "ai_render_offer_letter")
		# Fallback về template tĩnh
		tpl = OFFER_TEMPLATES.get(template_type, OFFER_TEMPLATES["chung"])
		ctx = {
			"name": app.get("applicant_name") or "",
			"title": "Anh/Chị",
			"designation": app.get("designation") or app.get("job_title") or "Nhân viên",
			"department": app.get("department") or "",
			"salary": fmt_money(salary_val) if salary_val else "[Thỏa thuận]",
			"company": company,
		}
		content = tpl["content"].format(**ctx)
		subject = tpl["subject"].format(**ctx)
		return {"subject": subject, "content": content, "html": _text_to_html(content), "ai": False}


# ═════════════════════════════════════════════════════════
#  AI RENDER — HỢP ĐỒNG LAO ĐỘNG (DeepSeek sinh nội dung HĐLĐ)
# ═════════════════════════════════════════════════════════

@frappe.whitelist()
def ai_render_contract(applicant, contract_type="thu_viec"):
	"""Dùng DeepSeek AI tự động sinh nội dung hợp đồng lao động/thử việc đầy đủ.
	
	Trả về: { title, content, clauses: [{title, body}], html }
	"""
	import requests as _http
	import os as _os

	_ensure_applicant_fields()
	app = frappe.get_doc("Job Applicant", applicant)

	api_key = _os.environ.get("DEEPSEEK_API_KEY", "")
	if not api_key:
		frappe.throw("Chưa cấu hình DEEPSEEK_API_KEY")

	salary_val = getattr(app, "custom_offered_salary", 0) or 0
	def fmt_money(v):
		try:
			return f"{int(float(v)):,} VNĐ".replace(",", ".")
		except Exception:
			return str(v)

	company = frappe.defaults.get_global_default("company") or "Công ty"
	today_str = frappe.utils.formatdate(frappe.utils.today(), "dd/MM/yyyy")

	type_labels = {
		"thu_viec": "Hợp đồng thử việc 02 tháng",
		"thu_viec_1": "Hợp đồng thử việc 01 tháng",
		"toan_thoi_gian": "Hợp đồng lao động toàn thời gian không xác định thời hạn",
	}
	contract_label = type_labels.get(contract_type, "Hợp đồng thử việc")

	prompt = f"""Bạn là luật sư lao động chuyên nghiệp, đang soạn thảo hợp đồng lao động Việt Nam theo Bộ luật Lao động 2019.

THÔNG TIN HỢP ĐỒNG:
- Loại hợp đồng: {contract_label}
- Bên A (Người sử dụng lao động): {company}
- Bên B (Người lao động): {app.get('applicant_name') or ''}
- Email Bên B: {app.get('email_id') or ''}
- Vị trí: {app.get('designation') or app.get('job_title') or 'Nhân viên'}
- Phòng ban: {app.get('department') or '[Phòng ban]'}
- Mức lương: {fmt_money(salary_val) if salary_val else '[Thỏa thuận]'}/tháng
- Ngày ký hợp đồng: {today_str}
- Ngày bắt đầu: [Điền ngày bắt đầu]

YÊU CẦU:
Soạn hợp đồng đầy đủ TIẾNG VIỆT CÓ DẤU, chuyên nghiệp, đúng pháp luật, gồm:
- Điều 1: Công việc và địa điểm làm việc
- Điều 2: Thời hạn hợp đồng  
- Điều 3: Tiền lương và phụ cấp
- Điều 4: Thời gian làm việc và nghỉ ngơi
- Điều 5: Trang bị bảo hộ lao động
- Điều 6: Bảo hiểm xã hội, y tế, thất nghiệp
- Điều 7: Đào tạo, bồi dưỡng nâng cao
- Điều 8: Điều khoản chung

Trả về JSON (không gì khác):
{{
  "title": "Tên hợp đồng",
  "clauses": [
    {{"title": "Điều 1 — ...", "body": "Nội dung điều khoản..."}},
    ...
  ]
}}"""

	try:
		resp = _http.post(
			"https://api.deepseek.com/chat/completions",
			headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
			json={
				"model": "deepseek-chat",
				"messages": [
					{"role": "system", "content": "Chỉ trả về JSON thuần, không markdown."},
					{"role": "user", "content": prompt},
				],
				"temperature": 0.2,
				"max_tokens": 3000,
			},
			timeout=45,
		)
		resp.raise_for_status()
		raw = resp.json()["choices"][0]["message"]["content"].strip()
		import re as _re, json as _json
		json_match = _re.search(r"\{.*\}", raw, _re.DOTALL)
		if json_match:
			raw = json_match.group(0)
		result = _json.loads(raw, strict=False)

		# Render thành plain text + HTML
		title = result.get("title", contract_label)
		clauses = result.get("clauses", [])
		plain_lines = [title, "=" * 60, f"Ngày ký: {today_str}", ""]
		html_clauses = []
		for cl in clauses:
			plain_lines.append(cl["title"])
			plain_lines.append(cl["body"])
			plain_lines.append("")
			html_clauses.append(
				f"<div style='margin-bottom:16px'>"
				f"<strong style='color:#1e3a5f;font-size:13px'>{cl['title']}</strong>"
				f"<p style='margin:6px 0 0;white-space:pre-line;font-size:13px'>{cl['body']}</p>"
				f"</div>"
			)
		plain_content = "\n".join(plain_lines)
		html_content = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
  body{{font-family:'Times New Roman',serif;font-size:13px;color:#1f2937;line-height:1.8;background:#f9fafb}}
  .wrap{{max-width:680px;margin:30px auto;background:#fff;border-radius:8px;padding:40px;box-shadow:0 2px 12px rgba(0,0,0,.1)}}
  h1{{text-align:center;font-size:17px;text-transform:uppercase;color:#1e3a5f;margin-bottom:4px}}
  .meta{{text-align:center;color:#6b7280;font-size:12px;margin-bottom:24px}}
  hr{{border:none;border-top:2px solid #1e3a5f;margin:20px 0}}
  .sig{{display:grid;grid-template-columns:1fr 1fr;gap:40px;margin-top:40px;text-align:center}}
  .sig div{{border-top:1px solid #9ca3af;padding-top:8px;font-size:12px;color:#374151}}
</style></head>
<body><div class="wrap">
  <h1>{title}</h1>
  <div class="meta">Số: ___/HĐ-{company[:3].upper()}/{frappe.utils.now_datetime().year} &nbsp;|&nbsp; Ngày ký: {today_str}</div>
  <hr>
  <p><em>Căn cứ Bộ luật Lao động nước CHXHCN Việt Nam năm 2019 và các văn bản hướng dẫn thi hành;</em></p>
  <p><em>Hai bên cùng thỏa thuận ký kết hợp đồng này:</em></p>
  <hr>
  {''.join(html_clauses)}
  <div class="sig">
    <div><strong>ĐẠI DIỆN BÊN A</strong><br><small>(Ký, đóng dấu, ghi rõ họ tên)</small><br><br><br>{company}</div>
    <div><strong>BÊN B</strong><br><small>(Ký, ghi rõ họ tên)</small><br><br><br>{app.applicant_name or ''}</div>
  </div>
</div></body></html>"""

		return {
			"title": title,
			"clauses": clauses,
			"content": plain_content,
			"html": html_content,
			"ai": True,
		}
	except Exception as e:
		frappe.log_error(f"AI render contract error: {e}", "ai_render_contract")
		return {"error": str(e), "ai": False}


# ═════════════════════════════════════════════════════════
#  SEND OFFER (Resend-powered version)
# ═════════════════════════════════════════════════════════

@frappe.whitelist()
def send_offer_resend(applicant, subject, content, email_id=None,
                      attach_pdf=False, contract_type="thu_viec", include_onboarding=False, contract_content=None):
	"""Gửi Offer Letter qua Resend API.
	Nhận plain-text content, tự convert sang HTML đẹp ở backend — tránh truyền HTML lớn qua params.
	"""
	_ensure_applicant_fields()
	_ensure_onboarding_fields()
	app = frappe.get_doc("Job Applicant", applicant)
	recipient = email_id or app.email_id
	if not recipient:
		frappe.throw("Ứng viên không có địa chỉ email")

	# Convert plain text → HTML đẹp (tránh truyền HTML khổng lồ qua params)
	final_html = _text_to_html(content)

	# Thêm link onboarding nếu được yêu cầu
	onboarding_url = None
	if frappe.utils.cstr(include_onboarding) in ("1", "true", "True"):
		token = _get_or_create_onboarding_token(app)
		site_url = frappe.utils.get_url()
		onboarding_url = f"{site_url}/hr_app/onboarding?token={token}"
		final_html += f"""
<hr style="margin:24px 0;border-color:#e5e7eb">
<div style="background:#f0fdf4;border:1px solid #bbf7d0;border-radius:10px;padding:16px 20px">
  <p style="margin:0 0 8px;font-weight:700;color:#15803d">📋 Điền thông tin hồ sơ trực tuyến</p>
  <p style="margin:0 0 10px;font-size:13px;color:#166534">Vui lòng hoàn thành form thông tin hồ sơ trước ngày nhận việc:</p>
  <a href="{onboarding_url}" style="display:inline-block;background:#16a34a;color:#fff;padding:10px 20px;border-radius:8px;text-decoration:none;font-weight:700;font-size:13px">👆 Điền thông tin ngay</a>
</div>"""

	# Sinh + đính kèm PDF
	attachments = []
	if frappe.utils.cstr(attach_pdf) in ("1", "true", "True"):
		try:
			pdf_bytes = _generate_contract_pdf(app, contract_type, contract_content)
			attachments = [{
				"fname": f"hop_dong_{contract_type}_{(app.get('applicant_name') or app.name).replace(' ', '_')}.pdf",
				"fcontent": pdf_bytes,
			}]
		except Exception as e:
			frappe.log_error(f"PDF gen error: {e}", "send_offer_resend")

	_send_via_resend(
		to=recipient,
		subject=subject,
		html_body=final_html,
		attachments=attachments or None,
	)

	_log("Job Applicant", applicant, "send_offer", f"Resend: {subject}")
	# Dùng frappe.db.set_value thay vì app.save() để tránh TimestampMismatchError
	note_extra = f"\n  PDF: {contract_type}" if attachments else ""
	note_extra += f"\n  Onboarding: {onboarding_url}" if onboarding_url else ""
	try:
		current_notes = frappe.db.get_value("Job Applicant", applicant, "notes") or ""
		new_notes = (current_notes + f"\n[OFFER_LETTER] Gửi ngày {frappe.utils.today()}:{note_extra}").strip()
		frappe.db.set_value("Job Applicant", applicant, "notes", new_notes, update_modified=False)
	except Exception as _ne:
		frappe.log_error(f"Không thể cập nhật notes: {_ne}", "send_offer_resend")

	return {"ok": True, "onboarding_url": onboarding_url}
