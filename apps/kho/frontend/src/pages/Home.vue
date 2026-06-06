<template>
  <div class="flex flex-col min-h-screen bg-gray-50 text-gray-900 font-sans">
    <header class="flex items-center justify-between border-b bg-white px-4 py-3 shadow-sm sticky top-0 z-20">
      <div class="flex items-center gap-2">
        <div class="p-1.5 bg-orange-100 rounded text-orange-600">
          <FeatherIcon name="package" class="h-5 w-5" />
        </div>
        <h1 class="text-lg font-bold text-gray-950">Phân hệ Quản lý Kho (ERPNext Stock)</h1>
      </div>
      <div class="flex items-center gap-3">
        <Button variant="subtle" @click="goPortal" class="flex items-center gap-1">
          <FeatherIcon name="arrow-left" class="h-4 w-4" />
          <span>Quay lại Cổng</span>
        </Button>
        <div class="h-4 w-[1px] bg-gray-200"></div>
        <span class="text-sm text-gray-600 font-medium">{{ user?.full_name || 'Administrator' }}</span>
        <Button variant="subtle" :loading="loggingOut" @click="logout" class="text-red-600 hover:text-red-700">
          Đăng xuất
        </Button>
      </div>
    </header>

    <main class="flex-1 p-4 max-w-6xl mx-auto w-full space-y-6">
      <!-- Quick Dashboard Metrics -->
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div class="rounded-xl border bg-white p-4 text-center shadow-xs cursor-pointer hover:shadow-md transition-shadow" @click="$router.push('/items')">
          <div class="text-2xl font-extrabold text-orange-600">{{ d?.total_items ?? 0 }}</div>
          <div class="text-xs font-semibold text-gray-500 uppercase tracking-wide mt-1">Mặt hàng</div>
        </div>
        <div class="rounded-xl border bg-white p-4 text-center shadow-xs cursor-pointer hover:shadow-md transition-shadow" @click="$router.push('/balance')">
          <div class="text-2xl font-extrabold text-emerald-600">{{ fmtShort(d?.total_stock_value) }}</div>
          <div class="text-xs font-semibold text-gray-500 uppercase tracking-wide mt-1">Giá trị tồn</div>
        </div>
        <div class="rounded-xl border bg-white p-4 text-center shadow-xs cursor-pointer hover:shadow-md transition-shadow" @click="$router.push('/warehouses')">
          <div class="text-2xl font-extrabold text-blue-600">{{ d?.warehouse_count ?? 0 }}</div>
          <div class="text-xs font-semibold text-gray-500 uppercase tracking-wide mt-1">Kho / Vị trí</div>
        </div>
        <div class="rounded-xl border bg-white p-4 text-center shadow-xs cursor-pointer hover:shadow-md transition-shadow" @click="$router.push('/reorder')">
          <div class="text-2xl font-extrabold" :class="(d?.low_stock_count) ? 'text-red-600 animate-pulse' : 'text-gray-400'">{{ d?.low_stock_count ?? 0 }}</div>
          <div class="text-xs font-semibold text-gray-500 uppercase tracking-wide mt-1">Hàng sắp hết</div>
        </div>
      </div>

      <!-- Setup warning -->
      <div v-if="setup && !setup.ready" class="rounded-xl border border-amber-200 bg-amber-50/50 p-4 flex items-start gap-3 shadow-xs">
        <FeatherIcon name="alert-triangle" class="h-5 w-5 text-amber-600 shrink-0 mt-0.5" />
        <div class="flex-1 text-sm text-amber-800">
          <div class="font-bold">Cảnh báo: Chưa hoàn tất cấu hình hạch toán kho</div>
          <div class="text-xs text-amber-700 mt-0.5">Vui lòng kích hoạt chế độ Tồn kho vĩnh viễn (Perpetual Inventory) và chỉ định đầy đủ tài khoản kho để hệ thống tự động ghi sổ tài chính kế toán khi phát sinh phiếu nhập/xuất.</div>
        </div>
        <Button variant="solid" theme="orange" @click="$router.push('/setup')" class="text-xs">Cấu hình ngay</Button>
      </div>

      <!-- Features Grouped List -->
      <div class="space-y-6">
        <div v-for="cat in categories" :key="cat.title" class="space-y-3">
          <div class="border-l-4 border-gray-400 pl-3">
            <h2 class="text-base font-bold text-gray-900">{{ cat.title }}</h2>
            <p class="text-xs text-gray-500">{{ cat.desc }}</p>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div v-for="m in cat.items" :key="m.key"
                 class="group rounded-xl border bg-white p-4 shadow-2xs hover:shadow-md hover:border-orange-200 transition-all cursor-pointer"
                 @click="$router.push(m.route)">
              <div class="flex items-start gap-3">
                <div class="flex h-10 w-10 items-center justify-center rounded-lg shrink-0 group-hover:scale-105 transition-transform" :class="m.bg">
                  <FeatherIcon :name="m.icon" class="h-5 w-5" :class="m.color" />
                </div>
                <div class="flex-1 min-w-0">
                  <h3 class="font-bold text-gray-900 group-hover:text-orange-600 transition-colors text-sm">
                    {{ m.name }}
                  </h3>
                  <p class="text-xs text-gray-500 mt-1 leading-relaxed">
                    {{ m.desc }}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Button, FeatherIcon, frappeRequest, LoadingIndicator } from 'frappe-ui'
import { useFrappeApi } from '../composables/useFrappeApi'

const { data: d } = useFrappeApi('kho.api.get_stock_value_dashboard', { initialData: {} })
const { data: setup } = useFrappeApi('kho.api.get_kho_setup_status', { initialData: null })
const { data: user } = useFrappeApi('portal.api.get_current_user')

const loggingOut = ref(false)

function goPortal() {
  window.location.href = '/portal_app'
}

const categories = [
  {
    title: '1. Danh mục & Cấu trúc (Master Data)',
    desc: 'Quản lý thông tin gốc hàng hóa, sơ đồ cây kho vị trí và các nhãn truy vết lô/serial.',
    items: [
      { key: 'items', name: 'Hàng hóa & UOM', desc: 'Quản lý danh mục sản phẩm, đơn vị tính, nhãn hiệu sản phẩm', icon: 'package', color: 'text-orange-600', bg: 'bg-orange-100', route: '/items' },
      { key: 'warehouses', name: 'Sơ đồ cây Kho', desc: 'Quản lý sơ đồ vị trí, kệ hàng phân cấp và liên kết tài khoản kế toán', icon: 'home', color: 'text-blue-600', bg: 'bg-blue-100', route: '/warehouses' },
      { key: 'batches', name: 'Quản lý theo Lô', desc: 'Theo dõi hàng hóa theo lô sản xuất, số lô và quản lý hạn sử dụng', icon: 'layers', color: 'text-purple-600', bg: 'bg-purple-100', route: '/items' },
      { key: 'serials', name: 'Theo dõi Serial', desc: 'Quản lý xuất nhập chi tiết và truy vết chính xác từng sản phẩm bằng số Serial', icon: 'hash', color: 'text-indigo-600', bg: 'bg-indigo-100', route: '/items' }
    ]
  },
  {
    title: '2. Giao dịch & Kho vận (Transactions)',
    desc: 'Thực hiện các bút toán kho vật lý và yêu cầu điều chuyển nguyên vật liệu.',
    items: [
      { key: 'entries', name: 'Nhập / Xuất / Chuyển', desc: 'Bút toán luân chuyển: Phiếu nhập mua, xuất dùng và điều chuyển nội bộ', icon: 'repeat', color: 'text-violet-600', bg: 'bg-violet-100', route: '/stock-entries' },
      { key: 'recon', name: 'Kiểm kê kho', desc: 'Lập phiếu đối chiếu thực tế và tự động điều chỉnh chênh lệch tồn kho', icon: 'check-square', color: 'text-teal-600', bg: 'bg-teal-100', route: '/reconciliation' },
      { key: 'mr', name: 'Yêu cầu vật tư', desc: 'Lập đề nghị cấp phát vật tư nội bộ hoặc yêu cầu mua hàng tự động', icon: 'file-text', color: 'text-rose-600', bg: 'bg-rose-100', route: '/material-requests' },
      { key: 'repack', name: 'Đóng gói & Định lượng', desc: 'Giao dịch chuyển đổi mặt hàng, tháo dỡ linh kiện hoặc đóng gói lại', icon: 'box', color: 'text-pink-600', bg: 'bg-pink-100', route: '/stock-entries' }
    ]
  },
  {
    title: '3. Báo cáo & Phân tích (Analytics)',
    desc: 'Bảng cân đối tồn kho, lịch sử dòng hàng thẻ kho và quản lý định mức đặt hàng.',
    items: [
      { key: 'balance', name: 'Bảng cân đối tồn', desc: 'Báo cáo tổng hợp số lượng và giá trị hàng tồn tại mỗi kho hàng', icon: 'pie-chart', color: 'text-emerald-600', bg: 'bg-emerald-100', route: '/balance' },
      { key: 'ledger', name: 'Sổ kho (Thẻ kho)', desc: 'Lịch sử dòng chảy nhập xuất chi tiết từng ngày của từng mặt hàng', icon: 'book-open', color: 'text-cyan-600', bg: 'bg-cyan-100', route: '/ledger' },
      { key: 'reorder', name: 'Tồn kho tối thiểu', desc: 'Cảnh báo hàng dưới định mức an toàn và quản lý đặt hàng tự động', icon: 'alert-triangle', color: 'text-red-600', bg: 'bg-red-100', route: '/reorder' }
    ]
  },
  {
    title: '4. Kế toán kho & Thiết lập (Configuration)',
    desc: 'Cấu hình kế toán kho vĩnh viễn và phương pháp định giá xuất kho.',
    items: [
      { key: 'valuation', name: 'Phương pháp Định giá', desc: 'Thiết lập cách tính giá vốn hàng tồn kho (FIFO hoặc Bình quân gia quyền)', icon: 'dollar-sign', color: 'text-sky-600', bg: 'bg-sky-100', route: '/items' },
      { key: 'setup', name: 'Kế toán kho vĩnh viễn', desc: 'Cấu hình tài khoản mặc định, bật Perpetual Inventory và tích hợp GL Entry', icon: 'settings', color: 'text-gray-600', bg: 'bg-gray-100', route: '/setup' }
    ]
  }
]

function fmtShort(v) {
  v = Number(v || 0)
  if (v >= 1e9) return (v / 1e9).toFixed(1) + ' tỷ'
  if (v >= 1e6) return (v / 1e6).toFixed(1) + ' tr'
  if (v >= 1e3) return (v / 1e3).toFixed(0) + ' k'
  return v.toLocaleString('vi-VN')
}
</script>
