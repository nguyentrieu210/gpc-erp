import json, urllib.request, http.cookiejar

cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
opener.open(urllib.request.Request("http://localhost:8000/api/method/login",
    data=json.dumps({"usr":"Administrator","pwd":"admin"}).encode(),
    headers={"Content-Type":"application/json"}))

test_applicants = [
    {
        "job_title": "HR-OPN-2026-0006",
        "applicant_name": "Nguyen Van An",
        "email_id": "an.nguyen@gmail.com",
        "phone_number": "0912345678",
        "cv_data": {
            "name": "Nguyen Van An",
            "email": "an.nguyen@gmail.com",
            "phone": "0912345678",
            "location": "Ho Chi Minh",
            "dob": "15/03/1995",
            "summary": "Ky su phan mem 7 nam kinh nghiem phat trien he thong enterprise. Chuyen sau ve kien truc microservices va cloud-native.",
            "education": [
                "DH Bach Khoa TPHCM - Ky su CNTT (2013-2018)",
                "Chung chi AWS Solutions Architect Professional"
            ],
            "experience": [
                "Tech Lead tai FPT Software (2020-nay): Dan dat team 8 nguoi",
                "Senior Developer tai VNG (2018-2020): Phat trien backend cho 10M nguoi dung",
                "Junior Developer tai TMA Solutions (2015-2018)"
            ],
            "skills": ["Python", "Go", "React", "AWS", "Docker", "Kubernetes", "Microservices", "PostgreSQL", "Redis", "CI/CD"],
            "languages": ["Tieng Anh - IELTS 7.5", "Tieng Nhat - N4"],
            "links": ["linkedin.com/in/annguyen", "github.com/annguyen"],
            "fit_score": 92,
            "fit_level": "Rat phu hop",
            "fit_reason": "Kinh nghiem Tech Lead va chuyen mon sau ve chuyen doi so",
            "strengths": ["7 nam kinh nghiem", "Da tung lam Tech Lead", "AWS Certified"],
            "gaps": ["Chua co kinh nghiem quan ly phong ban"]
        }
    },
    {
        "job_title": "HR-OPN-2026-0006",
        "applicant_name": "Tran Thi Binh",
        "email_id": "binh.tran@outlook.com",
        "phone_number": "0987654321",
        "cv_data": {
            "name": "Tran Thi Binh",
            "email": "binh.tran@outlook.com",
            "phone": "0987654321",
            "location": "Ha Noi",
            "dob": "22/07/1993",
            "summary": "Chuyen gia chuyen doi so 8 nam kinh nghiem tu van va trien khai ERP cho doanh nghiep.",
            "education": [
                "DH Kinh te Quoc dan - QTKD (2011-2015)",
                "MBA - DH RMIT (2018-2020)",
                "Chung chi SAP ERP Consultant"
            ],
            "experience": [
                "Chuyen gia tu van tai Deloitte (2018-nay): Tu van chien luoc so cho 15+ doanh nghiep",
                "BA tai MISA (2015-2018): Phan tich nghiep vu ERP"
            ],
            "skills": ["ERP", "SAP", "Business Analysis", "Project Management", "Digital Transformation", "Data Analytics", "Power BI"],
            "languages": ["Tieng Anh - TOEIC 900", "Tieng Trung - HSK 4"],
            "links": ["linkedin.com/in/binhtran"],
            "fit_score": 85,
            "fit_level": "Rat phu hop",
            "fit_reason": "Kinh nghiem tu van Big4 va MBA la diem cong lon",
            "strengths": ["8 nam chuyen doi so", "MBA RMIT", "Kinh nghiem Big4"],
            "gaps": ["Thieu kinh nghiem ky thuat sau"]
        }
    },
    {
        "job_title": "HR-OPN-2026-0005",
        "applicant_name": "Le Thi Huong",
        "email_id": "huong.le@yahoo.com",
        "phone_number": "0369852147",
        "cv_data": {
            "name": "Le Thi Huong",
            "email": "huong.le@yahoo.com",
            "phone": "0369852147",
            "location": "Da Nang",
            "dob": "10/11/1997",
            "summary": "Chuyen vien hanh chinh 4 nam kinh nghiem quan ly van phong cho cong ty cong nghe.",
            "education": [
                "DH Kinh te Da Nang - Quan tri Van phong (2015-2019)"
            ],
            "experience": [
                "Chuyen vien Hanh chinh tai Cong ty ABC (2020-nay): Quan ly van phong 50+ nhan vien",
                "Tro ly Hanh chinh tai VP Luat XYZ (2019-2020)"
            ],
            "skills": ["Quan ly van phong", "Microsoft Office", "Google Workspace", "Trello", "Soan thao van ban", "To chuc su kien"],
            "languages": ["Tieng Anh - TOEIC 700"],
            "links": [],
            "fit_score": 78,
            "fit_level": "Phu hop",
            "fit_reason": "Kinh nghiem hanh chinh phu hop, ky nang to chuc tot",
            "strengths": ["4 nam hanh chinh", "Ky nang to chuc", "Thanh thao cong cu"],
            "gaps": ["Chua co kinh nghiem linh vuc cong nghe"]
        }
    },
    {
        "job_title": "HR-OPN-2026-0006",
        "applicant_name": "Pham Minh Tuan",
        "email_id": "tuan.pham@hotmail.com",
        "phone_number": "0901234567",
        "cv_data": {
            "name": "Pham Minh Tuan",
            "email": "tuan.pham@hotmail.com",
            "phone": "0901234567",
            "location": "Ho Chi Minh",
            "dob": "05/09/1990",
            "summary": "Senior Engineering Manager 10+ nam xay dung va dan dat doi ngu ky thuat. Chuyen gia chien luoc cong nghe.",
            "education": [
                "DH Bach Khoa Ha Noi - Ky su CNTT (2008-2013)",
                "Thac si KHMT - DH Stanford (2014-2016)"
            ],
            "experience": [
                "Engineering Director tai Shopee (2021-nay): Quan ly 80+ ky su",
                "Senior EM tai Grab (2018-2021): Xay dung team 30 nguoi",
                "Tech Lead tai Google Singapore (2016-2018)"
            ],
            "skills": ["System Architecture", "Cloud Computing", "Team Leadership", "Agile", "Java", "Go", "Kubernetes", "AWS", "GCP"],
            "languages": ["Tieng Anh - IELTS 8.0", "Tieng Trung - Business"],
            "links": ["linkedin.com/in/minhtuanpham", "github.com/tuanpham"],
            "fit_score": 98,
            "fit_level": "Rat phu hop",
            "fit_reason": "Profile dang cap quoc te, kinh nghiem quan ly team lon",
            "strengths": ["10+ nam", "Google/Grab/Shopee", "Quan ly 80+ nguoi", "Stanford Master"],
            "gaps": ["Luong ky vong cao", "Can thich nghi mo hinh doanh nghiep vua"]
        }
    },
    {
        "job_title": "HR-OPN-2026-0005",
        "applicant_name": "Do Thanh Mai",
        "email_id": "mai.do@gmail.com",
        "phone_number": "0978123456",
        "cv_data": {
            "name": "Do Thanh Mai",
            "email": "mai.do@gmail.com",
            "phone": "0978123456",
            "location": "Ha Noi",
            "dob": "20/12/1998",
            "summary": "Chuyen vien hanh chinh tre, nang dong, 3 nam kinh nghiem startup cong nghe.",
            "education": [
                "Hoc vien Hanh chinh Quoc gia - Quan tri Van phong (2016-2020)"
            ],
            "experience": [
                "Office Manager tai Startup EdTech (2022-nay): Quan ly van phong 30 nhan vien",
                "Admin Assistant tai Cong ty FinTech (2020-2022)"
            ],
            "skills": ["Quan ly van phong", "Notion", "Slack", "Google Workspace", "Quan ly ngan sach"],
            "languages": ["Tieng Anh - IELTS 6.5", "Tieng Han - TOPIK 3"],
            "links": [],
            "fit_score": 72,
            "fit_level": "Phu hop",
            "fit_reason": "Nang dong, kinh nghiem startup, phu hop van hoa cong ty cong nghe",
            "strengths": ["Kinh nghiem startup", "Da ngon ngu", "Sang tao"],
            "gaps": ["Kinh nghiem con it (3 nam)", "Chua quan ly team"]
        }
    }
]

print(f"Creating {len(test_applicants)} applicants with full CV data...")
for i, a in enumerate(test_applicants):
    try:
        body = json.dumps(a).encode()
        req = urllib.request.Request("http://localhost:8000/api/method/hr.api.create_job_applicant",
            data=body, headers={"Content-Type": "application/json"})
        resp = opener.open(req)
        name = json.loads(resp.read())["message"].get("name", "FAIL")
        print(f"  {i+1}. {a['applicant_name']} -> {name} ({len(a['cv_data']['skills'])} skills, fit={a['cv_data']['fit_score']})")
    except Exception as e:
        print(f"  {i+1}. {a['applicant_name']} -> ERROR: {e}")

print("\nDONE! Ctrl+F5 to see all applicants with full CV data.")
