#!/bin/bash
# GPC ERP — Deploy script for server 171.244.140.133
# Run on server: bash /tmp/server-deploy.sh
set -e

BENCH="/home/frappe/frappe-bench"
SITE="hoangdat.gpcds.site"
APPS="portal hr crm_ui tckt kho kinhdoanh quantri muahang duan taisan"

echo "=== 1. Git pull ==="
cd $BENCH
if [ -d .git ]; then
    git pull origin master 2>&1 | tail -3
else
    echo "Not a git repo — please clone first:"
    echo "  cd $BENCH && git clone https://github.com/nguyentrieu210/gpc-erp.git ."
    exit 1
fi

echo "=== 2. pip install all apps ==="
for a in $APPS; do
    ./env/bin/pip install -e apps/$a -q 2>/dev/null
    mkdir -p sites/assets
    ln -sfn $BENCH/apps/$a/$a/public $BENCH/sites/assets/$a 2>/dev/null || true
    echo "  pip: $a"
done

echo "=== 3. Build frontend ==="
. /home/frappe/.nvm/nvm.sh 2>/dev/null
export PATH="/home/frappe/.nvm/versions/node/v24.12.0/bin:$PATH"
for a in $APPS; do
    if [ -f "apps/$a/frontend/package.json" ]; then
        echo "  building $a..."
        cd apps/$a/frontend
        [ ! -d node_modules ] && yarn install --silent 2>/dev/null || true
        yarn build --silent 2>/dev/null || yarn build
        cd $BENCH
    fi
done
echo "  build done"

echo "=== 4. bench install-app ==="
for a in $APPS; do
    bench --site $SITE install-app $a 2>&1 | tail -1
done

echo "=== 5. Seed data ==="
bench --site $SITE execute portal.setup.setup_portal 2>&1 | tail -2
bench --site $SITE execute taisan.api.setup_taisan 2>&1 | tail -2

echo "=== 6. Add site to hosts ==="
# Ensure Frappe accepts subdomain requests
bench set-nginx-port $SITE 8000 2>/dev/null || true

echo "=== 7. Setup Nginx subdomains ==="
cp $BENCH/deploy/nginx/gpcds.site.conf /etc/nginx/sites-available/gpcds.site 2>/dev/null || true
cp $BENCH/deploy/nginx/gpc-ssl.inc /etc/nginx/ 2>/dev/null || true
ln -sf /etc/nginx/sites-available/gpcds.site /etc/nginx/sites-enabled/gpcds.site 2>/dev/null || true
rm -f /etc/nginx/sites-enabled/default 2>/dev/null || true
nginx -t && systemctl reload nginx || service nginx reload

echo "=== 8. SSL Cert (Let's Encrypt) ==="
# Chỉ chạy 1 lần — cài certbot nếu chưa có
if ! command -v certbot &>/dev/null; then
    apt-get update -qq && apt-get install -y -qq certbot python3-certbot-nginx 2>/dev/null
fi
certbot --nginx -d gpcds.site -d "*.gpcds.site" --non-interactive --agree-tos --email trieu.nt93@gmail.com 2>/dev/null || \
    certbot --nginx -d gpcds.site --non-interactive --agree-tos --email trieu.nt93@gmail.com 2>/dev/null || \
    echo "SSL: run certbot manually"

echo "=== 9. bench build & restart ==="
bench build 2>&1 | tail -2
bench restart 2>&1 || supervisorctl restart all 2>&1
systemctl reload nginx 2>/dev/null || service nginx reload

echo ""
echo "===================================="
echo "  DEPLOY HOAN TAT"
echo "  https://gpcds.site          → Portal"
echo "  https://hr.gpcds.site       → Nhan su"
echo "  https://banhang.gpcds.site  → Kinh doanh"
echo "  https://tckt.gpcds.site     → Tai chinh"
echo "  https://muahang.gpcds.site  → Mua hang"
echo "  https://kho.gpcds.site      → Kho"
echo "  https://crm.gpcds.site      → CRM"
echo "  https://taisan.gpcds.site   → Tai san"
echo "  https://duan.gpcds.site     → Du an"
echo "  https://quantri.gpcds.site  → Quan tri"
echo "===================================="
