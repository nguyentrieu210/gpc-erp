<template>
  <div class="flex flex-col min-h-screen bg-gray-100">
    <header class="flex items-center gap-2 border-b bg-white px-4 py-3">
      <Button variant="ghost" @click="goBack" class="hover:!bg-gray-100 !text-gray-700"><FeatherIcon name="arrow-left" class="h-4 w-4" /></Button>
      <h1 class="text-lg font-semibold text-gray-900 flex-1">Tuyển dụng</h1>
      


      <!-- Divider -->
      <div class="w-px h-6 bg-gray-200 mx-1"></div>

      <!-- User info -->
      <div class="relative" id="profile-menu-container">
        <div 
          @click="profileMenuOpen = !profileMenuOpen" 
          class="flex items-center gap-2.5 pl-2 pr-3 py-1.5 rounded-xl hover:bg-gray-100/70 border border-transparent hover:border-gray-200 transition-all duration-200 cursor-pointer group select-none shrink-0"
        >
          <!-- Avatar -->
          <div class="relative shrink-0">
            <img
              v-if="currentUser.image"
              :src="currentUser.image"
              class="w-9 h-9 rounded-full object-cover border-2 border-white ring-2 ring-gray-200 shadow-sm transition-transform duration-200 group-hover:scale-[1.03]"
              :alt="currentUser.fullName"
            />
            <div
              v-else
              class="w-9 h-9 rounded-full flex items-center justify-center text-[13px] font-extrabold text-white shadow-sm ring-2 ring-white transition-all duration-200 group-hover:scale-[1.03] tracking-wide"
              :style="{ background: avatarColor(currentUser.fullName || currentUser.email) }"
            >
              {{ initials(currentUser.fullName || currentUser.email) }}
            </div>
            <!-- Online dot -->
            <span class="absolute bottom-0 right-0 w-2.5 h-2.5 bg-emerald-500 rounded-full border-2 border-white shadow-sm"></span>
          </div>
          <!-- Name + role -->
          <div class="hidden sm:flex flex-col leading-tight">
            <div class="flex items-center gap-1">
              <span class="text-xs font-bold text-gray-800 max-w-[100px] truncate group-hover:text-indigo-600 transition-colors">{{ currentUser.fullName || currentUser.email }}</span>
              <FeatherIcon name="chevron-down" class="h-3 w-3 text-gray-400 transition-transform duration-200 group-hover:text-gray-600" :class="profileMenuOpen ? 'rotate-180' : ''" />
            </div>
            <span class="text-[10px] text-gray-500 font-medium max-w-[120px] truncate">{{ currentUser.email }}</span>
          </div>
        </div>

        <!-- Dropdown menu -->
        <div 
          v-if="profileMenuOpen" 
          class="absolute right-0 mt-2 w-56 rounded-2xl border border-gray-200 bg-white p-2 shadow-xl z-50 animate-fadeIn"
        >
          <!-- User details block in menu -->
          <div class="px-3 py-2.5">
            <div class="text-xs font-bold text-gray-900 truncate">{{ currentUser.fullName || currentUser.email }}</div>
            <div class="text-[10px] text-gray-550 truncate mt-0.5">{{ currentUser.email }}</div>
          </div>
          <!-- Divider -->
          <div class="h-px bg-gray-100 my-1"></div>
          <!-- Actions -->
          <div class="space-y-0.5">
            <a 
              href="/portal_app" 
              class="flex items-center gap-2 px-3 py-2 text-xs font-bold text-gray-700 rounded-xl hover:bg-gray-50 hover:text-indigo-600 transition-colors"
            >
              <FeatherIcon name="grid" class="h-4 w-4 text-gray-400" />
              Về Trang chủ Portal
            </a>
            <button 
              @click="logout" 
              class="w-full flex items-center gap-2 px-3 py-2 text-xs font-bold text-red-600 rounded-xl hover:bg-red-50 transition-colors text-left"
            >
              <FeatherIcon name="log-out" class="h-4 w-4 text-red-400" />
              Đăng xuất
            </button>
          </div>
        </div>
      </div>
    </header>

    <!-- AI Loading Overlay -->
    <div v-if="aiLoading" class="fixed inset-0 z-[60] flex items-center justify-center bg-black/40">
      <div class="bg-white rounded-2xl shadow-lg p-8 max-w-sm mx-4 text-center space-y-5">
        <div class="relative mx-auto w-20 h-20">
          <div class="absolute inset-0 rounded-full border-4 border-purple-100"></div>
          <div class="absolute inset-0 rounded-full border-4 border-transparent border-t-purple-500 animate-spin"></div>
          <div class="absolute inset-2 rounded-full bg-purple-50 flex items-center justify-center"><span class="text-2xl">🤖</span></div>
        </div>
        <div>
          <div class="text-base font-semibold text-gray-800">{{ aiLoading }}</div>
          <div class="text-sm text-gray-700 mt-1">Xin vui lòng chờ trong giây lát...</div>
        </div>
        <div class="flex justify-center gap-1.5">
          <span class="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style="animation-delay:0s"></span>
          <span class="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style="animation-delay:0.15s"></span>
          <span class="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style="animation-delay:0.3s"></span>
        </div>
      </div>
    </div>

    <!-- Toast -->
    <div v-if="toast" class="fixed top-16 right-4 z-50 px-4 py-2 rounded-lg shadow-lg text-sm font-medium transition" :class="toast.startsWith('✅') ? 'bg-green-50 text-green-800 border border-green-200' : 'bg-red-50 text-red-800 border border-red-200'">{{ toast }}</div>

    <!-- Tab bar (Capsule design) -->
    <div class="px-4 py-2 bg-white border-b">
      <div class="flex p-1 bg-gray-100 rounded-xl max-w-4xl mx-auto relative shadow-sm">
        <button 
          v-for="t in tabs" 
          :key="t.key" 
          @click="switchTab(t.key)" 
          class="flex-1 flex items-center justify-center gap-1.5 py-2 px-3 text-xs font-bold rounded-lg transition-all duration-300 relative z-10"
          :class="tab === t.key ? 'text-white shadow-md' : 'text-gray-700 hover:text-gray-900 hover:bg-gray-200/40'"
          :style="tab === t.key ? 'background: linear-gradient(to right, #4f46e5, #7c3aed) !important; color: white !important;' : ''"
        >
          <FeatherIcon :name="t.icon" class="h-3.5 w-3.5" />
          <span>{{ t.label }}</span>
          <span 
            v-if="t.badge !== undefined && t.badge > 0" 
            class="ml-1 px-1.5 py-0.5 rounded-full text-[9px] font-extrabold transition-all duration-300"
            :class="tab === t.key ? 'bg-white text-indigo-700' : (t.badgeColor || 'bg-gray-200 text-gray-700')"
          >
           ⭐ {{ t.badge }}
          </span>
        </button>
      </div>
    </div>

    <!-- Reminder Banner -->
    <div v-if="todayInterviews.length > 0" class="mx-4 mt-4 bg-amber-50/70 border border-amber-200 rounded-xl p-4 flex items-start gap-3 shadow-sm animate-fadeIn">
      <div class="p-2 bg-amber-100 rounded-lg text-amber-800 shrink-0">
        <FeatherIcon name="bell" class="h-5 w-5 animate-pulse text-amber-600" />
      </div>
      <div class="flex-1 min-w-0">
        <h4 class="text-sm font-semibold text-amber-900">🔔 Nhắc nhở lịch phỏng vấn hôm nay</h4>
        <p class="text-xs text-amber-700 mt-1">
          Hôm nay bạn có <span class="font-bold text-amber-950">{{ todayInterviews.length }}</span> lịch phỏng vấn cần thực hiện:
        </p>
        <div class="mt-2 space-y-1">
          <div v-for="iv in todayInterviews" :key="iv.id" class="text-xs text-amber-950 flex items-center gap-2 flex-wrap">
            <span class="font-medium">•⭐ {{ iv.applicant_name }}</span> 
            <span class="text-amber-800">({{ iv.round }} -⭐ {{ iv.job_opening_title }})</span>
            <span class="font-semibold bg-amber-100/80 px-1.5 py-0.5 rounded text-[10px]">{{ $fmtDateTime(iv.date) }}</span>
            <span class="text-amber-800 font-medium">PV:⭐ {{ iv.interviewer }}</span>
          </div>
        </div>
      </div>
      <button @click="switchTab('interviews')" class="text-xs font-semibold text-amber-950 bg-amber-200/60 hover:bg-amber-200 px-3 py-1.5 rounded-lg border border-amber-300 transition shrink-0 self-center shadow-sm">
        Xem lịch
      </button>
    </div>

    <div class="flex-1 overflow-y-auto p-4">

      <!-- ═══════════════════ TAB: DASHBOARD ═══════════════════ -->
      <div v-if="tab==='dashboard'" class="w-full space-y-5 animate-fadeIn">
        <div v-if="dashLoading" class="flex items-center justify-center py-20"><LoadingIndicator /></div>
        <template v-else>
          <!-- Quick Shortcuts -->
          <div class="bg-white rounded-2xl border border-gray-300 p-5 shadow-sm">
            <h3 class="text-sm font-bold text-gray-800 mb-4 flex items-center gap-2">
              <span class="p-1.5 rounded-lg bg-amber-50 text-amber-500"><FeatherIcon name="zap" class="h-4 w-4" /></span>
              Lối tắt nhanh
            </h3>
            <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
              <button @click="openQuickAdd" class="shortcut-green flex items-center justify-center gap-2 py-3 px-4 rounded-xl transition-all duration-300 text-sm font-bold shadow-sm hover:shadow-md hover:-translate-y-0.5">
                <FeatherIcon name="user-plus" class="h-4 w-4 shrink-0" />
                Thêm ứng viên
              </button>
              <button @click="openNewJob" class="shortcut-indigo flex items-center justify-center gap-2 py-3 px-4 rounded-xl transition-all duration-300 text-sm font-bold shadow-sm hover:shadow-md hover:-translate-y-0.5">
                <FeatherIcon name="briefcase" class="h-4 w-4 shrink-0" />
                Đăng tin mới
              </button>
              <button @click="switchTab('pipeline')" class="shortcut-violet flex items-center justify-center gap-2 py-3 px-4 rounded-xl transition-all duration-300 text-sm font-bold shadow-sm hover:shadow-md hover:-translate-y-0.5">
                <FeatherIcon name="trello" class="h-4 w-4 shrink-0" />
                Xem Pipeline
              </button>
              <button @click="switchTab('interviews')" class="shortcut-pink flex items-center justify-center gap-2 py-3 px-4 rounded-xl transition-all duration-300 text-sm font-bold shadow-sm hover:shadow-md hover:-translate-y-0.5">
                <FeatherIcon name="calendar" class="h-4 w-4 shrink-0" />
                Lịch phỏng vấn
              </button>
            </div>
          </div>

          <!-- Key metrics -->
          <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <!-- Metric Card 1 -->
            <div class="bg-white rounded-2xl border border-gray-300 p-4 shadow-sm flex items-center gap-4 hover:-translate-y-1 hover:shadow-md transition-all duration-300 group cursor-pointer" @click="switchTab('jobs')">
              <div class="p-3 rounded-xl bg-indigo-50 text-indigo-600 group-hover:bg-indigo-600 group-hover:text-white transition-colors duration-300 shrink-0">
                <FeatherIcon name="briefcase" class="h-6 w-6" />
              </div>
              <div>
                <div class="text-2xl font-extrabold text-gray-900 leading-tight">{{ dash.jobs_open }}</div>
                <div class="text-xs font-bold text-gray-700 mt-0.5">Vị trí đang tuyển</div>
              </div>
            </div>
            <!-- Metric Card 2 -->
            <div class="bg-white rounded-2xl border border-gray-300 p-4 shadow-sm flex items-center gap-4 hover:-translate-y-1 hover:shadow-md transition-all duration-300 group cursor-pointer" @click="switchTab('applicants')">
              <div class="p-3 rounded-xl bg-violet-50 text-violet-600 group-hover:bg-violet-600 group-hover:text-white transition-colors duration-300 shrink-0">
                <FeatherIcon name="users" class="h-6 w-6" />
              </div>
              <div>
                <div class="text-2xl font-extrabold text-gray-900 leading-tight">{{ dash.applicants_total }}</div>
                <div class="text-xs font-bold text-gray-700 mt-0.5">Tổng ứng viên</div>
              </div>
            </div>
            <!-- Metric Card 3 -->
            <div class="bg-white rounded-2xl border border-gray-300 p-4 shadow-sm flex items-center gap-4 hover:-translate-y-1 hover:shadow-md transition-all duration-300 group cursor-pointer" @click="switchTab('applicants')">
              <div class="p-3 rounded-xl bg-emerald-50 text-emerald-600 group-hover:bg-emerald-600 group-hover:text-white transition-colors duration-300 shrink-0">
                <FeatherIcon name="user-plus" class="h-6 w-6" />
              </div>
              <div>
                <div class="text-2xl font-extrabold text-gray-900 leading-tight">{{ dash.applicants_today }}</div>
                <div class="text-xs font-bold text-gray-700 mt-0.5">Ứng viên hôm nay</div>
              </div>
            </div>
            <!-- Metric Card 4 -->
            <div class="bg-white rounded-2xl border border-gray-300 p-4 shadow-sm flex items-center gap-4 hover:-translate-y-1 hover:shadow-md transition-all duration-300 group cursor-pointer">
              <div class="p-3 rounded-xl bg-amber-50 text-amber-600 group-hover:bg-amber-600 group-hover:text-white transition-colors duration-300 shrink-0">
                <FeatherIcon name="trending-up" class="h-6 w-6" />
              </div>
              <div>
                <div class="text-2xl font-extrabold text-gray-900 leading-tight">{{ conversionRate }}%</div>
                <div class="text-xs font-bold text-gray-700 mt-0.5">Tỉ lệ trúng tuyển</div>
              </div>
            </div>
          </div>

          <!-- Grid for Recent Applicants & Upcoming Interviews -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
            <!-- Recent Applicants -->
            <div class="bg-white rounded-2xl border border-gray-300 shadow-sm p-5 flex flex-col justify-between">
              <div>
                <div class="flex items-center justify-between mb-4 pb-3 border-b border-gray-200">
                  <h3 class="text-sm font-bold text-gray-800 flex items-center gap-2">
                    <span class="p-1.5 rounded-lg bg-blue-50 text-blue-500"><FeatherIcon name="users" class="h-4 w-4" /></span>
                    Ứng viên mới ứng tuyển
                  </h3>
                  <button @click="switchTab('applicants')" class="text-xs font-semibold text-blue-600 hover:text-blue-800 transition-colors">Xem tất cả</button>
                </div>
                <div v-if="allApplicants.length" class="divide-y divide-gray-50">
                  <div v-for="a in allApplicants.slice(0, 5)" :key="a.name" @click="goApplicant(a)" class="flex items-center justify-between py-3 hover:bg-gray-100/50 px-2 rounded-xl transition cursor-pointer group">
                    <div class="flex items-center gap-3 max-w-[70%]">
                      <!-- Avatar with double ring -->
                      <img v-if="a.cv_avatar" :src="'data:image/jpeg;base64,' + a.cv_avatar" class="w-8 h-8 rounded-full object-cover border-2 border-white ring-1 ring-gray-200 shrink-0" />
                      <div v-else class="w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold text-white shrink-0 shadow-sm" :style="{ background: avatarColor(a.applicant_name) }">{{ initials(a.applicant_name) }}</div>
                      
                      <div class="truncate">
                        <div class="text-xs font-bold text-gray-800 group-hover:text-indigo-600 transition-colors truncate">{{ a.applicant_name }}</div>
                        <div class="text-[10px] text-gray-700 font-semibold truncate mt-0.5">{{ a.job_opening_title || a.job_title }}</div>
                      </div>
                    </div>
                    <div class="flex items-center gap-2.5 shrink-0">
                      <span class="text-[9px] px-2.5 py-0.5 rounded-full font-bold uppercase tracking-wider border shadow-sm" :class="statusChip(a.status)">{{ statusLabel(a.status) }}</span>
                      <span class="text-[10px] font-semibold text-gray-700">{{ $fmtDate((a.creation||'').split(' ')[0]) }}</span>
                    </div>
                  </div>
                </div>
                <div v-else class="text-center py-12 text-xs text-gray-700 flex flex-col items-center justify-center gap-2">
                  <FeatherIcon name="users" class="h-8 w-8 text-gray-300" />
                  <span>Chưa có ứng viên nào</span>
                </div>
              </div>
            </div>

            <!-- Upcoming Interviews -->
            <div class="bg-white rounded-2xl border border-gray-300 shadow-sm p-5 flex flex-col justify-between">
              <div>
                <div class="flex items-center justify-between mb-4 pb-3 border-b border-gray-200">
                  <h3 class="text-sm font-bold text-gray-800 flex items-center gap-2">
                    <span class="p-1.5 rounded-lg bg-purple-50 text-purple-500"><FeatherIcon name="calendar" class="h-4 w-4" /></span>
                    Lịch phỏng vấn sắp tới
                  </h3>
                  <button @click="switchTab('interviews')" class="text-xs font-semibold text-purple-600 hover:text-purple-800 transition-colors">Xem tất cả</button>
                </div>
                <div v-if="todayInterviews.length || nextInterviews.length" class="space-y-4">
                  <!-- Today Interviews Group -->
                  <div v-if="todayInterviews.length">
                    <div class="text-[10px] uppercase font-extrabold text-purple-600 tracking-wider mb-2 flex items-center gap-1.5">
                      <span class="w-1.5 h-1.5 rounded-full bg-purple-600 animate-pulse"></span>
                      Hôm nay
                    </div>
                    <div class="divide-y divide-gray-100 border border-gray-200 rounded-xl overflow-hidden bg-purple-50/20">
                      <div v-for="iv in todayInterviews.slice(0, 3)" :key="iv.id" @click="router.push('/applicant/' + iv.applicant_id)" class="flex items-center justify-between py-2.5 px-3 hover:bg-purple-50/50 transition cursor-pointer group">
                        <div class="truncate max-w-[65%] flex items-center gap-2.5">
                          <div class="w-8 h-8 rounded-full flex items-center justify-center bg-purple-100 text-purple-700 text-[10px] font-bold shrink-0 border border-purple-200 shadow-sm">
                            {{ formatTime(iv.date) || 'PV' }}
                          </div>
                          <div class="truncate">
                            <div class="text-xs font-bold text-gray-800 group-hover:text-purple-700 transition-colors truncate">{{ iv.applicant_name }}</div>
                            <div class="text-[10px] text-gray-600 truncate mt-0.5">{{ iv.round }}</div>
                          </div>
                        </div>
                        <div class="text-right shrink-0">
                          <div class="text-[10px] font-bold text-gray-700">Người PV:</div>
                          <div class="text-[10px] text-gray-800 font-semibold truncate">{{ iv.interviewer }}</div>
                        </div>
                      </div>
                    </div>
                  </div>

                  <!-- Upcoming Interviews Group -->
                  <div v-if="nextInterviews.length">
                    <div class="text-[10px] uppercase font-extrabold text-gray-500 tracking-wider mb-2 flex items-center gap-1.5">
                      <span class="w-1.5 h-1.5 rounded-full bg-gray-400"></span>
                      Tiếp theo
                    </div>
                    <div class="divide-y divide-gray-100 border border-gray-200 rounded-xl overflow-hidden bg-white">
                      <div v-for="iv in nextInterviews.slice(0, 4)" :key="iv.id" @click="router.push('/applicant/' + iv.applicant_id)" class="flex items-center justify-between py-2.5 px-3 hover:bg-gray-50/80 transition cursor-pointer group">
                        <div class="truncate max-w-[65%] flex items-center gap-2.5">
                          <div class="w-8 h-8 rounded-full flex items-center justify-center bg-gray-50 text-gray-750 text-[10px] font-bold shrink-0 border border-gray-200 shadow-sm">
                            {{ $fmtDate((iv.date||'').split(' ')[0]) }}
                          </div>
                          <div class="truncate">
                            <div class="text-xs font-bold text-gray-800 group-hover:text-indigo-600 transition-colors truncate">{{ iv.applicant_name }}</div>
                            <div class="text-[10px] text-gray-600 truncate mt-0.5">{{ iv.round }}</div>
                          </div>
                        </div>
                        <div class="text-right shrink-0">
                          <div class="text-[10px] font-bold text-gray-500">Người PV:</div>
                          <div class="text-[10px] text-gray-700 font-semibold truncate">{{ iv.interviewer }}</div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                <div v-else class="text-center py-12 text-xs text-gray-700 flex flex-col items-center justify-center gap-2">
                  <FeatherIcon name="calendar" class="h-8 w-8 text-gray-300" />
                  <span>Không có lịch phỏng vấn sắp tới</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Active Job Openings Tracker -->
          <div class="bg-white rounded-2xl border border-gray-300 shadow-sm p-5 space-y-4">
            <div class="flex items-center justify-between pb-3 border-b border-gray-200">
              <h3 class="text-sm font-bold text-gray-800 flex items-center gap-2">
                <span class="p-1.5 rounded-lg bg-indigo-50 text-indigo-600"><FeatherIcon name="briefcase" class="h-4 w-4" /></span>
                Theo dõi các vị trí đang tuyển dụng
              </h3>
              <button @click="switchTab('jobs')" class="text-xs font-semibold text-indigo-600 hover:text-indigo-800 transition-colors">Xem tất cả</button>
            </div>
            
            <div v-if="activeOpenings.length" class="overflow-x-auto">
              <table class="min-w-full divide-y divide-gray-200 text-xs">
                <thead>
                  <tr class="text-gray-500 uppercase tracking-wider text-left font-bold bg-gray-50/70">
                    <th class="px-4 py-3 rounded-l-xl">Chức danh / Phòng ban</th>
                    <th class="px-4 py-3">Chỉ tiêu</th>
                    <th class="px-4 py-3">Hồ sơ đã nhận</th>
                    <th class="px-4 py-3">Tiến độ tuyển dụng</th>
                    <th class="px-4 py-3">Hạn nộp hồ sơ</th>
                    <th class="px-4 py-3 text-right rounded-r-xl">Thao tác</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-gray-100">
                  <tr v-for="j in activeOpenings.slice(0, 5)" :key="j.name" class="hover:bg-gray-50/50 transition duration-150">
                    <td class="px-4 py-3.5">
                      <div class="font-bold text-gray-900">{{ j.job_title }}</div>
                      <div class="text-[10px] text-gray-700 font-semibold mt-0.5 flex items-center gap-1">
                        <span class="inline-block w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
                        {{ j.department || 'Chưa phân phòng ban' }}
                      </div>
                    </td>
                    <td class="px-4 py-3.5 font-bold text-gray-900">
                      {{ j.positions || 1 }}
                    </td>
                    <td class="px-4 py-3.5 font-bold text-indigo-600">
                      {{ applicantCounts[j.name] ?? 0 }}
                    </td>
                    <td class="px-4 py-3.5">
                      <!-- Progress bar -->
                      <div class="flex items-center gap-2 max-w-[150px]">
                        <div class="flex-1 h-2 bg-gray-100 rounded-full overflow-hidden">
                          <div class="h-full bg-gradient-to-r transition-all duration-500"
                            :class="getProgressColor((applicantCounts[j.name] || 0) / (j.positions || 1))"
                            :style="{ width: Math.min(100, ((applicantCounts[j.name] || 0) / (j.positions || 1)) * 100) + '%' }">
                          </div>
                        </div>
                        <span class="text-[10px] font-extrabold text-gray-700">
                          {{ Math.round(((applicantCounts[j.name] || 0) / (j.positions || 1)) * 100) }}%
                        </span>
                      </div>
                    </td>
                    <td class="px-4 py-3.5 font-semibold text-gray-700">
                      <span :class="isNearDeadline(j.closes_on) ? 'text-amber-600 font-bold' : ''">
                        {{ j.closes_on ? $fmtDate(j.closes_on) : 'Không giới hạn' }}
                      </span>
                    </td>
                    <td class="px-4 py-3.5 text-right">
                      <button @click="viewJobDetails(j)" class="px-2.5 py-1 text-[10px] font-bold text-indigo-600 bg-indigo-50 border border-indigo-100 rounded-lg hover:bg-indigo-600 hover:text-white hover:border-indigo-600 transition">
                        Chi tiết
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
            <div v-else class="text-center py-8 text-xs text-gray-700 flex flex-col items-center justify-center gap-2">
              <FeatherIcon name="briefcase" class="h-8 w-8 text-gray-300" />
              <span>Không có vị trí đang tuyển dụng</span>
            </div>
          </div>

          <!-- Grid for Source breakdown & Recruiter KPI Leaderboard -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
            <!-- Source breakdown -->
            <div class="bg-white rounded-2xl border border-gray-300 shadow-sm p-5" v-if="Object.keys(dash.by_source||{}).length">
              <h3 class="text-sm font-bold text-gray-800 mb-4 flex items-center gap-2">
                <span class="p-1.5 rounded-lg bg-emerald-50 text-emerald-500"><FeatherIcon name="pie-chart" class="h-4 w-4" /></span>
                Nguồn tuyển dụng chính
              </h3>
              <div class="space-y-3.5">
                <div v-for="(count, src) in dash.by_source" :key="src" class="flex items-center gap-3 text-xs">
                  <span class="w-24 truncate font-bold text-gray-800">{{ src }}</span>
                  <div class="flex-1 h-3 rounded-full bg-gray-100 overflow-hidden">
                    <div class="h-full rounded-full bg-gradient-to-r from-blue-500 to-indigo-500 transition-all duration-500" :style="{ width: sourcePct(count) + '%' }"></div>
                  </div>
                  <span class="w-12 text-right text-[11px] font-extrabold text-gray-800">{{ count }} hồ sơ ({{ sourcePct(count) }}%)</span>
                </div>
              </div>
            </div>

            <!-- Recruiter KPI Leaderboard -->
            <div class="bg-white rounded-2xl border border-gray-300 shadow-sm p-5">
              <h3 class="text-sm font-bold text-gray-800 mb-4 flex items-center gap-2">
                <span class="p-1.5 rounded-lg bg-amber-50 text-amber-500"><FeatherIcon name="award" class="h-4 w-4" /></span>
                Hiệu suất người phụ trách tuyển (KPI)
              </h3>
              <div v-if="recruiterKPIs.length" class="space-y-3.5">
                <div v-for="(rec, idx) in recruiterKPIs.slice(0, 5)" :key="rec.name" class="flex items-center justify-between text-xs">
                  <div class="flex items-center gap-2.5 max-w-[70%]">
                    <!-- Rank badge -->
                    <span class="w-5 h-5 rounded-full flex items-center justify-center font-extrabold shrink-0 text-[10px]" 
                      :class="idx === 0 ? 'bg-amber-100 text-amber-800' : idx === 1 ? 'bg-slate-100 text-slate-800' : idx === 2 ? 'bg-orange-100 text-orange-800' : 'bg-gray-100 text-gray-700'">
                      #{{ idx + 1 }}
                    </span>
                    <span class="font-bold text-gray-700 truncate">{{ rec.name }}</span>
                  </div>
                  <div class="flex items-center gap-3 shrink-0">
                    <div class="w-24 h-2.5 bg-gray-100 rounded-full overflow-hidden">
                      <div class="h-full bg-gradient-to-r from-amber-500 to-yellow-400 transition-all duration-500" :style="{ width: Math.min(100, (rec.count / (allApplicants.length || 1)) * 100) + '%' }"></div>
                    </div>
                    <span class="text-xs font-extrabold text-gray-950 w-12 text-right">{{ rec.count }} hồ sơ</span>
                  </div>
                </div>
              </div>
              <div v-else class="text-center py-12 text-xs text-gray-700 flex flex-col items-center justify-center gap-2">
                <FeatherIcon name="award" class="h-8 w-8 text-gray-300" />
                <span>Chưa có dữ liệu phân công nhân viên phụ trách</span>
              </div>
            </div>
          </div>
        </template>
      </div>

      <!-- ═══════════════════ TAB: VỊ TRÍ TUYỂN ═══════════════════ -->
      <div v-if="tab==='jobs'" class="max-w-5xl mx-auto space-y-5 animate-fadeIn">
        <!-- Header bar with search & actions -->
        <div class="flex items-center justify-between gap-3 flex-wrap">
          <div class="flex items-center gap-2.5 flex-wrap flex-1">
            <div class="relative flex-1 min-w-[180px] max-w-xs">
              <FeatherIcon name="search" class="absolute left-3 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-gray-700 pointer-events-none" />
              <input v-model="jobFilter.search" @input="refreshJobs" placeholder="Tìm vị tríí..." class="w-full text-sm border border-gray-300 rounded-xl pl-9 pr-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-300 bg-white shadow-sm" />
            </div>
            <select v-model="jobFilter.status" @change="refreshJobs" class="text-sm border border-gray-300 rounded-xl px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-300 bg-white shadow-sm">
              <option value="">Tất cả trạng thái</option>
              <option value="Open">🟢 Đang tuyển</option>
              <option value="Closed">⚫ Đ đóng</option>
            </select>
          </div>
          <button @click="openNewJob" class="btn-primary flex items-center gap-1.5 px-3.5 py-2 text-xs font-bold rounded-xl shadow-sm hover:-translate-y-0.5 transition-all duration-200">
            <FeatherIcon name="plus" class="h-3.5 w-3.5" /> Đăng tin mới
          </button>
        </div>

        <div v-if="loading" class="flex items-center justify-center py-20"><LoadingIndicator /></div>
        <div v-else-if="!openings?.length" class="text-center py-20 bg-white rounded-2xl border border-gray-200 shadow-sm">
          <div class="w-16 h-16 rounded-2xl bg-indigo-50 flex items-center justify-center mx-auto mb-4">
            <FeatherIcon name="briefcase" class="h-8 w-8 text-indigo-400" />
          </div>
          <p class="text-gray-800 font-medium mb-1">Chưa có vị trí tuyển dụng nào</p>
          <p class="text-gray-700 text-sm mb-4">Tạo vị trí đầu tiên để bắt đầu quy trình tuyển dụng</p>
          <button @click="openNewJob" class="px-5 py-2.5 bg-gradient-to-r from-indigo-600 to-violet-600 text-white text-sm font-bold rounded-xl shadow-md hover:shadow-lg transition">
            + Đăng tin đầu tiên
          </button>
        </div>

        <!-- Job Cards Grid -->
        <div v-else class="space-y-4">
          <div v-for="j in openings" :key="j.name" 
            class="app-card-interactive overflow-hidden"
            :class="j.status === 'Open' ? '' : 'opacity-75'">
            
            <!-- Card Top: colored accent bar -->
            <div class="h-1.5 w-full bg-gradient-to-r"
              :class="j.status === 'Open' ? 'from-indigo-500 via-violet-500 to-purple-500' : 'from-gray-300 to-gray-400'">
            </div>

            <!-- Main content row -->
            <div class="p-5 cursor-pointer" @click="toggleJob(j)">
              <div class="flex items-start gap-4">
                <!-- Job icon -->
                <div class="shrink-0 w-12 h-12 rounded-xl flex items-center justify-center text-xl shadow-sm"
                  :class="j.status === 'Open' ? 'bg-gradient-to-br from-indigo-50 to-violet-100' : 'bg-gray-100'">
                  💼
                </div>
                
                <!-- Main info -->
                <div class="flex-1 min-w-0">
                  <div class="flex items-start justify-between gap-3 flex-wrap">
                    <div class="min-w-0">
                      <div class="flex items-center gap-2 flex-wrap">
                        <h3 class="text-base font-bold text-gray-900 truncate">{{ j.job_title }}</h3>
                        <span class="text-[10px] px-2 py-0.5 rounded-full font-bold uppercase tracking-wider"
                          :class="j.status === 'Open' ? 'bg-emerald-100 text-emerald-800' : 'bg-gray-200 text-gray-800'">
                         ⭐ {{ j.status === 'Open' ? '● Đang tuyển' : '○ Đ đóng' }}
                        </span>
                      </div>
                      <div class="flex flex-wrap gap-x-3 gap-y-1 mt-1.5 text-xs text-gray-700">
                        <span v-if="j.designation" class="flex items-center gap-1">
                          <FeatherIcon name="tag" class="h-3 w-3" />⭐ {{ j.designation }}
                        </span>
                        <span v-if="j.department" class="flex items-center gap-1">
                          <FeatherIcon name="home" class="h-3 w-3" />⭐ {{ j.department }}
                        </span>
                        <span v-if="j.recruiter" class="flex items-center gap-1 text-violet-700 font-semibold">
                          <FeatherIcon name="user" class="h-3 w-3" />⭐ {{ j.recruiter }}
                        </span>
                        <span class="flex items-center gap-1">
                          <FeatherIcon name="users" class="h-3 w-3" />⭐ {{ j.positions || 1 }} vị trí
                        </span>
                        <span class="flex items-center gap-1">
                          <FeatherIcon name="clock" class="h-3 w-3" /> Hạn:⭐ {{ j.closes_on ? $fmtDate(j.closes_on) : 'Không giới hạn' }}
                        </span>
                      </div>
                    </div>

                    <!-- Right actions -->
                    <div class="flex items-center gap-2 shrink-0" @click.stop>
                      <!-- Salary badge -->
                      <span v-if="j.salary_range" class="text-xs px-2.5 py-1 rounded-full bg-emerald-100 text-emerald-800 font-bold border border-emerald-300 flex items-center gap-1">
                        💰⭐ {{ j.salary_range }}
                      </span>
                      <!-- Applicant count -->
                      <span class="text-xs bg-indigo-100 text-indigo-800 border border-indigo-200 px-2.5 py-1 rounded-full font-bold cursor-pointer hover:bg-indigo-200 transition" @click="toggleJob(j)">
                       ⭐ {{ applicantCounts[j.name] || 0 }} ứng viên
                      </span>
                      <!-- Status toggle -->
                      <button 
                        @click="toggleJobStatus(j)" 
                        class="relative inline-flex h-5 w-9 shrink-0 items-center rounded-full transition-colors focus:outline-none" 
                        :class="j.status === 'Open' ? 'bg-emerald-500' : 'bg-gray-300'"
                        :title="j.status === 'Open' ? 'Đóng vị trí' : 'Mở vị trí'"
                      >
                        <span 
                          class="inline-block h-3 w-3 transform rounded-full bg-white transition-transform shadow-sm" 
                          :class="j.status === 'Open' ? 'translate-x-5' : 'translate-x-1'"
                        ></span>
                      </button>
                      <a :href="fbShareUrl(j)" target="_blank" class="p-1.5 hover:bg-blue-50 rounded-lg text-gray-700 hover:text-blue-600 transition" title="Chia sẻ Facebook"><FeatherIcon name="facebook" class="h-3.5 w-3.5" /></a>
                      <button @click="openEditJob(j)" class="p-1.5 hover:bg-gray-100 rounded-lg text-gray-700 hover:text-indigo-600 transition" title="Sửa"><FeatherIcon name="edit" class="h-3.5 w-3.5" /></button>
                      <button @click="confirmDeleteJob(j)" class="p-1.5 hover:bg-red-50 rounded-lg text-gray-700 hover:text-red-600 transition" title="Xóa"><FeatherIcon name="trash-2" class="h-3.5 w-3.5" /></button>
                      <button @click="toggleJob(j)" class="p-1.5 hover:bg-gray-100 rounded-lg transition">
                        <FeatherIcon name="chevron-down" class="h-4 w-4 text-gray-700 transition-transform duration-300" :class="expanded===j.name?'rotate-180':''" />
                      </button>
                    </div>
                  </div>

                  <!-- Funnel stage chips -->
                  <div class="mt-3 flex flex-wrap gap-1.5">
                    <span 
                      v-for="stage in applicantStages" 
                      :key="stage.key" 
                      class="text-[10px] px-2 py-0.5 rounded-full font-semibold flex items-center gap-1 border"
                      :class="statusChip(stage.key)"
                    >
                     ⭐ {{ stage.label }}: <strong>{{ getJobStatusCount(j.name, stage.key) }}</strong>
                    </span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Expanded Applicants Section -->
            <div v-if="expanded===j.name" class="border-t border-gray-200 bg-gray-100/60">
              <div class="p-4">
                <!-- Search + add row -->
                <div class="flex items-center justify-between mb-3 flex-wrap gap-2">
                  <span class="text-sm font-bold text-gray-700 flex items-center gap-2">
                    <FeatherIcon name="users" class="h-4 w-4 text-indigo-500" />
                    Danh sách ứng viên ({{ filteredApplicants.length }})
                  </span>
                  <div class="flex items-center gap-2 flex-wrap">
                    <input v-model="appFilter.search" @input="applyAppFilter" placeholder="🔍 Tên, email..." class="text-sm border border-gray-300 rounded-lg px-2.5 py-1.5 w-32 focus:outline-none focus:ring-1 focus:ring-indigo-300 bg-white" />
                    <select v-model="appFilter.status" @change="applyAppFilter" class="text-sm border border-gray-300 rounded-lg px-2 py-1.5 focus:outline-none focus:ring-1 focus:ring-indigo-300 bg-white">
                      <option value="">Mọi TT</option><option v-for="s in applicantStages" :key="s.key" :value="s.key">{{ s.label }}</option>
                    </select>
                    <input :value="(newApplicant[j.name]||{}).name||''" @input="setApplicantField(j.name,'name',$event.target.value)" placeholder="Tên mới..." class="text-sm border border-gray-300 rounded-lg px-2.5 py-1.5 w-28 focus:outline-none focus:ring-1 focus:ring-indigo-300 bg-white" />
                    <input :value="(newApplicant[j.name]||{}).email||''" @input="setApplicantField(j.name,'email',$event.target.value)" placeholder="Email..." class="text-sm border border-gray-300 rounded-lg px-2.5 py-1.5 w-32 focus:outline-none focus:ring-1 focus:ring-indigo-300 bg-white" />
                    <Button size="sm" @click="addApplicant(j)" :loading="adding[j.name]" class="!bg-indigo-600 !text-white hover:!bg-indigo-700 font-bold border border-indigo-700 shadow-sm">+ Thêm</Button>
                  </div>
                </div>

                <div v-if="fetchingApp[j.name]" class="text-center py-6 text-gray-700 text-sm">Đang tải...</div>
                <div v-else-if="!filteredApplicants.length" class="text-center py-8 text-gray-700 text-sm flex flex-col items-center gap-2">
                  <FeatherIcon name="users" class="h-8 w-8 text-gray-200" />
                  <span>Chưa có ứng viên nào</span>
                </div>
                <div v-else class="space-y-2">
                  <div v-for="a in filteredApplicants" :key="a.name" 
                    class="flex items-center justify-between rounded-xl bg-white px-4 py-3 text-sm border border-gray-200 hover:border-indigo-200 hover:shadow-sm transition-all duration-200 group">
                    <div class="flex-1 flex items-center gap-3 cursor-pointer" @click="goApplicant(a)">
                      <!-- Avatar -->
                      <img v-if="a.cv_avatar" :src="'data:image/jpeg;base64,' + a.cv_avatar" class="w-9 h-9 rounded-full object-cover shrink-0 border-2 border-white ring-1 ring-gray-200 shadow-sm" />
                      <div v-else class="w-9 h-9 rounded-full flex items-center justify-center text-xs font-bold text-white shrink-0 shadow-sm" :style="{ background: avatarColor(a.applicant_name) }">{{ initials(a.applicant_name) }}</div>
                      
                      <div class="truncate">
                        <div class="flex items-center gap-2">
                          <span class="font-semibold text-gray-800 group-hover:text-indigo-600 transition-colors">{{ a.applicant_name }}</span>
                          <span v-if="a.cv_fit_score" class="text-[10px] px-1.5 py-0.5 rounded-full font-bold border" :class="fitScoreColor(a.cv_fit_score)">
                            🎯⭐ {{ a.cv_fit_score }}
                          </span>
                          <span v-if="a.resume_attachment" class="text-blue-400 text-xs" title="Đ nộp CV">📎</span>
                        </div>
                        <div class="text-gray-700 text-xs mt-0.5 flex items-center gap-2 flex-wrap">
                          <span>{{ a.email_id || '—' }}</span>
                          <span v-if="a.source_name" class="text-indigo-600 font-medium">⭐ {{ a.source_name }}</span>
                          <span v-if="a.lower_range || a.upper_range" class="text-emerald-600 font-bold bg-emerald-50 px-1.5 py-0.5 rounded border border-emerald-100 flex items-center gap-0.5">
                            💰 Mong muốn: {{ fmtMoney(a.lower_range) }}<span v-if="a.lower_range && a.upper_range">-</span>{{ fmtMoney(a.upper_range) }}
                          </span>
                          <span v-if="a.custom_offered_salary" class="text-indigo-600 font-bold bg-indigo-50 px-1.5 py-0.5 rounded border border-indigo-100 flex items-center gap-0.5">
                            💼 Offer: {{ fmtMoney(a.custom_offered_salary) }}
                          </span>
                        </div>
                      </div>
                    </div>
                    <div class="flex items-center gap-2">
                      <select :value="a.status" @change="onStatusChange(a, $event.target.value)" class="text-xs border border-gray-300 rounded-lg px-2.5 py-1.5 bg-white font-medium focus:outline-none focus:ring-1 focus:ring-indigo-300 cursor-pointer">
                        <option v-for="s in applicantStages" :key="s.key" :value="s.key">{{ s.label }}</option>
                      </select>
                      <button @click="confirmDeleteApplicant(a, j)" class="p-1.5 hover:bg-red-50 rounded-lg text-gray-700 hover:text-red-600 transition" title="Xóa ứng viên"><FeatherIcon name="trash-2" class="h-3.5 w-3.5" /></button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Nút Đăng tin tuyển dụng mới ở dưới bảng/danh sách -->
          <div class="flex justify-center pt-6 pb-2">
            <button @click="openNewJob" class="btn-primary flex items-center gap-2 px-6 py-3 text-sm font-bold rounded-xl shadow-md hover:shadow-lg hover:-translate-y-0.5 transition-all duration-200">
              <FeatherIcon name="plus" class="h-4.5 w-4.5" /> Đăng tin tuyển dụng mới
            </button>
          </div>
        </div>
      </div>

      <!-- ═══════════════════ TAB: ỨNG VIÊN ═══════════════════ -->
      <div v-if="tab==='applicants'" class="w-full space-y-4 animate-fadeIn">
        <!-- Header bar -->
        <div class="flex items-center gap-3 flex-wrap justify-between">
          <div class="flex items-center gap-2 flex-wrap">
            <div class="relative">
              <FeatherIcon name="search" class="absolute left-3 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-gray-700 pointer-events-none" />
              <input v-model="allAppFilter.search" placeholder="Tìm tên, email, SĐT..." class="text-sm border border-gray-300 rounded-xl pl-9 pr-3 py-2 w-56 focus:outline-none focus:ring-2 focus:ring-indigo-300 bg-white shadow-sm" />
            </div>
            <select v-model="allAppFilter.status" class="text-sm border border-gray-300 rounded-xl px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-300 bg-white shadow-sm">
              <option value="">Mọi trạng thái</option><option v-for="s in applicantStages" :key="s.key" :value="s.key">{{ s.label }}</option>
            </select>
            <select v-model="allAppFilter.job" class="text-sm border border-gray-300 rounded-xl px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-300 bg-white shadow-sm">
              <option value="">Tất cả vị trí</option>
              <option v-for="o in openings" :key="o.name" :value="o.name">{{ o.job_title }}</option>
            </select>
          </div>
          <div class="flex items-center gap-2">
            <span v-if="selectedApplicants.length" class="text-xs font-semibold text-red-600 bg-red-50 border border-red-200 rounded-xl px-3 py-1.5 flex items-center gap-2 animate-fadeIn">
              Đ chon:⭐ {{ selectedApplicants.length }}
              <button @click="deleteSelected" class="text-xs bg-red-600 text-white rounded-lg px-2.5 py-0.5 font-bold hover:bg-red-700 transition">Xóa đã chon</button>
            </span>
            <span class="text-xs font-medium text-gray-700 bg-white border border-gray-300 rounded-xl px-3 py-1.5 shadow-sm" v-if="!selectedApplicants.length">{{ filteredAllApplicants.length }} ứng viên</span>
            <button type="button" @click="exportToCSV" class="btn-primary flex items-center gap-1.5 px-3.5 py-2 text-xs font-bold rounded-xl shadow-sm hover:-translate-y-0.5 transition-all duration-200">
              <FeatherIcon name="download" class="h-3.5 w-3.5" /> Xuất CSV
            </button>
            <button type="button" @click="openQuickAdd" class="btn-success flex items-center gap-1.5 px-3.5 py-2 text-xs font-bold rounded-xl shadow-sm hover:shadow-md hover:-translate-y-0.5 transition-all duration-200">
              <FeatherIcon name="plus" class="h-3.5 w-3.5" /> Thêm ứng viên
            </button>
          </div>
        </div>

        <!-- Select All row -->
        <div v-if="filteredAllApplicants.length" class="flex items-center gap-2 px-1">
          <input type="checkbox" :checked="isAllSelected" @change="toggleSelectAll" class="w-4 h-4 rounded accent-indigo-600 cursor-pointer" />
          <span class="text-xs text-gray-700">Chọn tất cả⭐ {{ filteredAllApplicants.length }} ứng viên</span>
        </div>

        <div v-if="allAppsLoading" class="flex items-center justify-center py-20"><LoadingIndicator /></div>
        <div v-else-if="!filteredAllApplicants.length" class="text-center py-20 bg-white rounded-2xl border border-gray-200 shadow-sm">
          <div class="w-16 h-16 rounded-2xl bg-violet-50 flex items-center justify-center mx-auto mb-4">
            <FeatherIcon name="users" class="h-8 w-8 text-violet-400" />
          </div>
          <p class="text-gray-800 font-medium mb-1">Chưa có ứng viên nào</p>
          <p class="text-gray-700 text-sm mb-4">Thêm ứng viên vào hệ thống để bắt đầu theo dõi</p>
          <button type="button" @click="openQuickAdd" class="btn-success px-5 py-2.5 text-sm font-bold rounded-xl shadow-md hover:shadow-lg transition">
            + Thêm ứng viên đầu tiên
          </button>
        </div>

        <!-- Applicant Cards -->
        <div v-else class="space-y-2.5">
          <!-- Header row -->
          <div class="hidden md:flex items-center gap-4 px-4 py-2.5 bg-gray-250 border border-gray-300 rounded-xl text-[10px] font-bold text-gray-700 uppercase tracking-wider mb-2" style="background-color: #f3f4f6 !important;">
            <!-- Space for Checkbox + Index -->
            <div class="w-11 shrink-0 text-gray-500">#</div>
            <!-- Candidate Name -->
            <div class="flex-1">Ứng viên / Điểm AI</div>
            <!-- Job opening -->
            <div class="w-36 shrink-0">Chức danh ứng tuyển</div>
            <!-- AI Suggested roles -->
            <div class="hidden lg:block w-32 shrink-0">Chức danh gợi ý (AI)</div>
            <!-- Source & Date -->
            <div class="w-24 shrink-0 text-right">Nguồn / Ngày nộp</div>
            <!-- Status -->
            <div class="w-[100px] shrink-0 text-center">Trạng thái</div>
            <!-- Action placeholder -->
            <div class="w-10 shrink-0"></div>
          </div>
          <div v-for="(a, idx) in filteredAllApplicants" :key="a.name"
            class="group app-table-row-card overflow-hidden"
            @click="goApplicant(a)">
            <div class="flex items-center gap-4 px-4 py-3.5">
              <!-- Checkbox -->
              <div @click.stop class="shrink-0">
                <input type="checkbox" :value="a.name" v-model="selectedApplicants" class="w-4 h-4 rounded accent-indigo-600 cursor-pointer" />
              </div>

              <!-- Index -->
              <span class="text-xs text-gray-700 font-bold w-5 shrink-0">{{ idx + 1 }}</span>

              <!-- Avatar + Name -->
              <div class="flex items-center gap-3 flex-1 min-w-0">
                <div class="relative shrink-0">
                  <img v-if="a.cv_avatar" :src="'data:image/jpeg;base64,' + a.cv_avatar" class="w-10 h-10 rounded-full object-cover border-2 border-white ring-2 ring-gray-100 shadow-sm" />
                  <div v-else class="w-10 h-10 rounded-full flex items-center justify-center text-xs font-bold text-white ring-2 ring-white shadow-sm" :style="{ background: avatarColor(a.applicant_name) }">{{ initials(a.applicant_name) }}</div>
                  <!-- AI Score overlay -->
                  <span v-if="a.cv_fit_score" class="absolute -bottom-1 -right-1 w-5 h-5 rounded-full flex items-center justify-center text-[9px] font-black border-2 border-white shadow-sm" :class="fitScoreColor(a.cv_fit_score)">{{ a.cv_fit_score }}</span>
                </div>
                <div class="min-w-0">
                  <div class="font-bold text-gray-900 group-hover:text-indigo-600 transition-colors truncate">{{ a.applicant_name }}</div>
                  <div class="text-[11px] text-gray-700 mt-0.5 flex items-center gap-2 flex-wrap">
                    <span v-if="a.email_id" class="flex items-center gap-0.5"><FeatherIcon name="mail" class="h-3 w-3" />{{ a.email_id }}</span>
                    <span v-if="a.phone_number" class="flex items-center gap-0.5"><FeatherIcon name="phone" class="h-3 w-3" />{{ a.phone_number }}</span>
                    <span v-if="a.lower_range || a.upper_range" class="text-emerald-600 font-bold bg-emerald-50 px-1.5 py-0.5 rounded border border-emerald-100 flex items-center gap-0.5">
                      💰 Mong muốn: {{ fmtMoney(a.lower_range) }}<span v-if="a.lower_range && a.upper_range">-</span>{{ fmtMoney(a.upper_range) }}
                    </span>
                    <span v-if="a.custom_offered_salary" class="text-indigo-600 font-bold bg-indigo-50 px-1.5 py-0.5 rounded border border-indigo-100 flex items-center gap-0.5">
                      💼 Offer: {{ fmtMoney(a.custom_offered_salary) }}
                    </span>
                  </div>
                </div>
              </div>

              <!-- Job title -->
              <div class="hidden md:flex flex-col min-w-0 w-36 shrink-0">
                <span class="text-xs font-semibold text-gray-800 truncate">{{ a.job_opening_title || a.job_title || '—' }}</span>
                <span v-if="a.recruiter" class="text-[10px] text-violet-700 font-semibold mt-0.5 truncate">{{ a.recruiter }}</span>
              </div>

              <!-- AI Suggested roles -->
              <div class="hidden lg:flex items-center gap-1 flex-wrap w-32 shrink-0">
                <span v-for="s in (a.cv_suggested || []).slice(0, 2)" :key="s" class="text-[10px] bg-purple-100 text-purple-700 border border-purple-200 rounded-full px-1.5 py-0.5 font-semibold">{{ s }}</span>
                <span v-if="!(a.cv_suggested||[]).length" class="text-[10px] text-gray-700">—</span>
              </div>

              <!-- Source + Date -->
              <div class="hidden md:flex flex-col items-end shrink-0 w-24">
                <span class="text-[10px] bg-gray-100 text-gray-800 rounded-full px-2 py-0.5 font-semibold">{{ a.source || a.source_name || 'Website' }}</span>
                <span class="text-[10px] text-gray-700 mt-1">{{ $fmtDate((a.creation||'').split(' ')[0]) }}</span>
              </div>

              <!-- Status dropdown -->
              <div @click.stop class="shrink-0">
                <select :value="a.status" @change="onStatusChange(a, $event.target.value)" class="text-xs border border-gray-300 rounded-xl px-2.5 py-1.5 bg-white font-semibold focus:outline-none focus:ring-2 focus:ring-indigo-300 cursor-pointer">
                  <option v-for="s in applicantStages" :key="s.key" :value="s.key">{{ s.label }}</option>
                </select>
              </div>

              <!-- Attachments + Arrow -->
              <div class="flex items-center gap-1.5 text-gray-300 shrink-0">
                <span v-if="a.resume_attachment" class="text-blue-400 text-xs" title="Đ nộp CV">📎</span>
                <FeatherIcon name="chevron-right" class="h-4 w-4 opacity-0 group-hover:opacity-100 group-hover:text-indigo-400 transition-all" />
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- ═══════════════════ TAB: PHỎNG VẤN ═══════════════════ -->
      <div v-if="tab==='interviews'" class="w-full space-y-4 animate-fadeIn">
        <!-- Header bar -->
        <div class="flex items-center gap-3 flex-wrap justify-between">
          <div class="flex items-center gap-2 flex-wrap">
            <div class="relative">
              <FeatherIcon name="search" class="absolute left-3 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-gray-700 pointer-events-none" />
              <input v-model="interviewFilter.search" placeholder="Tìm ứng viên, vị trí..." class="text-sm border border-gray-300 rounded-xl pl-9 pr-3 py-2 w-56 focus:outline-none focus:ring-2 focus:ring-indigo-300 bg-white shadow-sm" />
            </div>
            <select v-model="interviewFilter.status" class="text-sm border border-gray-300 rounded-xl px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-300 bg-white shadow-sm">
              <option value="">Mọi trạng thái</option>
              <option value="scheduled">⏳ Chờ phỏng vấn</option>
              <option value="passed">✅ Đạt</option>
              <option value="failed">❌ Không đạt</option>
            </select>
            <select v-model="interviewFilter.interviewer" class="text-sm border border-gray-300 rounded-xl px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-300 bg-white shadow-sm">
              <option value="">Tất cả người phỏng vấn</option>
              <option v-for="name in uniqueInterviewers" :key="name" :value="name">{{ name }}</option>
            </select>
            <div class="flex items-center gap-1.5 ml-1 border-l pl-3 border-gray-300">
              <span class="text-xs text-gray-700 font-medium">Từ</span>
              <input v-model="interviewFilter.startDate" type="date" class="text-sm border border-gray-300 rounded-xl px-2.5 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-300 bg-white shadow-sm" />
              <span class="text-xs text-gray-700 font-medium">đến</span>
              <input v-model="interviewFilter.endDate" type="date" class="text-sm border border-gray-300 rounded-xl px-2.5 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-300 bg-white shadow-sm" />
              <button v-if="interviewFilter.startDate || interviewFilter.endDate" @click="clearDateFilter" class="text-xs text-red-500 hover:text-red-700 font-semibold shrink-0">Xóa lọc</button>
            </div>
          </div>
          <span class="text-xs font-medium text-gray-700 bg-white border border-gray-300 rounded-xl px-3 py-1.5 shadow-sm shrink-0">{{ filteredInterviews.length }} lịch PV</span>
        </div>

        <div v-if="interviewsLoading" class="flex items-center justify-center py-20"><LoadingIndicator /></div>
        <div v-else-if="!filteredInterviews.length" class="text-center py-20 bg-white rounded-2xl border border-gray-200 shadow-sm">
          <div class="w-16 h-16 rounded-2xl bg-purple-50 flex items-center justify-center mx-auto mb-4">
            <FeatherIcon name="calendar" class="h-8 w-8 text-purple-400" />
          </div>
          <p class="text-gray-800 font-medium mb-1">Chưa có lịch phỏng vấn nào</p>
          <p class="text-gray-700 text-sm">Lịch phỏng vấn sẽ xuất hiện khi bạn tạo buổi phỏng vấn cho ứng viên</p>
        </div>

        <!-- Interview Cards -->
        <div v-else class="space-y-3">
          <div v-for="(iv, idx) in filteredInterviews" :key="iv.id"
            class="group app-card-interactive overflow-hidden">

            <!-- Status color bar -->
            <div class="h-1 w-full"
              :class="iv.status === 'scheduled' ? 'bg-gradient-to-r from-purple-400 to-violet-500' : iv.status === 'passed' ? 'bg-gradient-to-r from-emerald-400 to-green-500' : 'bg-gradient-to-r from-red-400 to-rose-500'">
            </div>

            <div class="p-4">
              <div class="flex items-start gap-4 flex-wrap">
                <!-- Applicant info -->
                <div class="flex items-center gap-3 flex-1 min-w-[200px]">
                  <div class="relative shrink-0">
                    <img v-if="iv.cv_avatar" :src="'data:image/jpeg;base64,' + iv.cv_avatar" class="w-11 h-11 rounded-full object-cover border-2 border-white ring-2 ring-gray-100 shadow-sm" />
                    <div v-else class="w-11 h-11 rounded-full flex items-center justify-center text-xs font-bold text-white ring-2 ring-white shadow-sm" :style="{ background: avatarColor(iv.applicant_name) }">{{ initials(iv.applicant_name) }}</div>
                    <!-- Round indicator -->
                    <div class="absolute -bottom-1 -right-1 w-5 h-5 rounded-full flex items-center justify-center text-[8px] font-black border-2 border-white shadow-sm bg-purple-100 text-purple-700">
                     ⭐ {{ iv.round ? (iv.round.match(/\d+/) || ['?'])[0] : '?' }}
                    </div>
                  </div>
                  <div class="min-w-0">
                    <button class="font-bold text-gray-900 hover:text-indigo-600 transition-colors text-sm truncate block" @click="router.push('/applicant/' + iv.applicant_id)">
                     ⭐ {{ iv.applicant_name }}
                    </button>
                    <div class="text-[10px] text-gray-700 mt-0.5">{{ iv.email_id || iv.phone_number || '—' }}</div>
                  </div>
                </div>

                <!-- Job + Round -->
                <div class="flex flex-col gap-1 shrink-0">
                  <span class="text-xs text-gray-800 font-medium">{{ iv.job_opening_title || '—' }}</span>
                  <span class="text-[10px] font-bold px-2 py-0.5 rounded-full bg-purple-100 text-purple-800 border border-purple-200 w-fit">{{ iv.round }}</span>
                </div>

                <!-- Time + Interviewer -->
                <div class="flex flex-col gap-1 shrink-0">
                  <div class="flex items-center gap-1.5 text-xs font-semibold text-gray-800">
                    <FeatherIcon name="clock" class="h-3.5 w-3.5 text-gray-700" />
                   ⭐ {{ $fmtDateTime(iv.date) }}
                  </div>
                  <div class="flex items-center gap-1.5 text-[11px] text-gray-800 font-medium">
                    <FeatherIcon name="user" class="h-3 w-3 text-gray-700" />
                   ⭐ {{ iv.interviewer || '—' }}
                  </div>
                </div>

                <!-- Status badge -->
                <div class="shrink-0">
                  <span class="text-xs px-3 py-1.5 rounded-full font-bold border inline-flex items-center gap-1.5"
                    :class="iv.status === 'scheduled' ? 'bg-purple-100 text-purple-800 border-purple-300' : iv.status === 'passed' ? 'bg-emerald-100 text-emerald-800 border-emerald-300' : 'bg-red-100 text-red-800 border-red-300'">
                    <span class="w-1.5 h-1.5 rounded-full"
                      :class="iv.status === 'scheduled' ? 'bg-purple-600' : iv.status === 'passed' ? 'bg-emerald-600' : 'bg-red-600'">
                    </span>
                   ⭐ {{ iv.status === 'scheduled' ? 'Chờ PV' : iv.status === 'passed' ? 'Đạt' : 'Không đạt' }}
                  </span>
                </div>

                <!-- Actions -->
                <div class="flex items-center gap-2 flex-wrap shrink-0 ml-auto">
                  <Button size="sm" @click="router.push('/applicant/' + iv.applicant_id)" class="!bg-gray-100 !text-gray-700 hover:!bg-gray-200 border border-gray-300 font-medium">
                    <FeatherIcon name="user" class="h-3.5 w-3.5 mr-1" /> Hồ sơ
                  </Button>
                  <Button v-if="iv.status === 'scheduled'" size="sm" @click="openQuickResult(iv)" class="!bg-emerald-600 !text-white hover:!bg-emerald-700 font-bold border border-emerald-700 shadow-sm">
                    <FeatherIcon name="check-circle" class="h-3.5 w-3.5 mr-1" /> Nhập KQ
                  </Button>
                  <template v-else-if="iv.status === 'passed'">
                    <Button size="sm" @click="openScheduleAnotherRound(iv)" class="!bg-gray-100 !text-gray-700 hover:!bg-gray-200 border border-gray-300 font-medium">
                      <FeatherIcon name="calendar" class="h-3.5 w-3.5 mr-1" /> Lên lịch tiếp
                    </Button>
                    <span v-if="iv.is_converted" class="text-xs px-2.5 py-1 rounded-full bg-emerald-100 text-emerald-800 border border-emerald-300 font-bold">✓ Đ tuyển</span>
                    <Button v-else size="sm" @click="openConvertModal(iv)" class="!bg-emerald-600 !text-white hover:!bg-emerald-700 font-bold border border-emerald-700 shadow-sm">
                      <FeatherIcon name="user-plus" class="h-3.5 w-3.5 mr-1" /> Tạo nhân sự
                    </Button>
                  </template>
                  <template v-else-if="iv.status === 'failed'">
                    <Button size="sm" @click="openScheduleAnotherRound(iv)" class="!bg-gray-100 !text-gray-700 hover:!bg-gray-200 border border-gray-300 font-medium">
                      <FeatherIcon name="calendar" class="h-3.5 w-3.5 mr-1" /> Lên lịch tiếp
                    </Button>
                    <Button class="!bg-red-50 !text-red-700 border border-red-200 hover:!bg-red-100" size="sm" @click="openRejectModalFromInterview(iv)">
                      <FeatherIcon name="x-circle" class="h-3.5 w-3.5 mr-1" /> Từ chối
                    </Button>
                  </template>
                </div>
              </div>

              <!-- Result details (if completed) -->
              <div v-if="iv.status !== 'scheduled'" class="mt-3 pt-3 border-t border-gray-200">
                <div class="flex items-center gap-4 flex-wrap">
                  <div class="flex items-center gap-2">
                    <span class="text-xs text-gray-700">Điểm:</span>
                    <span class="text-sm font-black" :class="(iv.score||0) >= 70 ? 'text-emerald-600' : (iv.score||0) >= 50 ? 'text-amber-600' : 'text-red-600'">{{ iv.score || 0 }}/100</span>
                    <span v-if="iv.rating" class="text-xs text-amber-600 font-semibold">⭐ {{ iv.rating }}</span>
                  </div>
                  <div class="flex flex-wrap gap-1.5">
                    <span v-for="s in (iv.strengths || [])" :key="s" class="text-[10px] bg-emerald-50 text-emerald-700 border border-emerald-100 rounded-full px-2 py-0.5">+⭐ {{ s }}</span>
                    <span v-for="w in (iv.weaknesses || [])" :key="w" class="text-[10px] bg-red-50 text-red-700 border border-red-100 rounded-full px-2 py-0.5">-⭐ {{ w }}</span>
                  </div>
                  <p v-if="iv.notes" class="text-xs text-gray-700 italic truncate max-w-sm">{{ iv.notes }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- ═══════════════════ TAB: PIPELINE ═══════════════════ -->
      <div v-if="tab==='pipeline'" class="overflow-x-auto space-y-4 animate-fadeIn">
        <!-- Pipeline filter -->
        <div class="flex items-center gap-3 mb-2 max-w-4xl" v-if="allApplicants.length">
          <input v-model="pipelineFilter.search" @input="applyPipelineFilter" placeholder="🔍 Tìm ứng viên..." class="text-sm border border-gray-250 rounded-xl px-4 py-2 w-56 focus:outline-none focus:ring-1 focus:ring-indigo-500 bg-white" />
          <select v-model="pipelineFilter.job" @change="applyPipelineFilter" class="text-sm border border-gray-250 rounded-xl px-3 py-2 focus:outline-none focus:ring-1 focus:ring-indigo-500 bg-white">
            <option value="">Tất cả vị trí tuyển</option>
            <option v-for="o in openings" :key="o.name" :value="o.name">{{ o.job_title }}</option>
          </select>
        </div>

        <div v-if="pipelineLoading" class="flex items-center justify-center py-20"><LoadingIndicator /></div>
        <div v-else class="flex gap-4 pb-4" :style="{ minWidth: (pipelineCols.length * 240) + 'px' }">
          <div v-for="col in pipelineCols" :key="col.key" 
            class="flex-1 min-w-[220px] max-w-[320px] rounded-2xl p-3.5 transition-all duration-300 border-2 bg-gray-100" 
            :class="draggedOverCol === col.key ? 'border-dashed border-indigo-400 bg-indigo-50/40 shadow-inner scale-[1.01]' : 'border-transparent bg-gray-100'"
            @dragover.prevent="draggedOverCol = col.key" 
            @dragleave="draggedOverCol = null"
            @drop="onDropApplicant($event, col.key); draggedOverCol = null">
            
            <div class="flex items-center justify-between mb-4 px-1">
              <div class="flex items-center gap-2">
                <span class="w-3 h-3 rounded-full shadow-sm" 
                  :class="col.color === 'bg-blue-500' ? 'bg-blue-500' :
                          col.color === 'bg-amber-500' ? 'bg-amber-500' :
                          col.color === 'bg-purple-500' ? 'bg-purple-500' :
                          col.color === 'bg-orange-500' ? 'bg-orange-500' :
                          col.color === 'bg-green-500' ? 'bg-green-500' : 'bg-red-400'"></span>
                <span class="text-xs font-bold uppercase text-gray-700 tracking-wider">{{ col.label }}</span>
              </div>
              <span class="text-xs bg-white border border-gray-300 rounded-full px-2 py-0.5 font-bold text-gray-700 shadow-sm">{{ col.tasks.length }}</span>
            </div>

            <div class="space-y-3 max-h-[70vh] overflow-y-auto pr-1">
              <div v-for="a in col.tasks" :key="a.name"
                class="group app-card-interactive p-3.5 text-sm relative overflow-hidden"
                :class="{ 'opacity-40': dragApp===a.name }"
                draggable="true"
                @click="goApplicant(a)"
                @dragstart="dragApp=a.name; $event.dataTransfer.effectAllowed='move'">
                
                <div class="flex items-start gap-2.5">
                  <!-- Avatar -->
                  <img v-if="a.cv_avatar" :src="'data:image/jpeg;base64,' + a.cv_avatar" class="w-8 h-8 rounded-full object-cover shrink-0 border border-gray-200 shadow-sm" />
                  <div v-else class="w-8 h-8 rounded-full flex items-center justify-center text-[10px] font-bold text-white shrink-0 shadow-sm" :style="{ background: avatarColor(a.applicant_name) }">{{ initials(a.applicant_name) }}</div>
                  
                  <div class="flex-1 min-w-0">
                    <div class="font-bold text-gray-800 truncate group-hover:text-indigo-600 transition-colors">{{ a.applicant_name }}</div>
                    <div class="text-[10px] text-gray-700 font-semibold truncate mt-0.5">{{ a.job_opening_title || a.job_title }}</div>
                    <div class="text-[9px] text-slate-500 font-medium mt-1 flex items-center gap-1.5 flex-wrap">
                      <span v-if="a.lower_range || a.upper_range" class="text-emerald-600 font-bold bg-emerald-50/50 px-1 py-0.5 rounded border border-emerald-100/50">💰 {{ fmtMoney(a.lower_range) }}<span v-if="a.lower_range && a.upper_range">-</span>{{ fmtMoney(a.upper_range) }}</span>
                      <span v-if="a.custom_offered_salary" class="text-indigo-650 font-bold bg-indigo-50/50 px-1 py-0.5 rounded border border-indigo-100/50">💼 {{ fmtMoney(a.custom_offered_salary) }}</span>
                    </div>
                  </div>
                </div>

                <!-- Footer details -->
                <div class="flex items-center justify-between mt-3 pt-2.5 border-t border-gray-200 flex-wrap gap-1.5">
                  <!-- Source tag -->
                  <span class="text-[9px] font-bold text-gray-700 bg-gray-100/70 px-1.5 py-0.5 rounded uppercase tracking-wider">
                   ⭐ {{ a.source || a.source_name || 'Web' }}
                  </span>

                  <!-- Fit Score Badge -->
                  <span v-if="a.cv_fit_score" class="text-[10px] px-1.5 py-0.5 rounded-full font-extrabold border" :class="fitScoreColor(a.cv_fit_score)">
                    🎯⭐ {{ a.cv_fit_score }}
                  </span>
                  
                  <!-- Contact Indicators / Attachments -->
                  <div class="flex items-center gap-1.5 text-gray-300">
                    <span v-if="a.resume_attachment" class="text-blue-500 text-xs" title="Đ nộp CV">📎</span>
                    <FeatherIcon v-if="a.phone_number" name="phone" class="h-3 w-3" title="Có SĐT" />
                    <FeatherIcon v-if="a.email_id" name="mail" class="h-3 w-3" title="Có Email" />
                  </div>
                </div>
              </div>
              <div v-if="!col.tasks.length" class="text-xs text-center text-gray-700 py-10 italic">Trống</div>
            </div>
          </div>
        </div>
      </div>

    </div>

    <!-- Modal: Đăng tin tuyển dụng -->
    <div v-if="showJobForm" class="fixed inset-0 z-50 flex items-start justify-center bg-black/40 pt-8 overflow-y-auto" @click.self="closeJobForm">
      <div class="bg-white rounded-xl shadow-2xl w-full max-w-2xl mx-4 mb-8">
        <!-- Header -->
        <div class="px-6 py-4 border-b flex items-center justify-between sticky top-0 bg-white rounded-t-xl z-10">
          <h2 class="text-lg font-semibold">{{ editingJob ? 'Sửa tin tuyển dụng' : 'Đăng tin tuyển dụng mới' }}</h2>
          <div class="flex items-center gap-2">
            <button @click="generateJD" :disabled="!jobForm.job_title.trim() || generatingJD" class="text-sm bg-gradient-to-r from-blue-500 to-indigo-500 text-white px-4 py-1.5 rounded-lg font-medium hover:shadow-md disabled:opacity-50 flex items-center gap-1.5">
              <FeatherIcon name="zap" class="h-4 w-4" />
              <span v-if="generatingJD">🤖 AI đang viết...</span>
              <span v-else>🤖 AI soạn JD</span>
            </button>
            <button @click="closeJobForm" class="text-gray-700 hover:text-gray-800"><FeatherIcon name="x" class="h-5 w-5" /></button>
          </div>
        </div>

        <div class="p-6 space-y-4 max-h-[70vh] overflow-y-auto">
          <!-- Row 1: Chức danh + Phòng ban + Số lượng -->
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div>
              <label class="text-xs text-gray-700 font-medium">Chức danh <span class="text-red-400">*</span></label>
              <select v-model="jobForm.designation" @change="onDesignationChange" class="w-full border rounded-lg px-3 py-2 text-sm"><option value="">Chọn chức danh...</option><option v-for="d in designations" :key="d" :value="d">{{ d }}</option></select>
            </div>
            <div>
              <label class="text-xs text-gray-700 font-medium">Phòng ban</label>
              <select v-model="jobForm.department" class="w-full border rounded-lg px-3 py-2 text-sm"><option value="">Chọn phâng ban...</option><option v-for="d in departments" :key="d" :value="d">{{ d }}</option></select>
            </div>
            <div>
              <label class="text-xs text-gray-700 font-medium">Số lượng</label>
              <input v-model="jobForm.positions" type="number" min="1" class="w-full border rounded-lg px-3 py-2 text-sm" placeholder="1" />
            </div>
          </div>

          <!-- Row 2: Tên hiển thị + Lương + Người phụ trách -->
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div>
              <label class="text-xs text-gray-700 font-medium">Tên tin đăng</label>
              <input v-model="jobForm.job_title" class="w-full border rounded-lg px-3 py-2 text-sm" placeholder="Mặc định = Chức danh" />
              <div class="text-[10px] text-gray-700 mt-0.5">Để trống sẽ lấy tên chức danh</div>
            </div>
            <div>
              <label class="text-xs text-gray-700 font-medium">💵 Mức lương</label>
              <input v-model="jobForm.salary_range" class="w-full border rounded-lg px-3 py-2 text-sm" placeholder="VD: 15-25 triệu" />
            </div>
            <div>
              <label class="text-xs text-gray-700 font-medium">👤 Người phụ trách chính</label>
              <select v-model="jobForm.recruiter" class="w-full border rounded-lg px-3 py-2 text-sm">
                <option value="">Chọn nhân viên...</option>
                <option v-for="e in employees" :key="e.name" :value="e.employee_name">
                 ⭐ {{ e.employee_name }}<span v-if="e.designation"> —⭐ {{ e.designation }}</span>
                </option>
              </select>
            </div>
          </div>

          <!-- Row 3: Ngày -->
          <div class="grid grid-cols-2 gap-3">
            <div><label class="text-xs text-gray-700 font-medium">Ngày đăng</label><input :value="today" disabled class="w-full border rounded-lg px-3 py-2 text-sm bg-gray-100 text-gray-700" /></div>
            <div><label class="text-xs text-gray-700 font-medium">Ngày hết hạn</label><input v-model="jobForm.closes_on" type="date" class="w-full border rounded-lg px-3 py-2 text-sm" /></div>
          </div>

          <!-- Yêu cầu -->
          <div>
            <div class="flex items-center justify-between mb-1">
              <label class="text-xs text-gray-700 font-medium">📋 Yêu cầu</label>
              <button @click="addReq" class="text-xs text-blue-600 hover:underline">+ Thêm</button>
            </div>
            <div class="space-y-1.5">
              <div v-for="(r, i) in jobForm.requirements" :key="i" class="flex gap-2">
                <input v-model="jobForm.requirements[i]" class="flex-1 border rounded-lg px-3 py-1.5 text-sm" placeholder="Kỹ năng/kinh nghiệm/bằng cấp..." />
                <button @click="jobForm.requirements.splice(i,1)" class="text-gray-700 hover:text-red-500 shrink-0"><FeatherIcon name="x" class="h-4 w-4" /></button>
              </div>
            </div>
          </div>

          <!-- Quyền lợi -->
          <div>
            <div class="flex items-center justify-between mb-1">
              <label class="text-xs text-gray-700 font-medium">🎁 Quyền lợi</label>
              <button @click="addBen" class="text-xs text-blue-600 hover:underline">+ Thêm</button>
            </div>
            <div class="space-y-1.5">
              <div v-for="(b, i) in jobForm.benefits" :key="i" class="flex gap-2">
                <input v-model="jobForm.benefits[i]" class="flex-1 border rounded-lg px-3 py-1.5 text-sm" placeholder="Lương tháng 13, BHXH, du lịch..." />
                <button @click="jobForm.benefits.splice(i,1)" class="text-gray-700 hover:text-red-500 shrink-0"><FeatherIcon name="x" class="h-4 w-4" /></button>
              </div>
            </div>
          </div>

          <!-- Mô tả chi tiết -->
          <div>
            <label class="text-xs text-gray-700 font-medium">📝 Mô tả công việc <span class="text-red-400">*</span></label>
            <textarea v-model="jobForm.description" rows="4" class="w-full border rounded-lg px-3 py-2 text-sm" placeholder="Mô tả chi tiết về công việc, công ty, cơ hội phát triển..."></textarea>
          </div>

          <!-- JD Preview -->
          <div v-if="jdPreview" class="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl border border-blue-200 p-5 space-y-4">
            <div class="flex items-center justify-between">
              <span class="font-semibold text-blue-800 text-sm">👁 Xem trước tin tuyển dụng</span>
              <button @click="jdPreview=false" class="text-xs text-gray-700 hover:text-gray-700">Ẩn</button>
            </div>
            <div class="bg-white rounded-lg p-5 shadow-sm space-y-4 text-sm">
              <div>
                <h3 class="text-xl font-bold text-gray-900">{{ jobForm.job_title }}</h3>
                <div class="flex flex-wrap gap-2 mt-1 text-xs text-gray-700">
                  <span v-if="jobForm.salary_range">💰⭐ {{ jobForm.salary_range }}</span>
                  <span v-if="jobForm.department">🏢⭐ {{ jobForm.department }}</span>
                  <span>👥⭐ {{ jobForm.positions || 1 }} người</span>
                  <span>⏰ Hạn:⭐ {{ jobForm.closes_on || 'Không giới hạn' }}</span>
                </div>
              </div>
              <div v-if="jobForm.requirements.length" class="border-t pt-3">
                <div class="font-semibold text-gray-700 mb-2">📋 Yêu cầu</div>
                <ul class="space-y-1"><li v-for="r in jobForm.requirements" :key="r" class="flex gap-2 text-gray-800"><span class="text-blue-500">•</span>{{ r }}</li></ul>
              </div>
              <div v-if="jobForm.benefits.length" class="border-t pt-3">
                <div class="font-semibold text-gray-700 mb-2">🎁 Quyền lợi</div>
                <ul class="space-y-1"><li v-for="b in jobForm.benefits" :key="b" class="flex gap-2 text-gray-800"><span class="text-green-500">✓</span>{{ b }}</li></ul>
              </div>
              <div v-if="jobForm.description" class="border-t pt-3">
                <div class="font-semibold text-gray-700 mb-2">📝 Mô tả</div>
                <div class="text-gray-800 whitespace-pre-wrap">{{ jobForm.description }}</div>
              </div>
            </div>
          </div>
        </div>

        <!-- Footer -->
        <div class="px-6 py-4 border-t bg-gray-100 rounded-b-xl flex justify-between items-center">
          <span class="text-xs text-gray-700">🤖 AI sẽ soạn đầy đủ JD từ tên vị trí</span>
          <div class="flex gap-2">
            <Button @click="closeJobForm" class="!bg-gray-100 !text-gray-700 hover:!bg-gray-200 border border-gray-300 font-medium">Hủy</Button>
            <Button @click="createJob" :loading="creatingJob" class="!bg-emerald-600 !text-white hover:!bg-emerald-700 font-bold border border-emerald-700 shadow-sm">{{ editingJob ? 'Cập nhật tin' : '📢 Đăng tin'  }}</Button>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal: CV Preview (sau AI parse) -->
    <div v-if="cvPreview" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40" @click.self="cvPreview=null">
      <div class="bg-white rounded-xl shadow-2xl w-full max-w-lg mx-4 max-h-[85vh] overflow-y-auto">
        <div class="sticky top-0 bg-white border-b px-6 py-4 flex items-center justify-between">
          <h2 class="text-lg font-semibold">🤖 Xem trước CV đã parse</h2>
          <button @click="cvPreview=null" class="text-gray-700 hover:text-gray-800"><FeatherIcon name="x" class="h-5 w-5" /></button>
        </div>
        <div class="p-6 space-y-4">
          <!-- Avatar -->
          <div v-if="cvPreview.avatar_base64" class="flex justify-center">
            <img :src="'data:image/png;base64,' + cvPreview.avatar_base64" class="w-24 h-24 rounded-full object-cover border-4 border-white shadow-lg" />
          </div>
          <!-- Fit score -->
          <div v-if="cvPreview.fit_score" class="flex items-center gap-4 p-4 rounded-lg" :class="fitBg(cvPreview.fit_score)">
            <div class="text-3xl font-bold">{{ cvPreview.fit_score }}/100</div>
            <div>
              <div class="font-semibold">{{ cvPreview.fit_level || 'Điểm phù hợp' }}</div>
              <div class="text-sm opacity-75">{{ cvPreview.fit_reason }}</div>
            </div>
          </div>
          <!-- Basic info -->
          <div class="grid grid-cols-2 gap-3 text-sm">
            <div><span class="text-gray-700 text-xs">Họ tên</span><div class="font-medium">{{ cvPreview.name }}</div></div>
            <div><span class="text-gray-700 text-xs">Email</span><div class="font-medium">{{ cvPreview.email }}</div></div>
            <div><span class="text-gray-700 text-xs">SĐT</span><div class="font-medium">{{ cvPreview.phone }}</div></div>
            <div><span class="text-gray-700 text-xs">Địa chỉ</span><div class="font-medium">{{ cvPreview.location || '—' }}</div></div>
          </div>
          <!-- Strengths & Gaps -->
          <div v-if="(cvPreview.strengths||[]).length||(cvPreview.gaps||[]).length" class="grid grid-cols-2 gap-3">
            <div v-if="(cvPreview.strengths||[]).length">
              <div class="text-xs font-semibold text-green-700 mb-1">✅ Điểm mạnh</div>
              <ul class="space-y-0.5"><li v-for="s in cvPreview.strengths" :key="s" class="text-xs text-gray-800">{{ s }}</li></ul>
            </div>
            <div v-if="(cvPreview.gaps||[]).length">
              <div class="text-xs font-semibold text-red-700 mb-1">⚠️ Cần bổ sung</div>
              <ul class="space-y-0.5"><li v-for="g in cvPreview.gaps" :key="g" class="text-xs text-gray-800">{{ g }}</li></ul>
            </div>
          </div>
          <!-- Skills -->
          <div v-if="(cvPreview.skills||[]).length">
            <div class="text-xs font-semibold text-gray-800 mb-1.5">💡 Kỹ năng ({{ cvPreview.skills.length }})</div>
            <div class="flex flex-wrap gap-1"><span v-for="s in cvPreview.skills.slice(0,15)" :key="s" class="text-xs bg-blue-50 text-blue-700 rounded-full px-2 py-0.5">{{ s }}</span></div>
          </div>
          <!-- Education -->
          <div v-if="(cvPreview.education||[]).length">
            <div class="text-xs font-semibold text-gray-800 mb-1">🎓 Học vấn</div>
            <ul class="space-y-0.5"><li v-for="e in cvPreview.education.slice(0,4)" :key="e" class="text-xs text-gray-800">{{ e }}</li></ul>
          </div>
          <!-- Experience -->
          <div v-if="(cvPreview.experience||[]).length">
            <div class="text-xs font-semibold text-gray-800 mb-1">💼 Kinh nghiệm</div>
            <ul class="space-y-1"><li v-for="e in cvPreview.experience.slice(0,5)" :key="e" class="text-xs text-gray-700 border-l-2 border-gray-300 pl-2">{{ e }}</li></ul>
          </div>
        </div>
        <div class="sticky bottom-0 bg-gray-100 border-t px-6 py-3 flex justify-end gap-2">
          <Button @click="cvPreview=null" class="!bg-gray-100 !text-gray-700 hover:!bg-gray-200 border border-gray-300 font-medium">Hủy</Button>
          <Button @click="applyCVPreview" class="!bg-indigo-50 !text-indigo-700 hover:!bg-indigo-100 border border-indigo-200 font-bold shadow-sm">Điền form</Button>
          <Button @click="saveCVPreview" class="!bg-emerald-600 !text-white hover:!bg-emerald-700 font-bold border border-emerald-700 shadow-sm">Lưu ngay</Button>
        </div>
      </div>
    </div>

    <!-- Quick Add Applicant Modal - Vue-driven -->
    <div v-if="showQuickAdd" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40" @click.self="closeQuickAdd">
      <div class="bg-white rounded-xl shadow-2xl w-full mx-4 p-6 space-y-4 max-h-[90vh] overflow-y-auto transition-all duration-300" :class="quickAdd.cvPreview ? 'max-w-4xl' : 'max-w-md'">
        <div class="flex items-center justify-between border-b pb-2">
          <h3 class="text-lg font-semibold text-gray-900">➕ Thêm ứng viên mới</h3>
          <button @click="closeQuickAdd" class="text-gray-700 hover:text-gray-800"><FeatherIcon name="x" class="h-5 w-5" /></button>
        </div>

        <div class="grid grid-cols-1 gap-6" :class="quickAdd.cvPreview ? 'md:grid-cols-12' : ''">
          <!-- Left side: Form -->
          <div class="space-y-4" :class="quickAdd.cvPreview ? 'md:col-span-5 md:border-r md:pr-6' : ''">
            <div>
              <label class="text-xs text-gray-700 font-medium block mb-1">Vị trí tuyển dụng <span class="text-red-400">*</span></label>
              <select v-model="quickAdd.job" class="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500">
                <option value="">Chọn vị tríí...</option>
                <option v-for="o in openings" :key="o.name" :value="o.name">{{ o.job_title }}</option>
              </select>
            </div>
            <div>
              <label class="text-xs text-gray-700 font-medium block mb-1">Tải lên CV (PDF, DOCX)</label>
              <div class="flex items-center gap-2 border rounded-lg p-2 bg-gray-100">
                <label class="text-xs bg-white border rounded px-3 py-1.5 cursor-pointer hover:bg-gray-100 flex items-center gap-1 shrink-0 shadow-sm transition">
                  <FeatherIcon name="upload" class="h-3.5 w-3.5 text-gray-700" />
                  Chọn file...
                  <input type="file" accept=".pdf,.docx" class="hidden" @change="onQuickAddCV" />
                </label>
                <span v-if="quickAddParsing" class="text-xs text-purple-600 animate-pulse font-medium flex items-center gap-1">
                  🤖 AI đang parse...
                </span>
                <span v-else-if="quickAdd.file" class="text-xs text-green-600 truncate max-w-[180px] font-medium flex items-center gap-1" :title="quickAdd.file.name">
                  📎⭐ {{ quickAdd.file.name }}
                </span>
                <span v-else class="text-xs text-gray-700">Chưa chon file</span>
              </div>
              <div class="text-[10px] text-gray-700 mt-1">Chọn vị tríí tuyển dụng trước khi up CV để AI chấm điểm độ phù hợp</div>
            </div>

            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="text-xs text-gray-700 font-medium block mb-1">Họ tên <span class="text-red-400">*</span></label>
                <input v-model="quickAdd.name" class="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500" placeholder="Nguyễn Văn A" />
              </div>
              <div>
                <label class="text-xs text-gray-700 font-medium block mb-1">SĐT</label>
                <input v-model="quickAdd.phone" class="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500" placeholder="0912345678" />
              </div>
            </div>
            <div>
              <label class="text-xs text-gray-700 font-medium block mb-1">Email</label>
              <input v-model="quickAdd.email" class="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500" placeholder="email@example.com" />
            </div>
            <div>
              <label class="text-xs text-gray-700 font-medium block mb-1">Nguồn tuyển dụng</label>
              <select v-model="quickAdd.source" class="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500">
                <option value="">Chọn nguồn...</option>
                <option value="Website">Website</option>
                <option value="Facebook">Facebook</option>
                <option value="LinkedIn">LinkedIn</option>
                <option value="VietnamWorks">VietnamWorks</option>
                <option value="Người giới thiệu">Người giới thiệu</option>
                <option value="Khác">Khác</option>
              </select>
            </div>
            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="text-xs text-gray-700 font-medium block mb-1">Lương mong muốn (Tối thiểu)</label>
                <input v-model.number="quickAdd.lower_range" type="number" class="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500" placeholder="VD: 15000000" />
              </div>
              <div>
                <label class="text-xs text-gray-700 font-medium block mb-1">Lương mong muốn (Tối đa)</label>
                <input v-model.number="quickAdd.upper_range" type="number" class="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500" placeholder="VD: 20000000" />
              </div>
            </div>
            <div>
              <label class="text-xs text-gray-700 font-medium block mb-1">Lương offer phỏng vấn</label>
              <input v-model.number="quickAdd.custom_offered_salary" type="number" class="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500" placeholder="VD: 18000000" />
            </div>
            <div class="flex justify-end gap-2 pt-2 border-t">
              <Button @click="closeQuickAdd" class="btn-secondary font-medium">Hủy</Button>
              <Button @click="doQuickAdd" :loading="quickAdding" class="btn-success font-bold shadow-sm">Thêm ứng viên</Button>
            </div>
          </div>

          <!-- Right side: AI parsed results -->
          <div v-if="quickAdd.cvPreview" class="md:col-span-7 space-y-4 overflow-y-auto max-h-[70vh] pr-2 scrollbar-thin">
            <h4 class="text-sm font-semibold text-purple-800 flex items-center gap-1.5 pb-2 border-b">
              <span>🤖 Kết quả phân tích CV</span>
            </h4>
            
            <!-- Avatar & Fit Score -->
            <div class="flex flex-wrap items-center gap-4">
              <div v-if="quickAdd.cvPreview.avatar_base64" class="shrink-0">
                <img :src="'data:image/jpeg;base64,' + quickAdd.cvPreview.avatar_base64" class="w-14 h-14 rounded-full object-cover border shadow-sm" />
              </div>
              <div v-if="quickAdd.cvPreview.fit_score" class="flex-1 flex items-center gap-3 p-3 rounded-lg border" :class="fitBg(quickAdd.cvPreview.fit_score)">
                <div class="text-2xl font-bold shrink-0">{{ quickAdd.cvPreview.fit_score }}/100</div>
                <div>
                  <div class="font-semibold text-xs text-gray-800">{{ quickAdd.cvPreview.fit_level || 'Điểm phù hợp' }}</div>
                  <div class="text-[10px] text-gray-800 mt-0.5 leading-relaxed">{{ quickAdd.cvPreview.fit_reason }}</div>
                </div>
              </div>
            </div>

            <!-- Suggested Positions -->
            <div v-if="(quickAdd.cvPreview.suggested_positions || []).length" class="bg-purple-50 text-purple-800 rounded-lg p-2.5 text-[11px] border border-purple-100 flex items-center gap-1.5 flex-wrap animate-fadeIn">
              <span class="font-bold flex items-center gap-1">💡 Chức danh gợi ý:</span>
              <div class="flex flex-wrap gap-1">
                <span v-for="pos in quickAdd.cvPreview.suggested_positions" :key="pos" class="bg-white border border-purple-200 text-purple-700 px-1.5 py-0.5 rounded font-medium text-[10px]">{{ pos }}</span>
              </div>
            </div>

            <!-- Summary -->
            <div v-if="quickAdd.cvPreview.summary" class="bg-purple-50/50 rounded-lg p-3 text-xs border border-purple-100/50">
              <div class="font-semibold text-purple-900 mb-1">📝 Tóm tắt hồ sơ</div>
              <div class="text-gray-700 italic">"{{ quickAdd.cvPreview.summary }}"</div>
            </div>

            <!-- Meta Info (Dob, Gender, Location) -->
            <div class="grid grid-cols-3 gap-2 text-[11px] bg-gray-100 p-2.5 rounded-lg border border-gray-200">
              <div>
                <span class="text-gray-700">Ngày sinh</span>
                <div class="font-medium text-gray-700 mt-0.5">{{ quickAdd.cvPreview.dob || '—' }}</div>
              </div>
              <div>
                <span class="text-gray-700">Giới tính</span>
                <div class="font-medium text-gray-700 mt-0.5">{{ quickAdd.cvPreview.gender || '—' }}</div>
              </div>
              <div>
                <span class="text-gray-700">Địa chỉ</span>
                <div class="font-medium text-gray-700 mt-0.5 truncate" :title="quickAdd.cvPreview.location">{{ quickAdd.cvPreview.location || '—' }}</div>
              </div>
            </div>

            <!-- Strengths & Gaps -->
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div v-if="(quickAdd.cvPreview.strengths||[]).length">
                <div class="text-xs font-semibold text-green-700 mb-1 flex items-center gap-1">✅ Điểm mạnh</div>
                <ul class="space-y-1 bg-green-50/50 p-2.5 rounded-lg border border-green-100/50">
                  <li v-for="s in quickAdd.cvPreview.strengths" :key="s" class="text-[11px] text-gray-800 list-disc list-inside">{{ s }}</li>
                </ul>
              </div>
              <div v-if="(quickAdd.cvPreview.gaps||[]).length">
                <div class="text-xs font-semibold text-red-700 mb-1 flex items-center gap-1">⚠️ Cần bổ sung</div>
                <ul class="space-y-1 bg-red-50/50 p-2.5 rounded-lg border border-red-100/50">
                  <li v-for="g in quickAdd.cvPreview.gaps" :key="g" class="text-[11px] text-gray-800 list-disc list-inside">{{ g }}</li>
                </ul>
              </div>
            </div>

            <!-- Skills -->
            <div v-if="(quickAdd.cvPreview.skills||[]).length">
              <div class="text-xs font-semibold text-gray-800 mb-1">💡 Kỹ năng</div>
              <div class="flex flex-wrap gap-1 bg-gray-100 p-2 rounded-lg border border-gray-200">
                <span v-for="s in quickAdd.cvPreview.skills" :key="s" class="text-[10px] bg-blue-50 text-blue-700 rounded-full px-2 py-0.5 font-medium border border-blue-100">{{ s }}</span>
              </div>
            </div>

            <!-- Education -->
            <div v-if="(quickAdd.cvPreview.education||[]).length">
              <div class="text-xs font-semibold text-gray-800 mb-1">🎓 Học vấn</div>
              <ul class="space-y-1 bg-gray-100 p-2 rounded-lg border border-gray-200">
                <li v-for="e in quickAdd.cvPreview.education" :key="e" class="text-[10px] text-gray-800 border-l-2 border-blue-400 pl-2 py-0.5">{{ e }}</li>
              </ul>
            </div>

            <!-- Experience -->
            <div v-if="(quickAdd.cvPreview.experience||[]).length">
              <div class="text-xs font-semibold text-gray-800 mb-1">💼 Kinh nghiệm</div>
              <ul class="space-y-1.5 bg-gray-100 p-2 rounded-lg border border-gray-200">
                <li v-for="e in quickAdd.cvPreview.experience" :key="e" class="text-[10px] text-gray-700 border-l-2 border-purple-400 pl-2 py-0.5 whitespace-pre-line">{{ e }}</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal: Nhập kết quả phỏng vấn nhanh -->
    <div v-if="showQuickResultModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40" @click.self="showQuickResultModal=false">
      <div class="bg-white rounded-xl shadow-2xl w-full max-w-lg mx-4 p-6 space-y-4 max-h-[90vh] overflow-y-auto">
        <div class="flex items-center justify-between border-b pb-3">
          <h3 class="text-lg font-semibold text-gray-900">📝 Nhập kết quả phỏng vấn</h3>
          <button @click="showQuickResultModal=false" class="text-gray-700 hover:text-gray-800"><FeatherIcon name="x" class="h-5 w-5" /></button>
        </div>

        <div class="space-y-3">
          <div class="grid grid-cols-3 gap-2">
            <div>
              <label class="text-xs text-gray-700 block mb-1">Kết quả</label>
              <select v-model="quickResultForm.passed" class="w-full border rounded-lg px-3 py-2 text-sm">
                <option :value="true">Đạt</option>
                <option :value="false">Không đạt</option>
              </select>
            </div>
            <div>
              <label class="text-xs text-gray-700 block mb-1">Đánh gi chung</label>
              <select v-model="quickResultForm.rating" class="w-full border rounded-lg px-3 py-2 text-sm">
                <option value="">Chọn...</option>
                <option>Xuất sắc</option>
                <option>Tốt</option>
                <option>Khác</option>
                <option>Trung bình</option>
                <option>Yếu</option>
              </select>
            </div>
            <div>
              <label class="text-xs text-gray-700 block mb-1">Điểm (0-100)</label>
              <input v-model.number="quickResultForm.score" type="number" min="0" max="100" class="w-full border rounded-lg px-3 py-2 text-sm" />
            </div>
          </div>

          <div class="grid grid-cols-2 gap-3">
            <!-- Điểm mạnh -->
            <div class="space-y-1">
              <label class="text-xs text-gray-700">Điểm mạnh</label>
              <div class="max-h-36 overflow-y-auto space-y-0.5 bg-gray-100 rounded-lg p-2 border">
                <label v-for="s in presetStrengths" :key="s" class="flex items-center gap-1.5 cursor-pointer text-xs">
                  <input type="checkbox" :value="s" v-model="quickResultForm.strengthsChecked" class="w-3 h-3 rounded accent-green-600" />
                 ⭐ {{ s }}
                </label>
              </div>
              <input v-model="quickResultForm.strengthsCustom" class="w-full border rounded px-2 py-1 text-xs" placeholder="Thêm điểm mạnh khác..." />
            </div>
            <!-- Điểm yếu -->
            <div class="space-y-1">
              <label class="text-xs text-gray-700">Điểm yếu</label>
              <div class="max-h-36 overflow-y-auto space-y-0.5 bg-gray-100 rounded-lg p-2 border">
                <label v-for="w in presetWeaknesses" :key="w" class="flex items-center gap-1.5 cursor-pointer text-xs">
                  <input type="checkbox" :value="w" v-model="quickResultForm.weaknessesChecked" class="w-3 h-3 rounded accent-red-500" />
                 ⭐ {{ w }}
                </label>
              </div>
              <input v-model="quickResultForm.weaknessesCustom" class="w-full border rounded px-2 py-1 text-xs" placeholder="Thêm điểm yếu khác..." />
            </div>
          </div>

          <div class="grid grid-cols-2 gap-2">
            <div>
              <label class="text-xs text-gray-700 block mb-1">Ghi chờ</label>
              <textarea v-model="quickResultForm.notes" class="w-full border rounded-lg px-3 py-2 text-sm" rows="2" placeholder="Nhận xét chung..."></textarea>
            </div>
            <div>
              <label class="text-xs text-gray-700 block mb-1">ÝÝ kiến bổ sung</label>
              <textarea v-model="quickResultForm.exétra_notes" class="w-full border rounded-lg px-3 py-2 text-sm" rows="2" placeholder="Ý kiến khác..."></textarea>
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
               ⭐ {{ aiQuestionsError }}
              </div>
              <div v-else-if="!aiQuestions.length" class="text-xs text-gray-700 text-center py-4">
                Kháông tìm thấy dữ liệu CV phù hợp để gợi ý câu hỏi. Hãy chắc chắn ứng viên đã có file CV được phân tích.
              </div>
              <div v-else class="space-y-2">
                <div v-for="(q, index) in aiQuestions" :key="index" class="p-2.5 bg-white border border-purple-100/70 rounded-lg hover:border-purple-200 transition relative group shadow-sm">
                  <div class="text-xs font-medium text-gray-800 pr-6 leading-relaxed">{{ q.question }}</div>
                  <div class="text-[10px] text-purple-600 mt-1 italic flex items-center gap-1">
                    <span class="font-bold">Mục đích:</span>⭐ {{ q.purpose }}
                  </div>
                  <button type="button" @click="copyQuestion(q.question)" class="absolute top-2 right-2 p-1 rounded bg-gray-100 text-gray-700 hover:text-blue-600 hover:bg-blue-50 opacity-0 group-hover:opacity-100 transition shadow-sm" title="Sao chờp chưau hỏi">
                    <FeatherIcon name="copy" class="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="flex justify-end gap-2 pt-2 border-t">
          <Button @click="showQuickResultModal=false" class="btn-secondary font-medium">Hủy</Button>
          <Button @click="submitQuickResult" :loading="quickResultSubmitting" class="btn-success font-bold shadow-sm">Lưu kết quả</Button>
        </div>
      </div>
    </div>

    <!-- Modal: Xếp lịch phỏng vấn nhanh -->
    <div v-if="showQuickScheduleModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40" @click.self="showQuickScheduleModal=false">
      <div class="bg-white rounded-xl shadow-2xl w-full max-w-md mx-4 p-6 space-y-4 max-h-[90vh] overflow-y-auto">
        <div class="flex items-center justify-between border-b pb-3">
          <h3 class="text-lg font-semibold text-gray-900">📅 Lên lịch phỏng vấn nhanh</h3>
          <button @click="showQuickScheduleModal=false" class="text-gray-700 hover:text-gray-800"><FeatherIcon name="x" class="h-5 w-5" /></button>
        </div>

        <div class="space-y-3">
          <div>
            <label class="text-xs text-gray-700 block mb-1">Ứng viên</label>
            <div class="font-medium text-sm text-gray-800 bg-gray-100 px-3 py-2 rounded-lg border">{{ activeApplicant?.applicant_name }}</div>
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="text-xs text-gray-700 block mb-1">Vòng</label>
              <select v-model="quickScheduleForm.round" class="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500">
                <option>Vòng 1</option>
                <option>Vòng 2</option>
                <option>Vòng 3</option>
                <option>Phỏng vấn cuối</option>
              </select>
            </div>
            <div>
              <label class="text-xs text-gray-700 block mb-1">Ngày giờ</label>
              <input v-model="quickScheduleForm.date" type="datetime-local" class="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500" />
            </div>
          </div>
          <div>
            <label class="text-xs text-gray-700 block mb-1">Người phỏng vấn</label>
            <select v-model="quickScheduleForm.interviewer_employee" class="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500">
              <option value="">Chọn nhân viên...</option>
              <option v-for="e in employees" :key="e.name" :value="e.name">{{ e.employee_name }}<span v-if="e.designation"> —⭐ {{ e.designation }}</span></option>
            </select>
          </div>
          <div>
            <label class="text-xs text-gray-700 block mb-1">Ghi chờ</label>
            <input v-model="quickScheduleForm.notes" placeholder="Ghi chờ..." class="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500" />
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
               ⭐ {{ aiQuestionsError }}
              </div>
              <div v-else-if="!aiQuestions.length" class="text-xs text-gray-700 text-center py-4">
                Kháông tìm thấy dữ liệu CV phù hợp để gợi ý câu hỏi. Hãy chắc chắn ứng viên đã có file CV được phân tích.
              </div>
              <div v-else class="space-y-2">
                <div v-for="(q, index) in aiQuestions" :key="index" class="p-2.5 bg-white border border-purple-100/70 rounded-lg hover:border-purple-200 transition relative group shadow-sm">
                  <div class="text-xs font-medium text-gray-800 pr-6 leading-relaxed">{{ q.question }}</div>
                  <div class="text-[10px] text-purple-600 mt-1 italic flex items-center gap-1">
                    <span class="font-bold">Mục đích:</span>⭐ {{ q.purpose }}
                  </div>
                  <button type="button" @click="copyQuestion(q.question)" class="absolute top-2 right-2 p-1 rounded bg-gray-100 text-gray-700 hover:text-blue-600 hover:bg-blue-50 opacity-0 group-hover:opacity-100 transition shadow-sm" title="Sao chờp chưau hỏi">
                    <FeatherIcon name="copy" class="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="flex justify-end gap-2 pt-2 border-t">
          <Button @click="showQuickScheduleModal=false" class="btn-secondary font-medium">Hủy</Button>
          <Button @click="submitQuickSchedule" :loading="schedulingQuick" class="btn-success font-bold shadow-sm">Lên lịch & Chuyển trạng thái</Button>
        </div>
      </div>
    </div>

    <!-- Modal: Từ chối nhanh -->
    <div v-if="showQuickRejectModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40" @click.self="showQuickRejectModal=false">
      <div class="bg-white rounded-xl shadow-2xl w-full max-w-md mx-4 p-6 space-y-4 max-h-[90vh] overflow-y-auto">
        <div class="flex items-center justify-between border-b pb-3">
          <h3 class="text-lg font-semibold text-gray-900">❌ Từ chối ứng viên</h3>
          <button @click="showQuickRejectModal=false" class="text-gray-700 hover:text-gray-800"><FeatherIcon name="x" class="h-5 w-5" /></button>
        </div>

        <div class="space-y-3">
          <div>
            <label class="text-xs text-gray-700 block mb-1">Ứng viên</label>
            <div class="font-medium text-sm text-gray-800 bg-gray-100 px-3 py-2 rounded-lg border">{{ activeApplicant?.applicant_name }}</div>
          </div>
          <div>
            <label class="text-xs text-gray-700 block mb-1">L do từ chối</label>
            <textarea v-model="quickRejectForm.reason" rows="3" class="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500" placeholder="VD: Kinh nghiệm chưa phù hợp..."></textarea>
          </div>
          <div>
            <div class="flex items-center justify-between"><label class="text-xs text-gray-700">Yêu cầu chưan thiếu</label><button @click="quickRejectForm.missingReqs.push('')" class="text-xs text-blue-600">+ Thêm</button></div>
            <div class="space-y-1.5 mt-1">
              <div v-for="(r,i) in quickRejectForm.missingReqs" :key="i" class="flex gap-2">
                <input v-model="quickRejectForm.missingReqs[i]" class="flex-1 border rounded px-2 py-1 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500" placeholder="VD: Chưa có chứng chỉ AWS" />
                <button @click="quickRejectForm.missingReqs.splice(i,1)" class="text-gray-700 hover:text-red-500"><FeatherIcon name="x" class="h-4 w-4" /></button>
              </div>
            </div>
          </div>
        </div>

        <div class="flex justify-end gap-2 pt-2 border-t">
          <Button @click="showQuickRejectModal=false" class="btn-secondary font-medium">Hủy</Button>
          <Button @click="submitQuickReject" :loading="rejectingQuick" class="btn-danger font-bold">Xác nhận từ chối</Button>
        </div>
      </div>
    </div>

    <!-- Modal: Cón nhắc nhanh -->
    <div v-if="showQuickHoldModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40" @click.self="showQuickHoldModal=false">
      <div class="bg-white rounded-xl shadow-2xl w-full max-w-md mx-4 p-6 space-y-4 max-h-[90vh] overflow-y-auto">
        <div class="flex items-center justify-between border-b pb-3">
          <h3 class="text-lg font-semibold text-gray-900">🤔 Cân nhắc ứng viên</h3>
          <button @click="showQuickHoldModal=false" class="text-gray-700 hover:text-gray-800"><FeatherIcon name="x" class="h-5 w-5" /></button>
        </div>

        <div class="space-y-3">
          <div>
            <label class="text-xs text-gray-700 block mb-1">Ứng viên</label>
            <div class="font-medium text-sm text-gray-800 bg-gray-100 px-3 py-2 rounded-lg border">{{ activeApplicant?.applicant_name }}</div>
          </div>
          <div>
            <label class="text-xs text-gray-700 block mb-1">L do chưan nhắc</label>
            <input v-model="quickHoldForm.reason" class="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500" placeholder="VD: Cần thêm thời gian đánh gi..." />
          </div>
          <div>
            <div class="flex items-center justify-between"><label class="text-xs text-gray-700">Cần bổ sung thêm</label><button @click="quickHoldForm.missingReqs.push('')" class="text-xs text-blue-600">+ Thêm</button></div>
            <div class="space-y-1.5 mt-1">
              <div v-for="(r,i) in quickHoldForm.missingReqs" :key="i" class="flex gap-2">
                <input v-model="quickHoldForm.missingReqs[i]" class="flex-1 border rounded px-2 py-1 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500" placeholder="VD: Bổ sung chứng chỉ Cloud" />
                <button @click="quickHoldForm.missingReqs.splice(i,1)" class="text-gray-700 hover:text-red-500"><FeatherIcon name="x" class="h-4 w-4" /></button>
              </div>
            </div>
          </div>
        </div>

        <div class="flex justify-end gap-2 pt-2 border-t">
          <Button @click="showQuickHoldModal=false" class="btn-secondary font-medium">Hủy</Button>
          <Button @click="submitQuickHold" :loading="holdingQuick" class="btn-warning font-bold">Xác nhận cân nhắc</Button>
        </div>
      </div>
    </div>
    <!-- Modal: Tạo Nhân viên từ ứng viên trúng tuyển nhanh -->
    <div v-if="showConvertModal" class="fixed inset-0 z-50 flex items-start justify-center bg-black/40 pt-8 overflow-y-auto" @click.self="showConvertModal=false">
      <div class="bg-white rounded-xl shadow-2xl w-full max-w-lg mx-4 mb-8 p-6 space-y-4">
        <h3 class="text-lg font-semibold text-gray-900">👤 Tạo Nhân viên từ ứng viên</h3>
        <p class="text-sm text-gray-700 -mt-2">Thông tin tự động điền từ CV và hồ sơ ứng viên</p>

        <div v-if="convertLoading" class="flex items-center justify-center py-10">
          <LoadingIndicator />
        </div>
        <div v-else class="space-y-4">
          <div class="grid grid-cols-2 gap-3">
            <div><label class="text-xs text-gray-700 block mb-1">Họ <span class="text-red-400">*</span></label><input v-model="convertForm.first_name" class="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500" placeholder="Họ..." /></div>
            <div><label class="text-xs text-gray-700 block mb-1">Tên <span class="text-red-400">*</span></label><input v-model="convertForm.last_name" class="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500" placeholder="Tên..." /></div>
          </div>
          <div class="grid grid-cols-3 gap-3">
            <div>
              <label class="text-xs text-gray-700 block mb-1">Giới tính</label>
              <select v-model="convertForm.gender" class="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500">
                <option value="Male">Nam</option>
                <option value="Female">Nữ</option>
                <option value="Other">Khác</option>
              </select>
            </div>
            <div><label class="text-xs text-gray-700 block mb-1">Ngày sinh</label><input v-model="convertForm.dob" type="date" class="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500" /></div>
            <div><label class="text-xs text-gray-700 block mb-1">Ngày vào làm <span class="text-red-400">*</span></label><input v-model="convertForm.joining" type="date" class="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500" /></div>
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div><label class="text-xs text-gray-700 block mb-1">Email chưa nhân</label><input v-model="convertForm.email" class="w-full border rounded-lg px-3 py-2 text-sm bg-gray-100 focus:outline-none" readonly /></div>
            <div><label class="text-xs text-gray-700 block mb-1">SĐT</label><input v-model="convertForm.phone" class="w-full border rounded-lg px-3 py-2 text-sm bg-gray-100 focus:outline-none" readonly /></div>
          </div>
          <div><label class="text-xs text-gray-700 block mb-1">Địa chỉ</label><input v-model="convertForm.location" class="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500" placeholder="Nhập địa chỉ..." /></div>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="text-xs text-gray-700 block mb-1">Chức danh <span class="text-red-400">*</span></label>
              <select v-model="convertForm.designation" class="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500">
                <option value="">—</option>
                <option v-for="d in designations" :key="d" :value="d">{{ d }}</option>
              </select>
            </div>
            <div>
              <label class="text-xs text-gray-700 block mb-1">Phòng ban <span class="text-red-400">*</span></label>
              <select v-model="convertForm.department" class="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500">
                <option value="">—</option>
                <option v-for="d in departments" :key="d" :value="d">{{ d }}</option>
              </select>
            </div>
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div><label class="text-xs text-gray-700 block mb-1">Công ty <span class="text-red-400">*</span></label><input v-model="convertForm.company" class="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500" placeholder="GPC..." /></div>
            <div><label class="text-xs text-gray-700 block mb-1">Mức lương chính thức (Offer)</label><input v-model.number="convertForm.salary" type="number" class="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500" placeholder="VD: 15000000" /></div>
          </div>

          <div class="flex justify-end gap-2 pt-2 border-t">
            <Button @click="showConvertModal=false" class="btn-secondary font-medium">Hủy</Button>
            <Button @click="doConvert" :loading="converting" class="btn-success font-bold shadow-sm">Tạo nhân sự</Button>
          </div>
        </div>
      </div>
    </div>

    <!-- AI Chat Assistant Bubble -->
    <div class="fixed bottom-6 right-6 z-50">
      <!-- Floating Action Button -->
      <button 
        @click="toggleChat" 
        class="w-14 h-14 bg-purple-600 bg-gradient-to-tr from-purple-600 to-indigo-600 rounded-full flex items-center justify-center text-white shadow-lg hover:scale-105 active:scale-95 transition-all duration-200 cursor-pointer relative focus:outline-none"
      >
        <FeatherIcon v-if="!chatOpen" name="message-square" class="h-6 w-6 relative z-10" />
        <FeatherIcon v-else name="x" class="h-6 w-6 relative z-10" />
      </button>

      <!-- Chat Window -->
      <div 
        v-if="chatOpen" 
        class="fixed bottom-24 right-6 w-96 h-[500px] rounded-2xl bg-white shadow-xl border border-gray-300 flex flex-col overflow-hidden animate-fadeIn"
      >
        <!-- Header -->
        <div class="px-4 py-3 bg-purple-600 bg-gradient-to-r from-purple-600 to-indigo-600 text-white flex items-center justify-between shadow-sm">
          <div class="flex items-center gap-2.5">
            <div class="w-8 h-8 rounded-full bg-white/10 flex items-center justify-center text-base">🤖</div>
            <div>
              <div class="text-xs font-semibold leading-tight">Trợ lý Tuyển dụng AI</div>
              <div class="text-[9px] text-purple-200 flex items-center gap-1 mt-0.5">
                <span class="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse"></span>
                Đang trực tuyến
              </div>
            </div>
          </div>
          <button @click="chatOpen = false" class="text-white/80 hover:text-white transition"><FeatherIcon name="minus" class="h-4 w-4" /></button>
        </div>

        <!-- Message List -->
        <div ref="chatContainer" class="flex-1 p-4 overflow-y-auto space-y-3 bg-gray-100/50">
          <div v-for="(msg, idx) in chatMessages" :key="idx" class="flex flex-col" :class="msg.sender === 'user' ? 'items-end' : 'items-start'">
            <div 
              class="p-3 text-xs shadow-sm max-w-[85%] leading-relaxed" 
              :class="msg.sender === 'user' 
                ? 'bg-purple-600 bg-gradient-to-br from-purple-600 to-indigo-600 text-white rounded-2xl rounded-tr-none' 
                : 'bg-white text-gray-800 rounded-2xl rounded-tl-none border border-gray-200'"
            >
              <div v-html="renderMD(msg.text)"></div>
            </div>
            <span class="text-[9px] text-gray-700 mt-1 px-1">{{ msg.time }}</span>
          </div>

          <!-- Typing indicator -->
          <div v-if="chatTyping" class="flex items-start gap-1.5 self-start">
            <div class="bg-white text-gray-800 rounded-2xl rounded-tl-none border border-gray-200 p-3 text-xs shadow-sm flex items-center gap-1.5">
              <span class="text-xs">🤖 AI đang gõ</span>
              <div class="flex gap-1">
                <span class="w-1.5 h-1.5 bg-purple-500 rounded-full animate-bounce" style="animation-delay:0s"></span>
                <span class="w-1.5 h-1.5 bg-purple-500 rounded-full animate-bounce" style="animation-delay:0.15s"></span>
                <span class="w-1.5 h-1.5 bg-purple-500 rounded-full animate-bounce" style="animation-delay:0.3s"></span>
              </div>
            </div>
          </div>
        </div>

        <!-- Input Bar -->
        <form @submit.prevent="sendChatMessage" class="p-3 bg-white border-t flex gap-2 items-center">
          <input 
            v-model="chatInput" 
            placeholder="Hỏi trợ lý AI tuyển dụng..." 
            class="flex-1 border rounded-lg px-3 py-2 text-xs focus:outline-none focus:ring-1 focus:ring-purple-500 focus:border-purple-500"
            :disabled="chatTyping"
          />
          <button 
            type="submit" 
            class="p-2 rounded-lg bg-purple-600 bg-gradient-to-r from-purple-600 to-indigo-600 text-white hover:opacity-90 active:scale-95 transition disabled:opacity-50"
            :disabled="!chatInput.trim() || chatTyping"
          >
            <FeatherIcon name="send" class="h-3.5 w-3.5" />
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, reactive, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { frappeRequest, Button, FeatherIcon, LoadingIndicator } from 'frappe-ui'
import { useFrappeApi } from '../composables/useFrappeApi'
import { useRealtime } from '../composables/useRealtime'

const router = useRouter()

// --- Current logged-in user (from Frappe session/API) ---
const currentUser = ref({ email: 'Unknown', fullName: 'Unknown', image: null })

const profileMenuOpen = ref(false)

const closeProfileMenu = (e) => {
  const el = document.getElementById('profile-menu-container')
  if (el && !el.contains(e.target)) {
    profileMenuOpen.value = false
  }
}

async function logout() {
  try {
    await frappeRequest({ url: 'logout', method: 'POST' })
  } catch (e) {
    // ignore
  }
  window.location.href = '/portal_app/login'
}

function goBack() {
  if (window.history.length > 1) router.back()
  else router.push('/')
}

const tab = ref('dashboard')
const expanded = ref(null)
const showJobForm = ref(false)
const creatingJob = ref(false)
const adding = reactive({})
const fetchingApp = reactive({})
const dragApp = ref(null)
const draggedOverCol = ref(null)
const toast = ref('')
const cvFile = reactive({})
const cvParsed = reactive({})
const cvPreview = ref(null)  // Modal preview CV sau parse
const editingJob = ref(null) // Job đang sửa
const cvPreviewJobName = ref(null) // Job name của CV đang preview

// -- Quick Add --
const showQuickAdd = ref(false)
const quickAdding = ref(false)
const quickAdd = reactive({ job: '', name: '', email: '', phone: '', file: null, cvPreview: null, source: '', lower_range: 0, upper_range: 0, custom_offered_salary: 0 })
const quickAddParsing = ref(false)

async function onQuickAddCV(e) {
  const f = e.target.files?.[0]
  if (!f) return
  quickAdd.file = f
  quickAddParsing.value = true
  aiLoading.value = 'AI đang phân tích CV và đánh gi độ phù hợp...'
  try {
    const fd = new FormData(); fd.append('file', f)
    const res = await fetch('/api/method/hr.api.parse_cv?job_title=' + encodeURIComponent(quickAdd.job || ''), { method: 'POST', body: fd, headers: { 'X-Frappe-CSRF-Token': window.csrf_token || '' } })
    const p = (await res.json()).message || {}
    if (!p.error) {
      quickAdd.cvPreview = p
      if (p.name && !quickAdd.name) quickAdd.name = p.name
      if (p.email && !quickAdd.email) quickAdd.email = p.email
      if (p.phone && !quickAdd.phone) quickAdd.phone = p.phone
      toast.value = '✅ AI đã phân tích CV thành công'
      setTimeout(() => toast.value = '', 3000)
    } else {
      toast.value = '⚠️ ' + p.error
      setTimeout(() => toast.value = '', 3000)
    }
  } catch (err) {
    toast.value = '❌ Phân tích CV thất bại, vui lòng nhập tay'
    setTimeout(() => toast.value = '', 3000)
  } finally {
    quickAddParsing.value = false
    aiLoading.value = null
  }
}

function closeQuickAdd() {
  showQuickAdd.value = false
  quickAddParsing.value = false
  Object.assign(quickAdd, { job: '', name: '', email: '', phone: '', file: null, cvPreview: null, source: '', lower_range: 0, upper_range: 0, custom_offered_salary: 0 })
}

function openQuickAdd() {
  console.log('[QuickAdd] Opening modal, openings:', openings.value?.length)
  showQuickAdd.value = true
}

async function doQuickAdd() {
  if (!quickAdd.job || !quickAdd.name.trim()) return
  quickAdding.value = true
  try {
    let resume_attachment = null
    if (quickAdd.file) {
      const fd = new FormData(); fd.append('file', quickAdd.file); fd.append('is_private', '0'); fd.append('doctype', 'Job Applicant'); fd.append('fieldname', 'resume_attachment')
      const up = await (await fetch('/api/method/upload_file', { method: 'POST', body: fd, headers: { 'X-Frappe-CSRF-Token': window.csrf_token || '' } })).json()
      if (up.message?.file_url) resume_attachment = up.message.file_url
    }
    const params = {
      job_title: quickAdd.job,
      applicant_name: quickAdd.name.trim(),
      email_id: quickAdd.email.trim(),
      phone_number: quickAdd.phone.trim(),
      cv_data: quickAdd.cvPreview || null,
      resume_attachment,
      source_name: quickAdd.source || null,
      lower_range: quickAdd.lower_range || 0,
      upper_range: quickAdd.upper_range || 0,
      custom_offered_salary: quickAdd.custom_offered_salary || 0
    }
    await frappeRequest({ url: 'hr.api.create_job_applicant', method: 'POST', params })
    toast.value = '✅ Đã thêm ' + quickAdd.name
    setTimeout(() => toast.value = '', 3000)
    closeQuickAdd()
    await loadAllApplicants()
    await loadDashboard()
  } catch (e) { toast.value = '❌ ' + (e.message||'Lỗi'); setTimeout(() => toast.value = '', 3000) }
  quickAdding.value = false
}

// ── Realtime ──
useRealtime(['Job Applicant', 'Job Opening'], async (event, data) => {
  console.log('[realtime] refresh due to:', event, data?.doctype, data?.docname)
  if (data?.doctype === 'Job Opening') {
    await refreshJobs()
    if (tab.value === 'dashboard') await loadDashboard()
  }
  if (data?.doctype === 'Job Applicant') {
    if (tab.value === 'dashboard') await loadDashboard()
    if (tab.value === 'pipeline') await loadPipeline()
    // Refresh expanded job if any
    const j = openings.value?.find(o => o.name === expanded.value)
    if (j) await refreshApplicants(j)
  }
})

const tabs = computed(() => [
  { key: 'dashboard', label: 'Dashboard', icon: 'bar-chart-2' },
  { key: 'jobs', label: 'Vị trí tuyển', icon: 'briefcase', badge: openings.value?.filter(o => o.status === 'Open').length || 0, badgeColor: 'bg-indigo-600 text-white' },
  { key: 'applicants', label: 'Ứng viên', icon: 'users', badge: dash.value.applicants_today || 0, badgeColor: 'bg-emerald-500 text-white' },
  { key: 'interviews', label: 'Phỏng vấn', icon: 'calendar', badge: todayInterviews.value?.length || 0, badgeColor: 'bg-amber-500 text-white' },
  { key: 'pipeline', label: 'Pipeline', icon: 'trello' },
])

// -- Dashboard --
const dash = ref({ jobs_open: 0, applicants_total: 0, applicants_today: 0, by_status: {}, by_source: {} })
const dashLoading = ref(false)

const funnel = computed(() => [
  { key: 'Open', label: 'Ứng tuyển', count: dash.value.by_status?.Open || 0, color: 'bg-blue-400' },
  { key: 'Shortlisted', label: 'Sơ tuyển', count: dash.value.by_status?.Shortlisted || 0, color: 'bg-amber-400' },
  { key: 'Replied', label: 'Phỏng vấn', count: dash.value.by_status?.Replied || 0, color: 'bg-purple-400' },
  { key: 'Hold', label: 'Cân nhắc', count: dash.value.by_status?.Hold || 0, color: 'bg-orange-400' },
  { key: 'Accepted', label: 'Trúng tuyển', count: dash.value.by_status?.Accepted || 0, color: 'bg-green-400' },
  { key: 'Rejected', label: 'Từ chối', count: dash.value.by_status?.Rejected || 0, color: 'bg-red-400' },
])

const conversionRate = computed(() => {
  const t = dash.value.applicants_total
  const a = dash.value.by_status?.Accepted || 0
  return t ? Math.round(a / t * 100) : 0
})

function funnelHeight(count) {
  const max = Math.max(...funnel.value.map(f => f.count), 1)
  return Math.max(8, (count / max) * 100)
}

function sourcePct(count) {
  const t = dash.value.applicants_total || 1
  return Math.round(count / t * 100)
}

// -- Jobs --
const { data: openings, loading, fetch: refreshJobs } = useFrappeApi('hr.api.get_job_openings', { initialData: [] })
const { data: departments } = useFrappeApi('hr.api.get_departments', { initialData: [], auto: true })
const { data: designations } = useFrappeApi('hr.api.get_designations', { initialData: [], auto: true })

const generatingJD = ref(false)
const aiLoading = ref(null)  // string message = overlay hiện, null = ẩn
const jdPreview = ref(false)

function renderMD(text) {
  if (!text) return ''
  return text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\n- /g, '<br/>• ')
    .replace(/\n\n/g, '<br/><br/>')
    .replace(/\n/g, '<br/>')
}

async function generateJD() {
  const title = jobForm.job_title.trim()
  if (!title) return
  generatingJD.value = true
  aiLoading.value = 'AI đang phân tích và soạn JD phù hợp...'
  try {
    const jd = await frappeRequest({ url: 'hr.api.generate_jd', method: 'POST', params: { job_title: title, departments: JSON.stringify(departments.value || []) } })
    if (jd.job_title) jobForm.job_title = jd.job_title
    if (jd.description) jobForm.description = jd.description
    if (jd.requirements?.length) jobForm.requirements = jd.requirements
    if (jd.benefits?.length) jobForm.benefits = jd.benefits
    if (jd.salary_range) jobForm.salary_range = jd.salary_range
    if (jd.positions) jobForm.positions = parseInt(jd.positions) || 1
    if (jd.department && departments.value.includes(jd.department)) jobForm.department = jd.department
    jdPreview.value = true
    toast.value = '✅ AI đã soạn JD đầy đủ — xem preview'
    setTimeout(() => toast.value = '', 3000)
  } catch (e) { toast.value = '❌ ' + (e.message || 'Lỗi'); setTimeout(() => toast.value = '', 3000) }
  generatingJD.value = false
  aiLoading.value = null
}

function closeJobForm() {
  showJobForm.value = false
  editingJob.value = null
  jdPreview.value = false
  Object.assign(jobForm, { job_title: '', department: '', designation: '', description: '', closes_on: '', salary_range: '', positions: 1, recruiter: '', requirements: [''], benefits: [''] })
}
async function onDesignationChange() {
  // Auto-set job_title from designation if empty
  if (!jobForm.job_title.trim()) jobForm.job_title = jobForm.designation
  // Auto-suggest department based on existing employees with this designation
  if (!jobForm.department && jobForm.designation) {
    try {
      const r = await frappeRequest({ url: 'hr.api.get_designation_department', method: 'GET', params: { designation: jobForm.designation } })
      if (r.department && departments.value.includes(r.department)) jobForm.department = r.department
    } catch {}
  }
}
function addReq() { jobForm.requirements.push('') }
function addBen() { jobForm.benefits.push('') }

const jobFilter = reactive({ search: '', status: '' })
const jobApplicants = ref([])
const applicantCounts = ref({})
const allApplicants = ref([])
const pipelineLoading = ref(false)

// Filters
const appFilter = reactive({ search: '', status: '' })
const pipelineFilter = reactive({ search: '', job: '' })

const filteredApplicants = computed(() => {
  let arr = jobApplicants.value
  if (appFilter.search) {
    const q = appFilter.search.toLowerCase()
    arr = arr.filter(a => (a.applicant_name||'').toLowerCase().includes(q) || (a.email_id||'').toLowerCase().includes(q))
  }
  if (appFilter.status) {
    arr = arr.filter(a => a.status === appFilter.status)
  }
  return arr
})

const pipelineCols = computed(() => {
  let apps = allApplicants.value
  if (pipelineFilter.search) {
    const q = pipelineFilter.search.toLowerCase()
    apps = apps.filter(a => (a.applicant_name||'').toLowerCase().includes(q))
  }
  if (pipelineFilter.job) {
    apps = apps.filter(a => a.job_title === pipelineFilter.job)
  }
  return pipelineStages.map(s => ({ ...s, tasks: apps.filter(a => a.status === s.key) }))
})

const applicantStages = [
  { key: 'Open', label: 'Ứng tuyển' },
  { key: 'Shortlisted', label: 'Sơ tuyển' },
  { key: 'Replied', label: 'Phỏng vấn' },
  { key: 'Hold', label: 'Cân nhắc' },
  { key: 'Accepted', label: 'Trúng tuyển' },
  { key: 'Rejected', label: 'Từ chối' },
]
const pipelineStages = [
  { key: 'Open', label: 'Ứng tuyển', color: 'bg-blue-500' },
  { key: 'Shortlisted', label: 'Sơ tuyển', color: 'bg-amber-500' },
  { key: 'Replied', label: 'Phỏng vấn', color: 'bg-purple-500' },
  { key: 'Hold', label: 'Cân nhắc', color: 'bg-orange-500' },
  { key: 'Accepted', label: 'Trúng tuyển', color: 'bg-green-500' },
  { key: 'Rejected', label: 'Từ chối', color: 'bg-red-400' },
]

// -- All applicants tab --
const allAppFilter = reactive({ search: '', status: '', job: '' })
const allAppsLoading = ref(false)
const selectedApplicants = ref([])

const filteredAllApplicants = computed(() => {
  let arr = allApplicants.value
  if (allAppFilter.search) {
    const q = allAppFilter.search.toLowerCase()
    arr = arr.filter(a => (a.applicant_name||'').toLowerCase().includes(q) || (a.email_id||'').toLowerCase().includes(q) || (a.phone_number||'').includes(q))
  }
  if (allAppFilter.status) arr = arr.filter(a => a.status === allAppFilter.status)
  if (allAppFilter.job) arr = arr.filter(a => a.job_title === allAppFilter.job)
  return arr
})

const isAllSelected = computed(() => {
  const visible = filteredAllApplicants.value || []
  if (!visible.length) return false
  return visible.every(a => selectedApplicants.value.includes(a.name))
})

function toggleSelectAll() {
  const visible = filteredAllApplicants.value || []
  if (isAllSelected.value) {
    const visibleNames = visible.map(a => a.name)
    selectedApplicants.value = selectedApplicants.value.filter(name => !visibleNames.includes(name))
  } else {
    const newSelections = new Set([...selectedApplicants.value, ...visible.map(a => a.name)])
    selectedApplicants.value = Array.from(newSelections)
  }
}

async function deleteSelected() {
  const count = selectedApplicants.value.length
  if (!count) return
  if (!confirm(`Xóa ${count} ứng viên đã chon? Hành động này không thể hoàn tác.`)) return
  
  aiLoading.value = `Đang xóa ${count} ứng viên...`
  try {
    await frappeRequest({
      url: 'hr.api.delete_multiple_applicants',
      method: 'POST',
      params: {
        names: JSON.stringify(selectedApplicants.value)
      }
    })
    toast.value = `✅ Đ xóa thành công ${count} ứng viên`
    setTimeout(() => toast.value = '', 3000)
    selectedApplicants.value = []
    await loadAllApplicants()
    await loadDashboard()
  } catch (e) {
    toast.value = '❌ ' + (e.message || 'Lỗi khi xóa nhiều ứng viên')
    setTimeout(() => toast.value = '', 3000)
  } finally {
    aiLoading.value = null
  }
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
function avatarColor(n) { let h=0; for(let i=0;i<(n||'').length;i++)h=n.charCodeAt(i)+((h<<5)-h); const c=['#3b82f6','#8b5cf6','#ec4899','#f59e0b','#10b981','#6366f1','#ef4444','#84cc16']; return c[Math.abs(h)%c.length] }
function initials(n) {
  if (!n) return '?'
  const clean = n.replace(/[^\p{L}\p{N}\s]/gu, '').replace(/\s+/g, ' ').trim()
  if (!clean) return '?'
  const p = clean.split(/\s+/)
  return p.length >= 2 
    ? (p[p.length - 2][0] + p[p.length - 1][0]).toUpperCase() 
    : p[0].slice(0, 2).toUpperCase()
}

async function loadAllApplicants() {
  allAppsLoading.value = true
  selectedApplicants.value = []
  try {
    const data = await frappeRequest({ url: 'hr.api.get_job_applicants', method: 'GET', params: {} })
    allApplicants.value = data || []
  } catch {}
  allAppsLoading.value = false
}

// -- Lifecycle --
onMounted(async () => {
  document.addEventListener('click', closeProfileMenu)

  // Load current user info
  try {
    const userRes = await frappeRequest({ url: 'hr.api.get_current_user', method: 'GET' })
    if (userRes) {
      currentUser.value = userRes
    }
  } catch (err) {
    const session = window?.frappe?.session || {}
    const boot = window?.frappe?.boot || {}
    const user = session.user || 'Administrator'
    const info = boot.user_info?.[user] || {}
    currentUser.value = {
      email: info.email || user,
      fullName: info.fullname || info.full_name || boot.full_name || user,
      image: info.image || info.user_image || boot.user_image || null
    }
  }

  await Promise.all([
    loadDashboard(),
    refreshJobs(),
    loadAllApplicants(),
    loadAllInterviews(),
  ])
})

onUnmounted(() => {
  document.removeEventListener('click', closeProfileMenu)
})

watch(() => tab.value, async (t) => {
  if (t === 'dashboard') {
    await Promise.all([
      loadDashboard(),
      loadAllApplicants(),
      loadAllInterviews()
    ])
  }
  if (t === 'applicants') await loadAllApplicants()
  if (t === 'pipeline') await loadPipeline()
  if (t === 'interviews') await loadAllInterviews()
})

watch(openings, (jobs) => { loadAllCounts(jobs) })

async function loadAllCounts(jobs) {
  const list = jobs || openings.value || []
  for (const j of list) {
    try {
      const data = await frappeRequest({ url: 'hr.api.get_job_applicants', method: 'GET', params: { job: j.name } })
      applicantCounts.value[j.name] = (data || []).length
    } catch { applicantCounts.value[j.name] = '—' }
  }
}

// -- Interviews Tab --
const interviewsList = ref([])
const interviewsLoading = ref(false)
const interviewFilter = reactive({ search: '', status: '', interviewer: '', startDate: '', endDate: '' })

const activeOpenings = computed(() => {
  return (openings.value || []).filter(j => j.status === 'Open')
})

function getProgressColor(ratio) {
  if (ratio >= 1.0) return 'from-emerald-500 to-green-500'
  if (ratio >= 0.5) return 'from-blue-500 to-indigo-500'
  return 'from-amber-500 to-orange-500'
}

function formatTime(val) {
  if (!val) return ''
  const parts = String(val).trim().split(/[ T]/)
  if (parts.length < 2) return ''
  const timePart = parts[1]
  const match = timePart.match(/^(\d{1,2}):(\d{1,2})/)
  if (match) {
    return `${match[1].padStart(2, '0')}:${match[2].padStart(2, '0')}`
  }
  return ''
}

function viewJobDetails(j) {
  tab.value = 'jobs'
  expanded.value = j.name
}

function isNearDeadline(dateStr) {
  if (!dateStr) return false
  const deadline = new Date(dateStr)
  const today = new Date()
  const diffTime = deadline - today
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  return diffDays >= 0 && diffDays <= 7
}

const upcomingInterviews = computed(() => {
  return interviewsList.value.filter(iv => iv.status === 'scheduled')
})

const todayInterviews = computed(() => {
  const todayStr = new Date().toISOString().split('T')[0]
  return interviewsList.value.filter(iv => {
    if (iv.status !== 'scheduled' || !iv.date) return false
    const ivDate = iv.date.includes('T') ? iv.date.split('T')[0] : iv.date.split(' ')[0]
    return ivDate === todayStr
  })
})

const nextInterviews = computed(() => {
  const todayStr = new Date().toISOString().split('T')[0]
  return interviewsList.value.filter(iv => {
    if (iv.status !== 'scheduled' || !iv.date) return false
    const ivDate = iv.date.includes('T') ? iv.date.split('T')[0] : iv.date.split(' ')[0]
    return ivDate > todayStr
  }).sort((a, b) => new Date(a.date) - new Date(b.date))
})

function clearDateFilter() {
  interviewFilter.startDate = ''
  interviewFilter.endDate = ''
}

async function loadAllInterviews() {
  interviewsLoading.value = true
  try {
    const data = await frappeRequest({ url: 'hr.api.get_all_interviews', method: 'GET' })
    interviewsList.value = data || []
  } catch (e) {
    console.error(e)
  }
  interviewsLoading.value = false
}

const uniqueInterviewers = computed(() => {
  const set = new Set()
  interviewsList.value.forEach(iv => {
    if (iv.interviewer) set.add(iv.interviewer)
  })
  return Array.from(set)
})

const filteredInterviews = computed(() => {
  let arr = interviewsList.value
  if (interviewFilter.search) {
    const q = interviewFilter.search.toLowerCase()
    arr = arr.filter(iv => 
      (iv.applicant_name||'').toLowerCase().includes(q) || 
      (iv.job_opening_title||'').toLowerCase().includes(q)
    )
  }
  if (interviewFilter.status) {
    arr = arr.filter(iv => iv.status === interviewFilter.status)
  }
  if (interviewFilter.interviewer) {
    arr = arr.filter(iv => iv.interviewer === interviewFilter.interviewer)
  }
  if (interviewFilter.startDate) {
    arr = arr.filter(iv => iv.date && iv.date.split('T')[0] >= interviewFilter.startDate)
  }
  if (interviewFilter.endDate) {
    arr = arr.filter(iv => iv.date && iv.date.split('T')[0] <= interviewFilter.endDate)
  }
  return arr
})

// -- Quick Result Entry --
const showQuickResultModal = ref(false)
const quickResultInterview = ref(null)
const quickResultForm = reactive({
  passed: true,
  score: 70,
  rating: '',
  strengthsChecked: [],
  strengthsCustom: '',
  weaknessesChecked: [],
  weaknessesCustom: '',
  notes: '',
  exétra_notes: ''
})
const quickResultSubmitting = ref(false)

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
      aiQuestionsError.value = 'Kháông thể tải câu hỏi gợi ý'
    }
  } catch (err) {
    aiQuestionsError.value = err.message || 'Lỗi hệ thống'
  } finally {
    loadingAiQuestions.value = false
  }
}

function copyQuestion(text) {
  navigator.clipboard.writeTexét(text).then(() => {
    toast.value = '📋 Đ sao chép câu hỏi vào bộ nhớ tạm'
    setTimeout(() => toast.value = '', 2500)
  }).catch(() => {
    toast.value = '❌ Sao chép thất bại'
    setTimeout(() => toast.value = '', 2500)
  })
}

// -- AI Chat Assistant Bubble --
const chatOpen = ref(false)
const chatInput = ref('')
const chatTyping = ref(false)
const chatContainer = ref(null)
const chatMessages = ref([
  {
    sender: 'assistant',
    text: 'Xin chào! Tôi là Trợ lý Tuyển dụng AI. Tôi có thể giúp gì cho bạn hôm nay?\n\nBạn có thể hỏi tôi về:\n- Cách tạo vị trí tuyển dụng mới\n- Hướng dẫn tải lên và phân tích CV bằng AI\n- Cách lên lịch phỏng vấn và nhập kết quả\n- Các phím tắt nhanh trên Dashboard',
    time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }
])

function toggleChat() {
  chatOpen.value = !chatOpen.value
  if (chatOpen.value) {
    scrollToChatBottom()
  }
}

function scrollToChatBottom() {
  setTimeout(() => {
    if (chatContainer.value) {
      chatContainer.value.scrollTop = chatContainer.value.scrollHeight
    }
  }, 100)
}

async function sendChatMessage() {
  const text = chatInput.value.trim()
  if (!text || chatTyping.value) return
  
  chatMessages.value.push({
    sender: 'user',
    text,
    time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  })
  chatInput.value = ''
  chatTyping.value = true
  scrollToChatBottom()
  
  try {
    const history = chatMessages.value.slice(-10).map(m => ({
      sender: m.sender,
      text: m.text
    }))
    
    const res = await frappeRequest({
      url: 'hr.api.chat_recruitment_helper',
      method: 'POST',
      params: {
        message: text,
        history: JSON.stringify(history)
      }
    })
    
    chatMessages.value.push({
      sender: 'assistant',
      text: res?.response || 'Xin lỗi, tôi gặp sự cố khi xử lý câu trả lời.',
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    })
  } catch (err) {
    chatMessages.value.push({
      sender: 'assistant',
      text: '⚠️ Kháông thể kết nối với máy chủ AI. Vui lòng thử lại sau.',
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    })
  } finally {
    chatTyping.value = false
    scrollToChatBottom()
  }
}

const presetStrengths = [
  'Giao tiếp tốt', 'Kỹ thuật vững', 'Kinh nghiệm phù hợp', 'Làm việc nhóm tốt',
  'Chủ động, sáng tạo', 'Tiếng Anh tốt', 'Tư duy logic', 'Có tố chất lãnh đạo',
  'Giải quyết vấn đề tốt', 'Chịu được áp lực cao', 'Cầu tiến, ham học hỏi',
]
const presetWeaknesses = [
  'Thiếu kinh nghiệm quản lý', 'Kỹ năng gio tiếp cần cải thiện', 'Tiếng Anh chưa tốt',
  'Thiếu chứng chỉ chuyên môn', 'Chưa có kinh nghiệm thực tế', 'Kiến thức domain còn yếu',
  'Kỹ năng làm việc nhóm hạn chế', 'Kỹ năng thuyết trình yếu', 'ThiếuÝ kiến thức về cloud',
  'Chưa quen Agile/Scrum',
]

function openQuickResult(iv) {
  quickResultInterview.value = iv
  quickResultForm.passed = true
  quickResultForm.score = iv.score || 70
  quickResultForm.rating = iv.rating || ''
  quickResultForm.strengthsChecked = (iv.strengths || []).filter(s => presetStrengths.includes(s))
  quickResultForm.strengthsCustom = (iv.strengths || []).filter(s => !presetStrengths.includes(s)).join(', ')
  quickResultForm.weaknessesChecked = (iv.weaknesses || []).filter(w => presetWeaknesses.includes(w))
  quickResultForm.weaknessesCustom = (iv.weaknesses || []).filter(w => !presetWeaknesses.includes(w)).join(', ')
  quickResultForm.notes = iv.notes || ''
  quickResultForm.exétra_notes = iv.exétra_notes || ''
  showQuickResultModal.value = true
  loadAiSuggestedQuestions(iv.applicant_id)
}

async function submitQuickResult() {
  const iv = quickResultInterview.value
  if (!iv) return
  quickResultSubmitting.value = true
  try {
    const strengths = [...quickResultForm.strengthsChecked]
    if (quickResultForm.strengthsCustom.trim()) {
      strengths.push(...quickResultForm.strengthsCustom.split(',').map(s => s.trim()).filter(Boolean))
    }
    const weaknesses = [...quickResultForm.weaknessesChecked]
    if (quickResultForm.weaknessesCustom.trim()) {
      weaknesses.push(...quickResultForm.weaknessesCustom.split(',').map(s => s.trim()).filter(Boolean))
    }
    
    await frappeRequest({
      url: 'hr.api.submit_interview_result',
      method: 'POST',
      params: {
        applicant: iv.applicant_id,
        interview_id: iv.id,
        passed: quickResultForm.passed,
        score: quickResultForm.score,
        rating: quickResultForm.rating,
        strengths: JSON.stringify(strengths),
        weaknesses: JSON.stringify(weaknesses),
        notes: quickResultForm.notes,
        exétra_notes: quickResultForm.exétra_notes,
      }
    })
    
    toast.value = '✅ Đ lưu kết quả phỏng vấn'
    setTimeout(() => toast.value = '', 3000)
    showQuickResultModal.value = false
    quickResultInterview.value = null
    await loadAllInterviews()
    await loadDashboard()
  } catch (e) {
    toast.value = '❌ ' + (e.message || 'Lỗi')
    setTimeout(() => toast.value = '', 3000)
  }
  quickResultSubmitting.value = false
}

// -- Status Transitions and Modals --
const activeApplicant = ref(null)
const showQuickScheduleModal = ref(false)
const showQuickRejectModal = ref(false)
const showQuickHoldModal = ref(false)

const quickScheduleForm = ref({ round: 'Vòng 1', date: '', interviewer_employee: '', notes: '' })
const quickRejectForm = reactive({ reason: '', missingReqs: [''] })
const quickHoldForm = reactive({ reason: '', missingReqs: [''] })

const employees = ref([])
async function loadEmployees() {
  if (employees.value.length) return
  try {
    const data = await frappeRequest({ url: 'hr.api.get_employees', method: 'GET', params: {} })
    employees.value = data || []
  } catch {}
}

async function onStatusChange(applicant, newStatus) {
  activeApplicant.value = applicant
  
  if (newStatus === 'Replied') {
    quickScheduleForm.value = { round: 'Vòng 1', date: '', interviewer_employee: '', notes: '' }
    await loadEmployees()
    showQuickScheduleModal.value = true
    loadAiSuggestedQuestions(applicant.name)
  } else if (newStatus === 'Rejected') {
    Object.assign(quickRejectForm, { reason: '', missingReqs: [''] })
    showQuickRejectModal.value = true
  } else if (newStatus === 'Hold') {
    Object.assign(quickHoldForm, { reason: '', missingReqs: [''] })
    showQuickHoldModal.value = true
  } else {
    await moveApplicant(applicant, newStatus)
  }
}

const schedulingQuick = ref(false)
async function submitQuickSchedule() {
  const a = activeApplicant.value
  if (!a) return
  if (!quickScheduleForm.value.date) { toast.value = 'Vui lêng chon ngày giờ'; return }
  schedulingQuick.value = true
  try {
    await frappeRequest({ url: 'hr.api.schedule_interview', method: 'POST', params: { applicant: a.name, ...quickScheduleForm.value } })
    toast.value = '✅ Đ lên lịch phỏng vấn cho ' + a.applicant_name
    setTimeout(() => toast.value = '', 3000)
    a.status = 'Replied'
    showQuickScheduleModal.value = false
    activeApplicant.value = null
    await loadAllApplicants()
    if (tab.value === 'pipeline') await loadPipeline()
    if (tab.value === 'interviews') await loadAllInterviews()
  } catch (e) { toast.value = '❌ ' + (e.message || 'Lỗi'); setTimeout(() => toast.value = '', 3000) }
  schedulingQuick.value = false
}

const rejectingQuick = ref(false)
async function submitQuickReject() {
  const a = activeApplicant.value
  if (!a) return
  rejectingQuick.value = true
  try {
    await frappeRequest({
      url: 'hr.api.reject_applicant',
      method: 'POST',
      params: {
        name: a.name,
        reason: quickRejectForm.reason,
        missing_requirements: JSON.stringify(quickRejectForm.missingReqs.filter(r => r.trim()))
      }
    })
    toast.value = '✅ Đ từ chối ứng viên ' + a.applicant_name
    setTimeout(() => toast.value = '', 3000)
    a.status = 'Rejected'
    showQuickRejectModal.value = false
    activeApplicant.value = null
    await loadAllApplicants()
    if (tab.value === 'pipeline') await loadPipeline()
    await loadAllInterviews()
  } catch (e) { toast.value = '❌ ' + (e.message || 'Lỗi'); setTimeout(() => toast.value = '', 3000) }
  rejectingQuick.value = false
}

const holdingQuick = ref(false)
async function submitQuickHold() {
  const a = activeApplicant.value
  if (!a) return
  holdingQuick.value = true
  try {
    await frappeRequest({
      url: 'hr.api.hold_applicant',
      method: 'POST',
      params: {
        name: a.name,
        reason: quickHoldForm.reason,
        missing_requirements: JSON.stringify(quickHoldForm.missingReqs.filter(r => r.trim()))
      }
    })
    toast.value = '✅ Đ chuyển cân nhắc ứng viên ' + a.applicant_name
    setTimeout(() => toast.value = '', 3000)
    a.status = 'Hold'
    showQuickHoldModal.value = false
    activeApplicant.value = null
    await loadAllApplicants()
    if (tab.value === 'pipeline') await loadPipeline()
    await loadAllInterviews()
  } catch (e) { toast.value = '❌ ' + (e.message || 'Lỗi'); setTimeout(() => toast.value = '', 3000) }
  holdingQuick.value = false
}

// -- Dashboard --
async function loadDashboard() {
  dashLoading.value = true
  try { dash.value = await frappeRequest({ url: 'hr.api.get_recruitment_dashboard', method: 'GET', params: {} }) || dash.value } catch {}
  dashLoading.value = false
}

// -- Jobs --
const newApplicant = reactive({})

function setApplicantField(jobName, field, value) {
  if (!newApplicant[jobName]) newApplicant[jobName] = { name: '', email: '' }
  newApplicant[jobName][field] = value
}

function fbShareUrl(j) {
  const text = encodeURIComponent('GPC tuyển dụng: ' + j.job_title + ' - ' + (j.department||'') + '\n' + (j.description||'').slice(0,200))
  return 'https://www.facebook.com/sharer/sharer.php?u=' + encodeURIComponent(window.location.origin + '/hr_app') + '&quote=' + text
}
function goApplicant(a) { router.push('/applicant/' + a.name) }

const parsingCV = reactive({})

async function onCVFile(e, jobName) {
  const f = e.target.files?.[0]
  if (!f) return
  cvFile[jobName] = f

  // AI parse CV → auto-fill form
  parsingCV[jobName] = true
  aiLoading.value = 'AI đang phân tích CV và đánh gi độ phù hợp...'
  try {
    const fd = new FormData()
    fd.append('file', f)
    const res = await fetch('/api/method/hr.api.parse_cv?job_title=' + encodeURIComponent(jobName), { method: 'POST', body: fd, headers: { 'X-Frappe-CSRF-Token': window.csrf_token || '' } })
    const data = await res.json()
    const p = data.message || {}
    if (!p.error) {
      if (!newApplicant[jobName]) newApplicant[jobName] = { name: '', email: '' }
      if (p.name && !newApplicant[jobName].name) newApplicant[jobName].name = p.name
      if (p.email && !newApplicant[jobName].email) newApplicant[jobName].email = p.email
      // Lưu parsed data và hiện preview
      cvParsed[jobName] = p
      cvPreview.value = p
      cvPreviewJobName.value = jobName
      toast.value = '🤖 Xem trước CV — nhấn Lưu để thêm ứng viên'
      setTimeout(() => toast.value = '', 4000)
    } else {
      toast.value = '⚠️ ' + p.error
      setTimeout(() => toast.value = '', 3000)
    }
  } catch (e) { toast.value = '⚠️ Parse CV thất bại, điền tay nhé'; setTimeout(() => toast.value = '', 3000) }
  parsingCV[jobName] = false
  aiLoading.value = null
}

async function toggleJob(job) {
  if (expanded.value === job.name) { expanded.value = null; return }
  expanded.value = job.name
  if (!newApplicant[job.name]) newApplicant[job.name] = { name: '', email: '' }
  await refreshApplicants(job)
}

async function refreshApplicants(job) {
  fetchingApp[job.name] = true
  try {
    const data = await frappeRequest({ url: 'hr.api.get_job_applicants', method: 'GET', params: { job: job.name } })
    jobApplicants.value = data || []
    applicantCounts.value[job.name] = (data || []).length
    appFilter.search = ''; appFilter.status = ''
  } catch {}
  fetchingApp[job.name] = false
}

// -- Edit/Delete Job --
function openNewJob() {
  showJobForm.value = true
  loadEmployees()
}

async function openEditJob(j) {
  editingJob.value = j
  jobForm.job_title = j.job_title
  jobForm.department = j.department || ''
  jobForm.designation = j.designation || ''
  jobForm.closes_on = j.closes_on || ''
  jobForm.description = j.description || ''
  jobForm.salary_range = j.salary_range || ''
  jobForm.positions = j.positions || 1
  jobForm.recruiter = j.recruiter || ''
  showJobForm.value = true
  await loadEmployees()
}

async function confirmDeleteJob(j) {
  if (!confirm('Xóa vị trí "' + j.job_title + '"?')) return
  try {
    await frappeRequest({ url: 'hr.api.delete_job_opening', method: 'POST', params: { name: j.name } })
    toast.value = '✅ Đ xóa ' + j.job_title
    setTimeout(() => toast.value = '', 3000)
    await refreshJobs()
    await loadDashboard()
  } catch (e) { toast.value = '❌ ' + (e.message || 'Lỗi'); setTimeout(() => toast.value = '', 3000) }
}

async function doUpdateJob() {
  if (!editingJob.value) return
  try {
    await frappeRequest({ url: 'hr.api.update_job_opening', method: 'POST', params: { name: editingJob.value.name, ...jobForm } })
    showJobForm.value = false
    editingJob.value = null
    Object.assign(jobForm, { job_title: '', department: '', description: '' })
    await refreshJobs()
  } catch { /* ignore */ }
}

// -- CV Preview --
function fitScoreColor(s) { if(s>=80) return '!text-green-600 !bg-green-50 !border-green-300'; if(s>=60) return '!text-blue-600 !bg-blue-50 !border-blue-300'; if(s>=40) return '!text-amber-600 !bg-amber-50 !border-amber-300'; return '!text-red-600 !bg-red-50 !border-red-300' }
function fitBg(s) {
  if (s >= 80) return 'bg-green-50 border border-green-200'
  if (s >= 60) return 'bg-blue-50 border border-blue-200'
  if (s >= 40) return 'bg-amber-50 border border-amber-200'
  return 'bg-red-50 border border-red-200'
}

function applyCVPreview() {
  const p = cvPreview.value; const j = cvPreviewJobName.value
  if (!p || !j) return
  if (!newApplicant[j]) newApplicant[j] = { name: '', email: '' }
  if (p.name) newApplicant[j].name = p.name
  if (p.email) newApplicant[j].email = p.email
  if (p.phone) newApplicant[j].phone = p.phone
  toast.value = '✅ Đ điền thông tin từ CV'
  setTimeout(() => toast.value = '', 3000)
  cvPreview.value = null
}

async function saveCVPreview() {
  const p = cvPreview.value; const j = cvPreviewJobName.value
  if (!p || !j) return
  adding[j] = true
  try {
    const job = openings.value.find(o => o.name === j)
    if (!job) { toast.value = 'Kháông tìm thấy vị trí'; return }
    let resume_attachment = null
    // Upload CV file
    if (cvFile[j]) {
      const fd = new FormData()
      fd.append('file', cvFile[j])
      fd.append('is_private', '0')
      fd.append('doctype', 'Job Applicant')
      fd.append('fieldname', 'resume_attachment')
      try {
        const upRes = await fetch('/api/method/upload_file', { method: 'POST', body: fd, headers: { 'X-Frappe-CSRF-Token': window.csrf_token || '' } })
        const upData = await upRes.json()
        if (upData.message?.file_url) resume_attachment = upData.message.file_url
      } catch {}
    }
    const params = {
      job_title: j, applicant_name: p.name, email_id: p.email, phone_number: p.phone,
      cv_data: p,
      designation: job.designation || null,
      resume_attachment: resume_attachment,
    }
    const result = await frappeRequest({ url: 'hr.api.create_job_applicant', method: 'POST', params })
    toast.value = 'Đ lưu ' + (result?.applicant_name || '')
    setTimeout(() => toast.value = '', 3000)
    cvPreview.value = null
    delete cvFile[j]; delete cvParsed[j]
    await refreshApplicants(job)
    await loadDashboard()
    router.push('/applicant/' + result.name)
  } catch (e) { toast.value = (e.message || 'Lỗi'); setTimeout(() => toast.value = '', 4000) }
  adding[j] = false
}

async function addApplicant(job) {
  const a = newApplicant[job.name]
  if (!a?.name?.trim()) return
  adding[job.name] = true
  try {
    const params = { job_title: job.name, applicant_name: a.name.trim(), email_id: a.email?.trim() || null, phone_number: a.phone?.trim() || null }
    if (cvParsed[job.name]) params.cv_data = cvParsed[job.name]
    // Upload CV nếu chưa
    if (cvFile[job.name]) {
      const fd = new FormData()
      fd.append('file', cvFile[job.name])
      fd.append('is_private', '0')
      fd.append('doctype', 'Job Applicant')
      fd.append('fieldname', 'resume_attachment')
      const upRes = await fetch('/api/method/upload_file', { method: 'POST', body: fd, headers: { 'X-Frappe-CSRF-Token': window.csrf_token || '' } })
      const upData = await upRes.json()
      if (upData.message?.file_url) params.resume_attachment = upData.message.file_url
    }
    const result = await frappeRequest({ url: 'hr.api.create_job_applicant', method: 'POST', params })
    a.name = ''; a.email = ''
    delete cvFile[job.name]
    toast.value = '✅ Đ thêm ' + (result?.applicant_name || '')
    setTimeout(() => toast.value = '', 3000)
    await refreshApplicants(job)
  } catch (e) { toast.value = '❌ ' + (e.message || 'Lỗi'); setTimeout(() => toast.value = '', 4000) }
  adding[job.name] = false
}

async function confirmDeleteApplicant(a, job) {
  if (!confirm('Xóa ứng viên "' + a.applicant_name + '"?')) return
  try {
    await frappeRequest({ url: 'hr.api.delete_job_applicant', method: 'POST', params: { name: a.name } })
    toast.value = '✅ Đ xóa ' + a.applicant_name
    setTimeout(() => toast.value = '', 3000)
    await refreshApplicants(job)
    await loadDashboard()
    if (tab.value === 'pipeline') await loadPipeline()
  } catch (e) { toast.value = '❌ ' + (e.message || 'Lỗi'); setTimeout(() => toast.value = '', 3000) }
}

async function moveApplicant(applicant, newStatus) {
  try {
    await frappeRequest({ url: 'hr.api.update_applicant_status', method: 'POST', params: { name: applicant.name, status: newStatus } })
    applicant.status = newStatus
    if (tab.value === 'pipeline') await loadPipeline()
  } catch (e) { toast.value = '❌ ' + (e.message || 'Lỗi'); setTimeout(() => toast.value = '', 3000) }
}

function applyAppFilter() {} // nào-op, computed handles it
function applyPipelineFilter() {} // nào-op, computed handles it

// -- Pipeline --
async function loadPipeline() {
  pipelineLoading.value = true
  try {
    const data = await frappeRequest({ url: 'hr.api.get_job_applicants', method: 'GET', params: {} })
    allApplicants.value = data || []
  } catch {}
  pipelineLoading.value = false
}

async function onDropApplicant(e, toStatus) {
  e.preventDefault()
  if (!dragApp.value) return
  const app = allApplicants.value.find(a => a.name === dragApp.value)
  if (!app || app.status === toStatus) { dragApp.value = null; return }
  try {
    await frappeRequest({ url: 'hr.api.update_applicant_status', method: 'POST', params: { name: dragApp.value, status: toStatus } })
    app.status = toStatus
  } catch (e) { toast.value = '❌ ' + (e.message || 'Lỗi'); setTimeout(() => toast.value = '', 3000) }
  dragApp.value = null
}

// -- Create job --
const jobForm = reactive({ job_title: '', department: '', designation: '', description: '', closes_on: '', salary_range: '', positions: 1, recruiter: '', requirements: [''], benefits: [''] })
const today = new Date().toISOString().split('T')[0]

function buildJD() {
  // Nối requirements + benefits + salary vào description
  let desc = jobForm.description || ''
  if (jobForm.requirements.some(r => r.trim())) {
    desc += '\n\n**Yêu cầu:**\n' + jobForm.requirements.filter(r => r.trim()).map(r => '- ' + r.trim()).join('\n')
  }
  if (jobForm.benefits.some(b => b.trim())) {
    desc += '\n\n**Quyền lợi:**\n' + jobForm.benefits.filter(b => b.trim()).map(b => '- ' + b.trim()).join('\n')
  }
  if (jobForm.salary_range) {
    desc += '\n\n💰 Mức lương: ' + jobForm.salary_range
  }
  return desc
}

async function createJob() {
  if (!jobForm.designation) { toast.value = '❌ Vui lòng chon chức danh'; return }
  if (!jobForm.job_title.trim()) jobForm.job_title = jobForm.designation
  creatingJob.value = true
  try {
    const params = { ...jobForm, description: buildJD(), positions: jobForm.positions || 1 }
    if (editingJob.value) {
      await frappeRequest({ url: 'hr.api.update_job_opening', method: 'POST', params: { name: editingJob.value.name, ...params } })
    } else {
      await frappeRequest({ url: 'hr.api.create_job_opening', method: 'POST', params })
    }
    closeJobForm()
    await refreshJobs()
    await loadDashboard()
  } catch (e) { toast.value = '❌ ' + (e.message || 'Lỗi'); setTimeout(() => toast.value = '', 4000) }
  creatingJob.value = false
}

function switchTab(key) {
  tab.value = key
}

// -- Convert Applicant to Employee --
const showConvertModal = ref(false)
const convertLoading = ref(false)
const converting = ref(false)
const convertForm = ref({
  first_name: '', last_name: '', gender: 'Male', dob: '', joining: new Date().toISOString().split('T')[0],
  email: '', phone: '', location: '', designation: '', department: '', company: 'GPC',
  salary: 0,
})
const activeConvertApplicantId = ref(null)

async function openConvertModal(iv) {
  activeConvertApplicantId.value = iv.applicant_id
  showConvertModal.value = true
  convertLoading.value = true
  
  // Set defaults
  convertForm.value = {
    first_name: '', last_name: '', gender: 'Male', dob: '', joining: new Date().toISOString().split('T')[0],
    email: iv.email_id || '', phone: iv.phone_number || '', location: '', designation: '', department: '', company: 'GPC',
    salary: iv.custom_offered_salary || 0,
  }
  
  try {
    const detail = await frappeRequest({ url: 'hr.api.get_applicant_detail', method: 'GET', params: { name: iv.applicant_id } })
    if (detail) {
      // Split name
      const nameParts = (detail.applicant_name || '').trim().split(/\s+/)
      convertForm.value.first_name = nameParts.slice(0, -1).join(' ') || nameParts[0] || ''
      convertForm.value.last_name = nameParts.length > 1 ? nameParts[nameParts.length - 1] : ''
      
      const cv_data = detail.cv_data || {}
      if (cv_data.gender) {
        convertForm.value.gender = cv_data.gender === 'Nữ' || cv_data.gender === 'Female' ? 'Female' : 'Male'
      }
      if (cv_data.dob) {
        const dobStr = String(cv_data.dob).trim()
        const dmy = dobStr.match(/^(\d{1,2})[/\-.](\d{1,2})[/\-.](\d{4})$/)
        if (dmy) {
          const day = dmy[1].padStart(2, '0')
          const month = dmy[2].padStart(2, '0')
          const year = dmy[3]
          convertForm.value.dob = `${year}-${month}-${day}`
        } else {
          const ymd = dobStr.match(/^(\d{4})[/\-.](\d{1,2})[/\-.](\d{1,2})$/)
          if (ymd) {
            const year = ymd[1]
            const month = ymd[2].padStart(2, '0')
            const day = ymd[3].padStart(2, '0')
            convertForm.value.dob = `${year}-${month}-${day}`
          } else {
            convertForm.value.dob = dobStr.replace(/\//g, '-')
          }
        }
      }
      if (cv_data.location) {
        convertForm.value.location = cv_data.location
      }
      
      convertForm.value.designation = detail.designation || ''
      convertForm.value.department = detail.department || ''
      convertForm.value.salary = detail.custom_offered_salary || 0
    }
  } catch (e) {
    console.error(e)
  }
  convertLoading.value = false
}

async function doConvert() {
  if (!convertForm.value.first_name.trim() || !convertForm.value.last_name.trim()) {
    toast.value = '❌ Vui lòng nhập đầy đủ Họ và Tên'
    setTimeout(() => toast.value = '', 3000)
    return
  }
  if (!convertForm.value.designation || !convertForm.value.department) {
    toast.value = '❌ Vui lòng chon chức danh và phòng ban'
    setTimeout(() => toast.value = '', 3000)
    return
  }
  converting.value = true
  try {
    const params = {
      applicant: activeConvertApplicantId.value,
      first_name: convertForm.value.first_name,
      last_name: convertForm.value.last_name,
      gender: convertForm.value.gender,
      date_of_birth: convertForm.value.dob,
      date_of_joining: convertForm.value.joining,
      department: convertForm.value.department,
      designation: convertForm.value.designation,
      personal_email: convertForm.value.email,
      phone: convertForm.value.phone,
      location: convertForm.value.location,
      company: convertForm.value.company,
      salary: convertForm.value.salary || 0
    }
    await frappeRequest({ url: 'hr.api.convert_to_employee', method: 'POST', params })
    toast.value = '✅ Đã tuyển dụng nhân sự thành công'
    setTimeout(() => toast.value = '', 3000)
    showConvertModal.value = false
    activeConvertApplicantId.value = null
    await loadAllInterviews()
    await loadAllApplicants()
    await loadDashboard()
  } catch (e) {
    toast.value = '❌ ' + (e.message || 'Lỗi')
    setTimeout(() => toast.value = '', 3000)
  }
  converting.value = false
}

function suggestNexétRound(currentRound) {
  if (!currentRound) return 'Vòng 1'
  const r = currentRound.trim()
  if (r === 'Vòng 1') return 'Vòng 2'
  if (r === 'Vòng 2') return 'Vòng 3'
  if (r === 'Vòng 3') return 'Phỏng vấn cuối'
  return 'Vòng 1'
}

async function openScheduleAnotherRound(iv) {
  activeApplicant.value = { name: iv.applicant_id, applicant_name: iv.applicant_name }
  quickScheduleForm.value = {
    round: suggestNexétRound(iv.round),
    date: '',
    interviewer_employee: iv.interviewer_employee || '',
    notes: ''
  }
  await loadEmployees()
  showQuickScheduleModal.value = true
  loadAiSuggestedQuestions(iv.applicant_id)
}

function openRejectModalFromInterview(iv) {
  activeApplicant.value = { name: iv.applicant_id, applicant_name: iv.applicant_name }
  Object.assign(quickRejectForm, { reason: '', missingReqs: [''] })
  showQuickRejectModal.value = true
}

const recruiterKPIs = computed(() => {
  const counts = {}
  allApplicants.value.forEach(a => {
    const r = a.recruiter || 'Chưa phân chưang'
    counts[r] = (counts[r] || 0) + 1
  })
  return Object.entries(counts)
    .map(([name, count]) => ({ name, count }))
    .sort((a, b) => b.count - a.count)
})

function filterByFunnel(status) {
  allAppFilter.status = status
  switchTab('applicants')
}

function exportToCSV() {
  const visible = filteredAllApplicants.value || []
  if (!visible.length) {
    toast.value = '⚠️ Kháông có dữ liệu để xuất'
    setTimeout(() => toast.value = '', 3000)
    return
  }
  
  const headers = ['Họ tên', 'Email', 'Số điện thoại', 'Vị trí ứng tuyển', 'Trạng thái', 'Nguồn tuyển', 'Người tuyển', 'Ngày tạo']
  
  const rows = visible.map(a => [
    a.applicant_name || '',
    a.email_id || '',
    a.phone_number || '',
    a.job_opening_title || a.job_title || '',
    statusLabel(a.status),
    a.source || a.source_name || 'Website',
    a.recruiter || '',
    (a.creation || '').split(' ')[0]
  ])
  
  const csvContent = "\uFEFF" + [
    headers.join(','),
    ...rows.map(row => row.map(val => `"${String(val).replace(/"/g, '""')}"`).join(','))
  ].join('\n')
  
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.setAttribute('download', `danh_sách_ung_vien_${new Date().toISOString().split('T')[0]}.csv`)
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  
  toast.value = '✅ Xuất CSV thành công'
  setTimeout(() => toast.value = '', 3000)
}

function getJobStatusCount(jobName, statusKey) {
  return allApplicants.value.filter(a => a.job_title === jobName && a.status === statusKey).length
}

async function toggleJobStatus(j) {
  const newStatus = j.status === 'Open' ? 'Closed' : 'Open'
  try {
    await frappeRequest({
      url: 'hr.api.update_job_opening',
      method: 'POST',
      params: { name: j.name, status: newStatus }
    })
    j.status = newStatus
    toast.value = `✅ Đ chuyển vị trí sang ${newStatus === 'Open' ? 'Đang tuyển' : 'Đ đóng'}`
    setTimeout(() => toast.value = '', 3000)
    await Promise.all([refreshJobs(), loadDashboard()])
  } catch (e) {
    toast.value = '❌ ' + (e.message || 'Lỗi khi cập nhật trạng thái')
    setTimeout(() => toast.value = '', 3000)
  }
}
function fmtMoney(v) { if(!v) return ''; return new Intl.NumberFormat('vi-VN',{style:'currency',currency:'VND',maximumFractionDigits:0}).format(v) }
</script>

<style scoped>
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
.animate-fadeIn {
  animation: fadeIn 0.2s ease-out forwards;
}
</style>

