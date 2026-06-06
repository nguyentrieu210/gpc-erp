/**
 * GPC SHARED — Date/time utils (canonical). Format dd/mm/yyyy & dd/mm/yyyy hh:mm.
 * Sửa tại shared/ui rồi chạy shared/sync.sh.
 */

export function formatDate(val) {
  if (!val) return ''
  const str = String(val).trim()
  if (!str) return ''
  const datePart = str.split(/[ T]/)[0]
  const ymd = datePart.match(/^(\d{4})[/\-.](\d{1,2})[/\-.](\d{1,2})$/)
  if (ymd) {
    return `${ymd[3].padStart(2, '0')}/${ymd[2].padStart(2, '0')}/${ymd[1]}`
  }
  const dmy = datePart.match(/^(\d{1,2})[/\-.](\d{1,2})[/\-.](\d{4})$/)
  if (dmy) {
    return `${dmy[1].padStart(2, '0')}/${dmy[2].padStart(2, '0')}/${dmy[3]}`
  }
  try {
    const d = new Date(str)
    if (!isNaN(d.getTime())) {
      const day = String(d.getDate()).padStart(2, '0')
      const month = String(d.getMonth() + 1).padStart(2, '0')
      return `${day}/${month}/${d.getFullYear()}`
    }
  } catch (e) {}
  return val
}

export function formatDateTime(val) {
  if (!val) return ''
  const str = String(val).trim()
  if (!str) return ''
  const parts = str.split(/[ T]/)
  const datePart = parts[0]
  const timePart = parts[1] || ''
  const formattedDate = formatDate(datePart)
  if (!formattedDate || formattedDate === datePart) {
    try {
      const d = new Date(str)
      if (!isNaN(d.getTime())) {
        const day = String(d.getDate()).padStart(2, '0')
        const month = String(d.getMonth() + 1).padStart(2, '0')
        const hours = String(d.getHours()).padStart(2, '0')
        const minutes = String(d.getMinutes()).padStart(2, '0')
        return `${day}/${month}/${d.getFullYear()} ${hours}:${minutes}`
      }
    } catch (e) {}
    return val
  }
  if (timePart) {
    const m = timePart.match(/^(\d{1,2}):(\d{1,2})/)
    if (m) return `${formattedDate} ${m[1].padStart(2, '0')}:${m[2].padStart(2, '0')}`
  }
  return formattedDate
}

/** Hôm nay dạng YYYY-MM-DD (theo local). */
export function today() {
  const d = new Date()
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}
