/**
 * Date/time formatting utilities for the HR application.
 * Formats dates and times to "dd/mm/yyyy" and "dd/mm/yyyy hh:mm".
 */

export function formatDate(val) {
  if (!val) return ''
  const str = String(val).trim()
  if (!str) return ''

  // Split date from time if it contains both
  const datePart = str.split(/[ T]/)[0]

  // Try to match YYYY-MM-DD, YYYY/MM/DD, YYYY.MM.DD
  const ymd = datePart.match(/^(\d{4})[/\-.](\d{1,2})[/\-.](\d{1,2})$/)
  if (ymd) {
    const year = ymd[1]
    const month = ymd[2].padStart(2, '0')
    const day = ymd[3].padStart(2, '0')
    return `${day}/${month}/${year}`
  }

  // Try to match DD-MM-YYYY, DD/MM/YYYY, DD.MM.YYYY
  const dmy = datePart.match(/^(\d{1,2})[/\-.](\d{1,2})[/\-.](\d{4})$/)
  if (dmy) {
    const day = dmy[1].padStart(2, '0')
    const month = dmy[2].padStart(2, '0')
    const year = dmy[3]
    return `${day}/${month}/${year}`
  }

  // Fallback to JS Date parser
  try {
    const d = new Date(str)
    if (!isNaN(d.getTime())) {
      const day = String(d.getDate()).padStart(2, '0')
      const month = String(d.getMonth() + 1).padStart(2, '0')
      const year = d.getFullYear()
      return `${day}/${month}/${year}`
    }
  } catch (e) {}

  return val
}

export function formatDateTime(val) {
  if (!val) return ''
  const str = String(val).trim()
  if (!str) return ''

  // Split date and time
  const parts = str.split(/[ T]/)
  const datePart = parts[0]
  const timePart = parts[1] || ''

  // Format date part
  const formattedDate = formatDate(datePart)
  if (!formattedDate || formattedDate === datePart) {
    try {
      const d = new Date(str)
      if (!isNaN(d.getTime())) {
        const day = String(d.getDate()).padStart(2, '0')
        const month = String(d.getMonth() + 1).padStart(2, '0')
        const year = d.getFullYear()
        const hours = String(d.getHours()).padStart(2, '0')
        const minutes = String(d.getMinutes()).padStart(2, '0')
        return `${day}/${month}/${year} ${hours}:${minutes}`
      }
    } catch (e) {}
    return val
  }

  // Format time part (HH:MM)
  if (timePart) {
    const timeMatch = timePart.match(/^(\d{1,2}):(\d{1,2})/)
    if (timeMatch) {
      const hours = timeMatch[1].padStart(2, '0')
      const minutes = timeMatch[2].padStart(2, '0')
      return `${formattedDate} ${hours}:${minutes}`
    }
  }

  return formattedDate
}
