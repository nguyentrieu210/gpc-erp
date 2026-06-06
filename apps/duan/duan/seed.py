"""Seed test data for GPC ERP."""
import frappe
import random


def seed_all():
    seed_duan()
    seed_crm()
    seed_hr()
    print("✅ Seed done!")
    frappe.db.commit()


def seed_duan():
    if frappe.db.count("Project") > 2:
        return
    print("Seeding Dự án...")
    for code, name, status, pri, pct in [
        ("PRJ-001", "Website GPC ERP", "Open", "High", 25),
        ("PRJ-002", "Mobile App Khách hàng", "Open", "Medium", 10),
        ("PRJ-003", "Hệ thống Kho tự động", "Working", "High", 60),
        ("PRJ-004", "Cổng thanh toán online", "Open", "Medium", 5),
        ("PRJ-005", "Báo cáo BI Dashboard", "Completed", "Low", 100),
    ]:
        if not frappe.db.exists("Project", {"project_name": name}):
            frappe.get_doc({
                "doctype": "Project", "project_name": name,
                "status": status, "priority": pri,
                "percent_complete": pct,
                "expected_start_date": frappe.utils.add_days(frappe.utils.today(), -30),
                "expected_end_date": frappe.utils.add_days(frappe.utils.today(), random.randint(10, 90)),
            }).insert(ignore_permissions=True)

    proj_names = [p["name"] for p in frappe.get_all("Project", limit=5)]
    if frappe.db.count("Task") < 5 and proj_names:
        subjects = ["Phân tích yêu cầu", "Thiết kế UI/UX", "Lập trình Backend", "Lập trình Frontend",
                    "Kiểm thử", "Viết tài liệu", "Triển khai staging", "Review code",
                    "Sửa lỗi", "Họp kickoff", "Đào tạo user", "Go-live", "Backup database",
                    "Tối ưu performance", "Security audit"]
        for s in subjects:
            task = {
                "doctype": "Task", "subject": s,
                "project": random.choice(proj_names),
                "status": random.choice(["Open", "Working", "Pending Review", "Completed"]),
                "priority": random.choice(["Low", "Medium", "High"]),
            }
            frappe.get_doc(task).insert(ignore_permissions=True)
    print(f"  DUAN: {frappe.db.count('Project')} projects, {frappe.db.count('Task')} tasks")


def seed_crm():
    # Customers
    if frappe.db.count("Customer") < 3:
        print("Seeding CRM...")
        groups = [g["name"] for g in frappe.get_all("Customer Group", filters={"is_group": 0}, limit=10)]
        if not groups:
            groups = ["Commercial"]
        for name, ctype in [
            ("Công ty TNHH ABC", "Company"),
            ("Doanh nghiệp XYZ", "Company"),
            ("Hộ kinh doanh Minh Anh", "Individual"),
            ("Công ty CP Tech Việt", "Company"),
            ("Cá nhân Nguyễn Văn X", "Individual"),
        ]:
            if not frappe.db.exists("Customer", {"customer_name": name}):
                frappe.get_doc({
                    "doctype": "Customer", "customer_name": name,
                    "customer_type": ctype,
                    "customer_group": random.choice(groups),
                }).insert(ignore_permissions=True)
        custs = [c["name"] for c in frappe.get_all("Customer", limit=5)]
    else:
        custs = [c["name"] for c in frappe.get_all("Customer", limit=5)]

    # Leads
    if frappe.db.count("Lead") < 5:
        for lead_name, email, status in [
            ("Lead - ERP cloud", "contact1@abc.com", "Open"),
            ("Lead - App mobile", "contact2@xyz.com", "Open"),
            ("Lead - Tư vấn BI", "contact3@minhanh.com", "Replied"),
            ("Lead - Đào tạo nhân sự", "contact4@techviet.com", "Converted"),
            ("Lead - Bảo trì hệ thống", "contact5@abc.com", "Open"),
            ("Lead - Digital Marketing", "marketing@corp.com", "Replied"),
            ("Lead - Chuyển đổi số", "cds@gov.vn", "Open"),
            ("Lead - AI Chatbot", "ai@startup.vn", "Replied"),
        ]:
            if not frappe.db.exists("Lead", {"lead_name": lead_name}):
                frappe.get_doc({
                    "doctype": "Lead", "lead_name": lead_name,
                    "email_id": email, "status": status,
                    "company_name": lead_name.split(" - ")[1],
                }).insert(ignore_permissions=True)

    # Opportunities
    if frappe.db.count("Opportunity") < 3 and custs:
        for i, (opp_name, cust, amount) in enumerate([
            ("Triển khai ERP", custs[0], 500000000),
            ("App Mobile", custs[1] if len(custs) > 1 else custs[0], 200000000),
            ("BI Dashboard", custs[2] if len(custs) > 2 else custs[0], 150000000),
            ("Tư vấn Digital", custs[3] if len(custs) > 3 else custs[0], 80000000),
            ("Hỗ trợ kỹ thuật", custs[0], 30000000),
        ]):
            if not frappe.db.exists("Opportunity", {"opportunity_name": opp_name}):
                frappe.get_doc({
                    "doctype": "Opportunity", "opportunity_name": opp_name,
                    "opportunity_from": "Customer", "party_name": cust,
                    "opportunity_amount": amount,
                    "status": random.choice(["Open", "Quotation", "Replied"]),
                    "expected_closing": frappe.utils.add_days(frappe.utils.today(), 30),
                }).insert(ignore_permissions=True)
    print(f"  CRM: {frappe.db.count('Lead')} leads, {frappe.db.count('Opportunity')} opps, {frappe.db.count('Customer')} customers")


def seed_hr():
    if frappe.db.count("Employee") < 2:
        print("Seeding HR...")
        depts = [d["name"] for d in frappe.get_all("Department", limit=10)]
        if not depts:
            depts = ["All Departments"]
        for idx, (first, last) in enumerate([
            ("Trần", "Thị B"), ("Lê", "Văn C"), ("Phạm", "Thị D"), ("Hoàng", "Văn E"),
        ]):
            name = f"{first} {last}"
            if not frappe.db.exists("Employee", {"employee_name": name}):
                frappe.get_doc({
                    "doctype": "Employee",
                    "first_name": first, "last_name": last,
                    "employee_name": name,
                    "department": random.choice(depts),
                    "gender": "Female" if idx % 2 == 0 else "Male",
                    "date_of_birth": f"{1990 + idx}-01-15",
                    "status": "Active", "date_of_joining": "2025-01-15",
                }).insert(ignore_permissions=True)
    print(f"  HR: {frappe.db.count('Employee')} employees")


if __name__ == "__main__":
    seed_all()
