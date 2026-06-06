export function formatDate(val) {
  if (!val) return ''; const str = String(val).trim(); if (!str) return ''
  const datePart = str.split(/[ T]/)[0]
  const ymd = datePart.match(/^(\d{4})[/\-.](\d{1,2})[/\-.](\d{1,2})$/)
  if (ymd) return `${ymd[3].padStart(2,'0')}/${ymd[2].padStart(2,'0')}/${ymd[1]}`
  try { const d = new Date(str); if (!isNaN(d.getTime())) { return `${String(d.getDate()).padStart(2,'0')}/${String(d.getMonth()+1).padStart(2,'0')}/${d.getFullYear()}` } } catch (e) {}
  return val
}
export function formatDateTime(val) {
  if (!val) return ''; const d = new Date(val)
  if (!isNaN(d.getTime())) { return `${String(d.getDate()).padStart(2,'0')}/${String(d.getMonth()+1).padStart(2,'0')}/${d.getFullYear()} ${String(d.getHours()).padStart(2,'0')}:${String(d.getMinutes()).padStart(2,'0')}` }
  return val
}
