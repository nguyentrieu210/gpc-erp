/**
 * GPC SHARED — Number/money/text utils (canonical). Sửa tại shared/ui rồi chạy shared/sync.sh.
 */

/** 1234567 -> "1.234.567 ₫" */
export function fmtVnd(v) {
  return Number(v || 0).toLocaleString('vi-VN') + ' ₫'
}

/** 1234567 -> "1.234.567" (không ký hiệu tiền) */
export function money(v) {
  return Number(v || 0).toLocaleString('vi-VN')
}

/** 0.1234 -> "12,3%" */
export function pct(v, digits = 1) {
  return Number(v || 0).toFixed(digits).replace('.', ',') + '%'
}

/** Khởi tạo chữ cái viết tắt từ tên (1-2 ký tự). */
export function initials(n) {
  if (!n) return '?'
  const p = String(n).replace(/[^\p{L}\p{N}\s]/gu, '').split(/\s+/).filter(Boolean)
  if (!p.length) return '?'
  return p.length >= 2
    ? (p[p.length - 2][0] + p[p.length - 1][0]).toUpperCase()
    : p[0].slice(0, 2).toUpperCase()
}

const AVATAR_COLORS = ['#3b82f6', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981', '#6366f1', '#ef4444', '#84cc16', '#06b6d4', '#f97316']

/** Màu nền ổn định (hash từ tên) cho avatar/badge. */
export function avatarColor(n) {
  let h = 0
  const s = String(n || '')
  for (let i = 0; i < s.length; i++) h = s.charCodeAt(i) + ((h << 5) - h)
  return AVATAR_COLORS[Math.abs(h) % AVATAR_COLORS.length]
}
