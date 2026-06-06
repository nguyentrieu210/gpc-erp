#!/bin/bash
# Chạy 1 lần trong container `gpc-erp-dev-frappe-1` để tạo site dev erp.local.
#   docker exec gpc-erp-dev-frappe-1 bash /home/frappe/frappe-bench/dev/01-create-site.sh
# (hoặc đã được chạy sẵn khi dựng môi trường lần đầu)
set -e
cd /home/frappe/frappe-bench

# Trỏ bench về db/redis của dev compose
bench set-config -g db_host db
bench set-config -g db_port 3306
bench set-config -g redis_cache    "redis://redis:6379"
bench set-config -g redis_queue    "redis://redis:6379"
bench set-config -g redis_socketio "redis://redis:6379"
bench set-config -g socketio_port  9000
bench set-config -g developer_mode 1

# Tạo site + cài các app nền (tái dùng từ image, không tải lại)
bench new-site erp.local \
  --mariadb-root-password "Letdoit1@" \
  --admin-password "admin" \
  --mariadb-user-host-login-scope="%" \
  --install-app erpnext \
  --install-app hrms \
  --install-app crm \
  --install-app vi_translations

bench use erp.local
echo "===CREATE_SITE_DONE==="
