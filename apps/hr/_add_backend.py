import frappe
# Backend additions via bench console

# 1. Add close_job_opening endpoint
add_close = """
@frappe.whitelist()
def close_job_opening(name):
    '''Đóng tin tuyển dụng (set status=Closed).'''
    frappe.db.set_value('Job Opening', name, 'status', 'Closed')
    return {'ok': True, 'name': name}


@frappe.whitelist()
def export_attendance_csv(month=None, year=None, department=None):
    '''Xuất bảng công tháng ra CSV (UTF-8 BOM).'''
    from hr import api
    import csv, io
    grid = api.get_attendance_monthly_grid(month=month, year=year, department=department)
    buf = io.StringIO()
    w = csv.writer(buf)
    header = ['Mã NV', 'Họ tên', 'Phòng ban', 'Chức vụ'] + grid['days'] + ['CC', 'V', 'ĐM', 'Giờ']
    w.writerow(header)
    for r in grid['data']:
        row = [r['name'], r['employee_name'], r['department'], r.get('designation', '')]
        for d in grid['days']:
            cell = r.get(str(grid['month'].split('/')[0].lstrip('0') + '-' + str(d).zfill(2)) or '')
            if isinstance(cell, dict):
                row.append(cell.get('status', ''))
            else:
                row.append('')
        row.extend([r.get('present',0), r.get('absent',0), r.get('late',0), r.get('total_hours',0)])
        w.writerow(row)
    return {'filename': f'bang_cong_{grid["month"].replace("/","_")}.csv', 'content': buf.getvalue(), 'count': len(grid['data'])}


@frappe.whitelist()
def get_attendance_monthly_grid(month=None, year=None, department=None):
    '''Bảng công tháng dạng lưới: mỗi NV 1 dòng, mỗi ngày 1 cột.'''
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
    if department:
        filters['department'] = department
    emps = frappe.get_all('Employee', filters=filters, fields=['name', 'employee_name', 'department', 'designation'], order_by='employee_name asc', limit_page_length=0)

    att_map = {}
    for a in frappe.get_all('Attendance', filters={'docstatus': 1, 'attendance_date': ['between', [str(start), str(end)]]},
            fields=['employee', 'attendance_date', 'status', 'late_entry', 'working_hours'], limit_page_length=0):
        att_map[(a['employee'], str(a['attendance_date']))] = a

    cin_map = defaultdict(list)
    for c in frappe.get_all('Employee Checkin', filters={'time': ['>=', str(start) + ' 00:00:00'], 'time': ['<=', str(end) + ' 23:59:59']},
            fields=['employee', 'time', 'log_type'], order_by='time asc', limit_page_length=0):
        d = str(c['time'])[:10]
        cin_map[(c['employee'], d)].append({'time': str(c['time'])[11:16], 'type': c.get('log_type', 'IN')})

    days = [_date(year, month, d) for d in range(1, last + 1)]
    day_labels = [str(d.day) for d in days]
    day_full = [str(d) for d in days]

    rows = []
    for e in emps:
        row = {'name': e['name'], 'employee_name': e['employee_name'], 'department': e.get('department') or '', 'designation': e.get('designation') or ''}
        present, absent, late, total_hrs = 0, 0, 0, 0.0
        for d in days:
            ds = str(d)
            a = att_map.get((e['name'], ds))
            ci = cin_map.get((e['name'], ds), [])
            in_times = [x['time'] for x in ci if x['type'] == 'IN']
            out_times = [x['time'] for x in ci if x['type'] == 'OUT']
            row[f'd_{ds}'] = {
                'status': (a['status'] if a else ''),
                'late': (1 if a and a.get('late_entry') else 0),
                'hours': (a.get('working_hours', 0) if a else 0),
                'first_in': (in_times[0] if in_times else ''),
                'last_out': (out_times[-1] if out_times else ''),
            }
            if a:
                if a['status'] in ('Present', 'Work From Home', 'Half Day'): present += 1
                elif a['status'] == 'Absent': absent += 1
                if a.get('late_entry'): late += 1
                total_hrs += a.get('working_hours') or 0
        row['present'] = present; row['absent'] = absent; row['late'] = late; row['total_hours'] = round(total_hrs, 1)
        rows.append(row)

    return {'data': rows, 'days': day_labels, 'day_full': day_full, 'month': f'{month:02d}/{year}', 'total_employees': len(emps)}
"""

# Print what was added so I can append it to the file
print("FUNCTIONS_TO_ADD_COUNT", 3)
print("FIRST", "close_job_opening")
print("SECOND", "export_attendance_csv")
print("THIRD", "get_attendance_monthly_grid")
