#!/bin/bash
# GPC ERP — Update deploy (clone source + pip + build + install)
# Server already has frappe-bench with Frappe + ERPNext
set -e
echo "=== GPC ERP Update Deploy ==="
BENCH=/home/frappe/frappe-bench
SITE=hoangdat.gpcds.site
APPS="portal hr crm_ui tckt kho kinhdoanh quantri muahang duan taisan"
APP_DIRS="portal kinhdoanh tckt crm_ui muahang kho hr duan quantri taisan"

echo "=== Clone source ==="
su - frappe -c "rm -rf /tmp/gpc-src; git clone https://github.com/nguyentrieu210/gpc-erp.git /tmp/gpc-src 2>&1 | tail -3"

echo "=== Copy source ==="
su - frappe -c "cp -r /tmp/gpc-src/apps/* $BENCH/apps/ && cp -r /tmp/gpc-src/shared $BENCH/ && cp -r /tmp/gpc-src/deploy $BENCH/ && echo copied"

echo "=== pip install ==="
su - frappe -c "
export PATH=\$HOME/.pyenv/versions/3.14.0/bin:\$PATH
cd $BENCH
for a in $APPS; do
    ./env/bin/pip install -e apps/\$a -q 2>/dev/null
    ln -sfn $BENCH/apps/\$a/\$a/public $BENCH/sites/assets/\$a 2>/dev/null || true
    echo pip: \$a
done
"

echo "=== Build frontends ==="
su - frappe -c "
export PATH=\$HOME/.pyenv/versions/3.14.0/bin:\$HOME/.nvm/versions/node/v24.12.0/bin:\$PATH
. ~/.nvm/nvm.sh 2>/dev/null || true
cd $BENCH
for a in $APP_DIRS; do
    if [ -f apps/\$a/frontend/package.json ]; then
        echo building \$a
        cd apps/\$a/frontend
        [ ! -d node_modules ] && yarn install --silent 2>/dev/null || true
        yarn build --silent 2>/dev/null || yarn build
        cd $BENCH
    fi
done
echo BUILD DONE
"

echo "=== install-app ==="
su - frappe -c "
export PATH=\$HOME/.pyenv/versions/3.14.0/bin:\$PATH
cd $BENCH
for a in $APPS; do
    bench --site $SITE install-app \$a 2>&1 | tail -1
done
"

echo "=== Seed ==="
su - frappe -c "
export PATH=\$HOME/.pyenv/versions/3.14.0/bin:\$PATH
cd $BENCH
bench --site $SITE execute portal.setup.setup_portal 2>&1 | tail -2
bench --site $SITE execute taisan.api.setup_taisan 2>&1 | tail -2
"

echo "=== Nginx ==="
cp $BENCH/deploy/nginx/gpcds.site.conf /etc/nginx/sites-available/gpcds.site 2>/dev/null || true
ln -sf /etc/nginx/sites-available/gpcds.site /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t 2>&1 && nginx -s reload 2>&1 || systemctl reload nginx 2>&1 || true

echo "=== Restart ==="
su - frappe -c "
export PATH=\$HOME/.pyenv/versions/3.14.0/bin:\$PATH
cd $BENCH
bench build 2>&1 | tail -2
bench restart 2>&1
"

echo "=== DONE ==="
echo "https://gpcds.site"
echo "https://hr.gpcds.site"
echo "https://banhang.gpcds.site"
echo "https://tckt.gpcds.site"
echo "https://taisan.gpcds.site"
echo "https://muahang.gpcds.site"
echo "https://kho.gpcds.site"
echo "https://crm.gpcds.site"
