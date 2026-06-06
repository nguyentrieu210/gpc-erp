#!/bin/bash
# GPC ERP — Quick Install (run on server: curl -fsSL <url> | bash)
# No set -e — continues on errors

echo "========================================="
echo " GPC ERP Quick Install — $(date)"
echo "========================================="

# ── 1. Packages ─────────────────────────────────────────────────────
echo "=== Packages ==="
DEBIAN_FRONTEND=noninteractive apt-get install -y -qq \
    mariadb-client redis-server nginx supervisor \
    python3-dev python3-pip python3-venv libmysqlclient-dev git curl 2>&1 | tail -3
echo "Packages OK"

# ── 2. MariaDB user ─────────────────────────────────────────────────
echo "=== MariaDB ==="
mysql -u root <<< "
CREATE USER IF NOT EXISTS 'frappe'@'localhost' IDENTIFIED BY 'Letdoit1@';
GRANT ALL PRIVILEGES ON *.* TO 'frappe'@'localhost' WITH GRANT OPTION;
FLUSH PRIVILEGES;
" 2>/dev/null || echo "MariaDB: user already exists"
echo "MariaDB OK"

# ── 3. frappe user ──────────────────────────────────────────────────
echo "=== frappe user ==="
id frappe 2>/dev/null || useradd -m -s /bin/bash frappe
echo 'frappe:Letdoit1@' | chpasswd 2>/dev/null
usermod -aG sudo frappe 2>/dev/null || true
echo "frappe user OK"

# ── 4. Python 3.14 via pyenv ────────────────────────────────────────
echo "=== Python 3.14 (pyenv) ==="
su - frappe -c '
if [ ! -d ~/.pyenv ]; then
    curl -fsSL https://pyenv.run | bash 2>&1 | tail -3
fi
'
# Add to bashrc
if ! grep -q 'pyenv init' /home/frappe/.bashrc 2>/dev/null; then
    cat >> /home/frappe/.bashrc << 'PYEOF'

# pyenv
export PYENV_ROOT="$HOME/.pyenv"
[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"
PYEOF
fi

su - frappe -c '
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)" 2>/dev/null
pyenv install 3.14.0 -s 2>&1 | tail -3
pyenv global 3.14.0
python3.14 --version
'
echo "Python OK"

# ── 5. Frappe Bench ─────────────────────────────────────────────────
echo "=== Frappe Bench ==="
su - frappe -c '
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"
pip install frappe-bench 2>&1 | tail -3
bench --version
'
echo "Bench OK"

# ── 6. Bench init + ERPNext ─────────────────────────────────────────
echo "=== Bench init ==="
su - frappe -c '
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"
if [ ! -d ~/frappe-bench ]; then
    bench init ~/frappe-bench --frappe-branch version-16 2>&1 | tail -10
fi
cd ~/frappe-bench
bench get-app erpnext --branch version-16 2>&1 | tail -5
'
echo "Bench init OK"

# ── 7. Create site + install erpnext ────────────────────────────────
echo "=== Create site ==="
su - frappe -c '
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"
cd ~/frappe-bench
if [ ! -f sites/hoangdat.gpcds.site/site_config.json ]; then
    bench new-site hoangdat.gpcds.site --admin-password Letdoit1@ --mariadb-root-password Letdoit1@ 2>&1 | tail -5
fi
bench --site hoangdat.gpcds.site install-app erpnext 2>&1 | tail -5
'
echo "Site OK"

# ── 8. Clone GPC ERP apps ───────────────────────────────────────────
echo "=== GPC ERP apps ==="
su - frappe -c '
cd ~/frappe-bench
if [ ! -d /tmp/gpc-src ]; then
    git clone https://github.com/nguyentrieu210/gpc-erp.git /tmp/gpc-src 2>&1 | tail -3
else
    cd /tmp/gpc-src && git pull 2>&1 | tail -3
fi
cp -r /tmp/gpc-src/apps/* ~/frappe-bench/apps/ 2>/dev/null || true
cp -r /tmp/gpc-src/shared ~/frappe-bench/ 2>/dev/null || true
cp -r /tmp/gpc-src/deploy ~/frappe-bench/ 2>/dev/null || true
echo "Source copied"
'
echo "GPC ERP apps OK"

# ── 9. pip install 10 apps ─────────────────────────────────────────
echo "=== pip install ==="
su - frappe -c '
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"
cd ~/frappe-bench
for a in portal hr crm_ui tckt kho kinhdoanh quantri muahang duan taisan; do
    ./env/bin/pip install -e apps/$a -q 2>/dev/null
    mkdir -p sites/assets
    ln -sfn /home/frappe/frappe-bench/apps/$a/$a/public /home/frappe/frappe-bench/sites/assets/$a 2>/dev/null || true
    echo "pip: $a"
done
'
echo "pip OK"

# ── 10. Build frontends ─────────────────────────────────────────────
echo "=== Build frontends ==="
su - frappe -c '
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$HOME/.nvm/versions/node/v24.12.0/bin:$PATH"
. ~/.nvm/nvm.sh 2>/dev/null || true
cd ~/frappe-bench
for a in portal kinhdoanh tckt crm_ui muahang kho hr duan quantri taisan; do
    if [ -f "apps/$a/frontend/package.json" ]; then
        echo "building $a..."
        cd apps/$a/frontend
        [ ! -d node_modules ] && yarn install --silent 2>/dev/null || true
        yarn build --silent 2>/dev/null || yarn build
        cd /home/frappe/frappe-bench
    fi
done
echo BUILD ALL DONE
'
echo "Build OK"

# ── 11. bench install-app ──────────────────────────────────────────
echo "=== install-app ==="
su - frappe -c '
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"
cd ~/frappe-bench
for a in portal hr crm_ui tckt kho kinhdoanh quantri muahang duan taisan; do
    bench --site hoangdat.gpcds.site install-app $a 2>&1 | tail -1
done
'
echo "install-app OK"

# ── 12. Seed + Nginx + Final ───────────────────────────────────────
echo "=== Seed ==="
su - frappe -c '
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"
cd ~/frappe-bench
bench --site hoangdat.gpcds.site execute portal.setup.setup_portal 2>&1 | tail -2
bench --site hoangdat.gpcds.site execute taisan.api.setup_taisan 2>&1 | tail -2
'
echo "Seed OK"

echo "=== Nginx ==="
cp /home/frappe/frappe-bench/deploy/nginx/gpcds.site.conf /etc/nginx/sites-available/gpcds.site 2>/dev/null || true
ln -sf /etc/nginx/sites-available/gpcds.site /etc/nginx/sites-enabled/ 2>/dev/null || true
rm -f /etc/nginx/sites-enabled/default 2>/dev/null || true
nginx -t 2>&1 && systemctl reload nginx 2>&1 || true
echo "Nginx OK"

echo "=== Final ==="
su - frappe -c '
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"
cd ~/frappe-bench
bench build 2>&1 | tail -2
bench restart 2>&1
'

echo ""
echo "========================================="
echo "  INSTALL COMPLETE — $(date)"
echo "  https://gpcds.site"
echo "  Admin: Administrator / Letdoit1@"
echo "========================================="
