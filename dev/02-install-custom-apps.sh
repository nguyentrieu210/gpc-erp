#!/bin/bash
# Cài 7 custom app (editable) vào bench + site erp.local. Chạy sau 01-create-site.sh.
#   docker exec gpc-erp-dev-frappe-1 bash /home/frappe/frappe-bench/dev/02-install-custom-apps.sh
set -e
cd /home/frappe/frappe-bench

APPS="portal hr crm_ui tckt kho kinhdoanh duan"

# 1) Editable install + đăng ký vào bench (apps.txt) để build/migrate nhận diện
# LƯU Ý: apps.txt seed từ image có thể THIẾU newline cuối -> append sẽ dính dòng
# (vd "erpnextvi_translations"). Bảo đảm có newline cuối trước khi append.
[ -s sites/apps.txt ] && [ -n "$(tail -c1 sites/apps.txt)" ] && echo >> sites/apps.txt
for a in $APPS; do
  echo "=== pip install -e apps/$a ==="
  ./env/bin/pip install -e "apps/$a" --quiet
  grep -qx "$a" sites/apps.txt || echo "$a" >> sites/apps.txt
done

# 2) Cài vào site
for a in $APPS; do
  echo "=== install-app $a -> erp.local ==="
  bench --site erp.local install-app "$a"
done

bench --site erp.local migrate
echo "===INSTALL_CUSTOM_DONE==="
