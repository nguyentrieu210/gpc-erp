<template>
  <div class="flex flex-col min-h-screen bg-gray-50">
    <header class="flex items-center gap-2 border-b bg-white px-4 py-3">
      <Button variant="ghost" @click="$router.push('/employees')"><FeatherIcon name="arrow-left" class="h-4 w-4" /></Button>
      <h1 class="text-lg font-semibold text-gray-900 flex-1 truncate">{{ emp.employee_name || 'Đang tải...' }}</h1>
      <Button v-if="emp.name" size="sm" variant="subtle" @click="openEdit"><FeatherIcon name="edit-2" class="h-4 w-4" /> Sửa</Button>
    </header>

    <div v-if="toast" class="fixed top-16 right-4 z-50 px-4 py-2 rounded-lg shadow-lg text-sm font-medium" :class="toast.startsWith('✅') ? 'bg-green-50 text-green-800 border border-green-200' : 'bg-red-50 text-red-800 border border-red-200'">{{ toast }}</div>

    <div class="flex-1 overflow-y-auto p-4">
      <div v-if="loading" class="flex h-full items-center justify-center py-20"><LoadingIndicator /></div>
      <div v-else-if="error" class="text-red-500">{{ error }}</div>
      <div v-else class="max-w-3xl mx-auto space-y-4">

        <!-- Profile card -->
        <div class="app-card p-5 flex items-center gap-4">
          <label class="relative h-16 w-16 rounded-full shrink-0 flex items-center justify-center font-bold text-white text-xl overflow-hidden cursor-pointer group" :class="avatarColor(emp.employee_name)" title="Đổi ảnh đại diện">
            <img v-if="emp.image" :src="emp.image" class="h-full w-full object-cover" />
            <span v-else>{{ initials(emp.employee_name) }}</span>
            <span class="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition flex items-center justify-center">
              <FeatherIcon v-if="!uploadingImg" name="camera" class="h-5 w-5 text-white" />
              <LoadingIndicator v-else class="h-5 w-5 text-white" />
            </span>
            <input type="file" accept="image/*" class="hidden" @change="onAvatarFile" />
          </label>
          <div class="flex-1 min-w-0">
            <h2 class="text-lg font-semibold text-gray-900">{{ emp.employee_name }}</h2>
            <p class="text-sm text-gray-500">{{ emp.designation || 'Chưa có chức vụ' }}<span v-if="emp.department"> · {{ emp.department.split(' - ')[0] }}</span></p>
            <span class="inline-block mt-1 text-[10px] px-2 py-0.5 rounded-full" :class="emp.status === 'Active' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'">{{ emp.status === 'Active' ? 'Đang làm việc' : (emp.status || '—') }}</span>
          </div>
        </div>

        <!-- Nguồn tuyển dụng (liên kết Tuyển dụng ↔ Hồ sơ NV) -->
        <div v-if="source" class="rounded-lg border border-blue-200 bg-blue-50/50 shadow-sm p-4">
          <div class="flex items-center gap-2 mb-2">
            <FeatherIcon name="user-plus" class="h-4 w-4 text-blue-600" />
            <h2 class="text-sm font-semibold text-blue-800">Tuyển dụng từ ứng viên</h2>
          </div>
          <div class="grid grid-cols-2 gap-2 text-sm">
            <div><span class="text-gray-400">Ứng viên</span><div class="font-medium">{{ source.applicant_name || '—' }}</div></div>
            <div><span class="text-gray-400">Vị trí ứng tuyển</span><div class="font-medium">{{ source.job || '—' }}</div></div>
            <div><span class="text-gray-400">Ngày ứng tuyển</span><div class="font-medium">{{ source.applied || '—' }}</div></div>
            <div class="flex items-end">
              <button v-if="source.applicant" @click="$router.push('/applicant/' + encodeURIComponent(source.applicant))" class="text-sm text-blue-600 font-medium hover:underline flex items-center gap-1">
                Xem hồ sơ ứng viên <FeatherIcon name="arrow-right" class="h-3.5 w-3.5" />
              </button>
            </div>
          </div>
        </div>

        <!-- Thông tin chi tiết -->
        <div class="app-card">
          <div class="px-4 py-3 border-b"><h2 class="text-sm font-semibold text-gray-700">📋 Thông tin cá nhân</h2></div>
          <dl class="p-4 grid grid-cols-2 gap-3 text-sm">
            <div><span class="text-gray-400">Mã NV</span><div class="font-medium">{{ emp.name }}</div></div>
            <div><span class="text-gray-400">Công ty</span><div class="font-medium">{{ emp.company || '—' }}</div></div>
            <div><span class="text-gray-400">Phòng ban</span><div class="font-medium">{{ emp.department || '—' }}</div></div>
            <div><span class="text-gray-400">Chức vụ</span><div class="font-medium">{{ emp.designation || '—' }}</div></div>
            <div><span class="text-gray-400">Giới tính</span><div class="font-medium">{{ genderLabel(emp.gender) }}</div></div>
            <div><span class="text-gray-400">Ngày sinh</span><div class="font-medium">{{ $fmtDate(emp.date_of_birth) || '—' }}</div></div>
            <div><span class="text-gray-400">Ngày vào làm</span><div class="font-medium">{{ $fmtDate(emp.date_of_joining) || '—' }}</div></div>
            <div><span class="text-gray-400">SĐT</span><div class="font-medium">{{ emp.cell_number || '—' }}</div></div>
            <div><span class="text-gray-400">Email cá nhân</span><div class="font-medium truncate">{{ emp.personal_email || '—' }}</div></div>
            <div><span class="text-gray-400">Email công ty</span><div class="font-medium truncate">{{ emp.company_email || '—' }}</div></div>
          </dl>
        </div>

        <!-- Hợp đồng lao động -->
        <div class="app-card">
          <div class="px-4 py-3 border-b flex items-center gap-2">
            <FeatherIcon name="file-text" class="h-4 w-4 text-emerald-600" />
            <h2 class="text-sm font-semibold text-gray-700">Hợp đồng lao động</h2>
            <span v-if="contractWarning" class="ml-auto text-[10px] px-2 py-0.5 rounded-full bg-red-100 text-red-700">{{ contractWarning }}</span>
          </div>
          <dl class="p-4 grid grid-cols-2 gap-3 text-sm">
            <div><span class="text-gray-400">Loại hợp đồng</span><div class="font-medium">{{ emp.employment_type || '—' }}</div></div>
            <div><span class="text-gray-400">Ngày vào làm</span><div class="font-medium">{{ $fmtDate(emp.date_of_joining) || '—' }}</div></div>
            <div><span class="text-gray-400">Ngày hết hạn HĐ</span><div class="font-medium">{{ $fmtDate(emp.contract_end_date) || 'Không thời hạn' }}</div></div>
            <div><span class="text-gray-400">Lương cơ bản (Tháng)</span><div class="font-medium text-emerald-600">{{ emp.custom_luong_co_ban ? money(emp.custom_luong_co_ban) : '—' }}</div></div>
            <div><span class="text-gray-400">Lương khoán/năm</span><div class="font-medium text-gray-700">{{ emp.ctc ? money(emp.ctc) : '—' }}</div></div>
          </dl>
        </div>

        <!-- Tabs: Nghỉ phép / Chấm công / Lương -->
        <div class="app-card overflow-hidden">
          <div class="flex border-b">
            <button v-for="t in tabs" :key="t.key" @click="tab = t.key" class="flex-1 py-2.5 text-sm font-medium border-b-2 transition" :class="tab === t.key ? 'border-indigo-600 text-indigo-600' : 'border-transparent text-gray-500'">{{ t.label }}</button>
          </div>
          <div class="p-4">
            <!-- Nghỉ phép -->
            <div v-if="tab === 'leaves'">
              <div v-if="!leaves.length" class="text-center text-gray-400 py-6 text-sm">Chưa có đơn nghỉ phép</div>
              <div v-else class="space-y-2">
                <div v-for="l in leaves" :key="l.name" class="flex items-center justify-between rounded bg-gray-50 px-3 py-2 text-sm">
                  <div>
                    <span class="font-medium">{{ l.leave_type }}</span>
                    <span class="text-gray-500 ml-2 text-xs">{{ $fmtDate(l.from_date) }} → {{ $fmtDate(l.to_date) }}</span>
                  </div>
                  <div class="flex items-center gap-2">
                    <span class="text-xs text-gray-500">{{ l.total_leave_days }} ngày</span>
                    <span class="text-[10px] px-2 py-0.5 rounded-full" :class="leaveChip(l.status)">{{ leaveLabel(l.status) }}</span>
                  </div>
                </div>
              </div>
            </div>
            <!-- Chấm công -->
            <div v-else-if="tab === 'attendance'">
              <p class="text-xs text-gray-400 mb-2">Tháng hiện tại</p>
              <div v-if="!attendance.length" class="text-center text-gray-400 py-6 text-sm">Chưa có dữ liệu chấm công</div>
              <div v-else class="grid grid-cols-2 sm:grid-cols-3 gap-2">
                <div v-for="a in attendance" :key="a.name" class="flex items-center justify-between rounded bg-gray-50 px-3 py-1.5 text-sm">
                  <span class="text-gray-700">{{ a.attendance_date?.slice(5) }}</span>
                  <span class="text-[10px] px-2 py-0.5 rounded-full" :class="attChip(a.status)">{{ a.status }}</span>
                </div>
              </div>
            </div>
            <!-- Lương -->
            <div v-else-if="tab === 'salary'">
              <div class="flex items-center justify-between mb-3">
                <h3 class="text-sm font-semibold text-gray-700">Cấu hình lương & bảo hiểm</h3>
                <Button size="sm" @click="openSalaryConfig"><FeatherIcon name="settings" class="h-3.5 w-3.5" /> Thiết lập</Button>
              </div>
              <p class="text-xs font-medium text-gray-400 uppercase mt-4 mb-1">Phiếu lương gần đây</p>
              <div v-if="!salary.length" class="text-center text-gray-400 py-6 text-sm">Chưa có phiếu lương</div>
              <div v-else class="space-y-2">
                <div v-for="s in salary" :key="s.name" class="rounded bg-gray-50 px-3 py-2 text-sm">
                  <div class="flex items-center justify-between">
                    <span class="font-medium">{{ $fmtDate(s.start_date) }} → {{ $fmtDate(s.end_date) }}</span>
                    <span class="font-semibold text-emerald-600">{{ money(s.net_pay) }}</span>
                  </div>
                  <div class="text-xs text-gray-400 mt-0.5">Gross: {{ money(s.gross_pay) }} · Khấu trừ: {{ money(s.total_deduction) }}</div>
                </div>
              </div>
            </div>
            <!-- Lịch sử thay đổi -->
            <div v-else-if="tab === 'history'">
              <div v-if="!history.length" class="text-center text-gray-400 py-6 text-sm">Chưa có thay đổi nào được ghi nhận</div>
              <div v-else class="space-y-2">
                <div v-for="(h, idx) in history" :key="idx" class="flex items-start gap-3 text-sm">
                  <div class="w-2 h-2 rounded-full bg-indigo-400 mt-1.5 shrink-0"></div>
                  <div class="flex-1">
                    <div class="text-gray-800" v-html="h.content"></div>
                    <div class="text-xs text-gray-400 mt-0.5">{{ h.time }}<span v-if="h.user"> · {{ h.user }}</span></div>
                  </div>
                </div>
              </div>
            </div>
            <!-- Quyết định nhân sự -->
            <div v-else-if="tab === 'decisions'">
              <div class="flex flex-wrap gap-2 mb-4">
                <Button size="sm" @click="openDecision('promotion')"><FeatherIcon name="trending-up" class="h-3.5 w-3.5" /> Bổ nhiệm</Button>
                <Button size="sm" variant="subtle" @click="openDecision('transfer')"><FeatherIcon name="shuffle" class="h-3.5 w-3.5" /> Điều chuyển</Button>
                <Button size="sm" variant="subtle" @click="openDecision('reward')"><FeatherIcon name="award" class="h-3.5 w-3.5" /> Khen thưởng</Button>
                <Button size="sm" variant="subtle" @click="openDecision('discipline')"><FeatherIcon name="alert-triangle" class="h-3.5 w-3.5" /> Kỷ luật</Button>
                <Button size="sm" theme="red" variant="subtle" @click="openDecision('separation')"><FeatherIcon name="log-out" class="h-3.5 w-3.5" /> Thôi việc</Button>
              </div>
              <div v-if="!decisions.length" class="text-center text-gray-400 py-6 text-sm">Chưa có quyết định nào</div>
              <div v-else class="space-y-2">
                <div v-for="(d, i) in decisions" :key="i" class="flex items-center gap-3 rounded bg-gray-50 px-3 py-2 text-sm">
                  <FeatherIcon :name="decIcon(d.kind)" class="h-4 w-4 shrink-0" :class="decColor(d.kind)" />
                  <div class="flex-1 min-w-0">
                    <div class="font-medium text-gray-800">{{ d.label }}</div>
                    <div class="text-xs text-gray-500 truncate" v-html="d.detail"></div>
                  </div>
                  <span class="text-xs text-gray-400 shrink-0">{{ $fmtDate(d.date) }}</span>
                  <button @click="printDecision(d)" class="text-indigo-500 hover:text-indigo-700 shrink-0" title="In quyết định"><FeatherIcon name="printer" class="h-4 w-4" /></button>
                </div>
              </div>
            </div>
            <!-- Timeline công tác -->
            <div v-else-if="tab === 'timeline'">
              <div v-if="!timeline.length" class="text-center text-gray-400 py-6 text-sm">Chưa có dữ liệu</div>
              <div v-else class="relative pl-6 space-y-4">
                <div class="absolute left-[7px] top-1 bottom-1 w-px bg-gray-200"></div>
                <div v-for="(t, i) in timeline" :key="i" class="relative">
                  <div class="absolute -left-[20px] top-0.5 h-4 w-4 rounded-full bg-white border-2 border-indigo-400"></div>
                  <div class="flex items-center gap-2">
                    <FeatherIcon :name="t.icon" class="h-3.5 w-3.5 text-indigo-500 shrink-0" />
                    <span class="font-medium text-sm text-gray-800">{{ t.title }}</span>
                    <span class="text-xs text-gray-400">{{ $fmtDate(t.date) }}</span>
                  </div>
                  <div v-if="t.detail" class="text-xs text-gray-500 mt-0.5 ml-5" v-html="t.detail"></div>
                </div>
              </div>
            </div>
            <!-- Hồ sơ chi tiết -->
            <div v-else-if="tab === 'profile'">
              <div class="flex items-center justify-between mb-3">
                <h3 class="text-sm font-semibold text-gray-700">Hồ sơ chi tiết</h3>
                <Button size="sm" @click="openProfile"><FeatherIcon name="edit-2" class="h-3.5 w-3.5" /> Sửa hồ sơ</Button>
              </div>
              <dl class="grid grid-cols-2 gap-3 text-sm">
                <div><span class="text-gray-400">CCCD/CMND</span><div class="font-medium">{{ profile.cccd || '—' }}</div></div>
                <div><span class="text-gray-400">Mã số thuế</span><div class="font-medium">{{ profile.mst || '—' }}</div></div>
                <div><span class="text-gray-400">Số sổ BHXH</span><div class="font-medium">{{ profile.so_bhxh || '—' }}</div></div>
                <div><span class="text-gray-400">Hôn nhân</span><div class="font-medium">{{ maritalLabel(profile.marital_status) }}</div></div>
                <div><span class="text-gray-400">Ngân hàng</span><div class="font-medium">{{ profile.bank_name || '—' }}</div></div>
                <div><span class="text-gray-400">Số tài khoản</span><div class="font-medium">{{ profile.bank_ac_no || '—' }}</div></div>
                <div><span class="text-gray-400">Liên hệ khẩn cấp</span><div class="font-medium">{{ profile.emergency_contact || '—' }}</div></div>
                <div><span class="text-gray-400">SĐT khẩn cấp</span><div class="font-medium">{{ profile.emergency_phone || '—' }}</div></div>
                <div class="col-span-2"><span class="text-gray-400">Địa chỉ</span><div class="font-medium">{{ profile.current_address || '—' }}</div></div>
              </dl>
              <div v-if="profile.hoc_van && profile.hoc_van.length" class="mt-4">
                <h4 class="text-xs font-semibold text-gray-500 uppercase mb-1">Học vấn</h4>
                <div v-for="(h, i) in profile.hoc_van" :key="i" class="text-sm text-gray-700">• {{ h.truong }} — {{ h.bang_cap }} <span class="text-gray-400">({{ h.nam }})</span></div>
              </div>
              <div v-if="profile.kinh_nghiem && profile.kinh_nghiem.length" class="mt-3">
                <h4 class="text-xs font-semibold text-gray-500 uppercase mb-1">Kinh nghiệm</h4>
                <div v-for="(w, i) in profile.kinh_nghiem" :key="i" class="text-sm text-gray-700">• {{ w.cong_ty }} — {{ w.vi_tri }} <span class="text-gray-400">({{ w.thoi_gian }})</span></div>
              </div>
            </div>
            <!-- Hội nhập / Bàn giao -->
            <div v-else-if="tab === 'checklist'">
              <div v-for="ck in [{kind:'onboarding',label:'Hội nhập (Onboarding)'},{kind:'offboarding',label:'Bàn giao nghỉ việc (Offboarding)'}]" :key="ck.kind" class="mb-5">
                <div class="flex items-center justify-between mb-2">
                  <h3 class="text-sm font-semibold text-gray-700">{{ ck.label }}</h3>
                  <span class="text-xs text-gray-400">{{ doneCount(ck.kind) }}/{{ (checklists[ck.kind] || []).length }}</span>
                </div>
                <div class="space-y-1.5">
                  <label v-for="(item, i) in checklists[ck.kind]" :key="i" class="flex items-center gap-2 text-sm cursor-pointer">
                    <input type="checkbox" :checked="item.done" @change="toggleTask(ck.kind, i)" />
                    <span :class="item.done ? 'line-through text-gray-400' : 'text-gray-700'">{{ item.task }}</span>
                  </label>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal: Sửa hồ sơ chi tiết -->
    <div v-if="showProfile" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4" @click.self="showProfile = false">
      <div class="bg-white rounded-xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto p-6">
        <h2 class="text-lg font-semibold mb-4">Sửa hồ sơ — {{ emp.employee_name }}</h2>
        <div class="grid sm:grid-cols-2 gap-3 text-sm">
          <div><label class="text-xs text-gray-500">CCCD/CMND</label><input v-model="pForm.cccd" class="w-full border rounded-lg px-3 py-2" /></div>
          <div><label class="text-xs text-gray-500">Mã số thuế TNCN</label><input v-model="pForm.mst" class="w-full border rounded-lg px-3 py-2" /></div>
          <div><label class="text-xs text-gray-500">Số sổ BHXH</label><input v-model="pForm.so_bhxh" class="w-full border rounded-lg px-3 py-2" /></div>
          <div><label class="text-xs text-gray-500">Tình trạng hôn nhân</label><select v-model="pForm.marital_status" class="w-full border rounded-lg px-3 py-2"><option value="">—</option><option value="Single">Độc thân</option><option value="Married">Đã kết hôn</option><option value="Divorced">Ly hôn</option><option value="Widowed">Góa</option></select></div>
          <div><label class="text-xs text-gray-500">Ngân hàng</label><input v-model="pForm.bank_name" class="w-full border rounded-lg px-3 py-2" /></div>
          <div><label class="text-xs text-gray-500">Số tài khoản</label><input v-model="pForm.bank_ac_no" class="w-full border rounded-lg px-3 py-2" /></div>
          <div><label class="text-xs text-gray-500">Liên hệ khẩn cấp</label><input v-model="pForm.emergency_contact" class="w-full border rounded-lg px-3 py-2" /></div>
          <div><label class="text-xs text-gray-500">SĐT khẩn cấp</label><input v-model="pForm.emergency_phone" class="w-full border rounded-lg px-3 py-2" /></div>
          <div class="sm:col-span-2"><label class="text-xs text-gray-500">Địa chỉ hiện tại</label><input v-model="pForm.current_address" class="w-full border rounded-lg px-3 py-2" /></div>
        </div>
        <div class="mt-4">
          <div class="flex items-center justify-between mb-1"><label class="text-xs font-semibold text-gray-600 uppercase">Học vấn</label><button @click="pForm.hoc_van.push({truong:'',bang_cap:'',nam:''})" class="text-xs text-indigo-600">+ Thêm</button></div>
          <div v-for="(h, i) in pForm.hoc_van" :key="i" class="flex gap-1.5 mb-1.5 text-xs">
            <input v-model="h.truong" placeholder="Trường" class="border rounded px-2 py-1 flex-1" />
            <input v-model="h.bang_cap" placeholder="Bằng cấp" class="border rounded px-2 py-1 flex-1" />
            <input v-model="h.nam" placeholder="Năm" class="border rounded px-2 py-1 w-16" />
            <button @click="pForm.hoc_van.splice(i,1)" class="text-gray-400 hover:text-red-500"><FeatherIcon name="x" class="h-3.5 w-3.5" /></button>
          </div>
        </div>
        <div class="mt-3">
          <div class="flex items-center justify-between mb-1"><label class="text-xs font-semibold text-gray-600 uppercase">Kinh nghiệm</label><button @click="pForm.kinh_nghiem.push({cong_ty:'',vi_tri:'',thoi_gian:''})" class="text-xs text-indigo-600">+ Thêm</button></div>
          <div v-for="(w, i) in pForm.kinh_nghiem" :key="i" class="flex gap-1.5 mb-1.5 text-xs">
            <input v-model="w.cong_ty" placeholder="Công ty" class="border rounded px-2 py-1 flex-1" />
            <input v-model="w.vi_tri" placeholder="Vị trí" class="border rounded px-2 py-1 flex-1" />
            <input v-model="w.thoi_gian" placeholder="Thời gian" class="border rounded px-2 py-1 w-24" />
            <button @click="pForm.kinh_nghiem.splice(i,1)" class="text-gray-400 hover:text-red-500"><FeatherIcon name="x" class="h-3.5 w-3.5" /></button>
          </div>
        </div>
        <div class="flex justify-end gap-2 mt-5">
          <Button variant="subtle" @click="showProfile = false">Hủy</Button>
          <Button @click="saveProfile" :loading="savingProfile">Lưu hồ sơ</Button>
        </div>
      </div>
    </div>

    <!-- Modal: Quyết định nhân sự -->
    <div v-if="showDec" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4" @click.self="showDec = false">
      <div class="bg-white rounded-xl shadow-2xl w-full max-w-md p-6">
        <h2 class="text-lg font-semibold mb-4">{{ decTitle }}</h2>
        <div class="space-y-3">
          <template v-if="decType === 'promotion'">
            <div><label class="text-xs text-gray-500">Chức vụ mới</label>
              <select v-model="decForm.new_designation" class="w-full border rounded-lg px-3 py-2 text-sm"><option value="">— Giữ nguyên —</option><option v-for="d in designations" :key="d" :value="d">{{ d }}</option></select>
            </div>
            <div><label class="text-xs text-gray-500">Lương cơ bản mới <span class="text-gray-300">(trống = giữ nguyên)</span></label><input v-model.number="decForm.new_luong_co_ban" type="number" class="w-full border rounded-lg px-3 py-2 text-sm" /></div>
          </template>
          <template v-else-if="decType === 'transfer'">
            <div><label class="text-xs text-gray-500">Phòng ban mới <span class="text-red-400">*</span></label>
              <select v-model="decForm.new_department" class="w-full border rounded-lg px-3 py-2 text-sm"><option value="">—</option><option v-for="d in departments" :key="d" :value="d">{{ d }}</option></select>
            </div>
          </template>
          <template v-else-if="decType === 'reward' || decType === 'discipline'">
            <div><label class="text-xs text-gray-500">{{ decType === 'reward' ? 'Hình thức khen thưởng' : 'Hình thức kỷ luật' }} <span class="text-red-400">*</span></label><input v-model="decForm.title" class="w-full border rounded-lg px-3 py-2 text-sm" :placeholder="decType === 'reward' ? 'VD: Nhân viên xuất sắc' : 'VD: Khiển trách'" /></div>
            <div v-if="decType === 'reward'"><label class="text-xs text-gray-500">Số tiền thưởng (VNĐ)</label><input v-model.number="decForm.amount" type="number" class="w-full border rounded-lg px-3 py-2 text-sm" /></div>
          </template>
          <template v-else-if="decType === 'separation'">
            <p class="text-sm text-amber-600 bg-amber-50 rounded-lg p-2">⚠️ Nhân viên sẽ chuyển trạng thái "Đã nghỉ việc".</p>
          </template>
          <div><label class="text-xs text-gray-500">Ngày hiệu lực</label><input v-model="decForm.date" type="date" class="w-full border rounded-lg px-3 py-2 text-sm" /></div>
          <div><label class="text-xs text-gray-500">Lý do / Ghi chú</label><textarea v-model="decForm.reason" rows="2" class="w-full border rounded-lg px-3 py-2 text-sm"></textarea></div>
        </div>
        <div class="flex justify-end gap-2 mt-5">
          <Button variant="subtle" @click="showDec = false">Hủy</Button>
          <Button @click="submitDecision" :loading="decSaving">Ban hành quyết định</Button>
        </div>
      </div>
    </div>

    <!-- Modal: Sửa nhân viên -->
    <div v-if="showEdit" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4" @click.self="showEdit = false">
      <div class="bg-white rounded-xl shadow-2xl w-full max-w-lg p-6 max-h-[90vh] overflow-y-auto">
        <h2 class="text-lg font-semibold mb-4">Sửa thông tin nhân viên</h2>
        <div class="grid grid-cols-2 gap-3">
          <div><label class="text-xs text-gray-500">Họ</label><input v-model="editForm.first_name" class="w-full border rounded-lg px-3 py-2 text-sm" /></div>
          <div><label class="text-xs text-gray-500">Tên</label><input v-model="editForm.last_name" class="w-full border rounded-lg px-3 py-2 text-sm" /></div>
          <div><label class="text-xs text-gray-500">Giới tính</label>
            <select v-model="editForm.gender" class="w-full border rounded-lg px-3 py-2 text-sm"><option value="Male">Nam</option><option value="Female">Nữ</option><option value="Other">Khác</option></select>
          </div>
          <div><label class="text-xs text-gray-500">Ngày sinh</label><input v-model="editForm.date_of_birth" type="date" class="w-full border rounded-lg px-3 py-2 text-sm" /></div>
          <div><label class="text-xs text-gray-500">SĐT</label><input v-model="editForm.cell_number" class="w-full border rounded-lg px-3 py-2 text-sm" /></div>
          <div><label class="text-xs text-gray-500">Trạng thái</label>
            <select v-model="editForm.status" class="w-full border rounded-lg px-3 py-2 text-sm"><option value="Active">Đang làm</option><option value="Inactive">Nghỉ việc</option><option value="Left">Đã rời</option></select>
          </div>
          <div><label class="text-xs text-gray-500">Phòng ban</label>
            <select v-model="editForm.department" class="w-full border rounded-lg px-3 py-2 text-sm"><option value="">—</option><option v-for="d in departments" :key="d" :value="d">{{ d }}</option></select>
          </div>
          <div><label class="text-xs text-gray-500">Chức vụ</label>
            <select v-model="editForm.designation" class="w-full border rounded-lg px-3 py-2 text-sm"><option value="">—</option><option v-for="d in designations" :key="d" :value="d">{{ d }}</option></select>
          </div>
          <div class="col-span-2"><label class="text-xs text-gray-500">Email cá nhân</label><input v-model="editForm.personal_email" type="email" class="w-full border rounded-lg px-3 py-2 text-sm" /></div>
        </div>

        <div class="border-t my-4"></div>
        <p class="text-xs font-semibold text-gray-500 uppercase mb-2">Hợp đồng lao động</p>
        <div class="grid grid-cols-2 gap-3">
          <div><label class="text-xs text-gray-500">Loại hợp đồng</label>
            <select v-model="editForm.employment_type" class="w-full border rounded-lg px-3 py-2 text-sm"><option value="">—</option><option v-for="t in employmentTypes" :key="t" :value="t">{{ t }}</option></select>
          </div>
          <div><label class="text-xs text-gray-500">Ngày hết hạn HĐ</label><input v-model="editForm.contract_end_date" type="date" class="w-full border rounded-lg px-3 py-2 text-sm" /></div>
          <div><label class="text-xs text-gray-500">Lương cơ bản (Tháng)</label><input v-model.number="editForm.custom_luong_co_ban" type="number" class="w-full border rounded-lg px-3 py-2 text-sm" placeholder="VD: 15000000" /></div>
          <div><label class="text-xs text-gray-500">Lương khoán/năm (VNĐ)</label><input v-model.number="editForm.ctc" type="number" class="w-full border rounded-lg px-3 py-2 text-sm bg-gray-50" readonly placeholder="Tự động tính..." /></div>
        </div>

        <div class="flex justify-end gap-2 mt-5">
          <Button variant="subtle" @click="showEdit = false">Hủy</Button>
          <Button @click="submitEdit" :loading="saving">Lưu</Button>
        </div>
      </div>
    </div>

    <!-- Modal: Cấu hình lương & bảo hiểm (VN) -->
    <div v-if="showSalary" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4" @click.self="showSalary = false">
      <div class="bg-white rounded-xl shadow-2xl w-full max-w-3xl max-h-[90vh] overflow-y-auto p-6">
        <h2 class="text-lg font-semibold mb-1">Cấu hình lương — {{ emp.employee_name }}</h2>
        <p class="text-xs text-gray-500 mb-4">Lương cơ bản + phụ cấp + người phụ thuộc → tự tính BHXH/BHYT/BHTN (có trần) và thuế TNCN.</p>

        <div class="grid md:grid-cols-2 gap-6">
          <!-- LEFT: form -->
          <div class="space-y-3">
            <div class="grid grid-cols-2 gap-3">
              <div><label class="text-xs text-gray-500">Loại hợp đồng</label>
                <select v-model="salForm.loai_luong" class="w-full border rounded-lg px-3 py-2 text-sm"><option value="Gross">Gross (NLĐ chịu BH+thuế)</option><option value="Net">Net (thực nhận)</option></select>
              </div>
              <div><label class="text-xs text-gray-500">Vùng lương tối thiểu</label>
                <select v-model="salForm.vung" @change="recalc" class="w-full border rounded-lg px-3 py-2 text-sm"><option v-for="v in ['I','II','III','IV']" :key="v" :value="v">Vùng {{ v }}</option></select>
              </div>
            </div>
            <div><label class="text-xs text-gray-500">Lương cơ bản (đóng BH) <span class="text-red-400">*</span></label>
              <input v-model.number="salForm.luong_co_ban" @input="recalc" type="number" min="0" class="w-full border rounded-lg px-3 py-2 text-sm" placeholder="30000000" />
            </div>
            <div><label class="text-xs text-gray-500">Lương đóng BHXH <span class="text-gray-300">(để trống = lương cơ bản + PC đóng BH)</span></label>
              <input v-model.number="salForm.luong_dong_bhxh" @input="recalc" type="number" min="0" class="w-full border rounded-lg px-3 py-2 text-sm" placeholder="(tự tính)" />
            </div>

            <!-- Gross-up cho HĐ Net -->
            <div v-if="salForm.loai_luong === 'Net'" class="rounded-lg border border-indigo-200 bg-indigo-50/50 p-2.5 flex items-end gap-2">
              <div class="flex-1"><label class="text-xs text-indigo-700">Lương Net mong muốn</label>
                <input v-model.number="netTarget" type="number" min="0" class="w-full border rounded-lg px-2 py-1.5 text-sm" placeholder="25000000" />
              </div>
              <Button size="sm" variant="subtle" :loading="grossingUp" @click="doGrossUp">Quy đổi → lương cơ bản</Button>
            </div>

            <!-- Phụ cấp -->
            <div>
              <div class="flex items-center justify-between mb-1">
                <label class="text-xs font-semibold text-gray-600 uppercase">Phụ cấp</label>
                <select @change="addAllowance($event.target.value); $event.target.value=''" class="text-xs border rounded px-2 py-1">
                  <option value="">+ Thêm phụ cấp</option>
                  <option v-for="a in catalog" :key="a.ten" :value="a.ten">{{ a.ten }}</option>
                  <option value="__custom">+ Khoản tùy chỉnh…</option>
                </select>
              </div>
              <div v-if="!salForm.phu_cap.length" class="text-xs text-gray-400 py-1">Chưa có phụ cấp</div>
              <div v-for="(a, i) in salForm.phu_cap" :key="i" class="flex items-center gap-1.5 mb-1.5 text-xs">
                <input v-model="a.ten" class="border rounded px-2 py-1 flex-1 min-w-0" placeholder="Tên khoản" />
                <input v-model.number="a.so_tien" @input="recalc" type="number" class="border rounded px-2 py-1 w-24" placeholder="0" />
                <label class="flex items-center gap-0.5" title="Chịu thuế TNCN"><input type="checkbox" v-model="a.chiu_thue" @change="recalc" />T</label>
                <label class="flex items-center gap-0.5" title="Tính vào lương đóng BH"><input type="checkbox" v-model="a.dong_bh" @change="recalc" />BH</label>
                <input v-model.number="a.tran_mien" @input="recalc" type="number" class="border rounded px-1 py-1 w-16" title="Mức miễn thuế" placeholder="miễn" />
                <button @click="salForm.phu_cap.splice(i,1); recalc()" class="text-gray-400 hover:text-red-500"><FeatherIcon name="x" class="h-3.5 w-3.5" /></button>
              </div>
              <p class="text-[10px] text-gray-400">T = chịu thuế · BH = đóng bảo hiểm · ô cuối = mức miễn thuế (vd ăn ca 730k)</p>
            </div>

            <!-- Người phụ thuộc -->
            <div>
              <div class="flex items-center justify-between mb-1">
                <label class="text-xs font-semibold text-gray-600 uppercase">Người phụ thuộc (giảm trừ 4.4tr/người)</label>
                <button @click="addDependent" class="text-xs text-indigo-600">+ Thêm</button>
              </div>
              <div v-if="!salForm.nguoi_phu_thuoc.length" class="text-xs text-gray-400 py-1">Chưa khai NPT</div>
              <div v-for="(d, i) in salForm.nguoi_phu_thuoc" :key="i" class="flex items-center gap-1.5 mb-1.5 text-xs">
                <input v-model="d.ho_ten" class="border rounded px-2 py-1 flex-1 min-w-0" placeholder="Họ tên" />
                <select v-model="d.quan_he" class="border rounded px-1 py-1"><option>Con</option><option>Cha</option><option>Mẹ</option><option>Vợ/Chồng</option><option>Khác</option></select>
                <input v-model="d.mst" class="border rounded px-2 py-1 w-24" placeholder="MST" />
                <label class="flex items-center gap-0.5" title="Đang tính giảm trừ"><input type="checkbox" v-model="d.active" @change="recalc" />✓</label>
                <button @click="salForm.nguoi_phu_thuoc.splice(i,1); recalc()" class="text-gray-400 hover:text-red-500"><FeatherIcon name="x" class="h-3.5 w-3.5" /></button>
              </div>
            </div>
          </div>

          <!-- RIGHT: live preview -->
          <div class="rounded-xl border bg-gray-50/60 p-4 text-sm h-fit sticky top-0">
            <div class="text-xs font-semibold text-gray-500 uppercase mb-2">Bảng tính (xem trước)</div>
            <div class="flex justify-between py-1"><span class="text-gray-600">Tổng thu nhập (Gross)</span><span class="font-semibold">{{ money(pv.gross) }}</span></div>
            <div class="flex justify-between py-0.5 text-xs text-gray-500"><span>Lương đóng BH (đã trần)</span><span>{{ money(pv.bh_capped_xhyt) }}</span></div>
            <div class="border-t my-1.5"></div>
            <div class="text-xs text-red-500 font-medium">Khấu trừ (NLĐ)</div>
            <div class="flex justify-between py-0.5"><span class="text-gray-600">BHXH 8%</span><span class="text-red-600">-{{ money(pv.bhxh) }}</span></div>
            <div class="flex justify-between py-0.5"><span class="text-gray-600">BHYT 1.5%</span><span class="text-red-600">-{{ money(pv.bhyt) }}</span></div>
            <div class="flex justify-between py-0.5"><span class="text-gray-600">BHTN 1%</span><span class="text-red-600">-{{ money(pv.bhtn) }}</span></div>
            <div class="flex justify-between py-0.5"><span class="text-gray-600">Thuế TNCN <span class="text-gray-400">(TNTT {{ money(pv.assessable) }})</span></span><span class="text-red-600">-{{ money(pv.pit) }}</span></div>
            <div class="border-t my-1.5"></div>
            <div class="flex justify-between py-1 text-base"><span class="font-semibold text-gray-700">💰 Thực lãnh (Net)</span><span class="font-bold text-green-700">{{ money(pv.net) }}</span></div>
            <div class="flex justify-between py-0.5 text-xs text-gray-400"><span>BH doanh nghiệp đóng</span><span>{{ money(pv.bh_dn) }}</span></div>
          </div>
        </div>

        <div class="flex justify-end gap-2 mt-5">
          <Button variant="subtle" @click="showSalary = false">Hủy</Button>
          <Button @click="saveSalary" :loading="savingSalary">Lưu cấu hình lương</Button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { frappeRequest, Button, FeatherIcon, LoadingIndicator } from 'frappe-ui'

const route = useRoute()
const emp = ref({})
const leaves = ref([])
const attendance = ref([])
const salary = ref([])
const source = ref(null)
const history = ref([])
const loading = ref(true)
const error = ref(null)
const toast = ref('')
const tab = ref('leaves')
const uploadingImg = ref(false)

const departments = ref([])
const designations = ref([])
const employmentTypes = ref([])
const showEdit = ref(false)
const saving = ref(false)
const editForm = reactive({})

// Cấu hình lương VN
const showSalary = ref(false)
const savingSalary = ref(false)
const grossingUp = ref(false)
const netTarget = ref(null)
const catalog = ref([])
const pv = ref({})
const salForm = reactive({ loai_luong: 'Gross', vung: 'I', luong_co_ban: 0, luong_dong_bhxh: 0, phu_cap: [], nguoi_phu_thuoc: [] })
let recalcTimer = null

watch(() => editForm.custom_luong_co_ban, (val) => {
  editForm.ctc = (val || 0) * 12
})

const tabs = [
  { key: 'decisions', label: '📋 Quyết định' },
  { key: 'timeline', label: '🕓 Timeline' },
  { key: 'profile', label: '🗂 Hồ sơ' },
  { key: 'checklist', label: '✅ Hội nhập' },
  { key: 'leaves', label: '🌴 Nghỉ phép' },
  { key: 'attendance', label: '🕐 Chấm công' },
  { key: 'salary', label: '💰 Lương' },
  { key: 'history', label: '📜 Lịch sử' },
]

// Quyết định nhân sự
const decisions = ref([])
const timeline = ref([])
const showDec = ref(false)
const decType = ref('')
const decSaving = ref(false)
const decForm = reactive({ new_designation: '', new_luong_co_ban: null, new_department: '', title: '', amount: null, reason: '', date: '' })
const decTitleMap = { promotion: 'Quyết định bổ nhiệm / thăng chức', transfer: 'Quyết định điều chuyển', reward: 'Quyết định khen thưởng', discipline: 'Quyết định kỷ luật', separation: 'Quyết định thôi việc' }
const decTitle = computed(() => decTitleMap[decType.value] || 'Quyết định')
function decIcon(k) { return { promotion: 'trending-up', transfer: 'shuffle', separation: 'log-out', reward: 'award', discipline: 'alert-triangle' }[k] || 'file-text' }
function decColor(k) { return { promotion: 'text-green-600', transfer: 'text-blue-600', separation: 'text-red-600', reward: 'text-amber-600', discipline: 'text-orange-600' }[k] || 'text-gray-500' }

// Hồ sơ chi tiết + checklist
const profile = ref({})
const showProfile = ref(false)
const savingProfile = ref(false)
const pForm = reactive({ cccd: '', mst: '', so_bhxh: '', bank_name: '', bank_ac_no: '', emergency_contact: '', emergency_phone: '', marital_status: '', current_address: '', hoc_van: [], kinh_nghiem: [] })
const checklists = reactive({ onboarding: [], offboarding: [] })
function maritalLabel(m) { return { Single: 'Độc thân', Married: 'Đã kết hôn', Divorced: 'Ly hôn', Widowed: 'Góa' }[m] || '—' }
function doneCount(kind) { return (checklists[kind] || []).filter(x => x.done).length }

// Cảnh báo hợp đồng sắp/đã hết hạn
const contractWarning = computed(() => {
  if (!emp.value.contract_end_date) return ''
  const end = new Date(emp.value.contract_end_date)
  const days = Math.ceil((end - new Date()) / 86400000)
  if (days < 0) return 'Đã hết hạn'
  if (days <= 30) return `Còn ${days} ngày`
  return ''
})

function showToast(msg, ms = 3000) { toast.value = msg; setTimeout(() => toast.value = '', ms) }

async function load() {
  loading.value = true
  try {
    const res = await frappeRequest({ url: 'hr.api.get_employee_full', method: 'GET', params: { name: route.params.id } })
    emp.value = res.employee || {}
    leaves.value = res.leaves || []
    attendance.value = res.attendance || []
    salary.value = res.salary || []
    source.value = res.recruitment_source || null
    history.value = res.history || []
    loadDecisions(); loadTimeline(); loadProfile(); loadChecklists()
  } catch (e) { error.value = e.message || 'Lỗi tải dữ liệu' }
  loading.value = false
}

async function loadProfile() {
  try { profile.value = await frappeRequest({ url: 'hr.api.get_employee_profile', method: 'GET', params: { name: emp.value.name } }) || {} } catch {}
}
function openProfile() {
  const p = profile.value
  Object.assign(pForm, {
    cccd: p.cccd || '', mst: p.mst || '', so_bhxh: p.so_bhxh || '', bank_name: p.bank_name || '', bank_ac_no: p.bank_ac_no || '',
    emergency_contact: p.emergency_contact || '', emergency_phone: p.emergency_phone || '', marital_status: p.marital_status || '', current_address: p.current_address || '',
    hoc_van: (p.hoc_van || []).map(h => ({ ...h })), kinh_nghiem: (p.kinh_nghiem || []).map(w => ({ ...w })),
  })
  showProfile.value = true
}
async function saveProfile() {
  savingProfile.value = true
  try {
    await frappeRequest({ url: 'hr.api.save_employee_profile', method: 'POST', params: {
      name: emp.value.name, cccd: pForm.cccd, mst: pForm.mst, so_bhxh: pForm.so_bhxh, bank_name: pForm.bank_name, bank_ac_no: pForm.bank_ac_no,
      emergency_contact: pForm.emergency_contact, emergency_phone: pForm.emergency_phone, marital_status: pForm.marital_status, current_address: pForm.current_address,
      hoc_van: JSON.stringify(pForm.hoc_van), kinh_nghiem: JSON.stringify(pForm.kinh_nghiem),
    } })
    showProfile.value = false
    showToast('✅ Đã lưu hồ sơ')
    await loadProfile()
  } catch (e) { showToast('❌ ' + (e.message || 'Lỗi lưu'), 4000) }
  savingProfile.value = false
}
async function loadChecklists() {
  try {
    const [on, off] = await Promise.all([
      frappeRequest({ url: 'hr.api.get_checklist', method: 'GET', params: { employee: emp.value.name, kind: 'onboarding' } }),
      frappeRequest({ url: 'hr.api.get_checklist', method: 'GET', params: { employee: emp.value.name, kind: 'offboarding' } }),
    ])
    checklists.onboarding = on || []; checklists.offboarding = off || []
  } catch {}
}
async function toggleTask(kind, i) {
  checklists[kind][i].done = !checklists[kind][i].done
  try { await frappeRequest({ url: 'hr.api.save_checklist_tasks', method: 'POST', params: { employee: emp.value.name, kind, items: JSON.stringify(checklists[kind]) } }) } catch {}
}

async function loadDecisions() {
  try { decisions.value = await frappeRequest({ url: 'hr.api.get_decisions', method: 'GET', params: { employee: emp.value.name } }) || [] } catch {}
}
async function loadTimeline() {
  try { timeline.value = await frappeRequest({ url: 'hr.api.get_employee_timeline', method: 'GET', params: { employee: emp.value.name } }) || [] } catch {}
}

function openDecision(type) {
  decType.value = type
  Object.assign(decForm, { new_designation: '', new_luong_co_ban: null, new_department: '', title: '', amount: null, reason: '', date: new Date().toISOString().slice(0, 10) })
  showDec.value = true
  if (!designations.value.length) {
    frappeRequest({ url: 'hr.api.get_designations', method: 'GET', params: {} }).then(d => designations.value = d || []).catch(() => {})
  }
  if (!departments.value.length) {
    frappeRequest({ url: 'hr.api.get_departments', method: 'GET', params: {} }).then(d => departments.value = d || []).catch(() => {})
  }
}

async function submitDecision() {
  decSaving.value = true
  const n = emp.value.name, t = decType.value, f = decForm
  try {
    if (t === 'promotion') await frappeRequest({ url: 'hr.api.create_promotion', method: 'POST', params: { employee: n, new_designation: f.new_designation || undefined, new_luong_co_ban: f.new_luong_co_ban || undefined, promotion_date: f.date, reason: f.reason } })
    else if (t === 'transfer') await frappeRequest({ url: 'hr.api.create_transfer', method: 'POST', params: { employee: n, new_department: f.new_department || undefined, transfer_date: f.date, reason: f.reason } })
    else if (t === 'separation') await frappeRequest({ url: 'hr.api.create_separation', method: 'POST', params: { employee: n, separation_date: f.date, reason: f.reason } })
    else await frappeRequest({ url: 'hr.api.create_reward_discipline', method: 'POST', params: { employee: n, kind: t, title: f.title, amount: f.amount || 0, note: f.reason, date: f.date } })
    showDec.value = false
    showToast('✅ Đã ban hành quyết định')
    await load()
  } catch (e) { showToast('❌ ' + (e.message || 'Lỗi ban hành'), 4000) }
  decSaving.value = false
}

async function printDecision(d) {
  try {
    const params = d.doctype === 'Comment'
      ? { kind: d.kind, employee: emp.value.name, payload: JSON.stringify(d.data || {}) }
      : { kind: d.kind, name: d.name }
    const res = await frappeRequest({ url: 'hr.api.get_decision_print', method: 'GET', params })
    const w = window.open('', '_blank')
    if (w) { w.document.write(res.html); w.document.close() }
  } catch (e) { showToast('❌ ' + (e.message || 'Lỗi in quyết định'), 4000) }
}

async function onAvatarFile(e) {
  const f = e.target.files?.[0]
  if (!f) return
  uploadingImg.value = true
  try {
    const fd = new FormData()
    fd.append('file', f)
    fd.append('is_private', '0')
    fd.append('doctype', 'Employee')
    fd.append('docname', emp.value.name)
    fd.append('fieldname', 'image')
    const res = await fetch('/api/method/upload_file', { method: 'POST', headers: { 'X-Frappe-CSRF-Token': window.csrf_token || '' }, body: fd })
    const data = await res.json()
    const url = data.message?.file_url
    if (!url) throw new Error('Upload thất bại')
    await frappeRequest({ url: 'hr.api.set_employee_image', method: 'POST', params: { name: emp.value.name, file_url: url } })
    emp.value.image = url
    showToast('✅ Đã cập nhật ảnh đại diện')
  } catch (err) { showToast('❌ ' + (err.message || 'Lỗi upload ảnh'), 4000) }
  uploadingImg.value = false
  e.target.value = ''
}

function openEdit() {
  Object.assign(editForm, {
    first_name: emp.value.first_name || '', last_name: emp.value.last_name || '',
    gender: emp.value.gender || 'Male', date_of_birth: emp.value.date_of_birth || '',
    cell_number: emp.value.cell_number || '', status: emp.value.status || 'Active',
    department: emp.value.department || '', designation: emp.value.designation || '',
    personal_email: emp.value.personal_email || '',
    employment_type: emp.value.employment_type || '', contract_end_date: emp.value.contract_end_date || '',
    custom_luong_co_ban: emp.value.custom_luong_co_ban || null,
    ctc: emp.value.ctc || null,
  })
  showEdit.value = true
  if (!departments.value.length) {
    frappeRequest({ url: 'hr.api.get_departments', method: 'GET', params: {} }).then(d => departments.value = d || []).catch(() => {})
    frappeRequest({ url: 'hr.api.get_designations', method: 'GET', params: {} }).then(d => designations.value = d || []).catch(() => {})
    frappeRequest({ url: 'hr.api.get_employment_types', method: 'GET', params: {} }).then(d => employmentTypes.value = d || []).catch(() => {})
  }
}

async function submitEdit() {
  saving.value = true
  try {
    await frappeRequest({ url: 'hr.api.update_employee', method: 'POST', params: { name: emp.value.name, ...editForm } })
    showEdit.value = false
    showToast('✅ Đã lưu thay đổi')
    await load()
  } catch (e) { showToast('❌ ' + (e.message || 'Lỗi lưu'), 4000) }
  saving.value = false
}

const activeNptCount = () => salForm.nguoi_phu_thuoc.filter(d => d.active !== false).length

async function openSalaryConfig() {
  showSalary.value = true
  if (!catalog.value.length) {
    frappeRequest({ url: 'hr.api.get_allowance_catalog', method: 'GET', params: {} }).then(d => catalog.value = d || []).catch(() => {})
  }
  try {
    const d = await frappeRequest({ url: 'hr.api.get_employee_salary', method: 'GET', params: { name: emp.value.name } })
    Object.assign(salForm, {
      loai_luong: d.loai_luong || 'Gross', vung: d.vung || 'I',
      luong_co_ban: d.luong_co_ban || 0, luong_dong_bhxh: d.luong_dong_bhxh || 0,
      phu_cap: (d.phu_cap || []).map(a => ({ ten: a.ten, so_tien: a.so_tien || 0, chiu_thue: a.chiu_thue !== false, dong_bh: !!a.dong_bh, tran_mien: a.tran_mien || 0 })),
      nguoi_phu_thuoc: (d.nguoi_phu_thuoc || []).map(x => ({ ho_ten: x.ho_ten || '', quan_he: x.quan_he || 'Con', mst: x.mst || '', active: x.active !== false })),
    })
    pv.value = d.preview || {}
  } catch (e) { showToast('❌ ' + (e.message || 'Lỗi tải cấu hình lương'), 4000) }
}

function recalc() {
  clearTimeout(recalcTimer)
  recalcTimer = setTimeout(async () => {
    try {
      pv.value = await frappeRequest({ url: 'hr.api.preview_salary', method: 'POST', params: {
        luong_co_ban: salForm.luong_co_ban || 0, luong_dong_bhxh: salForm.luong_dong_bhxh || 0, vung: salForm.vung,
        phu_cap: JSON.stringify(salForm.phu_cap), npt_count: activeNptCount(),
      } })
    } catch {}
  }, 300)
}

function addAllowance(name) {
  if (!name) return
  if (name === '__custom') {
    salForm.phu_cap.push({ ten: 'Phụ cấp khác', so_tien: 0, chiu_thue: true, dong_bh: false, tran_mien: 0 })
  } else {
    const c = catalog.value.find(x => x.ten === name)
    salForm.phu_cap.push(c
      ? { ten: c.ten, so_tien: 0, chiu_thue: c.chiu_thue !== false, dong_bh: !!c.dong_bh, tran_mien: c.tran_mien || 0 }
      : { ten: name, so_tien: 0, chiu_thue: true, dong_bh: false, tran_mien: 0 })
  }
  recalc()
}

function addDependent() { salForm.nguoi_phu_thuoc.push({ ho_ten: '', quan_he: 'Con', mst: '', active: true }) }

async function doGrossUp() {
  if (!netTarget.value) { showToast('❌ Nhập lương Net mong muốn'); return }
  grossingUp.value = true
  try {
    const r = await frappeRequest({ url: 'hr.api.gross_up_basic', method: 'POST', params: {
      net_target: netTarget.value, phu_cap: JSON.stringify(salForm.phu_cap),
      npt_count: activeNptCount(), vung: salForm.vung, luong_dong_bhxh: salForm.luong_dong_bhxh || 0,
    } })
    salForm.luong_co_ban = r.luong_co_ban
    pv.value = r.result || {}
    showToast('✅ Lương cơ bản = ' + money(r.luong_co_ban))
  } catch (e) { showToast('❌ ' + (e.message || 'Lỗi quy đổi'), 4000) }
  grossingUp.value = false
}

async function saveSalary() {
  savingSalary.value = true
  try {
    await frappeRequest({ url: 'hr.api.save_employee_salary', method: 'POST', params: {
      name: emp.value.name, loai_luong: salForm.loai_luong, luong_co_ban: salForm.luong_co_ban || 0,
      luong_dong_bhxh: salForm.luong_dong_bhxh || 0, vung: salForm.vung,
      phu_cap: JSON.stringify(salForm.phu_cap), nguoi_phu_thuoc: JSON.stringify(salForm.nguoi_phu_thuoc),
    } })
    showSalary.value = false
    showToast('✅ Đã lưu cấu hình lương')
    await load()
  } catch (e) { showToast('❌ ' + (e.message || 'Lỗi lưu'), 4000) }
  savingSalary.value = false
}

function initials(name) {
  if (!name) return '?'
  const clean = name.replace(/[^\p{L}\p{N}\s]/gu, '').replace(/\s+/g, ' ').trim()
  if (!clean) return '?'
  const parts = clean.split(/\s+/)
  return ((parts[0]?.[0] || '') + (parts[parts.length - 1]?.[0] || '')).toUpperCase()
}
const AVATAR_COLORS = ['bg-indigo-500', 'bg-emerald-500', 'bg-blue-500', 'bg-purple-500', 'bg-pink-500', 'bg-amber-500', 'bg-cyan-500', 'bg-rose-500']
function avatarColor(name) {
  let h = 0
  for (const c of (name || '')) h = (h * 31 + c.charCodeAt(0)) >>> 0
  return AVATAR_COLORS[h % AVATAR_COLORS.length]
}
function genderLabel(g) { return { Male: 'Nam', Female: 'Nữ', Other: 'Khác' }[g] || g || '—' }
function money(v) { return (v || 0).toLocaleString('vi-VN') + ' ₫' }
function leaveLabel(s) { return { Open: 'Chờ duyệt', Approved: 'Đã duyệt', Rejected: 'Từ chối', Cancelled: 'Đã hủy' }[s] || s }
function leaveChip(s) { return { Open: 'bg-amber-100 text-amber-700', Approved: 'bg-green-100 text-green-700', Rejected: 'bg-red-100 text-red-700', Cancelled: 'bg-gray-100 text-gray-500' }[s] || 'bg-gray-100' }
function attChip(s) { return { Present: 'bg-green-100 text-green-700', Absent: 'bg-red-100 text-red-700', 'Half Day': 'bg-amber-100 text-amber-700', 'On Leave': 'bg-blue-100 text-blue-700', 'Work From Home': 'bg-cyan-100 text-cyan-700' }[s] || 'bg-gray-100 text-gray-600' }

const _validTabs = ['decisions', 'timeline', 'profile', 'checklist', 'leaves', 'attendance', 'salary', 'history']
if (route.query.tab && _validTabs.includes(route.query.tab)) tab.value = route.query.tab

onMounted(load)
</script>
