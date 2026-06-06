/**
 * GPC SHARED — printHtml (canonical). Mở HTML (chuỗi do backend trả) trong cửa sổ mới và in.
 * Sửa tại shared/ui rồi chạy shared/sync.sh.
 *
 * Backend trả về HTML string (mẫu VN dựng sẵn trong api.py). Frontend chỉ việc in.
 */
export function printHtml(html, title = 'In chứng từ') {
  const w = window.open('', '_blank', 'width=900,height=700')
  if (!w) {
    alert('Trình duyệt chặn cửa sổ in. Vui lòng cho phép pop-up.')
    return
  }
  w.document.open()
  w.document.write(`<!doctype html><html lang="vi"><head><meta charset="utf-8"><title>${title}</title></head><body>${html}</body></html>`)
  w.document.close()
  w.focus()
  // Đợi tài nguyên (ảnh/QR) load xong rồi mới in.
  setTimeout(() => { try { w.print() } catch (e) {} }, 350)
}
