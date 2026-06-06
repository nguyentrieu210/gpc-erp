<template>
  <div class="flex flex-col min-h-screen bg-gray-50">
    <header class="flex items-center gap-2 border-b bg-white px-4 py-3">
      <Button variant="ghost" @click="$router.push('/')"><FeatherIcon name="arrow-left" class="h-4 w-4" /></Button>
      <h1 class="text-lg font-semibold text-gray-900 flex-1">Quản lý nhân sự</h1>
      <button type="button" @click="printBadges" :disabled="badging" class="btn-secondary flex items-center gap-1.5 px-3.5 py-2 text-xs font-bold rounded-xl shadow-sm hover:-translate-y-0.5 transition-all duration-200">
        <FeatherIcon name="credit-card" class="h-3.5 w-3.5" /> {{ badging ? 'Đang...' : 'Thẻ NV' }}
      </button>
      <button type="button" @click="exportCSV()" :disabled="exporting" class="btn-secondary flex items-center gap-1.5 px-3.5 py-2 text-xs font-bold rounded-xl shadow-sm hover:-translate-y-0.5 transition-all duration-200">
        <FeatherIcon name="download" class="h-3.5 w-3.5" /> {{ exporting ? 'Đang xuất...' : 'Xuất CSV' }}
      </button>
      <button type="button" @click="openCreate" class="btn-success flex items-center gap-1.5 px-3.5 py-2 text-xs font-bold rounded-xl shadow-sm hover:shadow-md hover:-translate-y-0.5 transition-all duration-200">
        <FeatherIcon name="user-plus" class="h-3.5 w-3.5" /> Thêm nhân viên
      </button>
    </header>

    <div v-if="toast" class="fixed top-16 right-4 z-50 px-4 py-2 rounded-lg shadow-lg text-sm font-medium" :class="toast.startsWith('✅') ? 'bg-green-50 text-green-800 border border-green-200' : 'bg-red-50 text-red-800 border border-red-200'">{{ toast }}</div>

    <div class="flex-1 overflow-y-auto p-4">
      <div class="max-w-5xl mx-auto space-y-4">

        <!-- Dashboard stats -->
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <div class="rounded-lg border bg-white p-4 shadow-sm text-center"><div class="text-2xl font-bold text-indigo-600">{{ dash.total ?? '—' }}</div><div class="text-xs text-gray-500 mt-0.5">Đang làm việc</div></div>
          <div class="rounded-lg border bg-white p-4 shadow-sm text-center"><div class="text-2xl font-bold text-green-600">{{ dash.new_this_month ?? '—' }}</div><div class="text-xs text-gray-500 mt-0.5">Mới vào tháng này</div></div>
          <div class="rounded-lg border bg-white p-4 shadow-sm text-center"><div class="text-2xl font-bold text-cyan-600">{{ dash.departments ?? '—' }}</div><div class="text-xs text-gray-500 mt-0.5">Phòng ban</div></div>
          <div class="rounded-lg border bg-white p-4 shadow-sm text-center"><div class="text-2xl font-bold text-gray-500">{{ dash.inactive ?? '—' }}</div><div class="text-xs text-gray-500 mt-0.5">Đã nghỉ việc</div></div>
        </div>

        <!-- Cảnh báo -->
        <div v-if="alerts.count" class="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <div v-if="alerts.birthdays?.length" class="rounded-lg border border-pink-200 bg-pink-50/50 p-3">
            <h4 class="text-xs font-semibold text-pink-700 mb-2 flex items-center gap-1"><FeatherIcon name="gift" class="h-3.5 w-3.5" /> Sinh nhật sắp tới</h4>
            <div class="space-y-1"><div v-for="b in alerts.birthdays" :key="b.name" class="text-sm flex items-center justify-between cursor-pointer hover:text-pink-700" @click="$router.push('/employees/' + b.name)"><span class="truncate">{{ b.employee_name }}</span><span class="text-xs text-pink-600 shrink-0">{{ b.days === 0 ? 'Hôm nay 🎉' : 'còn ' + b.days + ' ngày' }}</span></div></div>
          </div>
          <div v-if="alerts.contracts_expiring?.length" class="rounded-lg border border-red-200 bg-red-50/50 p-3">
            <h4 class="text-xs font-semibold text-red-700 mb-2 flex items-center gap-1"><FeatherIcon name="alert-triangle" class="h-3.5 w-3.5" /> Hợp đồng sắp hết hạn</h4>
            <div class="space-y-1"><div v-for="c in alerts.contracts_expiring" :key="c.name" class="text-sm flex items-center justify-between cursor-pointer hover:text-red-700" @click="$router.push('/employees/' + c.name)"><span class="truncate">{{ c.employee_name }}</span><span class="text-xs shrink-0" :class="c.days < 0 ? 'text-red-700 font-medium' : 'text-red-600'">{{ c.days < 0 ? 'Đã hết ' + (-c.days) + ' ngày' : 'còn ' + c.days + ' ngày' }}</span></div></div>
          </div>
          <div v-if="alerts.anniversaries?.length" class="rounded-lg border border-amber-200 bg-amber-50/50 p-3">
            <h4 class="text-xs font-semibold text-amber-700 mb-2 flex items-center gap-1"><FeatherIcon name="award" class="h-3.5 w-3.5" /> Kỷ niệm thâm niên</h4>
            <div class="space-y-1"><div v-for="x in alerts.anniversaries" :key="x.name" class="text-sm flex items-center justify-between cursor-pointer hover:text-amber-700" @click="$router.push('/employees/' + x.name)"><span class="truncate">{{ x.employee_name }}</span><span class="text-xs text-amber-600 shrink-0">{{ x.years }} năm</span></div></div>
          </div>
        </div>


        <!-- Toolbar -->
        <div class="rounded-lg border bg-white shadow-sm p-3 space-y-3">
          <div class="flex items-center gap-2 flex-wrap">
            <input v-model="filter.search" @input="debouncedSearch" placeholder="🔍 Tìm tên, mã NV, SĐT..." class="text-sm border rounded-lg px-3 py-2 flex-1 min-w-[180px]" />
            <select v-model="filter.department" @change="reload" class="text-sm border rounded-lg px-2 py-2">
              <option value="">Tất cả phòng ban</option><option v-for="d in departments" :key="d" :value="d">{{ d }}</option>
            </select>
            <select v-model="filter.status" @change="reload" class="text-sm border rounded-lg px-2 py-2">
              <option value="Active">Đang làm việc</option><option value="Left">Đã nghỉ việc</option><option value="Inactive">Tạm nghỉ</option><option value="">Tất cả</option>
            </select>
            <button type="button" @click="showAdvanced = !showAdvanced" class="text-sm border rounded-lg px-3 py-2 flex items-center gap-1" :class="advancedActive ? 'border-indigo-400 text-indigo-600 bg-indigo-50' : 'text-gray-600'">
              <FeatherIcon name="filter" class="h-3.5 w-3.5" /> Lọc nâng cao <span v-if="advancedActive" class="text-[10px] bg-indigo-500 text-white rounded-full px-1.5">●</span>
            </button>
          </div>

          <!-- Advanced filters -->
          <div v-if="showAdvanced" class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2 pt-2 border-t">
            <select v-model="filter.designation" @change="reload" class="text-xs border rounded-lg px-2 py-1.5"><option value="">Mọi chức vụ</option><option v-for="d in designations" :key="d" :value="d">{{ d }}</option></select>
            <select v-model="filter.gender" @change="reload" class="text-xs border rounded-lg px-2 py-1.5"><option value="">Mọi giới tính</option><option value="Male">Nam</option><option value="Female">Nữ</option><option value="Other">Khác</option></select>
            <select v-model="filter.employment_type" @change="reload" class="text-xs border rounded-lg px-2 py-1.5"><option value="">Mọi loại HĐ</option><option v-for="t in employmentTypes" :key="t" :value="t">{{ t }}</option></select>
            <input v-model.number="filter.salary_min" @change="reload" type="number" placeholder="Lương từ" class="text-xs border rounded-lg px-2 py-1.5" />
            <input v-model.number="filter.salary_max" @change="reload" type="number" placeholder="Lương đến" class="text-xs border rounded-lg px-2 py-1.5" />
            <button type="button" @click="resetFilters" class="text-xs text-gray-500 hover:text-red-500 border rounded-lg px-2 py-1.5">Xóa lọc</button>
            <input v-model="filter.joined_from" @change="reload" type="date" title="Vào làm từ" class="text-xs border rounded-lg px-2 py-1.5" />
            <input v-model="filter.joined_to" @change="reload" type="date" title="Vào làm đến" class="text-xs border rounded-lg px-2 py-1.5" />
          </div>

          <!-- Sort + count -->
          <div class="flex items-center gap-2 flex-wrap text-xs text-gray-600 pt-2 border-t">
            <span class="font-medium">Tổng <b class="text-gray-900">{{ total }}</b> nhân viên</span>
            <div class="flex-1"></div>
            <span>Sắp xếp:</span>
            <select v-model="sortField" @change="reload" class="border rounded-lg px-2 py-1">
              <option value="employee_name">Tên</option><option value="date_of_joining">Ngày vào</option>
              <option value="custom_luong_co_ban">Lương</option><option value="designation">Chức vụ</option><option value="department">Phòng ban</option>
            </select>
            <button type="button" @click="toggleDir" class="border rounded-lg px-2 py-1 hover:bg-gray-50"><FeatherIcon :name="sortDir === 'asc' ? 'arrow-up' : 'arrow-down'" class="h-3.5 w-3.5" /></button>
            <span>·</span><span>Dòng:</span>
            <select v-model.number="pageLength" @change="reload" class="border rounded-lg px-2 py-1"><option :value="20">20</option><option :value="50">50</option><option :value="100">100</option></select>
          </div>
        </div>

        <!-- Bulk action bar -->
        <div v-if="selectedNames.length" class="sticky top-0 z-10 rounded-lg border border-indigo-300 bg-indigo-600 text-white shadow-md px-4 py-2.5 flex items-center gap-2 flex-wrap text-sm">
          <span class="font-semibold">Đã chọn {{ selectedNames.length }}</span>
          <button @click="clearSelection" class="text-indigo-200 hover:text-white text-xs underline">Bỏ chọn</button>
          <div class="flex-1"></div>
          <label class="bg-white/15 hover:bg-white/25 rounded-lg px-3 py-1.5 text-xs flex items-center gap-1 cursor-pointer"><FeatherIcon name="camera" class="h-3.5 w-3.5" /> Upload ảnh<input type="file" accept="image/*" multiple class="hidden" @change="bulkUploadAvatars" /></label>
          <button @click="exportCSV(selectedNames)" class="bg-white/15 hover:bg-white/25 rounded-lg px-3 py-1.5 text-xs flex items-center gap-1"><FeatherIcon name="download" class="h-3.5 w-3.5" /> Xuất CSV</button>
          <button @click="openBulk('department')" class="bg-white/15 hover:bg-white/25 rounded-lg px-3 py-1.5 text-xs flex items-center gap-1"><FeatherIcon name="shuffle" class="h-3.5 w-3.5" /> Đổi phòng ban</button>
          <button @click="openBulk('status')" class="bg-white/15 hover:bg-white/25 rounded-lg px-3 py-1.5 text-xs flex items-center gap-1"><FeatherIcon name="toggle-right" class="h-3.5 w-3.5" /> Đổi trạng thái</button>
          <button @click="bulkDelete" class="bg-red-500/80 hover:bg-red-500 rounded-lg px-3 py-1.5 text-xs flex items-center gap-1"><FeatherIcon name="trash-2" class="h-3.5 w-3.5" /> Xóa</button>
        </div>

        <!-- List -->
        <div v-if="loading && !rows.length" class="flex items-center justify-center py-20"><LoadingIndicator /></div>
        <div v-else-if="!rows.length" class="text-center text-gray-400 py-16 bg-white rounded-lg border">
          <FeatherIcon name="users" class="mx-auto mb-3 h-10 w-10 text-gray-300" />
          <p>Không tìm thấy nhân viên</p>
          <button type="button" class="btn-success px-4 py-2 text-xs font-bold rounded-xl shadow-sm mt-3" @click="openCreate">Thêm nhân viên đầu tiên</button>
        </div>
        <div v-else class="rounded-lg border bg-white shadow-sm overflow-hidden">
          <!-- header row -->
          <div class="flex items-center gap-3 px-4 py-2 border-b bg-gray-50/70 text-[11px] font-semibold text-gray-400 uppercase">
            <input type="checkbox" :checked="allOnPageSelected" @change="toggleSelectAll" class="shrink-0" />
            <span class="flex-1">Nhân viên</span>
            <span class="hidden md:block w-44">Liên hệ</span>
            <span class="hidden lg:block w-28">Vào làm</span>
            <span class="hidden lg:block w-28 text-right">Lương CB</span>
            <span class="w-20 text-center">Trạng thái</span>
            <span class="w-16 text-right">Thao tác</span>
          </div>
          <div class="divide-y">
            <div v-for="emp in rows" :key="emp.name" class="group flex items-center gap-3 px-4 py-2.5 hover:bg-gray-50" :class="{ 'bg-indigo-50/40': selected[emp.name] }">
              <input type="checkbox" :checked="!!selected[emp.name]" @change="toggleSelect(emp.name)" class="shrink-0" @click.stop />
              <div class="h-9 w-9 rounded-full shrink-0 flex items-center justify-center font-semibold text-white text-xs overflow-hidden cursor-pointer" :class="avatarColor(emp.employee_name)" @click="$router.push('/employees/' + emp.name)">
                <img v-if="emp.image" :src="emp.image" class="h-full w-full object-cover" /><span v-else>{{ initials(emp.employee_name) }}</span>
              </div>
              <div class="flex-1 min-w-0 cursor-pointer" @click="$router.push('/employees/' + emp.name)">
                <div class="font-medium text-gray-900 truncate text-sm">{{ emp.employee_name }} <span class="text-[10px] text-gray-400 font-normal">{{ emp.name }}</span></div>
                <div class="text-xs text-gray-500 truncate">{{ emp.designation || 'Chưa có chức vụ' }}<span v-if="emp.department"> · {{ emp.department.split(' - ')[0] }}</span><span v-if="emp.employment_type" class="text-gray-400"> · {{ emp.employment_type }}</span><span class="text-gray-400"> · {{ genderLabel(emp.gender) }}</span></div>
              </div>
              <div class="hidden md:block w-44 text-xs text-gray-500 shrink-0">
                <div v-if="emp.cell_number" class="truncate">📱 {{ emp.cell_number }}</div>
                <div v-if="emp.personal_email || emp.company_email" class="truncate">✉️ {{ emp.personal_email || emp.company_email }}</div>
                <div v-if="!emp.cell_number && !emp.personal_email && !emp.company_email" class="text-gray-300">—</div>
              </div>
              <div class="hidden lg:block w-28 text-xs text-gray-500 shrink-0">
                <div>{{ $fmtDate(emp.date_of_joining) || '—' }}</div>
                <div v-if="tenure(emp.date_of_joining)" class="text-gray-400">{{ tenure(emp.date_of_joining) }}</div>
              </div>
              <div class="hidden lg:block w-28 text-right text-xs shrink-0">
                <span v-if="emp.custom_luong_co_ban" class="font-medium text-emerald-600">{{ money(emp.custom_luong_co_ban) }}</span>
                <span v-else class="text-gray-300">—</span>
              </div>
              <span class="w-20 text-center shrink-0"><span class="text-[10px] px-2 py-0.5 rounded-full" :class="emp.status === 'Active' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'">{{ emp.status === 'Active' ? 'Đang làm' : emp.status === 'Left' ? 'Đã nghỉ' : emp.status === 'Inactive' ? 'Tạm nghỉ' : (emp.status || '—') }}</span></span>
              <div class="w-16 flex items-center justify-end gap-1 shrink-0">
                <button @click.stop="printOneBadge(emp)" class="text-gray-400 hover:text-emerald-600 p-1" title="In thẻ NV"><FeatherIcon name="credit-card" class="h-3.5 w-3.5" /></button>
                <label class="text-gray-400 hover:text-blue-600 p-1 cursor-pointer" title="Upload ảnh"><FeatherIcon name="camera" class="h-3.5 w-3.5" /><input type="file" accept="image/*" class="hidden" @change="e => uploadAvatar(e, emp)" /></label>
                <button @click.stop="openQuickEdit(emp)" class="text-gray-400 hover:text-indigo-600 p-1" title="Sửa nhanh"><FeatherIcon name="edit-2" class="h-3.5 w-3.5" /></button>
                <button @click.stop="$router.push('/employees/' + emp.name + '?tab=decisions')" class="text-gray-400 hover:text-amber-600 p-1" title="Quyết định"><FeatherIcon name="file-text" class="h-3.5 w-3.5" /></button>
              </div>
            </div>
          </div>
        </div>

        <!-- Pagination -->
        <div v-if="pages > 1" class="flex items-center justify-center gap-1 text-sm">
          <button @click="goPage(page - 1)" :disabled="page <= 1" class="px-2.5 py-1.5 rounded-lg border bg-white disabled:opacity-40 hover:bg-gray-50"><FeatherIcon name="chevron-left" class="h-4 w-4" /></button>
          <button v-for="p in pageList" :key="p" @click="typeof p === 'number' && goPage(p)" :disabled="p === '…'" class="min-w-[34px] px-2 py-1.5 rounded-lg border" :class="p === page ? 'bg-indigo-600 text-white border-indigo-600' : (p === '…' ? 'border-transparent cursor-default' : 'bg-white hover:bg-gray-50')">{{ p }}</button>
          <button @click="goPage(page + 1)" :disabled="page >= pages" class="px-2.5 py-1.5 rounded-lg border bg-white disabled:opacity-40 hover:bg-gray-50"><FeatherIcon name="chevron-right" class="h-4 w-4" /></button>
        </div>
      </div>
    </div>

    <!-- Modal: Sửa nhanh -->
    <div v-if="showQuickEdit" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4" @click.self="showQuickEdit = false">
      <div class="bg-white rounded-xl shadow-2xl w-full max-w-md p-6">
        <h2 class="text-lg font-semibold mb-4">Sửa nhanh — {{ qForm.employee_name }}</h2>
        <div class="grid grid-cols-2 gap-3 text-sm">
          <div><label class="text-xs text-gray-500">SĐT</label><input v-model="qForm.cell_number" class="w-full border rounded-lg px-3 py-2" /></div>
          <div><label class="text-xs text-gray-500">Trạng thái</label><select v-model="qForm.status" class="w-full border rounded-lg px-3 py-2"><option value="Active">Đang làm</option><option value="Inactive">Nghỉ việc</option><option value="Left">Đã rời</option></select></div>
          <div><label class="text-xs text-gray-500">Phòng ban</label><select v-model="qForm.department" class="w-full border rounded-lg px-3 py-2"><option value="">—</option><option v-for="d in departments" :key="d" :value="d">{{ d }}</option></select></div>
          <div><label class="text-xs text-gray-500">Chức vụ</label><select v-model="qForm.designation" class="w-full border rounded-lg px-3 py-2"><option value="">—</option><option v-for="d in designations" :key="d" :value="d">{{ d }}</option></select></div>
        </div>
        <div class="flex justify-end gap-2 mt-5">
          <button type="button" class="btn-secondary px-4 py-2 text-xs font-bold rounded-xl" @click="showQuickEdit = false">Hủy</button>
          <button type="button" class="btn-success px-4 py-2 text-xs font-bold rounded-xl" @click="saveQuickEdit" :disabled="qSaving">{{ qSaving ? 'Đang lưu...' : 'Lưu' }}</button>
        </div>
      </div>
    </div>

    <!-- Modal: thao tác hàng loạt -->
    <div v-if="bulkAction" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4" @click.self="bulkAction = ''">
      <div class="bg-white rounded-xl shadow-2xl w-full max-w-sm p-6">
        <h2 class="text-lg font-semibold mb-3">{{ bulkAction === 'department' ? 'Đổi phòng ban' : 'Đổi trạng thái' }} ({{ selectedNames.length }} NV)</h2>
        <select v-model="bulkValue" class="w-full border rounded-lg px-3 py-2 text-sm">
          <option value="">— Chọn —</option>
          <template v-if="bulkAction === 'department'"><option v-for="d in departments" :key="d" :value="d">{{ d }}</option></template>
          <template v-else><option value="Active">Đang làm</option><option value="Inactive">Nghỉ việc</option><option value="Left">Đã rời</option></template>
        </select>
        <div class="flex justify-end gap-2 mt-5">
          <button type="button" class="btn-secondary px-4 py-2 text-xs font-bold rounded-xl" @click="bulkAction = ''">Hủy</button>
          <button type="button" class="btn-success px-4 py-2 text-xs font-bold rounded-xl" @click="submitBulk" :disabled="!bulkValue || bulkBusy">{{ bulkBusy ? 'Đang...' : 'Áp dụng' }}</button>
        </div>
      </div>
    </div>

    <!-- Modal: Thêm nhân viên -->
    <div v-if="showForm" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4" @click.self="showForm = false">
      <div class="bg-white rounded-xl shadow-2xl w-full max-w-lg p-6 max-h-[90vh] overflow-y-auto">
        <h2 class="text-lg font-semibold mb-4">Thêm nhân viên mới</h2>
        <div class="grid grid-cols-2 gap-3">
          <div><label class="text-xs text-gray-500">Họ <span class="text-red-400">*</span></label><input v-model="form.first_name" class="w-full border rounded-lg px-3 py-2 text-sm" placeholder="Nguyễn Văn" /></div>
          <div><label class="text-xs text-gray-500">Tên</label><input v-model="form.last_name" class="w-full border rounded-lg px-3 py-2 text-sm" placeholder="An" /></div>
          <div><label class="text-xs text-gray-500">Giới tính</label><select v-model="form.gender" class="w-full border rounded-lg px-3 py-2 text-sm"><option value="Male">Nam</option><option value="Female">Nữ</option><option value="Other">Khác</option></select></div>
          <div><label class="text-xs text-gray-500">Ngày sinh</label><input v-model="form.date_of_birth" type="date" class="w-full border rounded-lg px-3 py-2 text-sm" /></div>
          <div><label class="text-xs text-gray-500">Ngày vào làm</label><input v-model="form.date_of_joining" type="date" class="w-full border rounded-lg px-3 py-2 text-sm" /></div>
          <div><label class="text-xs text-gray-500">SĐT</label><input v-model="form.cell_number" class="w-full border rounded-lg px-3 py-2 text-sm" placeholder="09xxxxxxxx" /></div>
          <div><label class="text-xs text-gray-500">Phòng ban</label><select v-model="form.department" class="w-full border rounded-lg px-3 py-2 text-sm"><option value="">—</option><option v-for="d in departments" :key="d" :value="d">{{ d }}</option></select></div>
          <div><label class="text-xs text-gray-500">Chức vụ</label><select v-model="form.designation" class="w-full border rounded-lg px-3 py-2 text-sm"><option value="">—</option><option v-for="d in designations" :key="d" :value="d">{{ d }}</option></select></div>
          <div class="col-span-2"><label class="text-xs text-gray-500">Email cá nhân</label><input v-model="form.personal_email" type="email" class="w-full border rounded-lg px-3 py-2 text-sm" placeholder="email@example.com" /></div>
        </div>
        <div class="flex justify-end gap-2 mt-5">
          <button type="button" class="btn-secondary px-4 py-2 text-xs font-bold rounded-xl shadow-sm" @click="showForm = false">Hủy</button>
          <button type="button" class="btn-success px-4 py-2 text-xs font-bold rounded-xl shadow-sm" @click="submitCreate" :disabled="creating">{{ creating ? 'Đang tạo...' : 'Tạo nhân viên' }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { frappeRequest, Button, FeatherIcon, LoadingIndicator } from 'frappe-ui'

const rows = ref([])
const total = ref(0)
const pages = ref(1)
const page = ref(1)
const pageLength = ref(20)
const loading = ref(false)
const toast = ref('')

const dash = ref({})
const alerts = ref({ count: 0 })
const exporting = ref(false)
const badging = ref(false)
const departments = ref([])
const designations = ref([])
const employmentTypes = ref([])

const filter = reactive({ search: '', department: '', status: 'Active', designation: '', gender: '', employment_type: '', salary_min: null, salary_max: null, joined_from: '', joined_to: '' })
const showAdvanced = ref(false)
const sortField = ref('employee_name')
const sortDir = ref('asc')

const selected = reactive({})
const selectedNames = computed(() => Object.keys(selected).filter(n => selected[n]))
const allOnPageSelected = computed(() => rows.value.length > 0 && rows.value.every(r => selected[r.name]))

const bulkAction = ref('')
const bulkValue = ref('')
const bulkBusy = ref(false)

const showQuickEdit = ref(false)
const qSaving = ref(false)
const qForm = reactive({ name: '', employee_name: '', cell_number: '', status: 'Active', department: '', designation: '' })

const showForm = ref(false)
const creating = ref(false)
const form = reactive({ first_name: '', last_name: '', gender: 'Male', date_of_birth: '', date_of_joining: '', cell_number: '', department: '', designation: '', personal_email: '' })

const advancedActive = computed(() => filter.designation || filter.gender || filter.employment_type || filter.salary_min || filter.salary_max || filter.joined_from || filter.joined_to)

const pageList = computed(() => {
  const p = page.value, n = pages.value, out = []
  const push = (x) => out.push(x)
  if (n <= 7) { for (let i = 1; i <= n; i++) push(i); return out }
  push(1)
  if (p > 3) push('…')
  for (let i = Math.max(2, p - 1); i <= Math.min(n - 1, p + 1); i++) push(i)
  if (p < n - 2) push('…')
  push(n)
  return out
})

function showToast(msg, ms = 3000) { toast.value = msg; setTimeout(() => toast.value = '', ms) }
function money(v) { return (Number(v) || 0).toLocaleString('vi-VN') + ' ₫' }
function genderLabel(g) { return { Male: 'Nam', Female: 'Nữ', Other: 'Khác' }[g] || '—' }
function tenure(d) {
  if (!d) return ''
  const s = new Date(d), now = new Date()
  let m = (now.getFullYear() - s.getFullYear()) * 12 + (now.getMonth() - s.getMonth())
  if (now.getDate() < s.getDate()) m--
  if (m < 0) return ''
  const y = Math.floor(m / 12), mo = m % 12
  return [y ? y + ' năm' : '', mo ? mo + ' tháng' : ''].filter(Boolean).join(' ') || '< 1 tháng'
}

let searchTimer = null
function debouncedSearch() { clearTimeout(searchTimer); searchTimer = setTimeout(reload, 350) }

async function fetchPage() {
  loading.value = true
  try {
    const params = { sort_field: sortField.value, sort_dir: sortDir.value, page: page.value, page_length: pageLength.value }
    for (const [k, v] of Object.entries(filter)) { if (v !== null && v !== '' && v !== undefined) params[k] = v }
    const res = await frappeRequest({ url: 'hr.api.get_employees_filtered', method: 'GET', params })
    rows.value = res.data || []
    total.value = res.total || 0
    pages.value = res.pages || 1
  } catch (e) { showToast('❌ ' + (e.message || 'Lỗi tải dữ liệu')) }
  loading.value = false
}
function reload() { page.value = 1; fetchPage() }
function goPage(n) { if (n >= 1 && n <= pages.value && n !== page.value) { page.value = n; fetchPage() } }
function toggleDir() { sortDir.value = sortDir.value === 'asc' ? 'desc' : 'asc'; reload() }
function resetFilters() { Object.assign(filter, { designation: '', gender: '', employment_type: '', salary_min: null, salary_max: null, joined_from: '', joined_to: '' }); reload() }

function toggleSelect(name) { selected[name] = !selected[name] }
function toggleSelectAll() { const all = allOnPageSelected.value; rows.value.forEach(r => selected[r.name] = !all) }
function clearSelection() { Object.keys(selected).forEach(k => delete selected[k]) }

function openBulk(action) { bulkAction.value = action; bulkValue.value = '' }
async function submitBulk() {
  bulkBusy.value = true
  try {
    const r = await frappeRequest({ url: 'hr.api.bulk_update_employees', method: 'POST', params: { names: JSON.stringify(selectedNames.value), field: bulkAction.value, value: bulkValue.value } })
    showToast('✅ Đã cập nhật ' + r.updated + ' NV')
    bulkAction.value = ''; clearSelection()
    await Promise.all([fetchPage(), loadDashboard()])
  } catch (e) { showToast('❌ ' + (e.message || 'Lỗi'), 4000) }
  bulkBusy.value = false
}
async function bulkUploadAvatars(e) {
  const files = e.target.files; if (!files?.length) return
  const names = selectedNames.value
  if (!names.length) { showToast('❌ Chọn NV trước khi upload'); e.target.value = ''; return }
  const fd = new FormData()
  fd.append('employees', JSON.stringify(names))
  for (const f of files) fd.append('avatars', f)
  try {
    const csrf = window.csrf_token || ''
    const res = await fetch('/api/method/hr.api.bulk_upload_avatars', { method: 'POST', headers: { 'X-Frappe-CSRF-Token': csrf }, body: fd })
    const data = await res.json()
    const r = data.message || data
    showToast('✅ Upload ' + (r.updated || 0) + '/' + names.length + ' NV')
    clearSelection(); await fetchPage()
  } catch (er) { showToast('❌ ' + (er.message || 'Lỗi upload')) }
  e.target.value = ''
}

async function bulkDelete() {
  if (!confirm(`Xóa ${selectedNames.value.length} nhân viên đã chọn? (NV có dữ liệu liên kết sẽ được giữ lại)`)) return
  try {
    const r = await frappeRequest({ url: 'hr.api.bulk_delete_employees', method: 'POST', params: { names: JSON.stringify(selectedNames.value) } })
    showToast(`✅ Đã xóa ${r.deleted}` + (r.skipped?.length ? ` · giữ lại ${r.skipped.length} (có liên kết)` : ''), 4500)
    clearSelection()
    await Promise.all([fetchPage(), loadDashboard()])
  } catch (e) { showToast('❌ ' + (e.message || 'Lỗi xóa'), 4000) }
}

function openQuickEdit(emp) {
  Object.assign(qForm, { name: emp.name, employee_name: emp.employee_name, cell_number: emp.cell_number || '', status: emp.status || 'Active', department: emp.department || '', designation: emp.designation || '' })
  showQuickEdit.value = true
}
async function saveQuickEdit() {
  qSaving.value = true
  try {
    await frappeRequest({ url: 'hr.api.update_employee', method: 'POST', params: { name: qForm.name, cell_number: qForm.cell_number, status: qForm.status, department: qForm.department, designation: qForm.designation } })
    showQuickEdit.value = false
    showToast('✅ Đã lưu')
    await fetchPage()
  } catch (e) { showToast('❌ ' + (e.message || 'Lỗi lưu'), 4000) }
  qSaving.value = false
}

async function loadDashboard() { try { dash.value = await frappeRequest({ url: 'hr.api.get_hr_dashboard', method: 'GET', params: {} }) || {} } catch {} }
async function loadAlerts() { try { alerts.value = await frappeRequest({ url: 'hr.api.get_hr_alerts', method: 'GET', params: {} }) || { count: 0 } } catch {} }

async function exportCSV(names = null) {
  exporting.value = true
  try {
    const params = names ? { names: JSON.stringify(names) } : { department: filter.department || undefined, status: filter.status || undefined }
    const res = await frappeRequest({ url: 'hr.api.export_employees_csv', method: 'GET', params })
    const blob = new Blob(['﻿' + (res.content || '')], { type: 'text/csv;charset=utf-8;' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a'); a.href = url; a.download = res.filename || 'nhan_vien.csv'; a.click(); URL.revokeObjectURL(url)
    showToast('✅ Đã xuất ' + (res.count || 0) + ' nhân viên')
  } catch (e) { showToast('❌ ' + (e.message || 'Lỗi xuất CSV'), 4000) }
  exporting.value = false
}

async function printBadges() {
  badging.value = true
  try {
    const names = selectedNames.value.length ? selectedNames.value : null
    const params = names ? { names: JSON.stringify(names) } : {}
    const res = await frappeRequest({ url: 'hr.api.get_employee_badges_batch', method: 'GET', params })
    const w = window.open('', '_blank'); if (w) { w.document.write(res.html); w.document.close() }
    showToast('✅ Mở trang in ' + (res.count || 0) + ' thẻ NV')
  } catch (e) { showToast('❌ ' + (e.message || 'Lỗi in thẻ'), 4000) }
  badging.value = false
}

async function printOneBadge(emp) {
  try {
    const res = await frappeRequest({ url: 'hr.api.get_employee_badge', method: 'GET', params: { name: emp.name } })
    const w = window.open('', '_blank'); if (w) { w.document.write(res.html); w.document.close() }
  } catch (e) { showToast('❌ ' + (e.message || 'Lỗi in thẻ'), 4000) }
}

async function uploadAvatar(e, emp) {
  const f = e.target.files?.[0]; if (!f) return
  try {
    const csrf = window.csrf_token || ''
    const fd = new FormData(); fd.append('file', f); fd.append('is_private', '0'); fd.append('doctype', 'Employee'); fd.append('docname', emp.name); fd.append('fieldname', 'image')
    const res = await fetch('/api/method/upload_file', { method: 'POST', headers: { 'X-Frappe-CSRF-Token': csrf }, body: fd })
    const data = await res.json()
    const url = data.message?.file_url
    if (!url) throw new Error('Upload fail')
    await frappeRequest({ url: 'hr.api.set_employee_image', method: 'POST', params: { name: emp.name, file_url: url } })
    showToast('✅ Đã cập nhật ảnh: ' + emp.employee_name)
    await fetchPage()
  } catch (er) { showToast('❌ ' + (er.message || 'Lỗi upload'), 4000) }
  e.target.value = ''
}

function openCreate() { Object.assign(form, { first_name: '', last_name: '', gender: 'Male', date_of_birth: '', date_of_joining: '', cell_number: '', department: '', designation: '', personal_email: '' }); showForm.value = true }
async function submitCreate() {
  if (!form.first_name.trim()) { showToast('❌ Nhập họ tên nhân viên'); return }
  creating.value = true
  try {
    const r = await frappeRequest({ url: 'hr.api.create_employee', method: 'POST', params: { ...form } })
    showForm.value = false
    showToast('✅ Đã tạo: ' + (r?.employee_name || ''))
    await Promise.all([loadDashboard(), reload()])
  } catch (e) { showToast('❌ ' + (e.message || 'Lỗi tạo nhân viên'), 4000) }
  creating.value = false
}

function initials(name) {
  if (!name) return '?'
  const clean = name.replace(/[^\p{L}\p{N}\s]/gu, '').replace(/\s+/g, ' ').trim()
  if (!clean) return '?'
  const p = clean.split(/\s+/)
  return ((p[0]?.[0] || '') + (p[p.length - 1]?.[0] || '')).toUpperCase()
}
const AVATAR_COLORS = ['bg-indigo-500', 'bg-emerald-500', 'bg-blue-500', 'bg-purple-500', 'bg-pink-500', 'bg-amber-500', 'bg-cyan-500', 'bg-rose-500']
function avatarColor(name) { let h = 0; for (const c of (name || '')) h = (h * 31 + c.charCodeAt(0)) >>> 0; return AVATAR_COLORS[h % AVATAR_COLORS.length] }

onMounted(async () => {
  await Promise.all([
    loadDashboard(), loadAlerts(), fetchPage(),
    frappeRequest({ url: 'hr.api.get_departments', method: 'GET', params: {} }).then(d => departments.value = d || []).catch(() => {}),
    frappeRequest({ url: 'hr.api.get_designations', method: 'GET', params: {} }).then(d => designations.value = d || []).catch(() => {}),
    frappeRequest({ url: 'hr.api.get_employment_types', method: 'GET', params: {} }).then(d => employmentTypes.value = d || []).catch(() => {}),
  ])
})
</script>
