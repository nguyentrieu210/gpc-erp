# GPC Custom ERP — Môi trường DEV (Windows + Docker)

Tái dùng image **`ghcr.io/nguyentrieu210/frappe-vn:v16`** (đã có frappe, erpnext, hrms, crm, insights, vi_translations + node v24/yarn/honcho) nên **không phải tải lại** các app nặng. Source 7 custom app nằm ở `..\apps`, bind-mount vào bench → **sửa trên Windows, chạy trong container**.

## Thành phần
| Service | Image | Vai trò |
|---|---|---|
| `db` | mariadb:11.8 | Database dev (root pass `Letdoit1@`) |
| `redis` | redis:8.6-alpine | cache + queue + socketio |
| `frappe` | frappe-vn:v16 | bench (web :8000, socketio :9000) |

- **Site dev:** `erp.local` — Administrator / `admin`
- **Volume:** `db-data`, `redis-data`, `sites` (site data nằm trong volume, không mất khi restart)

## Lệnh thường dùng
```powershell
# Bật/tắt
docker compose -f compose.dev.yaml up -d
docker compose -f compose.dev.yaml down            # giữ data
docker compose -f compose.dev.yaml down -v         # XOÁ data (làm lại từ đầu)

# Vào shell bench
docker exec -it gpc-erp-dev-frappe-1 bash

# Tạo site lần đầu (đã chạy sẵn). Xem dev/01-create-site.sh
# Cài 7 custom app vào site:           dev/02-install-custom-apps.sh

# Chạy server dev (web + socketio + worker):
docker exec -d gpc-erp-dev-frappe-1 bash -lc "cd /home/frappe/frappe-bench && bench start"
#  → http://localhost:8000   (Administrator / admin)

# Build lại frontend của 1 app sau khi sửa Vue:
docker exec gpc-erp-dev-frappe-1 bash -lc "cd /home/frappe/frappe-bench && bench build --app portal"

# Migrate sau khi thêm/sửa doctype:
docker exec gpc-erp-dev-frappe-1 bash -lc "cd /home/frappe/frappe-bench && bench --site erp.local migrate"
```

## Lưu ý
- Script `.sh` chạy **trong container (Linux)** — giữ line-ending **LF** (đừng để Windows đổi thành CRLF).
- 7 app: `portal, hr, crm_ui, tckt, kho, kinhdoanh, duan`. `crm_ui` = frontend CRM (đổi tên để khỏi trùng app `crm` của Frappe).
- Sub-domain (hr.abc, tckt.abc…) ráp ở giai đoạn sau bằng nginx; giai đoạn dev truy cập trực tiếp qua route `/portal_app`, `/hr_app`… trên `localhost:8000`.
