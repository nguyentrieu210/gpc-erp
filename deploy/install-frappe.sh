#!/bin/bash
# GPC ERP — Full Frappe v16 stack install on Ubuntu 25.04 bare metal
# Run: bash install-frappe.sh 2>&1 | tee /root/install.log
set -e

echo "========================================="
echo " GPC ERP — Full Stack Install"
echo " $(date)"
echo "========================================="

# ── 1. System dependencies ─────────────────────────────────────────
echo "=== 1. System packages ==="
apt-get update -qq
apt-get install -y -qq \
    git curl wget build-essential python3-dev python3-pip python3-venv \
    python3-setuptools python3-wheel libssl-dev libffi-dev \
    mariadb-server mariadb-client libmysqlclient-dev \
    redis-server nginx supervisor \
    xvfb libfontconfig wkhtmltopdf \
    libjpeg-dev zlib1g-dev libfreetype6-dev liblcms2-dev \
    libtiff5-dev libwebp-dev libharfbuzz-dev libfribidi-dev \
    tcl tk libxml2-dev libxslt1-dev \
    software-properties-common dirmngr apt-transport-https ca-certificates \
    gnupg2 2>&1 | tail -3

# ── 2. Node.js 24 ───────────────────────────────────────────────────
echo "=== 2. Node.js 24 ==="
if ! command -v node &>/dev/null; then
    curl -fsSL https://deb.nodesource.com/setup_24.x | bash - 2>&1 | tail -3
    apt-get install -y -qq nodejs 2>&1 | tail -3
fi
node --version

# ── 3. Yarn ─────────────────────────────────────────────────────────
echo "=== 3. Yarn ==="
npm install -g yarn 2>&1 | tail -2
yarn --version

# ── 4. MariaDB setup ────────────────────────────────────────────────
echo "=== 4. MariaDB ==="
systemctl start mariadb 2>/dev/null || service mariadb start 2>/dev/null
mysql -u root <<< "
CREATE USER IF NOT EXISTS 'frappe'@'localhost' IDENTIFIED BY 'Letdoit1@';
GRANT ALL PRIVILEGES ON *.* TO 'frappe'@'localhost' WITH GRANT OPTION;
FLUSH PRIVILEGES;
" 2>/dev/null || true

# Fix for Ubuntu 25.04: add utf8mb4 config
cat > /etc/mysql/mariadb.conf.d/90-gpc.cnf << 'MYSQL'
[mysqld]
character-set-server = utf8mb4
collation-server = utf8mb4_unicode_ci
innodb_buffer_pool_size = 512M
[client]
default-character-set = utf8mb4
MYSQL
systemctl restart mariadb 2>/dev/null || service mariadb restart 2>/dev/null
echo "MariaDB OK"

# ── 5. Redis ────────────────────────────────────────────────────────
echo "=== 5. Redis ==="
systemctl start redis-server 2>/dev/null || service redis-server start 2>/dev/null

# ── 6. Create frappe user ───────────────────────────────────────────
echo "=== 6. frappe user ==="
if ! id frappe &>/dev/null; then
    useradd -m -s /bin/bash frappe
    echo "frappe:Letdoit1@" | chpasswd
    usermod -aG sudo frappe
fi

# ── 7. Python 3.14 via pyenv (for frappe user) ──────────────────────
echo "=== 7. Python 3.14 ==="
su - frappe -c "
if [ ! -d ~/.pyenv ]; then
    curl -fsSL https://pyenv.run | bash 2>&1 | tail -5
fi
" 2>/dev/null || true

# Add pyenv to bashrc
grep -q 'pyenv init' /home/frappe/.bashrc 2>/dev/null || cat >> /home/frappe/.bashrc << 'PYENV'
export PYENV_ROOT="$HOME/.pyenv"
[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"
PYENV

su - frappe -c "
source ~/.bashrc
pyenv install 3.14.0 -s 2>&1 | tail -5
pyenv global 3.14.0
python3.14 --version
" 2>&1 | tail -5

# ── 8. Install bench ────────────────────────────────────────────────
echo "=== 8. Frappe Bench ==="
su - frappe -c "
source ~/.bashrc
pip install frappe-bench 2>&1 | tail -3
bench --version
" 2>&1 | tail -5

# ── 9. Init bench + get ERPNext ─────────────────────────────────────
echo "=== 9. Bench init ==="
su - frappe -c "
source ~/.bashrc
export PATH=\$HOME/.pyenv/versions/3.14.0/bin:\$PATH
if [ ! -d ~/frappe-bench ]; then
    bench init ~/frappe-bench --frappe-branch version-16 2>&1 | tail -10
fi
cd ~/frappe-bench
bench get-app erpnext --branch version-16 2>&1 | tail -5
" 2>&1 | tail -10

# ── 10. Create site ─────────────────────────────────────────────────
echo "=== 10. Create site ==="
su - frappe -c "
source ~/.bashrc
export PATH=\$HOME/.pyenv/versions/3.14.0/bin:\$PATH
cd ~/frappe-bench
if [ ! -f sites/hoangdat.gpcds.site/site_config.json ]; then
    bench new-site hoangdat.gpcds.site --admin-password Letdoit1@ --mariadb-root-password Letdoit1@ 2>&1 | tail -5
fi
bench --site hoangdat.gpcds.site install-app erpnext 2>&1 | tail -5
" 2>&1 | tail -10

# ── 11. Clone GPC ERP source ────────────────────────────────────────
echo "=== 11. Clone GPC ERP ==="
su - frappe -c "
cd ~/frappe-bench
if [ ! -f shared/sync.sh ]; then
    git clone https://github.com/nguyentrieu210/gpc-erp.git /tmp/gpc-src 2>&1 | tail -3
    cp -r /tmp/gpc-src/apps /home/frappe/frappe-bench/
    cp -r /tmp/gpc-src/shared /home/frappe/frappe-bench/
    cp -r /tmp/gpc-src/deploy /home/frappe/frappe-bench/
    rm -rf /tmp/gpc-src
fi
" 2>&1 | tail -5

# ── 12. pip install + build + install-app ────────────────────────────
echo "=== 12. Install custom apps ==="
su - frappe -c "
source ~/.bashrc
export PATH=\$HOME/.pyenv/versions/3.14.0/bin:\$HOME/.nvm/versions/node/v24.12.0/bin:\$PATH
. ~/.nvm/nvm.sh 2>/dev/null
cd ~/frappe-bench
for a in portal hr crm_ui tckt kho kinhdoanh quantri muahang duan taisan; do
    ./env/bin/pip install -e apps/\$a -q 2>/dev/null
    mkdir -p sites/assets
    ln -sfn /home/frappe/frappe-bench/apps/\$a/\$a/public /home/frappe/frappe-bench/sites/assets/\$a 2>/dev/null || true
    echo \"pip: \$a\"
done
" 2>&1

su - frappe -c "
source ~/.bashrc
export PATH=\$HOME/.pyenv/versions/3.14.0/bin:\$HOME/.nvm/versions/node/v24.12.0/bin:\$PATH
. ~/.nvm/nvm.sh 2>/dev/null
cd ~/frappe-bench
for a in portal kinhdoanh tckt crm_ui muahang kho hr duan quantri taisan; do
    if [ -f apps/\$a/frontend/package.json ]; then
        echo \"building \$a...\"
        cd apps/\$a/frontend
        [ ! -d node_modules ] && yarn install --silent 2>/dev/null || true
        yarn build --silent 2>/dev/null || yarn build
        cd /home/frappe/frappe-bench
    fi
done
echo BUILD DONE
" 2>&1

su - frappe -c "
source ~/.bashrc
export PATH=\$HOME/.pyenv/versions/3.14.0/bin:\$PATH
cd ~/frappe-bench
for a in portal hr crm_ui tckt kho kinhdoanh quantri muahang duan taisan; do
    bench --site hoangdat.gpcds.site install-app \$a 2>&1 | tail -1
done
" 2>&1

# ── 13. Seed + Nginx + Build ────────────────────────────────────────
echo "=== 13. Seed + Nginx + Final ==="
su - frappe -c "
source ~/.bashrc
export PATH=\$HOME/.pyenv/versions/3.14.0/bin:\$PATH
cd ~/frappe-bench
bench --site hoangdat.gpcds.site execute portal.setup.setup_portal 2>&1 | tail -2
bench --site hoangdat.gpcds.site execute taisan.api.setup_taisan 2>&1 | tail -2
" 2>&1

# Nginx config
cp /home/frappe/frappe-bench/deploy/nginx/gpcds.site.conf /etc/nginx/sites-available/gpcds.site 2>/dev/null || true
ln -sf /etc/nginx/sites-available/gpcds.site /etc/nginx/sites-enabled/ 2>/dev/null || true
rm -f /etc/nginx/sites-enabled/default 2>/dev/null || true
nginx -t 2>&1 && systemctl reload nginx 2>&1 || true

# Final build + restart
su - frappe -c "
source ~/.bashrc
export PATH=\$HOME/.pyenv/versions/3.14.0/bin:\$PATH
cd ~/frappe-bench
bench build 2>&1 | tail -2
bench restart 2>&1
" 2>&1

# ── 14. Setup bench production ──────────────────────────────────────
echo "=== 14. Production setup ==="
su - frappe -c "
source ~/.bashrc
export PATH=\$HOME/.pyenv/versions/3.14.0/bin:\$PATH
cd ~/frappe-bench
bench setup production frappe 2>&1 | tail -5
bench setup nginx 2>&1 | tail -3
" 2>&1

nginx -t 2>&1 && systemctl reload nginx 2>&1 || service nginx reload 2>&1

echo ""
echo "========================================="
echo "  INSTALL COMPLETE — $(date)"
echo "  https://gpcds.site  → Portal"
echo "  Admin: Administrator / Letdoit1@"
echo "========================================="
