#!/bin/bash
# GPC ERP - Final fix and deploy
# Run directly on server: bash go.sh
set -e
cd /home/frappe/frappe-bench

echo "=== Fix ctypes ==="
DEBIAN_FRONTEND=noninteractive apt-get install -y -qq libffi-dev 2>/dev/null || true

# Rebuild Python with ctypes
su - frappe -c '
export PYENV_ROOT=$HOME/.pyenv
export PATH=$PYENV_ROOT/bin:$PATH
eval "$(pyenv init -)" 2>/dev/null
pyenv install 3.14.0 -s 2>&1 | tail -3
pyenv global 3.14.0
python3.14 -c "import ctypes; print(ctypes)"
'

# Recreate env
rm -rf env
su - frappe -c '
export PYENV_ROOT=$HOME/.pyenv
export PATH=$PYENV_ROOT/bin:/usr/bin:/bin:$PATH
eval "$(pyenv init -)" 2>/dev/null
cd /home/frappe/frappe-bench
python3.14 -m venv env
./env/bin/pip install -e apps/frappe -q
./env/bin/pip install -e apps/erpnext -q
'

# Test
su - frappe -c '
export PYENV_ROOT=$HOME/.pyenv
export PATH=$PYENV_ROOT/bin:$PATH
eval "$(pyenv init -)" 2>/dev/null
cd /home/frappe/frappe-bench
bench --site hoangdat.gpcds.site list-apps 2>&1 | head -15
'

# Install custom apps
su - frappe -c '
export PYENV_ROOT=$HOME/.pyenv
export PATH=$PYENV_ROOT/bin:$HOME/.nvm/versions/node/v24.12.0/bin:/usr/bin:/bin:$PATH
. $HOME/.nvm/nvm.sh 2>/dev/null || true
eval "$(pyenv init -)" 2>/dev/null
cd /home/frappe/frappe-bench

# pip all custom apps
for a in portal hr crm_ui tckt kho kinhdoanh quantri muahang duan taisan; do
    ./env/bin/pip install -e apps/$a -q 2>/dev/null
    ln -sfn /home/frappe/frappe-bench/apps/$a/$a/public /home/frappe/frappe-bench/sites/assets/$a 2>/dev/null || true
    echo pip: $a
done

# install-app
for a in portal hr crm_ui tckt kho kinhdoanh quantri muahang duan taisan; do
    bench --site hoangdat.gpcds.site install-app $a 2>&1 | tail -1
done

# seed
bench --site hoangdat.gpcds.site execute portal.setup.setup_portal 2>&1 | tail -2
bench --site hoangdat.gpcds.site execute taisan.api.setup_taisan 2>&1 | tail -2

# build site bundles
bench build 2>&1 | tail -3

# restart
bench restart 2>&1 | tail -3
'

echo "=== ALL DONE ==="
echo "https://gpcds.site"
