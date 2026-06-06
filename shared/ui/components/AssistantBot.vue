<!-- GPC SHARED — AssistantBot. Trợ lý AI chuyên nghiệp: nút góc phải dưới → panel chat.
  Markdown light, context-aware, local knowledge + DeepSeek fallback. -->
<template>
  <Teleport to="body">
    <!-- Floating button -->
    <button v-if="!open" @click="open = true"
      class="fixed bottom-6 right-6 z-[9999] group flex items-center justify-center w-12 h-12 rounded-full text-white shadow-[0_8px_32px_rgba(99,102,241,0.35)] hover:shadow-[0_8px_32px_rgba(236,72,153,0.45)] transition-all duration-300 hover:-translate-y-1 hover:scale-105 active:scale-95 cursor-pointer border border-white/20"
      style="background: linear-gradient(135deg, #4f46e5 0%, #a855f7 50%, #ec4899 100%) !important;"
      title="Trợ lý AI GPC">
      <!-- Pulse effect back of the icon -->
      <span class="absolute inset-0 rounded-full bg-white/20 animate-ping opacity-75 group-hover:animate-none"></span>
      <svg class="relative w-5.5 h-5.5 text-white animate-sparkle" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
        <path stroke-linecap="round" stroke-linejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09zM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 002.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 002.455 2.456L21.75 6l-1.036.259a3.375 3.375 0 00-2.455 2.456z" />
      </svg>
    </button>

    <!-- Chat panel -->
    <Transition name="bot">
      <div v-if="open" class="fixed bottom-6 right-6 z-[9999] w-[420px] max-w-[calc(100vw-2rem)] h-[580px] max-h-[calc(100vh-5rem)]
        bg-white rounded-2xl shadow-[0_12px_40px_rgba(31,38,135,0.25)] border border-indigo-100 flex flex-col overflow-hidden">

        <!-- Header -->
        <div class="flex items-center gap-3 px-4 py-3.5 border-b border-indigo-100/20 text-white shrink-0"
             style="background: linear-gradient(to right, #4f46e5, #7c3aed) !important; color: #ffffff !important;">
          <div class="w-9 h-9 rounded-xl bg-white/10 backdrop-blur-md border border-white/20 flex items-center justify-center shadow-sm">
            <svg class="w-5 h-5 text-white animate-pulse" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09zM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 002.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 002.455 2.456L21.75 6l-1.036.259a3.375 3.375 0 00-2.455 2.456z" />
            </svg>
          </div>
          <div class="flex-1 text-white">
            <div class="text-sm font-extrabold tracking-tight text-white">Trợ lý GPC ERP</div>
            <div class="text-[10px] text-indigo-100 flex items-center gap-1.5 mt-0.5">
              <span class="relative flex h-2 w-2">
                <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span class="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
              </span>
              <span class="text-indigo-100">Sẵn sàng · AI + Kiến thức nghiệp vụ</span>
            </div>
          </div>
          <button @click="clear" v-if="msgs.length" class="text-indigo-200 hover:text-white hover:bg-white/10 p-1.5 rounded-lg transition" title="Xoá hội thoại">
            <FeatherIcon name="trash-2" class="h-4 w-4" />
          </button>
          <button @click="open = false" class="text-indigo-200 hover:text-white hover:bg-white/10 p-1.5 rounded-lg transition" title="Đóng">
            <FeatherIcon name="x" class="h-4 w-4" />
          </button>
        </div>

        <!-- Welcome screen -->
        <div v-if="!msgs.length" class="flex-1 overflow-y-auto p-5 space-y-5 bg-gradient-to-b from-white to-indigo-50/20">
          <div class="text-center pt-3">
            <div class="relative w-16 h-16 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg shadow-indigo-500/20 animate-float"
                 style="background: linear-gradient(135deg, #4f46e5 0%, #a855f7 50%, #ec4899 100%) !important;">
              <!-- Glow back -->
              <span class="absolute inset-0 rounded-2xl bg-gradient-to-tr from-indigo-500 via-purple-500 to-pink-500 blur-md opacity-40"></span>
              <svg class="relative w-8 h-8 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09zM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 002.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 002.455 2.456L21.75 6l-1.036.259a3.375 3.375 0 00-2.455 2.456z" />
              </svg>
            </div>
            <h3 class="text-lg font-extrabold text-gray-900 tracking-tight mb-1">Xin chào! Tôi có thể giúp gì?</h3>
            <p class="text-[12px] text-gray-500 leading-relaxed max-w-xs mx-auto">Tôi hiểu tất cả các phân hệ: Bán hàng, Mua hàng, Kho, Tài chính, Nhân sự, CRM, Tài sản...</p>
          </div>

          <div class="space-y-2.5">
            <div class="text-[10px] font-bold text-gray-400 uppercase tracking-widest px-1">Câu hỏi gợi ý</div>
            <div class="grid grid-cols-1 gap-2">
              <button v-for="qc in quickChips" :key="qc.q" @click="ask(qc.q)"
                class="text-left text-xs px-3.5 py-2.5 rounded-xl border border-gray-100 bg-white hover:bg-gradient-to-r hover:from-indigo-50/50 hover:to-purple-50/30 hover:border-indigo-200 transition-all duration-300 flex items-center gap-3 shadow-sm hover:shadow active:scale-[0.99] group">
                <span class="w-7 h-7 rounded-lg flex items-center justify-center shrink-0 text-sm shadow-sm transition-transform group-hover:scale-110" :class="qc.bg + ' ' + qc.color">{{ qc.emoji }}</span>
                <span class="text-gray-700 font-medium group-hover:text-indigo-950 transition-colors">{{ qc.q }}</span>
              </button>
            </div>
          </div>
        </div>

        <!-- Messages -->
        <div v-else ref="msgList" class="flex-1 overflow-y-auto p-4 space-y-4 bg-slate-50/50">
          <div v-for="(m, i) in msgs" :key="i" class="flex gap-2.5" :class="m.role === 'user' ? 'flex-row-reverse' : ''">
            <!-- Avatar -->
            <div class="w-7 h-7 rounded-full flex items-center justify-center shrink-0 mt-0.5 shadow-sm border text-white"
                 :class="m.role === 'user' ? 'bg-indigo-50 border-indigo-200 text-indigo-600 text-[9px] font-bold' : ''"
                 :style="m.role !== 'user' ? 'background: linear-gradient(135deg, #4f46e5 0%, #6d28d9 100%) !important; border-color: rgba(79, 70, 229, 0.2) !important;' : ''">
              <span v-if="m.role === 'user'">U</span>
              <svg v-else class="w-3.5 h-3.5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09zM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 002.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 002.455 2.456L21.75 6l-1.036.259a3.375 3.375 0 00-2.455 2.456z" />
              </svg>
            </div>
            <!-- Bubble -->
            <div class="max-w-[82%] min-w-0">
              <div class="text-[13px] leading-relaxed whitespace-pre-wrap break-words px-3.5 py-2.5 rounded-2xl shadow-sm"
                :class="m.role === 'user'
                  ? 'user-bubble text-white rounded-tr-sm'
                  : 'bg-white text-gray-800 rounded-tl-sm border border-indigo-50/80'"
                :style="m.role === 'user' ? 'background: linear-gradient(135deg, #4f46e5 0%, #6d28d9 100%) !important;' : ''"
                v-html="renderMd(m.text)">
              </div>
            </div>
          </div>

          <!-- Thinking indicator -->
          <div v-if="thinking" class="flex items-center gap-3 ml-10 py-2">
            <div class="thinking-radar">
              <span class="radar-dot bg-indigo-600"></span>
              <span class="radar-ring border-indigo-400"></span>
              <span class="radar-ring-2 border-indigo-400"></span>
            </div>
            <span class="text-xs text-indigo-500 font-medium animate-pulse">Trợ lý đang suy nghĩ...</span>
          </div>
        </div>

        <!-- Input -->
        <div class="border-t border-indigo-50 bg-white p-3.5 shrink-0">
          <div class="relative flex items-center rounded-2xl bg-gray-50 border border-gray-100 focus-within:border-indigo-300 focus-within:bg-white focus-within:ring-4 focus-within:ring-indigo-100 transition-all duration-300 px-3.5 py-1.5 gap-2">
            <textarea v-model="input" @keydown.enter.exact.prevent="ask(input)" rows="1"
              placeholder="Hỏi bất kỳ điều gì về ERP..."
              class="flex-1 resize-none bg-transparent border-0 p-0 text-sm outline-none focus:ring-0 text-gray-800 placeholder-gray-400 max-h-24 py-1.5"
              style="min-height:24px"
              :disabled="thinking"
              ref="inputEl"
              @input="autoResize"></textarea>
            
            <button @click="ask(input)" :disabled="!input.trim() || thinking"
              class="w-8 h-8 rounded-xl flex items-center justify-center shrink-0 transition-all duration-300 shadow-sm text-white
                     disabled:bg-gray-200 disabled:text-gray-400 disabled:opacity-50 disabled:scale-95 disabled:shadow-none
                     hover:scale-105 active:scale-95"
              style="background: linear-gradient(135deg, #4f46e5 0%, #6d28d9 100%) !important;">
              <FeatherIcon name="send" class="h-3.5 w-3.5 text-white" />
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue'
import { FeatherIcon } from 'frappe-ui'
import { callApi } from '../composables/useFrappeApi'

const open = ref(false)
const input = ref('')
const thinking = ref(false)
const msgs = ref([])
const msgList = ref(null)
const inputEl = ref(null)

const quickChips = [
  { q: 'Cách tạo đơn bán hàng?', emoji: '🛒', bg: 'bg-rose-50', color: 'text-rose-600' },
  { q: 'Làm sao chạy bảng lương?', emoji: '💰', bg: 'bg-emerald-50', color: 'text-emerald-600' },
  { q: 'Cách đối chiếu ngân hàng?', emoji: '🏦', bg: 'bg-blue-50', color: 'text-blue-600' },
  { q: 'Quy trình mua hàng thế nào?', emoji: '📦', bg: 'bg-amber-50', color: 'text-amber-600' },
  { q: 'Cách ghi nhận tài sản cố định?', emoji: '🏗️', bg: 'bg-teal-50', color: 'text-teal-600' },
  { q: 'Xem báo cáo tài chính ở đâu?', emoji: '📊', bg: 'bg-violet-50', color: 'text-violet-600' },
  { q: 'Quy trình tuyển dụng ra sao?', emoji: '👤', bg: 'bg-indigo-50', color: 'text-indigo-600' },
  { q: 'Cách quản lý kho & kiểm kê?', emoji: '🏭', bg: 'bg-orange-50', color: 'text-orange-600' },
]

// ── Markdown light render ──
function renderMd(text) {
  if (!text) return ''
  let html = String(text)
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/\*\*(.+?)\*\*/g, '<strong class="font-semibold text-gray-900">$1</strong>')
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    .replace(/`(.+?)`/g, '<code class="px-1 py-0.5 bg-gray-100 rounded text-[11px] font-mono text-rose-600">$1</code>')
    .replace(/\n/g, '<br>')
    .replace(/—/g, '—')
  return html
}

// ── Knowledge base ──
const knowledge = {
  'tạo đơn bán hàng|đơn bán|sales order|so|bán hàng': '**Kinh doanh → Đơn bán (SO)** → nhấn **Tạo đơn bán**\n\n1. Chọn **khách hàng** (tìm theo tên)\n2. Thêm **mặt hàng** (tìm theo tên/mã)\n3. Nhập **số lượng** & **đơn giá**\n4. Nhấn **Lưu & chốt**\n\n✅ Đơn ở trạng thái "Đã chốt" — có thể tạo phiếu giao hoặc hóa đơn từ đây.',
  'xuất hóa đơn|hóa đơn|sales invoice|si|hoá đơn|hđ': 'Từ **Đơn bán (SO)** đã chốt:\n1. Mở chi tiết đơn bán → nhấn **Tạo hóa đơn**\n2. Hoặc vào **Kinh doanh → Hóa đơn (SI)** → **Tạo hóa đơn**\n3. Nhấn **Lưu & ghi sổ**\n\n📊 Bút toán tự động: `Dr 131 / Cr 5111 + VAT`',
  'ghi nhận tài sản|tài sản cố định|tscđ|asset|taisan|khấu hao': 'Vào **Tài sản → Danh sách TSCĐ** → **Ghi nhận tài sản**:\n\n1. Nhập **tên TS**, chọn **loại TSCĐ**\n2. Chọn **mã hàng** (Item) từ danh mục kho\n3. Nhập **nguyên giá** & **ngày đưa vào SD**\n4. Nhấn **Lưu & ghi sổ**\n\n📅 Hệ thống tự tạo lịch khấu hao đường thẳng 36 tháng. Xem tại tab "Khấu hao" trong chi tiết tài sản.',
  'chạy bảng lương|bảng lương|payroll|lương|tính lương': 'Vào **Nhân sự → Bảng lương**:\n\n1. Chọn **tháng/năm** → nhấn **Chạy lương**\n2. Hệ thống tự sinh phiếu lương cho NV có `ctc` (lương khoán/năm)\n3. Có thể **chốt từng phiếu** hoặc **chốt tất cả**\n4. **Khóa kỳ** để bảo vệ dữ liệu sau khi chốt\n\n💡 Vào **Thuế & Phúc lợi** để xem ước tính BHXH/BHYT/BHTN/thuế TNCN.',
  'đối chiếu ngân hàng|bank recon|đối chiếu|bank|ngân hàng': 'Vào **Tài chính → Đối chiếu NH**:\n\n1. Chọn **tài khoản ngân hàng**\n2. Chọn các giao dịch cần đối chiếu (Payment Entry / Journal Entry)\n3. Nhấn **Đối chiếu**\n\n✅ Hệ thống tạo `Bank Clearance` & cập nhật `clearance_date`.',
  'quy trình mua hàng|mua hàng|purchase|po|mua|nhập mua|procurement': '**Quy trình Mua hàng đầy đủ:**\n\n1. 📝 **Đề nghị mua** (PR) — gửi duyệt\n2. 📧 **Yêu cầu báo giá** (RFQ) — gửi nhiều NCC (tùy chọn)\n3. 📋 **Đơn mua** (PO) — chốt gửi NCC\n4. 📥 **Nhập mua** (PR) — hàng về kho → `Dr 1561 / Cr SRBNB`\n5. 🧾 **Hóa đơn mua** (PI) — công nợ 331 → `Dr SRBNB+VAT / Cr 331`\n6. 💵 **Thanh toán** — `Dr 331 / Cr 1111`',
  'báo cáo tài chính|báo cáo|p&l|balance sheet|bảng cân đối|kết quả kinh doanh|tài chính': 'Vào **Tài chính**:\n\n• **Sổ cái (GL)**: tra cứu mọi bút toán, click để drill-down\n• **Cân đối TK**: bảng cân đối phát sinh theo kỳ\n• **KQKD (P&L)**: báo cáo lãi lỗ\n• **CĐKT (BS)**: bảng cân đối kế toán\n• **Lưu chuyển tiền**: dòng tiền vào/ra\n• **Ngân sách**: dự toán vs thực tế\n\n🔍 Tất cả đều có bộ lọc ngày tháng.',
  'quản lý kho|kho|stock|tồn kho|nhập kho|xuất kho|kiểm kê|warehouse': 'Vào **Kho**:\n\n• **Hàng hóa**: danh sách, tồn kho theo kho, QR code\n• **Phiếu kho**: Nhập/Xuất/Chuyển kho → `Dr 1561 / Cr Chênh lệch kho`\n• **Kiểm kê**: đối chiếu tồn thực tế vs hệ thống\n• **Thẻ kho**: sổ chi tiết từng mặt hàng\n• **Cảnh báo**: tồn dưới định mức, lô sắp hết hạn\n• **Landed Cost**: phân bổ chi phí vận chuyển vào giá vốn',
  'tuyển dụng|tuyển|recruitment|ứng viên|phỏng vấn|job|tuyen': 'Vào **Nhân sự → Tuyển dụng**:\n\n1. 📌 **Đăng vị trí** (AI soạn JD tự động)\n2. 👤 **Thêm ứng viên** (upload CV → AI parse thông tin)\n3. 🎯 **Kéo thả Pipeline** (Mới → Sơ tuyển → Phỏng vấn → Cân nhắc → Trúng tuyển)\n4. 📅 **Lịch phỏng vấn** (AI gợi ý câu hỏi)\n5. 💌 **Gửi thư mời** (AI soạn, in mẫu VN)\n6. ✅ **Nhận việc** → tự tạo hồ sơ NV',
  'crm|lead|cơ hội|khách hàng|opportunity|chiến dịch': 'Vào **CRM**:\n\n• **Lead** (kanban): Mới → Mở → Đã LH → Cơ hội → Báo giá → Chuyển đổi\n• **Cơ hội** (kanban): Đánh giá → Phân tích → Đề xuất → Đàm phán → Thắng/Thua\n• **Khách hàng**: danh sách & hồ sơ KH\n• **Liên hệ**: danh bạ\n• **Hoạt động**: việc cần làm / theo dõi\n• **Chiến dịch**: marketing campaign',
  'phiếu kế toán|journal entry|bút toán|je|định khoản': 'Vào **Tài chính → Phiếu kế toán**:\n\n1. Nhấn **Tạo phiếu**\n2. Nhập **diễn giải**\n3. Thêm các dòng **định khoản** (chọn TK → nhập Nợ/Có)\n4. Đảm bảo **cân đối** (Nợ = Có)\n5. Nhấn **Lưu & ghi sổ**\n\n📊 Có thể **in phiếu kế toán** mẫu VN từ nút 🖨️.',
}

function localAnswer(q) {
  const lower = q.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '')
  for (const [keys, answer] of Object.entries(knowledge)) {
    if (keys.split('|').some(k => lower.includes(k))) return answer
  }
  return null
}

async function ask(question) {
  if (thinking.value) return
  const q = (typeof question === 'string' ? question : input.value).trim()
  if (!q) return
  input.value = ''
  msgs.value.push({ role: 'user', text: q })

  const local = localAnswer(q)
  if (local) {
    msgs.value.push({ role: 'bot', text: local })
    await nextTick(); scrollBottom()
    return
  }

  thinking.value = true
  await nextTick(); scrollBottom()
  try {
    const res = await callApi('portal.api.erp_assistant', { question: q, context: window.location.pathname }, 'GET')
    const answer = res?.answer || res?.message || res
    msgs.value.push({ role: 'bot', text: typeof answer === 'string' ? answer : JSON.stringify(answer) })
  } catch (e) {
    msgs.value.push({ role: 'bot', text: '⚠️ Xin lỗi, tôi chưa trả lời được câu này.\n\nBạn có thể thử:\n• Hỏi ngắn gọn và cụ thể hơn\n• Dùng từ khóa nghiệp vụ (vd: "tạo đơn bán", "chạy lương", "kiểm kê")\n• Vào menu **Cấu hình** trong từng phân hệ để xem hướng dẫn chi tiết' })
  } finally { thinking.value = false; await nextTick(); scrollBottom() }
}

function clear() { msgs.value = [] }

function scrollBottom() {
  nextTick(() => {
    if (msgList.value) msgList.value.scrollTop = msgList.value.scrollHeight
  })
}

function autoResize() {
  const el = inputEl.value
  if (!el) return
  el.style.height = 'auto'
  el.style.height = Math.min(el.scrollHeight, 120) + 'px'
}
</script>

<style scoped>
.bot-enter-active {
  transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
}
.bot-leave-active {
  transition: all 0.25s cubic-bezier(0.36, 0.07, 0.19, 0.97);
}
.bot-enter-from, .bot-leave-to {
  opacity: 0;
  transform: translateY(30px) scale(0.92);
}

@keyframes float {
  0% { transform: translateY(0px); }
  50% { transform: translateY(-6px); }
  100% { transform: translateY(0px); }
}

@keyframes sparkle {
  0%, 100% { transform: scale(1); opacity: 0.9; }
  50% { transform: scale(1.1) rotate(5deg); opacity: 1; filter: drop-shadow(0 0 4px rgba(99,102,241,0.4)); }
}

.animate-float {
  animation: float 4s ease-in-out infinite;
}

.animate-sparkle {
  animation: sparkle 2s ease-in-out infinite;
}

/* Radar thinking effect */
.thinking-radar {
  position: relative;
  width: 14px;
  height: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.radar-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
}

.radar-ring, .radar-ring-2 {
  position: absolute;
  border: 1.5px solid;
  border-radius: 50%;
  width: 100%;
  height: 100%;
  animation: radar-pulse 1.8s cubic-bezier(0.215, 0.610, 0.355, 1) infinite;
  opacity: 0;
}

.radar-ring-2 {
  animation-delay: 0.6s;
}

@keyframes radar-pulse {
  0% {
    transform: scale(0.5);
    opacity: 0;
  }
  50% {
    opacity: 0.5;
  }
  100% {
    transform: scale(2.2);
    opacity: 0;
  }
}

/* Overwrite markdown elements inside user bubble to maintain high contrast */
.user-bubble strong {
  color: inherit !important;
}

.user-bubble code {
  color: #fff !important;
  background-color: rgba(255, 255, 255, 0.2) !important;
}
</style>
