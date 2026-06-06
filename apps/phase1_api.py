"""Phase 1: Fix interview + add reject/hold/result APIs + fix cv_data storage."""
path = "/home/frappe/frappe-bench/apps/hr/hr/api.py"
with open(path) as f:
    c = f.read()

# ========== 1. Fix schedule_interview ==========
old_sched = '@frappe.whitelist()\ndef schedule_interview(applicant, round_name="Vong 1", date=None, interviewer=None, notes=""):'
if old_sched not in c:
    old_sched = '@frappe.whitelist()\ndef schedule_interview(applicant, round_name'
    # Find the actual signature
    import re
    m = re.search(r'@frappe\.whitelist\(\)\ndef schedule_interview\([^)]+\):', c)
    if m:
        old_sched = m.group()
        print("Found schedule_interview:", old_sched[:80])

new_sched = '''@frappe.whitelist()
def schedule_interview(applicant, round_name="Vong 1", date=None, interviewer=None, notes=""):
\t"""Len lich phong van - luu JSON structured."""
\timport json as _json, datetime as _dt
\tiv = {
\t\t"id": _dt.datetime.now().strftime("%Y%m%d%H%M%S"),
\t\t"round": round_name, "date": date or frappe.utils.today(),
\t\t"interviewer": interviewer or "", "notes": notes or "",
\t\t"status": "scheduled", "score": None, "strengths": [], "weaknesses": []
\t}
\tdoc = frappe.get_doc("Job Applicant", applicant)
\texisting = (doc.notes or "").strip()
\tdoc.notes = existing + "\\n[INTERVIEW] " + _json.dumps(iv, ensure_ascii=False)
\tdoc.status = "Replied"
\tdoc.save(ignore_permissions=True)
\t_log("Job Applicant", applicant, "schedule_interview", f"{round_name} - {iv['date']}")
\treturn {"ok": True, "interview": iv}'''

# ========== 2. Add submit_interview_result ==========
old_detail = '@frappe.whitelist()\ndef get_applicant_detail(name):'

new_apis = '''@frappe.whitelist()
def submit_interview_result(applicant, interview_id, passed=True, score=0, strengths=None, weaknesses=None, notes=""):
\t"""Nhap ket qua phong van."""
\timport json as _json
\tdoc = frappe.get_doc("Job Applicant", applicant)
\tnotes_text = doc.notes or ""
\tupdated = False
\tlines = notes_text.split("\\n")
\tfor i, line in enumerate(lines):
\t\tline = line.strip()
\t\tif line.startswith("[INTERVIEW] "):
\t\t\ttry:
\t\t\t\tiv = _json.loads(line[12:])
\t\t\t\tif iv.get("id") == interview_id:
\t\t\t\t\tiv["status"] = "passed" if passed else "failed"
\t\t\t\t\tiv["score"] = int(score) if score else 0
\t\t\t\t\tiv["strengths"] = _json.loads(strengths) if isinstance(strengths, str) else (strengths or [])
\t\t\t\t\tiv["weaknesses"] = _json.loads(weaknesses) if isinstance(weaknesses, str) else (weaknesses or [])
\t\t\t\t\tiv["notes"] = notes
\t\t\t\t\tlines[i] = "[INTERVIEW] " + _json.dumps(iv, ensure_ascii=False)
\t\t\t\t\tupdated = True
\t\t\t\t\tbreak
\t\t\texcept: pass
\tif not updated:
\t\tfrappe.throw("Khong tim thay lich phong van")
\tdoc.notes = "\\n".join(lines)
\tif passed:
\t\tdoc.status = "Accepted"
\tdoc.save(ignore_permissions=True)
\t_log("Job Applicant", applicant, "interview_result", f"{'Dat' if passed else 'Khong dat'} - Score: {score}")
\treturn {"ok": True}


@frappe.whitelist()
def reject_applicant(name, reason="", missing_requirements=None):
\t"""Tu choi ung vien voi ly do."""
\timport json as _json
\tdoc = frappe.get_doc("Job Applicant", name)
\tdoc.status = "Rejected"
\tentry = {"reason": reason, "date": frappe.utils.today(), "missing": _json.loads(missing_requirements) if isinstance(missing_requirements, str) else (missing_requirements or [])}
\tdoc.notes = (doc.notes or "").strip() + "\\n[REJECT] " + _json.dumps(entry, ensure_ascii=False)
\tdoc.save(ignore_permissions=True)
\t_log("Job Applicant", name, "reject", reason[:100])
\treturn {"ok": True}


@frappe.whitelist()
def hold_applicant(name, reason="", missing_requirements=None):
\t"""Can nhac ung vien - ghi nhan yeu cau con thieu."""
\timport json as _json
\tdoc = frappe.get_doc("Job Applicant", name)
\tdoc.status = "Hold"
\tentry = {"reason": reason, "date": frappe.utils.today(), "missing": _json.loads(missing_requirements) if isinstance(missing_requirements, str) else (missing_requirements or [])}
\tdoc.notes = (doc.notes or "").strip() + "\\n[HOLD] " + _json.dumps(entry, ensure_ascii=False)
\tdoc.save(ignore_permissions=True)
\t_log("Job Applicant", name, "hold", reason[:100])
\treturn {"ok": True}


@frappe.whitelist()
def get_applicant_detail(name):'''

# ========== 3. Fix get_applicant_detail to return interview_history + clean_notes ==========
old_detail_body = '''def get_applicant_detail(name):
\t"""Chi tiet ung vien — kem CV parsed data."""
\timport json as _json, re as _re
\tdoc = frappe.get_doc("Job Applicant", name)
\tresult = doc.as_dict()

\t# Parse CVDATA tu notes
\tcv_data = {}
\tnotes = result.get("notes") or ""
\tfor line in notes.split("\\n"):
\t\tif line.strip().startswith("[CVDATA] "):
\t\t\ttry:
\t\t\t\tcv_data = _json.loads(line.strip()[8:])
\t\t\texcept Exception:
\t\t\t\tpass
\t\t\tbreak

\t# Loc log entries de khong hien thi trong notes
\tclean_notes = [l for l in notes.split("\\n") if l.strip() and not l.strip().startswith("[LOG ") and not l.strip().startswith("[CVDATA]")]
\tresult["cv_data"] = cv_data
\tresult["clean_notes"] = "\\n".join(clean_notes).strip()
\treturn result'''

new_detail_body = '''def get_applicant_detail(name):
\t"""Chi tiet ung vien — CV data + interview history + clean notes."""
\timport json as _json
\tdoc = frappe.get_doc("Job Applicant", name)
\tresult = doc.as_dict()

\tnotes = result.get("notes") or ""
\tcv_data = {}
\tinterview_history = []
\tclean_lines = []

\tfor line in notes.split("\\n"):
\t\tline_s = line.strip()
\t\tif not line_s:
\t\t\tcontinue
\t\tif line_s.startswith("[CVDATA] "):
\t\t\ttry: cv_data = _json.loads(line_s[8:])
\t\t\texcept: pass
\t\telif line_s.startswith("[INTERVIEW] "):
\t\t\ttry: interview_history.append(_json.loads(line_s[12:]))
\t\t\texcept: pass
\t\telif line_s.startswith("[REJECT] "):
\t\t\ttry: result["reject_info"] = _json.loads(line_s[9:])
\t\t\texcept: pass
\t\telif line_s.startswith("[HOLD] "):
\t\t\ttry: result["hold_info"] = _json.loads(line_s[7:])
\t\t\texcept: pass
\t\telif not line_s.startswith("[LOG ") and not line_s.startswith("[DA TUYEN]"):
\t\t\tclean_lines.append(line_s)

\tresult["cv_data"] = cv_data
\tresult["interview_history"] = interview_history
\tresult["clean_notes"] = "\\n".join(clean_lines).strip()
\treturn result'''

# Apply all changes
for old, new in [
    (old_sched, new_sched),
    (old_detail, new_apis),
    (old_detail_body, new_detail_body),
]:
    if old in c:
        c = c.replace(old, new)
        print(f"OK: {old[:50]}...")
    else:
        print(f"FAIL: {old[:50]}...")

with open(path, "w") as f:
    f.write(c)
print("DONE - api.py updated")
