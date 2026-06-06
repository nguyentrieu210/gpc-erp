#!/bin/bash
# GPC ERP — Final Deploy (curl this from GitHub)
B=/home/frappe/.pyenv/versions/3.14.0/bin/bench
S=hoangdat.gpcds.site
cd /home/frappe/frappe-bench

echo "=== Build frontends ==="
for a in portal kinhdoanh tckt crm_ui muahang kho hr duan quantri taisan; do
    if [ -f apps/$a/frontend/package.json ]; then
        echo "building $a..."
        cd apps/$a/frontend
        [ ! -d node_modules ] && yarn install --silent 2>/dev/null || true
        yarn build --silent 2>/dev/null || yarn build
        cd /home/frappe/frappe-bench
    fi
done
echo "BUILD OK"

echo "=== install-app ==="
for a in portal hr crm_ui tckt kho kinhdoanh quantri muahang duan taisan; do
    echo "install $a..."
    $B --site $S install-app $a 2>&1 | tail -1
done
echo "INSTALL OK"

echo "=== Seed ==="
$B --site $S execute portal.setup.setup_portal 2>&1 | tail -2
$B --site $S execute taisan.api.setup_taisan 2>&1 | tail -2
echo "SEED OK"

echo "=== bench build ==="
$B build 2>&1 | tail -3

echo "=== restart ==="
$B restart 2>&1 | tail -3

echo "=== DONE ==="
echo "https://gpcds.site"
echo "Admin: Administrator / Letdoit1@"
