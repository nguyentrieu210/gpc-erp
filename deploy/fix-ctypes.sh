#!/bin/bash
echo Fixing _ctypes
DEBIAN_FRONTEND=noninteractive apt-get install -y libffi-dev
export PYENV_ROOT=/home/frappe/.pyenv
export PATH=$PYENV_ROOT/bin:$PATH
su - frappe -c "pyenv uninstall -f 3.14.0; pyenv install 3.14.0; pyenv global 3.14.0; python3.14 -c 'import ctypes; print(ctypes)'"
cd /home/frappe/frappe-bench
rm -rf env
su - frappe -c "cd /home/frappe/frappe-bench; python3.14 -m venv env"
su - frappe -c "cd /home/frappe/frappe-bench; ./env/bin/pip install -e apps/frappe -q"
su - frappe -c "cd /home/frappe/frappe-bench; ./env/bin/pip install -e apps/erpnext -q"
su - frappe -c "cd /home/frappe/frappe-bench; /home/frappe/.pyenv/versions/3.14.0/bin/bench --site hoangdat.gpcds.site list-apps"
echo FIX_DONE
