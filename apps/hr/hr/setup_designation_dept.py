"""Setup Designation-Department mapping with exact Vietnamese names."""
import frappe

def run():
    cf = frappe.db.exists("Custom Field", "Designation-default_department")
    if not cf:
        frappe.get_doc({
            "doctype": "Custom Field",
            "dt": "Designation",
            "fieldname": "default_department",
            "label": "Phong ban mac dinh",
            "fieldtype": "Link",
            "options": "Department",
            "insert_after": "description",
            "translatable": 0,
        }).insert(ignore_permissions=True)
        print("Created Custom Field")

    # Exact mappings using real DB names
    mappings = [
        # Tai chinh - Ke toan
        ("Ke toan vien", "Tai khoan - G"),
        ("Truong phong tai chinh", "Tai khoan - G"),
        ("Giam doc tai chinh (CFO)", "Tai khoan - G"),
        # Hanh chinh - Nhan su
        ("Tro ly hanh chinh", "Nhan su - G"),
        ("Chuyen vien hanh chinh", "Nhan su - G"),
        ("Truong phong Nhan su", "Nhan su - G"),
        ("Thu ky", "Nhan su - G"),
        # Kinh doanh
        ("Nhan vien kinh doanh", "Ban hang - G"),
        ("Truong phong phat trien kinh doanh", "Ban hang - G"),
        ("Tu van vien", "Ban hang - G"),
        # Marketing
        ("Chuyen vien Marketing", "Tiep thi - G"),
        ("Truong phong Marketing", "Tiep thi - G"),
        ("Truong phong Marketing & Kinh doanh", "Tiep thi - G"),
        # Cong nghe - IT
        ("Lap trinh vien", "Phong Chuyen doi so - G"),
        ("Ky su", "Phong Chuyen doi so - G"),
        ("Chuyen vien phan tich", "Phong Chuyen doi so - G"),
        ("Chuyen vien phan tich nghiep vu", "Phong Chuyen doi so - G"),
        ("Truong phong chuyen doi so", "Phong Chuyen doi so - G"),
        ("Giam doc cong nghe (CTO)", "Phong Chuyen doi so - G"),
        ("Truong nhom Test", "Phong Chuyen doi so - G"),
        # San pham
        ("Truong phong san pham", "Nghien cuu & Phat trien - G"),
        ("Nghien cuu vien", "Nghien cuu & Phat trien - G"),
        # Chat luong
        ("Quan ly chat luong", "Quan ly chat luong - G"),
        # Mua hang
        ("Nha thiet ke", "Mua hang - G"),
        # CSKH
        ("Nhan vien cham soc khach hang", "Dich vu khach hang - G"),
        # Quan ly cap cao
        ("Tong giam doc (CEO)", "Quan ly - G"),
        ("Giam doc dieu hanh", "Quan ly - G"),
        ("Giam doc van hanh (COO)", "Quan ly - G"),
        ("Chu tich", "Quan ly - G"),
        ("Pho chu tich", "Quan ly - G"),
        ("Quan ly", "Quan ly - G"),
        ("Quan ly du an", "Quan ly - G"),
        ("Tro ly dieu hanh", "Quan ly - G"),
        # Khac
        ("Cong tac vien", "Nhan su - G"),
        ("Dieu phoi", "Dieu phoi - G"),
    ]

    count = 0
    for desig, dept in mappings:
        if frappe.db.exists("Designation", desig) and frappe.db.exists("Department", dept):
            frappe.db.set_value("Designation", desig, "default_department", dept)
            count += 1
        else:
            print(f"  SKIP: {desig} or {dept} not found")

    frappe.db.commit()
    print(f"Mapped {count}/{len(mappings)} designations")
