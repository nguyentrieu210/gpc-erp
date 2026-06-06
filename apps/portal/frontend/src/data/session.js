// Đọc user đang đăng nhập từ cookie Frappe (`user_id`). Guest = chưa đăng nhập.
export function sessionUser() {
  const cookies = new URLSearchParams(document.cookie.split('; ').join('&'))
  let user = cookies.get('user_id')
  if (user === 'Guest') user = null
  return user
}
