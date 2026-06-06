#!/bin/bash
# GPC ERP — Final server-side deploy
# Run: curl -fsSL https://raw.githubusercontent.com/nguyentrieu210/gpc-erp/master/deploy/final.sh | bash
BENCH=/home/frappe/frappe-bench
SITE=hoangdat.gpcds.site
echo "=== GPC Final Deploy ==="

# Ensure pip has all deps
cd $BENCH
./env/bin/pip install frappe-bench -q 2>/dev/null
./env/bin/pip install -e apps/frappe -q 2>/dev/null
./env/bin/pip install -e apps/erpnext -q 2>/dev/null

echo "=== Fix ctypes ==="
./env/bin/python -c "import ctypes; print(ctypes.__file__)" || {
    echo "ctypes broken, fixing..."
    apt-get install -y -qq libffi-dev liblzma-dev
    su - frappe -c "/home/frappe/.pyenv/bin/pyenv uninstall -f 3.14.0; /home/frappe/.pyenv/bin/pyenv install 3.14.0"
    cd $BENCH && rm -rf env
    /home/frappe/.pyenv/versions/3.14.0/bin/python3.14 -m venv env
    ./env/bin/pip install frappe-bench -q
    ./env/bin/pip install -e apps/frappe -q
    ./env/bin/pip install -e apps/erpnext -q
}

echo "=== Install custom apps ==="
for a in portal hr crm_ui tckt kho kinhdoanh quantri muahang duan taisan; do
    ./env/bin/pip install -e apps/$a -q 2>/dev/null
    ln -sfn $BENCH/apps/$a/$a/public $BENCH/sites/assets/$a 2>/dev/null || true
    echo "pip: $a"
done

echo "=== Build frontends ==="
export PATH=$HOME/.nvm/versions/node/v24.12.0/bin:$PATH
. $HOME/.nvm/nvm.sh 2>/dev/null || true
for a in portal kinhdoanh tckt crm_ui muahang kho hr duan quantri taisan; do
    if [ -f apps/$a/frontend/package.json ]; then
        echo "building $a..."
        cd apps/$a/frontend
        [ ! -d node_modules ] && yarn install --silent 2>/dev/null || true
        yarn build --silent 2>/dev/null || yarn build
        cd $BENCH
    fi
done
echo "BUILD DONE"

echo "=== bench install-app ==="
for a in portal hr crm_ui tckt kho kinhdoanh quantri muahang duan taisan; do
    ./env/bin/bench --site $SITE install-app $a 2>&1 | tail -1
done

echo "=== Seed ==="
./env/bin/bench --site $SITE execute portal.setup.setup_portal 2>&1 | tail -2
./env/bin/bench --site $SITE execute taisan.api.setup_taisan 2>&1 | tail -2

echo "=== bench build + restart ==="
./env/bin/bench build 2>&1 | tail -2
./env/bin/bench restart 2>&1 | tail -2

echo "=== DONE ==="
echo "https://gpcds.site"
