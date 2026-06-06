<template>
  <div class="flex flex-col min-h-screen bg-gray-100">
    <header class="flex items-center gap-2 border-b bg-white px-4 py-3">
      <Button variant="ghost" @click="goBack" class="hover:!bg-gray-100 !text-gray-700"><FeatherIcon name="arrow-left" class="h-4 w-4" /></Button>
      <h1 class="text-lg font-semibold text-gray-900 flex-1 truncate">{{ app?.applicant_name || 'Ứng viên' }}</h1>
      <button v-if="app" @click="openEditModal" class="p-1.5 hover:bg-gray-100 rounded text-slate-500 hover:text-blue-600" title="Sửa thông tin"><FeatherIcon name="edit" class="h-4 w-4" /></button>
      <button v-if="app" @click="confirmDelete" class="p-1.5 hover:bg-red-50 rounded text-slate-500 hover:text-red-600" title="Xóa"><FeatherIcon name="trash-2" class="h-4 w-4" /></button>
      <Button v-if="linkedEmployee" size="sm" @click="$router.push('/employees/' + linkedEmployee.id)" class="btn-secondary font-medium"><FeatherIcon name="user-check" class="h-4 w-4" /> Hồ sơ NV</Button>
    </header>

    <div class="flex-1 overflow-y-auto p-4">
      <div v-if="loading" class="flex items-center justify-center py-20"><LoadingIndicator /></div>
      <div v-else-if="error" class="p-4 text-red-500">{{ error }}</div>
      <div v-else-if="app" class="max-w-6xl mx-auto space-y-6 animate-fadeIn">

        <!-- Banner (Redesigned Profile Header) -->
        <div class="rounded-2xl text-white p-6 relative overflow-hidden shadow-lg border border-indigo-900/40" style="background: linear-gradient(to right, #0f172a, #070a13, #0f172a) !important;">
          <!-- Decorative blur elements -->
          <div class="absolute -top-10 -right-10 w-40 h-40 bg-indigo-500/20 rounded-full blur-2xl pointer-events-none"></div>
          <div class="absolute -bottom-10 -left-10 w-40 h-40 bg-purple-500/20 rounded-full blur-2xl pointer-events-none"></div>
          
          <div class="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
            <div class="flex items-center gap-5">
              <label class="relative cursor-pointer group shrink-0" title="Tải lên ảnh đại diện">
                <img v-if="cv?.avatar_base64 || customAvatar" :src="customAvatar || ('data:image/jpeg;base64,' + cv.avatar_base64)" class="w-20 h-20 rounded-full object-cover border-4 border-white/10 group-hover:border-white/40 ring-2 ring-white/20 transition-all duration-300 shadow-md" />
                <div v-else class="w-20 h-20 rounded-full flex items-center justify-center text-2xl font-bold text-white group-hover:opacity-90 ring-2 ring-white/20 transition-all" :style="{ background: avatarColor(app.applicant_name) }">{{ initials(app.applicant_name) }}</div>
                <div class="absolute inset-0 rounded-full bg-black/40 flex items-center justify-center opacity-0 group-hover:opacity-100 transition duration-300">
                  <FeatherIcon name="camera" class="h-6 w-6 text-white" />
                </div>
                <input type="file" accept="image/*" class="hidden" @change="onAvatarChange" />
              </label>
              
              <div class="min-w-0 space-y-1.5">
                <div class="flex items-center gap-3 flex-wrap">
                  <h2 class="text-2xl font-extrabold tracking-tight">{{ app.applicant_name }}</h2>
                  <span class="text-xs font-bold px-3 py-1 rounded-full uppercase tracking-wider border backdrop-blur-md shadow-sm" :class="statusChip(app.status)">
                    {{ statusLabel(app.status) }}
                  </span>
                </div>
                <div class="flex flex-wrap items-center gap-x-4 gap-y-1.5 text-sm text-gray-300 font-medium">
                  <span class="flex items-center gap-1.5" v-if="app.email_id"><FeatherIcon name="mail" class="h-3.5 w-3.5 opacity-70" /> {{ app.email_id }}</span>
                  <span class="flex items-center gap-1.5" v-if="app.phone_number"><FeatherIcon name="phone" class="h-3.5 w-3.5 opacity-70" /> {{ app.phone_number }}</span>
                  <span class="flex items-center gap-1.5" v-if="cv?.location"><FeatherIcon name="map-pin" class="h-3.5 w-3.5 opacity-70" /> {{ cv.location }}</span>
                </div>
              </div>
            </div>

            <!-- Fit score & Actions -->
            <div class="flex items-center gap-4 self-start md:self-center shrink-0">
              <div v-if="cv?.fit_score" class="flex flex-col items-center">
                <div class="w-16 h-16 rounded-full flex items-center justify-center text-xl font-extrabold shrink-0 border-2 shadow-md bg-white" :class="fitColor(cv.fit_score)">
                  {{ cv.fit_score }}
                </div>
                <span class="text-[10px] text-slate-300 font-bold mt-1.5 uppercase tracking-widest">AI Fit Score</span>
              </div>
              
              <div class="flex flex-col gap-2">
                <div class="flex gap-2">
                  <Button v-if="canSchedule" size="sm" class="btn-primary shadow-sm font-bold tracking-wide hover:scale-[1.02] active:scale-[0.98] transition-transform" @click="scrollToInterview"><FeatherIcon name="calendar" class="h-3.5 w-3.5 mr-1" /> Phỏng vấn</Button>
                  <Button v-if="app.status !== 'Rejected' && app.status !== 'Accepted'" size="sm" class="btn-primary shadow-sm font-bold tracking-wide hover:scale-[1.02] active:scale-[0.98] transition-transform !bg-amber-600 border border-amber-700 hover:!bg-amber-700 focus:!bg-amber-700 active:!bg-amber-800" @click="openOfferLetterModal"><FeatherIcon name="mail" class="h-3.5 w-3.5 mr-1" /> Thư mời</Button>
                  <Button v-if="canHold" size="sm" variant="subtle" class="!bg-white/10 hover:!bg-white/20 focus:!bg-white/20 active:!bg-white/30 !text-white border border-white/15 shadow-sm font-bold hover:scale-[1.02] active:scale-[0.98] transition-transform" @click="showHoldModal=true"><FeatherIcon name="pause-circle" class="h-3.5 w-3.5 mr-1" /> Cân nhắc</Button>
                </div>
                <div class="flex gap-2">
                  <Button v-if="canReject" size="sm" variant="subtle" class="!bg-red-500/15 hover:!bg-red-500/25 focus:!bg-red-500/25 active:!bg-red-500/35 !text-red-300 border border-red-500/20 shadow-sm font-bold hover:scale-[1.02] active:scale-[0.98] transition-transform" @click="showRejectModal=true"><FeatherIcon name="x-circle" class="h-3.5 w-3.5 mr-1" /> Từ chối</Button>
                  <Button v-if="app.status==='Accepted' && !linkedEmployee" size="sm" class="btn-success shadow-sm font-bold tracking-wide hover:scale-[1.02] active:scale-[0.98] transition-transform" @click="openConvert"><FeatherIcon name="user-plus" class="h-3.5 w-3.5 mr-1" /> Nhận việc</Button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div v-if="toast" class="px-4 py-2.5 rounded-xl text-sm font-bold shadow-sm animate-fadeIn" :class="toast.startsWith('✅') ? 'bg-green-50 text-green-800 border border-green-200' : 'bg-red-50 text-red-800 border border-red-200'">{{ toast }}</div>

        <!-- Linked employee -->
        <div v-if="linkedEmployee" class="flex items-center gap-3 rounded-2xl border border-green-200 bg-green-50/60 px-5 py-4 shadow-sm">
          <FeatherIcon name="check-circle" class="h-5 w-5 text-green-600 shrink-0" />
          <div class="flex-1 text-sm"><span class="font-bold text-green-800">Đã tiếp nhận thành nhân sự chính thức</span><span class="text-green-700"> · {{ linkedEmployee.name }} ({{ linkedEmployee.id }})</span></div>
          <button @click="$router.push('/employees/' + linkedEmployee.id)" class="text-sm text-green-700 font-bold hover:underline shrink-0 flex items-center gap-1">Mở hồ sơ <FeatherIcon name="arrow-right" class="h-3.5 w-3.5" /></button>
        </div>

        <!-- Grid Split layout -->
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 items-start">
          
          <!-- Left Column (2/3 width on desktop) -->
          <div class="lg:col-span-2 space-y-6">
            <!-- Personal Info Card -->
            <div class="app-card p-5">
              <div class="flex items-center justify-between mb-4 pb-3 border-b border-gray-200">
                <h2 class="text-sm font-bold text-gray-800 flex items-center gap-2">
                  <span class="p-1.5 rounded-lg bg-indigo-50 text-indigo-600"><FeatherIcon name="user" class="h-4 w-4" /></span>
                  Thông tin cá nhân hồ sơ
                </h2>
              </div>
              <div class="grid grid-cols-2 sm:grid-cols-3 gap-4 text-xs">
                <div><span class="text-slate-500 font-medium block mb-1">Họ tên ứng viên</span><div class="font-bold text-gray-800 text-sm">{{ app.applicant_name }}</div></div>
                <div><span class="text-slate-500 font-medium block mb-1">Địa chỉ Email</span><div class="font-bold text-gray-800 text-sm break-all">{{ app.email_id || '—' }}</div></div>
                <div><span class="text-slate-500 font-medium block mb-1">Số điện thoại</span><div class="font-bold text-gray-800 text-sm">{{ app.phone_number || '—' }}</div></div>
                <div><span class="text-slate-500 font-medium block mb-1">Chức danh ứng tuyển</span><div class="font-bold text-gray-800 text-sm">{{ app.designation || '—' }}</div></div>
                <div><span class="text-slate-500 font-medium block mb-1">Quốc gia</span><div class="font-bold text-gray-800 text-sm">{{ app.country || '—' }}</div></div>
                <div><span class="text-slate-500 font-medium block mb-1">Giới tính</span><div class="font-bold text-gray-800 text-sm">{{ cv?.gender || '—' }}</div></div>
                <div><span class="text-slate-500 font-medium block mb-1">Nguồn tuyển dụng</span><div class="font-bold text-gray-800 text-sm">{{ app.source_name || app.source || '—' }}</div></div>
                <div><span class="text-slate-500 font-medium block mb-1">Mã tin tuyển dụng</span><div class="font-bold text-gray-800 text-sm truncate">{{ app.job_opening_title || app.job_title || '—' }}</div></div>
                <div><span class="text-slate-500 font-medium block mb-1">Rank lương vị trí</span><div class="font-bold text-indigo-600 text-sm">{{ app.job_salary_range || '—' }}</div></div>
                <div><span class="text-slate-500 font-medium block mb-1">Lương offer phỏng vấn</span><div class="font-bold text-emerald-600 text-sm">{{ app.custom_offered_salary ? fmtMoney(app.custom_offered_salary) + ' VNĐ' : '—' }}</div></div>
                <div><span class="text-slate-500 font-medium block mb-1">Ngày nộp hồ sơ</span><div class="font-bold text-gray-800 text-sm">{{ $fmtDate(app.creation) || '—' }}</div></div>
                <div v-if="cv?.dob"><span class="text-slate-500 font-medium block mb-1">Ngày sinh</span><div class="font-bold text-gray-800 text-sm">{{ cv.dob }}</div></div>
                <div v-if="cv?.location" class="col-span-2"><span class="text-slate-500 font-medium block mb-1">Địa chỉ thường trú</span><div class="font-bold text-gray-800 text-sm">{{ cv.location }}</div></div>
              </div>
              <div v-if="app.lower_range || app.upper_range" class="text-xs mt-4 pt-4 border-t border-gray-200 flex items-center gap-1">
                <span class="text-slate-500 font-medium">Lương mong muốn:</span>
                <span class="font-bold text-emerald-600 bg-emerald-50 px-2.5 py-1 rounded-lg border border-emerald-100 text-sm">
                  💰 {{ fmtMoney(app.lower_range) }}{{ app.lower_range && app.upper_range ? ' - ' : '' }}{{ fmtMoney(app.upper_range) }}
                </span>
              </div>
              <div v-if="app.cover_letter" class="mt-4 pt-4 border-t border-gray-200">
                <div class="text-slate-700 font-bold text-xs mb-2 flex items-center gap-1.5"><FeatherIcon name="edit-2" class="h-3.5 w-3.5" /> Thư giới thiệu (Cover Letter)</div>
                <div class="text-xs text-gray-700 bg-gray-100 rounded-xl p-3.5 leading-relaxed whitespace-pre-wrap max-h-36 overflow-y-auto border border-gray-200">
                  {{ app.cover_letter }}
                </div>
              </div>
              <div v-if="app.reject_info" class="mt-4">
                <div class="text-xs bg-red-50 border border-red-200 rounded-xl p-4">
                  <div class="font-bold text-red-800 flex items-center gap-1.5 text-sm"><FeatherIcon name="x-circle" class="h-4 w-4" /> Lý do từ chối tuyển dụng</div>
                  <div class="text-red-700 mt-2 font-medium leading-relaxed">{{ app.reject_info.reason }}</div>
                  <div v-if="(app.reject_info.missing||[]).length" class="text-xs text-red-600 mt-3 pt-2.5 border-t border-red-100 flex flex-wrap gap-1.5 items-center">
                    <span class="font-bold">Các điểm thiếu sót:</span>
                    <span v-for="tag in app.reject_info.missing" :key="tag" class="bg-red-100 text-red-800 px-2 py-0.5 rounded font-semibold">{{ tag }}</span>
                  </div>
                </div>
              </div>
              <div v-if="app.hold_info" class="mt-4">
                <div class="text-xs bg-amber-50 border border-amber-200 rounded-xl p-4">
                  <div class="font-bold text-amber-800 flex items-center gap-1.5 text-sm"><FeatherIcon name="pause-circle" class="h-4 w-4" /> Thông tin cân nhắc thêm</div>
                  <div class="text-amber-700 mt-2 font-medium leading-relaxed">{{ app.hold_info.reason }}</div>
                  <div v-if="(app.hold_info.missing||[]).length" class="text-xs text-amber-600 mt-3 pt-2.5 border-t border-amber-100 flex flex-wrap gap-1.5 items-center">
                    <span class="font-bold">Hồ sơ cần bổ sung:</span>
                    <span v-for="tag in app.hold_info.missing" :key="tag" class="bg-amber-100 text-amber-800 px-2 py-0.5 rounded font-semibold">{{ tag }}</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- AI Evaluation Card -->
            <div v-if="hasCvData" class="bg-white rounded-2xl border border-gray-300 shadow-sm p-5 space-y-5">
              <div class="flex items-center justify-between pb-3 border-b border-gray-200">
                <h2 class="text-sm font-bold text-gray-800 flex items-center gap-2">
                  <span class="p-1.5 rounded-lg bg-indigo-50 text-indigo-600"><FeatherIcon name="cpu" class="h-4 w-4" /></span>
                  🤖 Trợ lý AI Phân tích hồ sơ
                </h2>
              </div>
              
              <!-- Fit score + summary -->
              <div v-if="cv.fit_score" class="flex items-start gap-4 p-4 rounded-2xl bg-indigo-50/30 border border-indigo-100/50">
                <div class="w-14 h-14 rounded-full flex items-center justify-center text-lg font-extrabold shrink-0 border-2 bg-white shadow-sm" :class="fitColor(cv.fit_score)">
                  {{ cv.fit_score }}
                </div>
                <div class="space-y-1">
                  <div class="text-sm font-bold text-gray-800 flex items-center gap-1.5">
                    {{ cv.fit_level || 'Đo phù hợp hồ sơ' }}
                  </div>
                  <div class="text-xs text-slate-700 leading-relaxed">{{ cv.fit_reason }}</div>
                </div>
              </div>
              
              <div v-if="cv.summary" class="text-xs text-indigo-900 bg-indigo-50/50 rounded-2xl p-4 leading-relaxed border border-indigo-100/30 whitespace-pre-wrap">
                <span class="font-bold block text-indigo-950 mb-1">Tóm tắt ứng viên:</span>
                {{ cv.summary }}
              </div>

              <!-- Strengths & Gaps -->
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-4" v-if="(cv.strengths||[]).length||(cv.gaps||[]).length">
                <!-- Strengths card -->
                <div v-if="(cv.strengths||[]).length" class="bg-emerald-50/30 border border-emerald-100 rounded-2xl p-4 shadow-sm">
                  <div class="text-xs font-extrabold text-emerald-800 mb-3 flex items-center gap-1.5 uppercase tracking-wider">
                    <span class="p-1 rounded bg-emerald-100 text-emerald-600"><FeatherIcon name="check" class="h-3 w-3" /></span>
                    Điểm mạnh nổi bật
                  </div>
                  <ul class="space-y-2">
                    <li v-for="s in cv.strengths" :key="s" class="text-xs text-gray-700 flex items-start gap-2 leading-relaxed">
                      <span class="text-emerald-500 text-sm leading-none mt-0.5">•</span>
                      <span>{{ s }}</span>
                    </li>
                  </ul>
                </div>

                <!-- Gaps card -->
                <div v-if="(cv.gaps||[]).length" class="bg-rose-50/30 border border-rose-100 rounded-2xl p-4 shadow-sm">
                  <div class="text-xs font-extrabold text-rose-800 mb-3 flex items-center gap-1.5 uppercase tracking-wider">
                    <span class="p-1 rounded bg-rose-100 text-rose-600"><FeatherIcon name="alert-triangle" class="h-3 w-3" /></span>
                    Hạn chế / Điểm thiếu sót
                  </div>
                  <ul class="space-y-2">
                    <li v-for="g in cv.gaps" :key="g" class="text-xs text-gray-700 flex items-start gap-2 leading-relaxed">
                      <span class="text-rose-400 text-sm leading-none mt-0.5">•</span>
                      <span>{{ g }}</span>
                    </li>
                  </ul>
                </div>
              </div>

              <!-- Skills -->
              <div v-if="(cv.skills||[]).length" class="pt-2">
                <div class="text-xs font-bold text-slate-700 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                  <FeatherIcon name="zap" class="h-3.5 w-3.5" />
                  Kỹ năng chuyên môn ({{ cv.skills.length }})
                </div>
                <div class="flex flex-wrap gap-1.5">
                  <span v-for="s in cv.skills" :key="s" class="text-xs bg-indigo-50 text-indigo-700 rounded-lg px-2.5 py-1 font-semibold border border-indigo-100/40">{{ s }}</span>
                </div>
              </div>

              <!-- Languages -->
              <div v-if="(cv.languages||[]).length" class="pt-2">
                <div class="text-xs font-bold text-slate-700 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                  <FeatherIcon name="globe" class="h-3.5 w-3.5" />
                  Khả năng ngoại ngữ
                </div>
                <div class="flex flex-wrap gap-2">
                  <span v-for="l in cv.languages" :key="l" class="text-xs bg-gray-100 text-gray-700 rounded-lg px-2.5 py-1 font-semibold border border-gray-300/50">{{ l }}</span>
                </div>
              </div>

              <!-- Timeline for Experience -->
              <div v-if="(cv.experience||[]).length" class="pt-2 space-y-3">
                <div class="text-xs font-bold text-slate-700 uppercase tracking-wider flex items-center gap-1.5">
                  <FeatherIcon name="briefcase" class="h-3.5 w-3.5" />
                  Quá trình kinh nghiệm làm việc
                </div>
                <div class="relative pl-6 border-l-2 border-gray-300 ml-3 space-y-5 py-1">
                  <div v-for="(exp, idx) in cv.experience" :key="idx" class="relative group">
                    <!-- Timeline dot -->
                    <div class="absolute -left-[31px] top-1 w-4 h-4 rounded-full bg-white border-4 border-indigo-600 transition-all group-hover:scale-110 shadow-sm"></div>
                    
                    <div class="text-[10px] text-indigo-600 font-extrabold group-hover:text-indigo-800 transition-colors uppercase tracking-wider" v-if="getYearRange(exp)">
                      {{ getYearRange(exp) }}
                    </div>
                    <div class="text-xs font-bold text-gray-800 mt-0.5 leading-relaxed">
                      {{ cleanTimelineText(exp) }}
                    </div>
                  </div>
                </div>
              </div>

              <!-- Timeline for Education -->
              <div v-if="(cv.education||[]).length" class="pt-2 space-y-3">
                <div class="text-xs font-bold text-slate-700 uppercase tracking-wider flex items-center gap-1.5">
                  <FeatherIcon name="book-open" class="h-3.5 w-3.5" />
                  Lịch sử học vấn & Đào tạo
                </div>
                <div class="relative pl-6 border-l-2 border-gray-300 ml-3 space-y-5 py-1">
                  <div v-for="(edu, idx) in cv.education" :key="idx" class="relative group">
                    <!-- Timeline dot -->
                    <div class="absolute -left-[31px] top-1 w-4 h-4 rounded-full bg-white border-4 border-violet-600 transition-all group-hover:scale-110 shadow-sm"></div>
                    
                    <div class="text-[10px] text-violet-600 font-extrabold group-hover:text-violet-800 transition-colors uppercase tracking-wider" v-if="getYearRange(edu)">
                      {{ getYearRange(edu) }}
                    </div>
                    <div class="text-xs font-bold text-gray-800 mt-0.5 leading-relaxed">
                      {{ cleanTimelineText(edu) }}
                    </div>
                  </div>
                </div>
              </div>

              <!-- Links -->
              <div v-if="(cv.links||[]).length" class="pt-2">
                <div class="text-xs font-bold text-slate-700 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                  <FeatherIcon name="link" class="h-3.5 w-3.5" />
                  Đường dẫn liên kết (Portfolio / Git / LinkedIn)
                </div>
                <div class="flex flex-wrap gap-2">
                  <a v-for="l in cv.links" :key="l" :href="l.startsWith('http')?l:'https://'+l" target="_blank" class="text-xs text-indigo-600 hover:text-indigo-800 font-bold bg-indigo-50/50 hover:bg-indigo-50 border border-indigo-200 rounded-lg px-2.5 py-1 shadow-sm flex items-center gap-1">
                    <FeatherIcon name="external-link" class="h-3 w-3" />
                    {{ l.replace(/^https?:\/\/(www\.)?/, '') }}
                  </a>
                </div>
              </div>
            </div>

            <!-- Interview Card -->
            <div id="interview-section" class="bg-white rounded-2xl border border-gray-300 shadow-sm p-5">
              <div class="flex items-center justify-between mb-4 pb-3 border-b border-gray-200">
                <h2 class="text-sm font-bold text-gray-800 flex items-center gap-2">
                  <span class="p-1.5 rounded-lg bg-indigo-50 text-indigo-600"><FeatherIcon name="calendar" class="h-4 w-4" /></span>
                  Tiến trình phỏng vấn
                </h2>
                <Button v-if="!showScheduleForm" size="sm" class="btn-primary rounded-xl font-bold shadow-sm" @click="openScheduleForm">+ Thêm lịch</Button>
              </div>
              
              <!-- Schedule Form -->
              <div v-if="showScheduleForm" class="p-4 rounded-2xl border border-purple-100 bg-purple-50/10 space-y-4 mb-4">
                <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <label class="text-xs font-bold text-slate-700 block mb-1">Vòng phỏng vấn</label>
                    <select v-model="ivForm.round" class="w-full border border-gray-250 rounded-xl px-3 py-2 text-xs focus:outline-none focus:ring-1 focus:ring-indigo-500 bg-white">
                      <option>Vòng 1</option>
                      <option>Vòng 2</option>
                      <option>Vòng 3</option>
                      <option>Phỏng vấn cuối</option>
                    </select>
                  </div>
                  <div>
                    <label class="text-xs font-bold text-slate-700 block mb-1">Ngày & Giờ</label>
                    <input v-model="ivForm.date" type="datetime-local" class="w-full border border-gray-250 rounded-xl px-3 py-2 text-xs focus:outline-none focus:ring-1 focus:ring-indigo-500 bg-white" />
                  </div>
                  <div>
                    <label class="text-xs font-bold text-slate-700 block mb-1">Người phỏng vấn chính</label>
                    <select v-model="ivForm.interviewer_employee" class="w-full border border-gray-250 rounded-xl px-3 py-2 text-xs focus:outline-none focus:ring-1 focus:ring-indigo-500 bg-white">
                      <option value="">Chọn nhân viên...</option>
                      <option v-for="e in employees" :key="e.name" :value="e.name">
                        {{ e.employee_name }}<span v-if="e.designation"> — {{ e.designation }}</span>
                      </option>
                    </select>
                  </div>
                  <div>
                    <label class="text-xs font-bold text-slate-700 block mb-1">Ghi chú ban đầu</label>
                    <input v-model="ivForm.notes" placeholder="Ghi chú chi tiết..." class="w-full border border-gray-250 rounded-xl px-3 py-2 text-xs focus:outline-none focus:ring-1 focus:ring-indigo-500 bg-white" />
                  </div>
                </div>

                <!-- AI Suggested Questions Panel -->
                <div class="border border-purple-100 rounded-xl bg-purple-50/30 overflow-hidden">
                  <button type="button" @click="showSuggestedQuestions = !showSuggestedQuestions" class="w-full flex items-center justify-between px-4 py-2.5 bg-purple-50/60 hover:bg-purple-50 text-xs font-semibold text-purple-900 transition focus:outline-none">
                    <span class="flex items-center gap-1.5">
                      <span>🤖 Câu hỏi phỏng vấn gợi ý bằng AI</span>
                      <span v-if="aiQuestions.length" class="bg-purple-200 text-purple-800 rounded-full px-1.5 py-0.5 text-[10px]">{{ aiQuestions.length }}</span>
                    </span>
                    <FeatherIcon :name="showSuggestedQuestions ? 'chevron-up' : 'chevron-down'" class="h-3.5 w-3.5" />
                  </button>
                  <div v-if="showSuggestedQuestions" class="p-3 border-t border-purple-100/50 space-y-2.5 max-h-60 overflow-y-auto">
                    <div v-if="loadingAiQuestions" class="flex items-center justify-center py-4 gap-2 text-xs text-purple-700">
                      <div class="w-4.5 h-4.5 rounded-full border-2 border-purple-200 border-t-purple-600 animate-spin"></div>
                      Đang phân tích CV để gợi ý câu hỏi...
                    </div>
                    <div v-else-if="aiQuestionsError" class="text-xs text-red-500 bg-red-50/50 p-2 rounded-lg border border-red-100/50">
                      {{ aiQuestionsError }}
                    </div>
                    <div v-else-if="!aiQuestions.length" class="text-xs text-slate-700 text-center py-4">
                      Không tìm thấy dữ liệu CV phù hợp để gợi ý câu hỏi.
                    </div>
                    <div v-else class="space-y-2">
                      <div v-for="(q, index) in aiQuestions" :key="index" class="p-2.5 bg-white border border-purple-100/70 rounded-lg hover:border-purple-200 transition relative group shadow-sm">
                        <div class="text-xs font-medium text-gray-800 pr-6 leading-relaxed">{{ q.question }}</div>
                        <div class="text-[10px] text-purple-600 mt-1 italic flex items-center gap-1">
                          <span class="font-bold">Mục đích:</span> {{ q.purpose }}
                        </div>
                        <button type="button" @click="copyQuestion(q.question)" class="absolute top-2 right-2 p-1 rounded bg-gray-100 text-slate-500 hover:text-blue-600 hover:bg-blue-50 opacity-0 group-hover:opacity-100 transition shadow-sm" title="Sao chép câu hỏi">
                          <FeatherIcon name="copy" class="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </div>
                  </div>
                </div>

                <div class="flex justify-end gap-2">
                  <Button size="sm" class="btn-secondary rounded-xl font-bold" @click="showScheduleForm=false">Hủy</Button>
                  <Button size="sm" class="btn-primary rounded-xl font-bold shadow-sm" @click="doSchedule" :loading="scheduling">Lên lịch</Button>
                </div>
              </div>

              <!-- Interview List -->
              <div class="space-y-4">
                <div v-if="!interviewHistory.length && !showScheduleForm" class="text-xs text-slate-500 text-center py-12 flex flex-col items-center justify-center gap-2">
                  <FeatherIcon name="calendar" class="h-8 w-8 text-gray-300" />
                  <span>Chưa có lịch sử hoặc kế hoạch phỏng vấn</span>
                </div>
                <div v-else class="space-y-4">
                  <div v-for="iv in interviewHistory" :key="iv.id" class="rounded-2xl border border-gray-200 bg-gray-100/50 p-4 hover:bg-gray-100 transition duration-200">
                    <div class="flex items-start justify-between flex-wrap gap-2">
                      <div class="flex items-center gap-3">
                        <!-- Round Icon indicator -->
                        <div class="w-10 h-10 rounded-xl flex items-center justify-center text-xs font-extrabold shrink-0 shadow-sm" 
                          :class="iv.status==='scheduled'?'bg-purple-100 text-purple-700':iv.status==='passed'?'bg-emerald-100 text-emerald-700':'bg-rose-100 text-rose-700'">
                          {{ (iv.round||'').replace('Vòng ','') }}
                        </div>
                        <div>
                          <div class="text-xs font-bold text-gray-800">{{ (iv.round||'').replace('Vong ','Vòng ').replace('Phong van','Phỏng vấn') }}</div>
                          <div class="text-[10px] text-slate-500 font-semibold mt-0.5">
                            {{ $fmtDateTime(iv.date) }} <span v-if="iv.interviewer" class="text-indigo-600 font-bold">· PV: {{ iv.interviewer }}</span>
                          </div>
                        </div>
                      </div>
                      <div class="flex items-center gap-2">
                        <span class="text-[10px] px-2.5 py-0.5 rounded-full font-bold uppercase tracking-wider border shadow-sm" 
                          :class="iv.status==='scheduled'?'bg-purple-50 text-purple-700 border-purple-200':iv.status==='passed'?'bg-emerald-50 text-emerald-700 border-emerald-200':'bg-rose-50 text-rose-700 border-rose-200'">
                          {{ iv.status==='scheduled'?'⏳ Chờ PV':iv.status==='passed'?'✅ Đạt': '❌ Không đạt' }}
                        </span>
                        <Button v-if="iv.status==='scheduled'" size="sm" class="btn-success rounded-lg text-xs font-bold shadow-sm" @click="openResultForm(iv)">Nhập KQ</Button>
                      </div>
                    </div>

                    <!-- Result Input Form -->
                    <div v-if="resultFormId===iv.id" class="mt-4 pt-4 border-t border-gray-300 space-y-4">
                      <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
                        <div>
                          <label class="text-xs font-bold text-slate-700 block mb-1">Kết quả tuyển</label>
                          <select v-model="resultForm.passed" class="w-full border border-gray-250 rounded-xl px-2 py-1 text-xs focus:outline-none focus:ring-1 focus:ring-indigo-500 bg-white">
                            <option :value="true">Đạt</option>
                            <option :value="false">Không đạt</option>
                          </select>
                        </div>
                        <div>
                          <label class="text-xs font-bold text-slate-700 block mb-1">Đánh giá chung</label>
                          <select v-model="resultForm.rating" class="w-full border border-gray-250 rounded-xl px-2 py-1 text-xs focus:outline-none focus:ring-1 focus:ring-indigo-500 bg-white">
                            <option value="">Chọn loại...</option>
                            <option>Xuất sắc</option>
                            <option>Tốt</option>
                            <option>Khá</option>
                            <option>Trung bình</option>
                            <option>Yếu</option>
                          </select>
                        </div>
                        <div>
                          <label class="text-xs font-bold text-slate-700 block mb-1">Điểm (0-100)</label>
                          <input v-model.number="resultForm.score" type="number" min="0" max="100" class="w-full border border-gray-250 rounded-xl px-2 py-1 text-xs focus:outline-none focus:ring-1 focus:ring-indigo-500 bg-white" />
                        </div>
                      </div>
                      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                        <!-- Điểm mạnh -->
                        <div class="space-y-1.5">
                          <label class="text-xs font-bold text-slate-700 block mb-1">Điểm mạnh ứng viên</label>
                          <div class="max-h-36 overflow-y-auto space-y-0.5 bg-gray-100 rounded-xl p-2.5 border border-gray-300">
                            <label v-for="s in presetStrengths" :key="s" class="flex items-center gap-1.5 cursor-pointer text-xs">
                              <input type="checkbox" :value="s" v-model="resultForm.strengthsChecked" class="w-3.5 h-3.5 rounded accent-green-600" />
                              <span class="text-gray-700 font-medium">{{ s }}</span>
                            </label>
                          </div>
                          <input v-model="resultForm.strengthsCustom" class="w-full border border-gray-250 rounded-xl px-3 py-1.5 text-xs focus:outline-none focus:ring-1 focus:ring-indigo-500 bg-white" placeholder="Thêm điểm mạnh khác..." />
                        </div>
                        <!-- Điểm yếu -->
                        <div class="space-y-1.5">
                          <label class="text-xs font-bold text-slate-700 block mb-1">Hạn chế cần cải thiện</label>
                          <div class="max-h-36 overflow-y-auto space-y-0.5 bg-gray-100 rounded-xl p-2.5 border border-gray-300">
                            <label v-for="w in presetWeaknesses" :key="w" class="flex items-center gap-1.5 cursor-pointer text-xs">
                              <input type="checkbox" :value="w" v-model="resultForm.weaknessesChecked" class="w-3.5 h-3.5 rounded accent-red-500" />
                              <span class="text-gray-700 font-medium">{{ w }}</span>
                            </label>
                          </div>
                          <input v-model="resultForm.weaknessesCustom" class="w-full border border-gray-250 rounded-xl px-3 py-1.5 text-xs focus:outline-none focus:ring-1 focus:ring-indigo-500 bg-white" placeholder="Thêm điểm yếu khác..." />
                        </div>
                      </div>
                      <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                        <div>
                          <label class="text-xs font-bold text-slate-700 block mb-1">Nhận xét tổng quát</label>
                          <textarea v-model="resultForm.notes" class="w-full border border-gray-250 rounded-xl px-3 py-2 text-xs focus:outline-none focus:ring-1 focus:ring-indigo-500 bg-white" rows="2" placeholder="Nhận xét chung..."></textarea>
                        </div>
                        <div>
                          <label class="text-xs font-bold text-slate-700 block mb-1">Ý kiến người PV bổ sung</label>
                          <textarea v-model="resultForm.extra_notes" class="w-full border border-gray-250 rounded-xl px-3 py-2 text-xs focus:outline-none focus:ring-1 focus:ring-indigo-500 bg-white" rows="2" placeholder="Ý kiến khác..."></textarea>
                        </div>
                      </div>

                      <!-- AI Suggested Questions in result -->
                      <div class="border border-purple-100 rounded-xl bg-purple-50/30 overflow-hidden">
                        <button type="button" @click="showSuggestedQuestions = !showSuggestedQuestions" class="w-full flex items-center justify-between px-4 py-2.5 bg-purple-50/60 hover:bg-purple-50 text-xs font-semibold text-purple-900 transition focus:outline-none">
                          <span class="flex items-center gap-1.5">
                            <span>🤖 Câu hỏi phỏng vấn gợi ý bằng AI</span>
                            <span v-if="aiQuestions.length" class="bg-purple-200 text-purple-800 rounded-full px-1.5 py-0.5 text-[10px]">{{ aiQuestions.length }}</span>
                          </span>
                          <FeatherIcon :name="showSuggestedQuestions ? 'chevron-up' : 'chevron-down'" class="h-3.5 w-3.5" />
                        </button>
                        <div v-if="showSuggestedQuestions" class="p-3 border-t border-purple-100/50 space-y-2.5 max-h-60 overflow-y-auto">
                          <div v-if="loadingAiQuestions" class="flex items-center justify-center py-4 gap-2 text-xs text-purple-700">
                            <div class="w-4.5 h-4.5 rounded-full border-2 border-purple-200 border-t-purple-600 animate-spin"></div>
                            Đang phân tích CV...
                          </div>
                          <div v-else-if="aiQuestionsError" class="text-xs text-red-500 bg-red-50/50 p-2 rounded-lg border border-red-100/50">
                            {{ aiQuestionsError }}
                          </div>
                          <div v-else-if="!aiQuestions.length" class="text-xs text-slate-700 text-center py-4">
                            Không có câu hỏi gợi ý.
                          </div>
                          <div v-else class="space-y-2">
                            <div v-for="(q, index) in aiQuestions" :key="index" class="p-2.5 bg-white border border-purple-100/70 rounded-lg hover:border-purple-200 transition relative group shadow-sm">
                              <div class="text-xs font-medium text-gray-800 pr-6 leading-relaxed">{{ q.question }}</div>
                              <div class="text-[10px] text-purple-600 mt-1 italic flex items-center gap-1">
                                <span class="font-bold">Mục đích:</span> {{ q.purpose }}
                              </div>
                              <button type="button" @click="copyQuestion(q.question)" class="absolute top-2 right-2 p-1 rounded bg-gray-100 text-slate-500 hover:text-blue-600 hover:bg-blue-50 opacity-0 group-hover:opacity-100 transition shadow-sm" title="Sao chép câu hỏi">
                                <FeatherIcon name="copy" class="w-3.5 h-3.5" />
                              </button>
                            </div>
                          </div>
                        </div>
                      </div>

                      <div class="flex justify-end gap-2">
                        <Button size="sm" class="btn-secondary rounded-xl font-bold" @click="resultFormId=null">Hủy</Button>
                        <Button size="sm" class="btn-success rounded-xl font-bold shadow-sm" @click="submitResult(iv)" :loading="submittingResult">Lưu kết quả</Button>
                      </div>
                    </div>

                    <!-- Completed Result Display -->
                    <div v-if="iv.status!=='scheduled' && (iv.score || iv.rating)" class="mt-3.5 pt-3.5 border-t border-gray-300 text-xs space-y-2">
                      <div class="flex flex-wrap gap-x-4 gap-y-1">
                        <span><span class="text-slate-500 font-bold">Điểm đánh giá:</span> <strong class="text-indigo-600 font-extrabold">{{ iv.score }}/100</strong></span>
                        <span v-if="iv.rating"><span class="text-slate-500 font-bold">Xếp loại:</span> <strong class="text-amber-600 font-extrabold">{{ iv.rating }}</strong></span>
                      </div>
                      <div v-if="(iv.strengths||[]).length" class="flex items-center gap-1.5 flex-wrap">
                        <span class="text-[10px] font-bold text-emerald-800 bg-emerald-50 border border-emerald-100 rounded px-1.5 py-0.5" v-for="s in iv.strengths" :key="s">+ {{ s }}</span>
                      </div>
                      <div v-if="(iv.weaknesses||[]).length" class="flex items-center gap-1.5 flex-wrap">
                        <span class="text-[10px] font-bold text-rose-800 bg-rose-50 border border-rose-100 rounded px-1.5 py-0.5" v-for="w in iv.weaknesses" :key="w">- {{ w }}</span>
                      </div>
                      <div v-if="iv.notes" class="text-xs text-gray-600 leading-relaxed bg-white border border-gray-200 p-2.5 rounded-lg whitespace-pre-line shadow-sm">
                        <span class="font-bold text-slate-700 block mb-0.5">Nhận xét chính:</span>
                        {{ iv.notes }}
                      </div>
                      <div v-if="iv.extra_notes" class="text-xs text-slate-700 leading-relaxed pl-2.5 border-l-2 border-gray-300">
                        <span class="font-bold block mb-0.5 text-[10px] text-slate-500 uppercase tracking-wider">Ý kiến người PV:</span>
                        {{ iv.extra_notes }}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- CV / Documents Card -->
            <div class="app-card p-5" v-if="app.resume_attachment || app.clean_notes">
              <h2 class="text-sm font-bold text-gray-800 mb-4 flex items-center gap-2">
                <span class="p-1.5 rounded-lg bg-indigo-50 text-indigo-600"><FeatherIcon name="file-text" class="h-4 w-4" /></span>
                Tài liệu & Ghi chú ứng viên
              </h2>
              <div class="space-y-4">
                <!-- CV Attachment Link -->
                <div v-if="app.resume_attachment" class="flex items-center justify-between p-3.5 bg-gray-100 rounded-xl border border-gray-200 hover:bg-gray-100/50 transition">
                  <div class="flex items-center gap-2.5">
                    <span class="p-2 bg-blue-100 text-blue-600 rounded-lg"><FeatherIcon name="paperclip" class="h-4 w-4" /></span>
                    <div>
                      <div class="text-xs font-bold text-gray-800">Tệp tin CV ứng viên</div>
                      <div class="text-[10px] text-gray-450 font-semibold">Đã tải lên hệ thống</div>
                    </div>
                  </div>
                  <a :href="app.resume_attachment" target="_blank" class="text-xs bg-white hover:bg-indigo-600 hover:text-white text-indigo-600 font-bold px-3 py-1.5 rounded-lg border border-indigo-200 transition-colors shadow-sm">
                    Xem chi tiết
                  </a>
                </div>

                <!-- Notes Section -->
                <div v-if="app.clean_notes" class="pt-3 border-t border-gray-200">
                  <div class="text-xs font-extrabold text-slate-700 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                    <FeatherIcon name="edit-3" class="h-3.5 w-3.5" />
                    Ghi chú nội bộ
                  </div>
                  <div class="text-xs text-gray-700 bg-gray-100 rounded-xl p-3.5 leading-relaxed border border-gray-200 whitespace-pre-wrap max-h-48 overflow-y-auto">
                    {{ app.clean_notes }}
                  </div>
                </div>
              </div>
            </div>

          </div> <!-- End Left Column -->

          <!-- Right Column (1/3 width on desktop) -->
          <div class="space-y-6">
            
            <!-- Document Checklist Redesign -->
            <div class="app-card p-5">
              <div class="flex items-center justify-between mb-4 pb-3 border-b border-gray-200">
                <h2 class="text-sm font-bold text-gray-800 flex items-center gap-2">
                  <span class="p-1.5 rounded-lg bg-green-50 text-green-600"><FeatherIcon name="check-square" class="h-4 w-4" /></span>
                  Checklist hồ sơ
                </h2>
                <span class="text-xs font-extrabold text-green-600 bg-green-50 px-2 py-0.5 rounded-full">{{ checkedCount }}/{{ checklist.length }} mục</span>
              </div>
              <div class="space-y-2 max-h-[400px] overflow-y-auto pr-1">
                <div v-if="!checklist.length" class="text-sm text-slate-500 text-center py-6">Chưa có checklist</div>
                <label 
                  v-for="(item, idx) in checklist" 
                  :key="idx" 
                  class="flex items-center gap-3 py-2 px-2.5 rounded-xl cursor-pointer hover:bg-gray-100 transition-colors duration-200 border border-transparent hover:border-gray-50"
                >
                  <!-- Circle Checkbox -->
                  <input 
                    type="checkbox" 
                    :checked="item.done" 
                    @change="toggleChecklist(idx)" 
                    class="w-4.5 h-4.5 rounded-full border-gray-300 text-emerald-600 focus:ring-emerald-500 cursor-pointer accent-emerald-500" 
                  />
                  <span 
                    class="text-sm flex-1 transition-all duration-300" 
                    :class="item.done ? 'text-slate-500 line-through italic' : 'text-gray-700 font-semibold'"
                  >
                    {{ item.label }}
                  </span>
                  <span v-if="item.done" class="text-[10px] text-slate-500 font-semibold shrink-0 bg-gray-100 px-1.5 py-0.5 rounded">{{ $fmtDateTime(item.date) }}</span>
                </label>
              </div>
              <!-- Add custom item -->
              <div class="flex gap-2 pt-3 mt-3 border-t border-gray-200">
                <input v-model="newCheckItem" @keyup.enter="addCheckItem" placeholder="Hồ sơ khác..." class="flex-1 border border-gray-250 rounded-xl px-3 py-1.5 text-xs focus:outline-none focus:ring-1 focus:ring-indigo-500 bg-gray-100/50" />
                <Button size="sm" class="btn-primary rounded-xl font-bold shadow-sm disabled:opacity-50" @click="addCheckItem" :disabled="!newCheckItem.trim()">+ Thêm</Button>
              </div>
            </div>

            <!-- Job Offers -->
            <div v-if="jobOffers.length" class="app-card p-5">
              <h2 class="text-sm font-bold text-gray-800 mb-4 flex items-center gap-2">
                <span class="p-1.5 rounded-lg bg-amber-50 text-amber-600"><FeatherIcon name="mail" class="h-4 w-4" /></span>
                Thư mời · Job Offer
              </h2>
              <div class="space-y-3">
                <div v-for="jo in jobOffers" :key="jo.name" class="rounded-xl border p-3 text-sm">
                  <div class="flex items-center justify-between">
                    <span class="font-semibold text-gray-800">{{ jo.designation }}</span>
                    <span class="text-[10px] px-2 py-0.5 rounded-full" :class="offerChip(jo.status)">{{ offerLabel(jo.status) }}</span>
                  </div>
                  <div v-if="jo.offer_terms" class="mt-1.5 space-y-0.5">
                    <div v-for="(t, i) in jo.offer_terms" :key="i" class="text-xs text-gray-500 flex justify-between">
                      <span>{{ t.offer_term }}</span><span class="font-medium">{{ t.value }}</span>
                    </div>
                  </div>
                  <div class="flex justify-end gap-2 mt-2">
                    <button @click="printOffer(jo)" class="text-xs text-indigo-600 hover:underline">🖨 In thư mời</button>
                    <button v-if="jo.status==='Awaiting Response'" @click="acceptOffer(jo)" class="text-xs text-green-600 hover:underline font-semibold">✅ Nhận lời</button>
                  </div>
                </div>
              </div>
            </div>

            <!-- Activity Log Redesign -->
            <div class="app-card p-5" v-if="activityLog.length">
              <h2 class="text-sm font-bold text-gray-800 mb-4 flex items-center gap-2">
                <span class="p-1.5 rounded-lg bg-indigo-50 text-indigo-600"><FeatherIcon name="activity" class="h-4 w-4" /></span>
                Nhật ký hoạt động
              </h2>
              <div class="space-y-4 max-h-[300px] overflow-y-auto pr-1">
                <div v-for="(log, idx) in activityLog" :key="idx" class="flex gap-3 text-xs">
                  <div class="flex flex-col items-center shrink-0">
                    <div class="w-2.5 h-2.5 rounded-full mt-1 shrink-0 shadow-sm border-2 border-white ring-1" :class="[logIcon(log.action), 'ring-gray-100']"></div>
                    <div v-if="idx < activityLog.length - 1" class="w-0.5 flex-1 bg-gray-100 mt-1"></div>
                  </div>
                  <div class="flex-1 pb-2">
                    <div class="font-bold text-gray-800">{{ logLabel(log.action) }}</div>
                    <div class="text-[10px] text-slate-500 font-semibold mt-0.5">{{ log.time }} · {{ log.user }}</div>
                    <div v-if="log.detail" class="text-[11px] text-slate-700 mt-1 bg-gray-100 rounded-lg p-2 leading-relaxed border border-gray-200/50">{{ log.detail }}</div>
                  </div>
                </div>
              </div>
            </div>

          </div> <!-- End Right Column -->

        </div> <!-- End Grid Split layout -->
      </div>
    </div>

    <!-- Reject Modal -->
    <div v-if="showRejectModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40" @click.self="showRejectModal=false">
      <div class="bg-white rounded-xl shadow-2xl w-full max-w-md mx-4 p-6">
        <h3 class="text-lg font-semibold mb-4">❌ Từ chối ứng viên</h3>
        <div class="space-y-3">
          <div><label class="text-xs text-slate-700">Lý do từ chối</label><textarea v-model="rejectForm.reason" rows="3" class="w-full border rounded-lg px-3 py-2 text-sm" placeholder="VD: Kinh nghiệm chưa phù hợp..."></textarea></div>
          <div><div class="flex items-center justify-between"><label class="text-xs text-slate-700">Yêu cầu còn thiếu</label><button @click="rejectForm.missingReqs.push('')" class="text-xs text-blue-600">+ Thêm</button></div>
            <div class="space-y-1.5 mt-1"><div v-for="(r,i) in rejectForm.missingReqs" :key="i" class="flex gap-2"><input v-model="rejectForm.missingReqs[i]" class="flex-1 border rounded px-2 py-1 text-sm" placeholder="VD: Chưa có chứng chỉ AWS" /><button @click="rejectForm.missingReqs.splice(i,1)" class="text-slate-500 hover:text-red-500"><FeatherIcon name="x" class="h-4 w-4" /></button></div></div>
          </div>
        </div>
        <div class="flex justify-end gap-2 mt-4"><Button @click="showRejectModal=false" class="btn-secondary font-medium">Hủy</Button><Button @click="doReject" :loading="actionLoading" class="btn-danger font-bold">Xác nhận từ chối</Button></div>
      </div>
    </div>

    <!-- Hold Modal -->
    <div v-if="showHoldModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40" @click.self="showHoldModal=false">
      <div class="bg-white rounded-xl shadow-2xl w-full max-w-md mx-4 p-6">
        <h3 class="text-lg font-semibold mb-4">🤔 Cân nhắc</h3>
        <div class="space-y-3">
          <div><label class="text-xs text-slate-700">Lý do</label><input v-model="holdForm.reason" class="w-full border rounded-lg px-3 py-2 text-sm" placeholder="VD: Cần thêm thời gian đánh giá..." /></div>
          <div><div class="flex items-center justify-between"><label class="text-xs text-slate-700">Cần bổ sung thêm</label><button @click="holdForm.missingReqs.push('')" class="text-xs text-blue-600">+ Thêm</button></div>
            <div class="space-y-1.5 mt-1"><div v-for="(r,i) in holdForm.missingReqs" :key="i" class="flex gap-2"><input v-model="holdForm.missingReqs[i]" class="flex-1 border rounded px-2 py-1 text-sm" placeholder="VD: Bổ sung chứng chỉ XYZ" /><button @click="holdForm.missingReqs.splice(i,1)" class="text-slate-500 hover:text-red-500"><FeatherIcon name="x" class="h-4 w-4" /></button></div></div>
          </div>
        </div>
        <div class="flex justify-end gap-2 mt-4"><Button @click="showHoldModal=false" class="btn-secondary font-medium">Hủy</Button><Button @click="doHold" :loading="actionLoading" class="btn-warning font-bold">Xác nhận cân nhắc</Button></div>
      </div>
    </div>

    <!-- Convert Modal -->
    <div v-if="showConvert" class="fixed inset-0 z-50 flex items-start justify-center bg-black/40 pt-8 overflow-y-auto" @click.self="showConvert=false">
      <div class="bg-white rounded-xl shadow-2xl w-full max-w-lg mx-4 mb-8 p-6 space-y-4">
        <h3 class="text-lg font-semibold">👤 Tạo Nhân viên từ ứng viên</h3>
        <p class="text-sm text-slate-700 -mt-2">Thông tin tự động điền từ CV và hồ sơ ứng viên</p>

        <div class="grid grid-cols-2 gap-3">
          <div><label class="text-xs text-slate-700">Họ</label><input v-model="convertForm.first_name" class="w-full border rounded px-3 py-2 text-sm" placeholder="Họ..." /></div>
          <div><label class="text-xs text-slate-700">Tên</label><input v-model="convertForm.last_name" class="w-full border rounded px-3 py-2 text-sm" placeholder="Tên..." /></div>
        </div>
        <div class="grid grid-cols-3 gap-3">
          <div><label class="text-xs text-slate-700">Giới tính</label><select v-model="convertForm.gender" class="w-full border rounded px-3 py-2 text-sm"><option value="">—</option><option>Nam</option><option>Nữ</option><option>Khác</option></select></div>
          <div><label class="text-xs text-slate-700">Ngày sinh</label><input v-model="convertForm.dob" type="date" class="w-full border rounded px-3 py-2 text-sm" /></div>
          <div><label class="text-xs text-slate-700">Ngày vào làm</label><input v-model="convertForm.joining" type="date" class="w-full border rounded px-3 py-2 text-sm" /></div>
        </div>
        <div class="grid grid-cols-2 gap-3">
          <div><label class="text-xs text-slate-700">Email cá nhân</label><input v-model="convertForm.email" class="w-full border rounded px-3 py-2 text-sm bg-gray-100" readonly /></div>
          <div><label class="text-xs text-slate-700">SĐT</label><input v-model="convertForm.phone" class="w-full border rounded px-3 py-2 text-sm bg-gray-100" readonly /></div>
        </div>
        <div><label class="text-xs text-slate-700">Địa chỉ</label><input v-model="convertForm.location" class="w-full border rounded px-3 py-2 text-sm" placeholder="Nhập địa chỉ..." /></div>
        <div class="grid grid-cols-2 gap-3">
          <div><label class="text-xs text-slate-700">Chức danh</label><select v-model="convertForm.designation" class="w-full border rounded px-3 py-2 text-sm"><option value="">—</option><option v-for="d in designations" :key="d" :value="d">{{ d }}</option></select></div>
          <div><label class="text-xs text-slate-700">Phòng ban</label><select v-model="convertForm.department" class="w-full border rounded px-3 py-2 text-sm"><option value="">—</option><option v-for="d in departments" :key="d" :value="d">{{ d }}</option></select></div>
        </div>
        <div class="grid grid-cols-2 gap-3">
          <div><label class="text-xs text-slate-700">Công ty</label><input v-model="convertForm.company" class="w-full border rounded px-3 py-2 text-sm" placeholder="GPC..." /></div>
          <div><label class="text-xs text-slate-700">Mức lương chính thức (Offer)</label><input v-model.number="convertForm.salary" type="number" class="w-full border rounded px-3 py-2 text-sm" placeholder="VD: 15000000" /></div>
        </div>

        <div class="flex justify-end gap-2 pt-2"><Button @click="showConvert=false" class="btn-secondary font-medium">Hủy</Button><Button @click="doConvert" :loading="converting" class="btn-success font-bold shadow-sm">Tạo nhân viên</Button></div>
      </div>
    </div>

    <!-- Offer Letter Modal -->
    <div v-if="showOfferLetterModal" class="fixed inset-0 z-50 flex items-start justify-center bg-black/40 pt-6 overflow-y-auto" @click.self="showOfferLetterModal=false">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-2xl mx-4 mb-8 overflow-hidden">
        <!-- Modal Header -->
        <div class="bg-gradient-to-r from-amber-500 to-orange-500 px-6 py-4 flex items-center justify-between">
          <div class="flex items-center gap-3">
            <div class="w-9 h-9 rounded-xl bg-white/20 flex items-center justify-center">
              <FeatherIcon name="mail" class="h-5 w-5 text-white" />
            </div>
            <div>
              <h3 class="text-base font-bold text-white">Gửi thư mời nhận việc</h3>
              <p class="text-xs text-amber-100">{{ app?.applicant_name }}</p>
            </div>
          </div>
          <button @click="showOfferLetterModal=false" class="text-white/70 hover:text-white transition">
            <FeatherIcon name="x" class="h-5 w-5" />
          </button>
        </div>

        <div class="p-6 space-y-4">
          <!-- Template selector + AI Render -->
          <div class="bg-amber-50 border border-amber-200 rounded-xl p-4 space-y-3">
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-2">
                <FeatherIcon name="layout" class="h-4 w-4 text-amber-600" />
                <span class="text-xs font-bold text-amber-800 uppercase tracking-wide">Chọn mẫu thư mời</span>
              </div>
              <button
                @click="aiRenderOffer"
                :disabled="aiRenderingOffer"
                class="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-gradient-to-r from-violet-600 to-indigo-600 text-white text-xs font-bold shadow-sm hover:from-violet-700 hover:to-indigo-700 transition disabled:opacity-60"
              >
                <span v-if="aiRenderingOffer" class="w-3 h-3 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
                <span v-else>✨</span>
                {{ aiRenderingOffer ? 'AI đang soạn...' : 'AI Render' }}
              </button>
            </div>
            <div class="flex flex-wrap gap-2">
              <button
                v-for="tpl in offerTemplates" :key="tpl.key"
                @click="applyTemplate(tpl.key)"
                :disabled="loadingTemplate || aiRenderingOffer"
                class="px-3 py-1.5 text-xs font-semibold rounded-lg border transition-all duration-150"
                :class="selectedTemplate===tpl.key ? 'bg-amber-500 text-white border-amber-500 shadow-sm' : 'bg-white text-amber-700 border-amber-300 hover:bg-amber-100'"
              >
                {{ loadingTemplate && selectedTemplate===tpl.key ? '...' : tpl.label }}
              </button>
            </div>
            <p v-if="aiRenderingOffer" class="text-[11px] text-violet-700 font-medium animate-pulse">⏳ DeepSeek AI đang cá nhân hóa thư mời cho ứng viên này...</p>
          </div>

          <!-- Email + Subject -->
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label class="text-xs text-slate-700 font-medium block mb-1.5">Email ứng viên <span class="text-red-400">*</span></label>
              <input v-model="offerForm.email" class="w-full border rounded-xl px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-amber-300" placeholder="email@example.com" />
            </div>
            <div>
              <label class="text-xs text-slate-700 font-medium block mb-1.5">Tiêu đề <span class="text-red-400">*</span></label>
              <input v-model="offerForm.subject" class="w-full border rounded-xl px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-amber-300" placeholder="Tiêu đề email..." />
            </div>
          </div>

          <!-- Content -->
          <div>
            <label class="text-xs text-slate-700 font-medium block mb-1.5">Nội dung thư mời <span class="text-red-400">*</span></label>
            <textarea v-model="offerForm.content" rows="10" class="w-full border rounded-xl px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-amber-300 font-mono text-xs leading-relaxed" placeholder="Nội dung thư mời..."></textarea>
          </div>

          <!-- Options row -->
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <!-- PDF Attachment -->
            <div class="border border-gray-200 rounded-xl p-3.5 space-y-2.5 bg-gray-50">
              <label class="flex items-center gap-2 cursor-pointer">
                <input type="checkbox" v-model="offerForm.attach_pdf" class="w-4 h-4 rounded accent-indigo-600" />
                <span class="text-xs font-bold text-gray-800 flex items-center gap-1.5">
                  <FeatherIcon name="file-text" class="h-3.5 w-3.5 text-indigo-500" />
                  Đính kèm hợp đồng PDF
                </span>
              </label>
              <div v-if="offerForm.attach_pdf" class="pl-6 space-y-2">
                <select v-model="offerForm.contract_type" class="w-full border border-gray-200 rounded-lg px-2.5 py-1.5 text-xs bg-white">
                  <option v-for="ct in contractTypes" :key="ct.key" :value="ct.key">{{ ct.label }}</option>
                </select>
                <div class="flex items-center justify-between">
                  <button
                    @click="aiRenderContract"
                    :disabled="aiRenderingContract"
                    class="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-gradient-to-r from-violet-600 to-indigo-600 text-white text-[11px] font-bold shadow-sm hover:from-violet-700 hover:to-indigo-700 transition disabled:opacity-60"
                  >
                    <span v-if="aiRenderingContract" class="w-2.5 h-2.5 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
                    <span v-else>🤖</span>
                    {{ aiRenderingContract ? 'AI đang soạn...' : 'AI Render HĐLĐ' }}
                  </button>
                </div>
                <div>
                  <label class="text-[10px] text-slate-700 font-bold block mb-1">Nội dung văn bản hợp đồng PDF:</label>
                  <textarea
                    v-model="offerForm.contract_content"
                    rows="6"
                    class="w-full border border-gray-200 rounded-lg px-2 py-1.5 text-[10px] leading-relaxed font-mono focus:outline-none focus:ring-2 focus:ring-amber-300 transition-all duration-300"
                    :class="aiRenderingContract ? 'border-violet-400 ring-2 ring-violet-100 bg-violet-50/10' : 'bg-white'"
                    placeholder="Nội dung hợp đồng..."
                  ></textarea>
                </div>
                <p class="text-[10px] text-gray-500">File PDF hợp đồng sẽ tự động kèm vào email</p>
              </div>
            </div>

            <!-- Onboarding Link -->
            <div class="border border-gray-200 rounded-xl p-3.5 space-y-2.5 bg-gray-50">
              <label class="flex items-center gap-2 cursor-pointer">
                <input type="checkbox" v-model="offerForm.include_onboarding" class="w-4 h-4 rounded accent-emerald-600" />
                <span class="text-xs font-bold text-gray-800 flex items-center gap-1.5">
                  <FeatherIcon name="link" class="h-3.5 w-3.5 text-emerald-500" />
                  Gửi kèm link điền hồ sơ
                </span>
              </label>
              <div v-if="offerForm.include_onboarding" class="pl-6">
                <p class="text-[10px] text-emerald-700 font-semibold">Ứng viên sẽ nhận link để tự điền thông tin cá nhân, ngân hàng, BHXH trước ngày nhận việc.</p>
              </div>
            </div>
          </div>

          <!-- Onboarding link preview (after send) -->
          <div v-if="onboardingLink" class="flex items-center gap-2 bg-emerald-50 border border-emerald-200 rounded-xl px-4 py-3">
            <FeatherIcon name="check-circle" class="h-4 w-4 text-emerald-500 shrink-0" />
            <div class="flex-1 min-w-0">
              <p class="text-xs font-semibold text-emerald-800">Link onboarding đã tạo:</p>
              <a :href="onboardingLink" target="_blank" class="text-[11px] text-emerald-700 underline truncate block">{{ onboardingLink }}</a>
            </div>
            <button @click="copyOnboardingLink" class="text-xs text-emerald-600 font-bold hover:text-emerald-800 shrink-0">Sao chép</button>
          </div>
        </div>

        <div class="flex items-center justify-between px-6 py-4 border-t bg-gray-50">
          <div class="flex items-center gap-1.5 text-[11px] text-gray-500">
            <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 2L11 13M22 2L15 22l-4-9-9-4 20-7z"/></svg>
            Gửi qua <span class="font-bold text-gray-700">Resend</span>
          </div>
          <div class="flex gap-2">
            <Button @click="showOfferLetterModal=false" class="btn-secondary font-medium">Hủy</Button>
            <Button @click="sendOfferLetter" :loading="sendingOffer" class="btn-success font-bold shadow-sm">
              <FeatherIcon name="send" class="h-3.5 w-3.5 mr-1" /> Gửi Thư Mời
            </Button>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal: Sửa thông tin ứng viên -->
    <div v-if="showEditModal" class="fixed inset-0 z-50 flex items-start justify-center bg-black/40 pt-8 overflow-y-auto" @click.self="showEditModal=false">
      <div class="bg-white rounded-xl shadow-2xl w-full max-w-lg mx-4 mb-8 p-6 space-y-4">
        <div class="flex items-center justify-between border-b pb-3">
          <h3 class="text-lg font-semibold text-gray-900">✏️ Sửa thông tin ứng viên</h3>
          <button @click="showEditModal=false" class="text-slate-500 hover:text-gray-600"><FeatherIcon name="x" class="h-5 w-5" /></button>
        </div>

        <div class="space-y-3">
          <!-- Họ tên & SĐT -->
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="text-xs text-slate-700 font-medium block mb-1">Họ tên <span class="text-red-400">*</span></label>
              <input v-model="editForm.applicant_name" class="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500" />
            </div>
            <div>
              <label class="text-xs text-slate-700 font-medium block mb-1">SĐT</label>
              <input v-model="editForm.phone_number" class="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500" />
            </div>
          </div>

          <!-- Email & Quốc gia -->
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="text-xs text-slate-700 font-medium block mb-1">Email</label>
              <input v-model="editForm.email_id" type="email" class="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500" />
            </div>
            <div>
              <label class="text-xs text-slate-700 font-medium block mb-1">Quốc gia</label>
              <input v-model="editForm.country" class="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500" />
            </div>
          </div>

          <!-- Vị trí tuyển dụng -->
          <div>
            <label class="text-xs text-slate-700 font-medium block mb-1">Vị trí ứng tuyển <span class="text-red-400">*</span></label>
            <select v-model="editForm.job_title" class="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500">
              <option value="">Chọn vị trí...</option>
              <option v-for="o in openings" :key="o.name" :value="o.name">{{ o.job_title }}</option>
            </select>
          </div>

          <!-- Nguồn tuyển dụng -->
          <div>
            <label class="text-xs text-slate-700 font-medium block mb-1">Nguồn tuyển dụng</label>
            <select v-model="editForm.source_name" class="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500">
              <option value="">Chọn nguồn...</option>
              <option value="Website">Website</option>
              <option value="Facebook">Facebook</option>
              <option value="LinkedIn">LinkedIn</option>
              <option value="VietnamWorks">VietnamWorks</option>
              <option value="Người giới thiệu">Người giới thiệu</option>
              <option value="Khác">Khác</option>
            </select>
          </div>

          <!-- Lương mong muốn -->
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="text-xs text-slate-700 font-medium block mb-1">Lương mong muốn (Tối thiểu)</label>
              <input v-model.number="editForm.lower_range" type="number" class="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500" />
            </div>
            <div>
              <label class="text-xs text-slate-700 font-medium block mb-1">Lương mong muốn (Tối đa)</label>
              <input v-model.number="editForm.upper_range" type="number" class="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500" />
            </div>
          </div>
          <div>
            <label class="text-xs text-slate-700 font-medium block mb-1">Lương offer phỏng vấn</label>
            <input v-model.number="editForm.custom_offered_salary" type="number" class="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500" />
          </div>

          <!-- Cover letter / Thư giới thiệu -->
          <div>
            <label class="text-xs text-slate-700 font-medium block mb-1">Thư giới thiệu (Cover Letter)</label>
            <textarea v-model="editForm.cover_letter" rows="3" class="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500" placeholder="Thư giới thiệu của ứng viên..."></textarea>
          </div>
        </div>

        <div class="flex justify-end gap-2 pt-2 border-t">
          <Button @click="showEditModal=false" class="btn-secondary font-medium">Hủy</Button>
          <Button @click="saveEdit" :loading="savingEdit" class="btn-success font-bold shadow-sm">Cập nhật</Button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, reactive, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { frappeRequest, Button, FeatherIcon, LoadingIndicator } from 'frappe-ui'

const route = useRoute()
const router = useRouter()
const app = ref(null)
const loading = ref(true)
const error = ref(null)
const toast = ref('')
const activityLog = ref([])
const actionLoading = ref(false)
const submittingResult = ref(false)

const aiQuestions = ref([])
const loadingAiQuestions = ref(false)
const aiQuestionsError = ref('')
const activeQuestionsApplicantId = ref(null)
const showSuggestedQuestions = ref(true)

async function loadAiSuggestedQuestions(applicantId) {
  if (!applicantId) return
  if (activeQuestionsApplicantId.value === applicantId && aiQuestions.value.length > 0) {
    return
  }
  activeQuestionsApplicantId.value = applicantId
  loadingAiQuestions.value = true
  aiQuestionsError.value = ''
  aiQuestions.value = []
  try {
    const res = await frappeRequest({
      url: 'hr.api.get_ai_suggested_questions',
      method: 'GET',
      params: { applicant: applicantId }
    })
    if (res && res.error) {
      aiQuestionsError.value = res.error
    } else if (Array.isArray(res)) {
      aiQuestions.value = res
    } else {
      aiQuestionsError.value = 'Không thể tải câu hỏi gợi ý'
    }
  } catch (err) {
    aiQuestionsError.value = err.message || 'Lỗi hệ thống'
  } finally {
    loadingAiQuestions.value = false
  }
}

function copyQuestion(text) {
  navigator.clipboard.writeText(text).then(() => {
    toast.value = '📋 Đã sao chép câu hỏi vào bộ nhớ tạm'
    setTimeout(() => toast.value = '', 2500)
  }).catch(() => {
    toast.value = '❌ Sao chép thất bại'
    setTimeout(() => toast.value = '', 2500)
  })
}

const cv = computed(() => {
  const d = app.value?.cv_data
  if (!d || !Object.keys(d).length) return null
  // Check if there's at least one meaningful field with data
  const hasData = d.fit_score || d.summary || (d.skills||[]).length || (d.education||[]).length ||
    (d.experience||[]).length || (d.languages||[]).length || (d.strengths||[]).length ||
    (d.gaps||[]).length || (d.links||[]).length || d.fit_level || d.fit_reason || d.name || d.email
  return hasData ? d : null
})
const hasCvData = computed(() => !!cv.value)
const interviewHistory = computed(() => app.value?.interview_history || [])
const linkedEmployee = computed(() => {
  const n = app.value?.notes || ''
  const m = n.match(/\[DA TUYEN\] employee=(\S+)/)
  return m ? { id: m[1], name: app.value?.applicant_name } : null
})
const canSchedule = computed(() => ['Open','Shortlisted','Replied','Hold'].includes(app.value?.status))
const canHold = computed(() => ['Open','Shortlisted','Replied'].includes(app.value?.status))
const canReject = computed(() => !['Rejected','Accepted'].includes(app.value?.status))

const showScheduleForm = ref(false)
const scheduling = ref(false)
const employees = ref([])
const customAvatar = ref(null)
const newCheckItem = ref('')
// Default checklist for Vietnamese HR
const defaultChecklist = [
  { label: 'Sơ yếu lý lịch (có xác nhận địa phương)', done: false, date: null },
  { label: 'CMND/CCCD (bản sao công chứng)', done: false, date: null },
  { label: 'Bằng cấp chuyên môn (bản sao công chứng)', done: false, date: null },
  { label: 'Chứng chỉ liên quan', done: false, date: null },
  { label: 'Giấy khám sức khỏe', done: false, date: null },
  { label: 'Ảnh 3x4 (2 tấm)', done: false, date: null },
  { label: 'Đơn xin việc', done: false, date: null },
  { label: 'Sổ BHXH (nếu có)', done: false, date: null },
]
const checklist = ref([])
const checkedCount = computed(() => checklist.value.filter(i => i.done).length)
const jobOffers = ref([])

const ivForm = ref({ round: 'Vòng 1', date: '', interviewer_employee: '', notes: '' })
const resultFormId = ref(null)
// -- Interview result form --
const presetStrengths = [
  'Giao tiếp tốt', 'Kỹ thuật vững', 'Kinh nghiệm phù hợp', 'Làm việc nhóm tốt',
  'Chủ động, sáng tạo', 'Tiếng Anh tốt', 'Tư duy logic', 'Có tố chất lãnh đạo',
  'Giải quyết vấn đề tốt', 'Chịu được áp lực cao', 'Cầu tiến, ham học hỏi',
]
const presetWeaknesses = [
  'Thiếu kinh nghiệm quản lý', 'Kỹ năng giao tiếp cần cải thiện', 'Tiếng Anh chưa tốt',
  'Thiếu chứng chỉ chuyên môn', 'Chưa có kinh nghiệm thực tế', 'Kiến thức domain còn yếu',
  'Kỹ năng làm việc nhóm hạn chế', 'Kỹ năng thuyết trình yếu', 'Thiếu kiến thức về cloud',
  'Chưa quen Agile/Scrum',
]
const resultForm = reactive({ passed: true, score: 70, rating: '', strengthsChecked: [], strengthsCustom: '', weaknessesChecked: [], weaknessesCustom: '', notes: '', extra_notes: '' })
const submitResultForm = reactive({ ...resultForm })
const showRejectModal = ref(false)
const rejectForm = reactive({ reason: '', missingReqs: [''] })
const showHoldModal = ref(false)
const holdForm = reactive({ reason: '', missingReqs: [''] })
const showConvert = ref(false)
const converting = ref(false)
const designations = ref([])
const departments = ref([])
const convertForm = ref({
  first_name: '', last_name: '', gender: '', dob: '', joining: new Date().toISOString().split('T')[0],
  email: '', phone: '', location: '', designation: '', department: '', company: 'GPC',
  salary: 0,
})

// Offer Letter refs
const showOfferLetterModal = ref(false)
const sendingOffer = ref(false)
const offerForm = ref({ email: '', subject: '', content: '', attach_pdf: false, contract_type: 'thu_viec', contract_content: '', include_onboarding: false })
const offerTemplates = ref([])
const contractTypes = ref([])
const loadingTemplate = ref(false)
const onboardingLink = ref('')
const aiRenderingOffer = ref(false)
const aiRenderingContract = ref(false)
const contractPreviewReady = ref(false)
const offerContentHtml = ref('')  // HTML version từ AI để gửi Resend

onMounted(async () => {
  const id = route.params.id
  if (!id) { error.value = 'Không có ID ứng viên'; loading.value = false; return }
  try {
    const [detail, logs] = await Promise.all([
      frappeRequest({ url: 'hr.api.get_applicant_detail', method: 'GET', params: { name: id } }),
      frappeRequest({ url: 'hr.api.get_activity_log', method: 'GET', params: { doctype: 'Job Applicant', docname: id } }),
    ])
    app.value = detail || {}
    activityLog.value = logs || []
    // Parse checklist from notes or use default
    checklist.value = (detail?.checklist && detail.checklist.length) ? detail.checklist : JSON.parse(JSON.stringify(defaultChecklist))
    loadJobOffers()
  } catch (e) { error.value = e.message || 'Lỗi tải dữ liệu' }
  loading.value = false
})

async function refreshDetail() {
  try {
    const detail = await frappeRequest({ url: 'hr.api.get_applicant_detail', method: 'GET', params: { name: app.value.name } })
    app.value = detail || app.value
    const logs = await frappeRequest({ url: 'hr.api.get_activity_log', method: 'GET', params: { doctype: 'Job Applicant', docname: app.value.name } })
    activityLog.value = logs || []
    // Refresh checklist from detail
    if (detail?.checklist && detail.checklist.length) checklist.value = detail.checklist
    loadJobOffers()
  } catch {}
}

async function loadJobOffers() {
  try { jobOffers.value = await frappeRequest({ url: 'hr.api.get_job_offers', method: 'GET', params: { applicant: app.value.name } }) || [] } catch {}
}

function offerLabel(s) { return { 'Awaiting Response': 'Chờ phản hồi', 'Accepted': 'Đã nhận lời', 'Rejected': 'Từ chối' }[s] || s }
function offerChip(s) { return { 'Awaiting Response': 'bg-amber-50 text-amber-700', 'Accepted': 'bg-green-50 text-green-700', 'Rejected': 'bg-red-50 text-red-700' }[s] || 'bg-gray-50 text-gray-500' }

async function printOffer(jo) {
  try {
    const res = await frappeRequest({ url: 'hr.api.print_appointment_letter', method: 'GET', params: { name: jo.name } })
    const w = window.open('', '_blank'); if (w) { w.document.write(res.html); w.document.close() }
  } catch (e) { toast.value = '❌ ' + (e.message || 'Lỗi in thư mời'); setTimeout(() => toast.value = '', 3000) }
}

async function acceptOffer(jo) {
  try {
    const r = await frappeRequest({ url: 'hr.api.accept_job_offer', method: 'POST', params: { name: jo.name } })
    toast.value = '✅ Đã nhận lời · NV: ' + r.employee_name
    setTimeout(() => toast.value = '', 3000)
    await Promise.all([refreshDetail(), loadJobOffers()])
  } catch (e) { toast.value = '❌ ' + (e.message || 'Lỗi'); setTimeout(() => toast.value = '', 3000) }
}

async function doSchedule() {
  if (!ivForm.value.date) { toast.value = 'Vui lòng chọn ngày giờ'; return }
  scheduling.value = true
  try {
    await frappeRequest({ url: 'hr.api.schedule_interview', method: 'POST', params: { applicant: app.value.name, ...ivForm.value } })
    toast.value = '✅ Đã lên lịch phỏng vấn'
    setTimeout(() => toast.value = '', 3000)
    showScheduleForm.value = false
    ivForm.value = { round: 'Vòng 1', date: '', interviewer_employee: '', notes: '' }
    await refreshDetail()
  } catch (e) { toast.value = (e.message||'Lỗi') }
  scheduling.value = false
}

function goBack() {
  if (window.history.length > 1) router.back()
  else router.push('/')
}

function scrollToInterview() {
  openScheduleForm()
  setTimeout(() => {
    const el = document.getElementById('interview-section')
    if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }, 100)
}

async function loadEmployees() {
  if (employees.value.length) return
  try {
    const data = await frappeRequest({ url: 'hr.api.get_employees', method: 'GET', params: {} })
    employees.value = data || []
  } catch {}
}

// Watch for schedule form to open → load employees
watch(showScheduleForm, async (val) => { if (val) await loadEmployees() })

function openScheduleForm() {
  // Auto-compute next round number from existing interviews
  const existing = interviewHistory.value || []
  let next = 1
  for (const iv of existing) {
    const m = (iv.round || '').match(/Vòng (\d+)/)
    if (m) next = Math.max(next, parseInt(m[1]) + 1)
  }
  if (next <= 3) ivForm.value.round = `Vòng ${next}`
  else ivForm.value.round = 'Phỏng vấn cuối'
  showScheduleForm.value = true
  loadEmployees()
  if (app.value?.name) {
    loadAiSuggestedQuestions(app.value.name)
  }
}

async function onAvatarChange(e) {
  const file = e.target.files?.[0]
  if (!file) return
  const reader = new FileReader()
  reader.onload = async () => {
    const b64 = reader.result.split(',')[1]
    customAvatar.value = reader.result
    try {
      await frappeRequest({ url: 'hr.api.save_applicant_avatar', method: 'POST', params: { name: app.value.name, avatar_base64: b64 }})
      toast.value = '✅ Đã cập nhật ảnh đại diện'
      setTimeout(() => toast.value = '', 3000)
      await refreshDetail()
    } catch (e) { toast.value = '❌ ' + (e.message||'Lỗi'); setTimeout(() => toast.value = '', 3000) }
  }
  reader.readAsDataURL(file)
}

// -- Checklist --
async function saveChecklist() {
  try {
    await frappeRequest({ url: 'hr.api.save_checklist', method: 'POST', params: {
      name: app.value.name,
      checklist: JSON.stringify(checklist.value)
    }})
  } catch {}
}

async function toggleChecklist(idx) {
  checklist.value[idx].done = !checklist.value[idx].done
  checklist.value[idx].date = checklist.value[idx].done ? new Date().toISOString().split('T')[0] : null
  await saveChecklist()
}

async function addCheckItem() {
  const label = newCheckItem.value.trim()
  if (!label) return
  checklist.value.push({ label, done: false, date: null })
  newCheckItem.value = ''
  await saveChecklist()
}

function openResultForm(iv) {
  resultFormId.value = iv.id
  resultForm.passed = true; resultForm.score = iv.score || 70
  resultForm.rating = iv.rating || ''
  resultForm.strengthsChecked = (iv.strengths || []).filter(s => presetStrengths.includes(s))
  resultForm.strengthsCustom = (iv.strengths || []).filter(s => !presetStrengths.includes(s)).join(', ')
  resultForm.weaknessesChecked = (iv.weaknesses || []).filter(w => presetWeaknesses.includes(w))
  resultForm.weaknessesCustom = (iv.weaknesses || []).filter(w => !presetWeaknesses.includes(w)).join(', ')
  resultForm.notes = iv.notes || ''; resultForm.extra_notes = iv.extra_notes || ''
  if (app.value?.name) {
    loadAiSuggestedQuestions(app.value.name)
  }
}

async function submitResult(iv) {
  submittingResult.value = true
  try {
    const strengths = [...resultForm.strengthsChecked]
    if (resultForm.strengthsCustom.trim()) strengths.push(...resultForm.strengthsCustom.split(',').map(s => s.trim()).filter(Boolean))
    const weaknesses = [...resultForm.weaknessesChecked]
    if (resultForm.weaknessesCustom.trim()) weaknesses.push(...resultForm.weaknessesCustom.split(',').map(s => s.trim()).filter(Boolean))
    await frappeRequest({ url: 'hr.api.submit_interview_result', method: 'POST', params: {
      applicant: app.value.name, interview_id: iv.id, passed: resultForm.passed, score: resultForm.score,
      rating: resultForm.rating,
      strengths: JSON.stringify(strengths),
      weaknesses: JSON.stringify(weaknesses),
      notes: resultForm.notes,
      extra_notes: resultForm.extra_notes,
    }})
    toast.value = '✅ Đã lưu kết quả phỏng vấn'
    setTimeout(() => toast.value = '', 3000)
    resultFormId.value = null
    await refreshDetail()
  } catch (e) { toast.value = (e.message||'Lỗi') }
  submittingResult.value = false
}

async function doReject() {
  actionLoading.value = true
  try {
    await frappeRequest({ url: 'hr.api.reject_applicant', method: 'POST', params: {
      name: app.value.name, reason: rejectForm.reason,
      missing_requirements: JSON.stringify(rejectForm.missingReqs.filter(r=>r.trim()))
    }})
    toast.value = '✅ Đã từ chối ứng viên'
    setTimeout(() => toast.value = '', 3000)
    showRejectModal.value = false
    await refreshDetail()
  } catch (e) { toast.value = (e.message||'Lỗi') }
  actionLoading.value = false
}

async function doHold() {
  actionLoading.value = true
  try {
    await frappeRequest({ url: 'hr.api.hold_applicant', method: 'POST', params: {
      name: app.value.name, reason: holdForm.reason,
      missing_requirements: JSON.stringify(holdForm.missingReqs.filter(r=>r.trim()))
    }})
    toast.value = '✅ Đã chuyển sang cân nhắc'
    setTimeout(() => toast.value = '', 3000)
    showHoldModal.value = false
    await refreshDetail()
  } catch (e) { toast.value = (e.message||'Lỗi') }
  actionLoading.value = false
}

async function confirmDelete() {
  if (!confirm('Xóa ứng viên "' + (app.value?.applicant_name||'') + '"?')) return
  try {
    await frappeRequest({ url: 'hr.api.delete_job_applicant', method: 'POST', params: { name: app.value.name } })
    router.back()
  } catch (e) { alert('Lỗi: ' + (e.message||e)) }
}

async function openConvert() {
  const a = app.value
  const cv_data = app.value?.cv_data || {}
  // Parse name into first/last
  const nameParts = (a.applicant_name || '').trim().split(/\s+/)
  convertForm.value.first_name = nameParts.slice(0, -1).join(' ') || nameParts[0] || ''
  convertForm.value.last_name = nameParts.length > 1 ? nameParts[nameParts.length - 1] : ''
  convertForm.value.email = a.email_id || cv_data.email || ''
  convertForm.value.phone = a.phone_number || cv_data.phone || ''
  convertForm.value.location = cv_data.location || ''
  convertForm.value.dob = cv_data.dob ? cv_data.dob.replace(/\//g, '-') : ''
  convertForm.value.designation = a.designation || ''
  convertForm.value.department = a.department || ''
  convertForm.value.salary = a.custom_offered_salary || 0
  // Fetch designations & departments if not loaded
  if (!designations.value.length) {
    try {
      const [d1, d2] = await Promise.all([
        frappeRequest({ url: 'hr.api.get_designations', method: 'GET', params: {} }),
        frappeRequest({ url: 'hr.api.get_departments', method: 'GET', params: {} }),
      ])
      designations.value = d1 || []; departments.value = d2 || []
    } catch {}
  }
  // Auto-fill department from designation mapping
  if (!convertForm.value.department && convertForm.value.designation) {
    try {
      const r = await frappeRequest({ url: 'hr.api.get_designation_department', method: 'GET', params: { designation: convertForm.value.designation } })
      if (r.department && departments.value.includes(r.department)) convertForm.value.department = r.department
    } catch {}
  }
  showConvert.value = true
}

async function doConvert() {
  converting.value = true
  try {
    const f = convertForm.value
    const r = await frappeRequest({ url: 'hr.api.convert_to_employee', method: 'POST', params: {
      applicant: app.value.name,
      first_name: f.first_name, last_name: f.last_name,
      gender: f.gender || null,
      date_of_birth: f.dob || null,
      date_of_joining: f.joining || null,
      personal_email: f.email, phone: f.phone,
      location: f.location, designation: f.designation,
      department: f.department, company: f.company,
      salary: f.salary || 0,
    }})
    toast.value = '✅ Đã tạo nhân viên: ' + (r.employee||'')
    setTimeout(() => toast.value = '', 3000)
    showConvert.value = false
    await refreshDetail()
  } catch (e) { toast.value = (e.message||'Lỗi') }
  converting.value = false
}

function statusLabel(s) {
  if (!s) return '—'
  const key = s.toLowerCase()
  const m = {
    open: 'Ứng tuyển',
    shortlisted: 'Sơ tuyển',
    replied: 'Phỏng vấn',
    hold: 'Cân nhắc',
    accepted: 'Trúng tuyển',
    rejected: 'Từ chối',
    'ứng tuyển': 'Ứng tuyển',
    'sơ tuyển': 'Sơ tuyển',
    'phỏng vấn': 'Phỏng vấn',
    'cân nhắc': 'Cân nhắc',
    'trúng tuyển': 'Trúng tuyển',
    'từ chối': 'Từ chối'
  }
  return m[key] || s
}
function statusChip(s) {
  if (!s) return '!bg-gray-100 !text-gray-700'
  const key = s.toLowerCase()
  const m = {
    open: '!bg-blue-100 !text-blue-700',
    shortlisted: '!bg-amber-100 !text-amber-700',
    replied: '!bg-purple-100 !text-purple-700',
    hold: '!bg-orange-100 !text-orange-700',
    accepted: '!bg-green-100 !text-green-700',
    rejected: '!bg-red-100 !text-red-700',
    'ứng tuyển': '!bg-blue-100 !text-blue-700',
    'sơ tuyển': '!bg-amber-100 !text-amber-700',
    'phỏng vấn': '!bg-purple-100 !text-purple-700',
    'cân nhắc': '!bg-orange-100 !text-orange-700',
    'trúng tuyển': '!bg-green-100 !text-green-700',
    'từ chối': '!bg-red-100 !text-red-700'
  }
  return m[key] || '!bg-gray-100 !text-gray-700'
}
function logLabel(a) { const m={create_applicant:'📝 Tạo ứng viên',schedule_interview:'📅 Lên lịch PV',interview_result:'📊 Kết quả PV',status_change:'🔄 Đổi trạng thái',reject:'❌ Từ chối',hold:'🤔 Cân nhắc',convert:'👤 Tạo NV'}; return m[a]||a }
function logIcon(a) { const m={create_applicant:'bg-blue-500',schedule_interview:'bg-purple-500',interview_result:'bg-green-500',status_change:'bg-amber-500',reject:'bg-red-500',hold:'bg-orange-500',convert:'bg-indigo-500'}; return m[a]||'bg-gray-400' }
function fitColor(s) { if(s>=80) return '!text-green-600 !bg-green-50 !border-green-300'; if(s>=60) return '!text-blue-600 !bg-blue-50 !border-blue-300'; if(s>=40) return '!text-amber-600 !bg-amber-50 !border-amber-300'; return '!text-red-600 !bg-red-50 !border-red-300' }
function fmtMoney(v) { if(!v) return ''; return new Intl.NumberFormat('vi-VN',{style:'currency',currency:'VND',maximumFractionDigits:0}).format(v) }
function initials(n) {
  if (!n) return '?'
  const clean = n.replace(/[^\p{L}\p{N}\s]/gu, '').replace(/\s+/g, ' ').trim()
  if (!clean) return '?'
  const p = clean.split(/\s+/)
  return p.length >= 2 
    ? (p[p.length - 2][0] + p[p.length - 1][0]).toUpperCase() 
    : p[0].slice(0, 2).toUpperCase()
}
function avatarColor(n) { let h=0; for(let i=0;i<(n||'').length;i++)h=n.charCodeAt(i)+((h<<5)-h); const c=['#3b82f6','#8b5cf6','#ec4899','#f59e0b','#10b981','#6366f1','#ef4444','#84cc16']; return c[Math.abs(h)%c.length] }

// -- Edit Applicant --
const showEditModal = ref(false)
const savingEdit = ref(false)
const openings = ref([])
const editForm = reactive({
  applicant_name: '',
  phone_number: '',
  email_id: '',
  job_title: '',
  lower_range: 0,
  upper_range: 0,
  custom_offered_salary: 0,
  country: 'Vietnam',
  cover_letter: '',
  source_name: '',
})

async function openEditModal() {
  const a = app.value
  if (!a) return
  editForm.applicant_name = a.applicant_name
  editForm.phone_number = a.phone_number || ''
  editForm.email_id = a.email_id || ''
  editForm.job_title = a.job_title || ''
  editForm.lower_range = a.lower_range || 0
  editForm.upper_range = a.upper_range || 0
  editForm.custom_offered_salary = a.custom_offered_salary || 0
  editForm.country = a.country || 'Vietnam'
  editForm.cover_letter = a.cover_letter || ''
  editForm.source_name = a.source_name || ''
  
  showEditModal.value = true
  
  // Load openings if not loaded
  if (!openings.value.length) {
    try {
      const data = await frappeRequest({ url: 'hr.api.get_job_openings', method: 'GET', params: {} })
      openings.value = data || []
    } catch {}
  }
}

async function saveEdit() {
  if (!editForm.applicant_name.trim()) {
    toast.value = '⚠️ Vui lòng nhập họ tên ứng viên'
    setTimeout(() => toast.value = '', 3000)
    return
  }
  savingEdit.value = true
  try {
    await frappeRequest({
      url: 'hr.api.update_job_applicant',
      method: 'POST',
      params: {
        name: app.value.name,
        ...editForm
      }
    })
    toast.value = '✅ Đã cập nhật thông tin ứng viên'
    setTimeout(() => toast.value = '', 3000)
    showEditModal.value = false
    await refreshDetail()
  } catch (e) {
    toast.value = '❌ ' + (e.message || 'Lỗi lưu thông tin')
    setTimeout(() => toast.value = '', 3000)
  } finally {
    savingEdit.value = false
  }
}

function getYearRange(text) {
  if (!text) return ''
  const match = text.match(/^((?:\d{2}\/)?\d{4}\s*[-–]\s*(?:(?:\d{2}\/)?\d{4}|nay|present|hiện tại|đến nay))/i)
  if (match) return match[1]
  const matchAny = text.match(/((?:\d{2}\/)?\d{4}\s*[-–]\s*(?:(?:\d{2}\/)?\d{4}|nay|present|hiện tại|đến nay))/i)
  if (matchAny) return matchAny[1]
  return ''
}

function cleanTimelineText(text) {
  if (!text) return ''
  const range = getYearRange(text)
  if (range && text.startsWith(range)) {
    return text.substring(range.length).replace(/^[:\s\-–\s]+/, '')
  }
  return text
}

const selectedTemplate = ref('')

async function openOfferLetterModal() {
  const a = app.value
  onboardingLink.value = ''
  offerForm.value = {
    email: a.email_id || '',
    subject: '',
    content: '',
    attach_pdf: false,
    contract_type: 'thu_viec',
    contract_content: '',
    include_onboarding: false,
  }
  selectedTemplate.value = ''
  showOfferLetterModal.value = true
  // Load templates + contract types
  try {
    const [tpls, cts] = await Promise.all([
      frappeRequest({ url: 'hr.api.get_offer_templates', method: 'GET', params: {} }),
      frappeRequest({ url: 'hr.api.get_contract_types', method: 'GET', params: {} }),
    ])
    offerTemplates.value = tpls || []
    contractTypes.value = cts || []
    // Auto-apply first template
    if (tpls?.length) await applyTemplate(tpls[0].key)
    if (cts?.length) await applyContractTemplate(offerForm.value.contract_type)
  } catch {}
}

async function applyContractTemplate(key) {
  if (!app.value?.name) return
  try {
    const res = await frappeRequest({
      url: 'hr.api.get_contract_template',
      method: 'GET',
      params: { template_key: key, applicant: app.value.name }
    })
    offerForm.value.contract_content = res.content || ''
  } catch {}
}

watch(() => offerForm.value.contract_type, async (newVal) => {
  if (newVal) {
    await applyContractTemplate(newVal)
  }
})

async function applyTemplate(key) {
  loadingTemplate.value = true
  selectedTemplate.value = key
  try {
    const res = await frappeRequest({
      url: 'hr.api.get_offer_template',
      method: 'GET',
      params: { template_key: key, applicant: app.value.name }
    })
    offerForm.value.subject = res.subject || offerForm.value.subject
    offerForm.value.content = res.content || offerForm.value.content
  } catch {}
  loadingTemplate.value = false
}

function copyOnboardingLink() {
  navigator.clipboard.writeText(onboardingLink.value).then(() => {
    toast.value = '📋 Đã sao chép link onboarding'
    setTimeout(() => toast.value = '', 2500)
  })
}

async function aiRenderOffer() {
  if (!app.value?.name) return
  aiRenderingOffer.value = true
  try {
    const res = await frappeRequest({
      url: 'hr.api.ai_render_offer_letter',
      method: 'GET',
      params: { applicant: app.value.name, template_type: selectedTemplate.value || 'chung' }
    })
    if (res?.subject) offerForm.value.subject = res.subject
    if (res?.content) {
      const fullText = res.content
      let i = 0
      offerForm.value.content = ""
      const timer = setInterval(() => {
        if (i < fullText.length) {
          offerForm.value.content += fullText.slice(i, i + 4)
          i += 4
        } else {
          clearInterval(timer)
          offerForm.value.content = fullText
          if (res?.html) offerContentHtml.value = res.html
          aiRenderingOffer.value = false
          toast.value = res?.ai ? '✨ AI đã soạn thư mời cá nhân hóa!' : '📝 Dùng mẫu tĩnh (AI không khả dụng)'
          setTimeout(() => toast.value = '', 3000)
        }
      }, 15)
    } else {
      aiRenderingOffer.value = false
    }
  } catch (e) {
    toast.value = '❌ AI Render lỗi: ' + (e.message || e)
    setTimeout(() => toast.value = '', 3000)
    aiRenderingOffer.value = false
  }
}

async function aiRenderContract() {
  if (!app.value?.name) return
  aiRenderingContract.value = true
  contractPreviewReady.value = false
  try {
    const res = await frappeRequest({
      url: 'hr.api.ai_render_contract',
      method: 'GET',
      params: { applicant: app.value.name, contract_type: offerForm.value.contract_type }
    })
    if (res?.content) {
      const fullText = res.content
      let i = 0
      offerForm.value.contract_content = ""
      const timer = setInterval(() => {
        if (i < fullText.length) {
          offerForm.value.contract_content += fullText.slice(i, i + 5)
          i += 5
        } else {
          clearInterval(timer)
          offerForm.value.contract_content = fullText
          contractPreviewReady.value = true
          aiRenderingContract.value = false
          toast.value = '🤖 AI đã soạn xong hợp đồng! PDF sẽ dùng nội dung này.'
          setTimeout(() => toast.value = '', 4000)
        }
      }, 15)
    } else {
      aiRenderingContract.value = false
      toast.value = '⚠️ AI hợp đồng lỗi, sẽ dùng template mặc định'
      setTimeout(() => toast.value = '', 4000)
    }
  } catch (e) {
    toast.value = '❌ Lỗi AI Contract: ' + (e.message || e)
    setTimeout(() => toast.value = '', 3000)
    aiRenderingContract.value = false
  }
}

async function sendOfferLetter() {
  if (!offerForm.value.email || !offerForm.value.subject || !offerForm.value.content) {
    toast.value = '⚠️ Vui lòng nhập đầy đủ email, tiêu đề và nội dung'
    setTimeout(() => toast.value = '', 3000)
    return
  }
  sendingOffer.value = true
  try {
    const textToSend = offerForm.value.content
    // Create structured Job Offer in backend (HRMS doctype)
    const salary = app.value.custom_offered_salary || convertForm.value.salary || 0
    try {
      await frappeRequest({ url: 'hr.api.create_job_offer', method: 'POST', params: {
        applicant: app.value.name, designation: app.value.designation || '', salary,
      } })
      await loadJobOffers()
    } catch {}
    // Send email via Resend
    const res = await frappeRequest({
      url: 'hr.api.send_offer_resend',
      method: 'POST',
      params: {
        applicant: app.value.name,
        email_id: offerForm.value.email,
        subject: offerForm.value.subject,
        content: textToSend,
        attach_pdf: offerForm.value.attach_pdf ? '1' : '0',
        contract_type: offerForm.value.contract_type,
        contract_content: offerForm.value.contract_content,
        include_onboarding: offerForm.value.include_onboarding ? '1' : '0',
      }
    })
    toast.value = '✅ Đã gửi thư mời & tạo Job Offer!'
    setTimeout(() => toast.value = '', 3000)
    if (res?.onboarding_url) {
      onboardingLink.value = res.onboarding_url
    } else {
      showOfferLetterModal.value = false
    }
    const logs = await frappeRequest({ url: 'hr.api.get_activity_log', method: 'GET', params: { doctype: 'Job Applicant', docname: app.value.name } })
    activityLog.value = logs || []
  } catch (e) {
    toast.value = '❌ Lỗi gửi Resend: ' + (e.message || e)
    setTimeout(() => toast.value = '', 3000)
  }
  sendingOffer.value = false
}
</script>

