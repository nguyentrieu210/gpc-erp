// === GPC DEBUG CONSOLE ===
// Paste toàn bộ vào browser console (F12 → Console) của http://localhost:8000/duan_app
// Rồi chạy: await debug()

async function debug() {
  const r = []; const log = (s) => { r.push(s); console.log(s) }

  // 1. Auth
  const cookies = document.cookie.split('; ').join('&')
  const userId = new URLSearchParams(cookies).get('user_id')
  log(`1. Auth: user_id=${userId || 'KHÔNG CÓ → chưa login'}`)

  // 2. Network test — gọi API trực tiếp
  log('2. Gọi API...')
  const t0 = performance.now()
  try {
    const res = await fetch('/api/method/duan.api.get_dashboard')
    const json = await res.json()
    const ms = (performance.now() - t0).toFixed(0)
    if (json.message) {
      log(`   ✅ API OK (${ms}ms): ${JSON.stringify(json.message).slice(0,80)}...`)
    } else if (json.exc_type) {
      log(`   ❌ API Permission Error: ${json.exc_type}`)
      log(`   👉 Cần login lại: window.location.href='/portal_app/login'`)
    } else {
      log(`   ⚠️ API lạ: ${JSON.stringify(json).slice(0,120)}`)
    }
  } catch (e) {
    log(`   💀 Network fail: ${e.message}`)
  }

  // 3. Vue state
  log('3. Vue state:')
  try {
    const app = document.querySelector('#app')
    if (!app || !app._vnode) { log('   ❌ #app chưa mount → Vue crash khi init'); }
    else {
      const vm = app.__vue_app__?._instance?.proxy
      if (!vm) { log('   ⚠️ Vue mounted but no root instance'); }
      else {
        log(`   Vue OK, route: ${vm.$route?.path || '?'}`)
        // check if setup data exists
        const comp = vm.$?.subTree?.component
        log(`   Component: ${comp?.type?.name || comp?.type?.__name || 'unknown'}`)
      }
    }
  } catch (e) { log(`   💀 Vue check error: ${e.message}`) }

  // 4. ResourceFetcher config
  log('4. frappe-ui config:')
  try {
    const { getConfig } = await import('/assets/duan/frontend/assets/index-' +
      document.querySelector('script[src*="index-"]')?.src?.match(/index-[^/]+\.js/)?.[0]?.replace('.js','') + '.js')
    log('   (không check được — dùng manual)')
  } catch {}
  const src = document.querySelector('script[src*="index-"]')?.src
  log(`   JS bundle: ${src || 'KHÔNG TÌM THẤY'}`)

  // Tổng kết
  const sep = '='.repeat(50)
  log(sep)
  if (!userId) {
    log('🔴 KẾT LUẬN: Chưa login → vào portal_app/login trước')
  } else if (r.find(x => x.includes('API OK'))) {
    log('🟢 KẾT LUẬN: API OK, lỗi nằm ở Vue/component. Kiểm tra:')
    log('   - Template có dùng LoadingIndicator đã import chưa?')
    log('   - createResource có bị treo do method:POST?')
  } else if (r.find(x => x.includes('Permission'))) {
    log('🔴 KẾT LUẬN: Auth hết hạn → xóa cookie + login lại')
  } else {
    log('🟡 KẾT LUẬN: Không xác định được. Copy toàn bộ log trên gửi cho dev.')
  }
  log(sep)
  return r.join('\n')
}

// Tự động chạy
debug()
