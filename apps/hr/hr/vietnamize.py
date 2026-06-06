"""One-off: Việt hóa master data HR (rename document → tự cập nhật mọi liên kết).

Chạy: echo "from hr.vietnamize import run; run()" | bench --site erp.local console
"""
import frappe

DESIGNATIONS = {
	"Accountant": "Kế toán viên",
	"Administrative Assistant": "Trợ lý hành chính",
	"Administrative Officer": "Chuyên viên hành chính",
	"Analyst": "Chuyên viên phân tích",
	"Associate": "Cộng tác viên",
	"Business Analyst": "Chuyên viên phân tích nghiệp vụ",
	"Business Development Manager": "Trưởng phòng phát triển kinh doanh",
	"Chief Executive Officer": "Tổng giám đốc (CEO)",
	"Chief Financial Officer": "Giám đốc tài chính (CFO)",
	"Chief Operating Officer": "Giám đốc vận hành (COO)",
	"Chief Technology Officer": "Giám đốc công nghệ (CTO)",
	"Consultant": "Tư vấn viên",
	"Customer Service Representative": "Nhân viên chăm sóc khách hàng",
	"Designer": "Nhà thiết kế",
	"Engineer": "Kỹ sư",
	"Executive Assistant": "Trợ lý điều hành",
	"Finance Manager": "Trưởng phòng tài chính",
	"Head of Marketing and Sales": "Trưởng phòng Marketing & Kinh doanh",
	"HR Manager": "Trưởng phòng Nhân sự",
	"Manager": "Quản lý",
	"Managing Director": "Giám đốc điều hành",
	"Marketing Manager": "Trưởng phòng Marketing",
	"Marketing Specialist": "Chuyên viên Marketing",
	"President": "Chủ tịch",
	"Product Manager": "Trưởng phòng sản phẩm",
	"Project Manager": "Quản lý dự án",
	"Researcher": "Nghiên cứu viên",
	"Sales Representative": "Nhân viên kinh doanh",
	"Secretary": "Thư ký",
	"Software Developer": "Lập trình viên",
	"Vice President": "Phó chủ tịch",
}

LEAVE_TYPES = {
	"Casual Leave": "Nghỉ việc riêng",
	"Compensatory Off": "Nghỉ bù",
	"Leave Without Pay": "Nghỉ không lương",
	"Privilege Leave": "Nghỉ phép năm",
	"Sick Leave": "Nghỉ ốm",
}

EMPLOYMENT_TYPES = {
	"Apprentice": "Học việc",
	"Commission": "Theo hoa hồng",
	"Contract": "HĐ xác định thời hạn",
	"Full-time": "Toàn thời gian",
	"Intern": "Thực tập",
	"Part-time": "Bán thời gian",
	"Piecework": "Khoán việc",
	"Probation": "Thử việc",
}

EXPENSE_TYPES = {
	"Calls": "Điện thoại",
	"Food": "Ăn uống",
	"Medical": "Y tế",
	"Others": "Khác",
	"Travel": "Công tác",
}

MAP = [
	("Designation", DESIGNATIONS),
	("Leave Type", LEAVE_TYPES),
	("Employment Type", EMPLOYMENT_TYPES),
	("Expense Claim Type", EXPENSE_TYPES),
]


def run():
	total_ok, total_skip = 0, 0
	for doctype, mapping in MAP:
		for old, new in mapping.items():
			if not frappe.db.exists(doctype, old):
				continue  # đã rename hoặc không có
			if frappe.db.exists(doctype, new):
				print(f"SKIP {doctype}: '{new}' đã tồn tại")
				total_skip += 1
				continue
			try:
				frappe.rename_doc(doctype, old, new, force=True, show_alert=False)
				total_ok += 1
			except Exception as e:
				print(f"FAIL {doctype} '{old}' → '{new}': {e}")
				total_skip += 1
	frappe.db.commit()
	print(f"DONE: renamed={total_ok}, skipped={total_skip}")
	return {"renamed": total_ok, "skipped": total_skip}
