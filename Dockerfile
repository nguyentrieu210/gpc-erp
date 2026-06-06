FROM ghcr.io/nguyentrieu210/frappe-vn:v16

LABEL org.opencontainers.image.source="https://github.com/nguyentrieu210/gpc-erp"
LABEL org.opencontainers.image.description="GPC Custom ERP — 9 custom apps baked in"
LABEL org.opencontainers.image.licenses="MIT"

WORKDIR /home/frappe/frappe-bench

# ── Copy source các custom app ──────────────────────────────────────────────
COPY --chown=frappe:frappe apps/portal     apps/portal
COPY --chown=frappe:frappe apps/hr         apps/hr
COPY --chown=frappe:frappe apps/crm_ui     apps/crm_ui
COPY --chown=frappe:frappe apps/tckt       apps/tckt
COPY --chown=frappe:frappe apps/kho        apps/kho
COPY --chown=frappe:frappe apps/kinhdoanh  apps/kinhdoanh
COPY --chown=frappe:frappe apps/quantri    apps/quantri
COPY --chown=frappe:frappe apps/muahang    apps/muahang
COPY --chown=frappe:frappe apps/duan       apps/duan

# ── pip install editable + symlink assets ────────────────────────────────────
RUN for a in portal hr crm_ui tckt kho kinhdoanh quantri muahang duan; do \
      echo "=== installing $a ==="; \
      ./env/bin/pip install -e "apps/$a" -q; \
      mkdir -p sites/assets; \
      ln -sfn /home/frappe/frappe-bench/apps/$a/$a/public \
              /home/frappe/frappe-bench/sites/assets/$a; \
    done

# ── Bộ UI dùng chung: copy + sync vào src/_shared của từng app trước khi build ─
COPY --chown=frappe:frappe shared shared
RUN bash shared/sync.sh

# ── Build Vue frontend cho từng app có frontend/ ────────────────────────────
# node/yarn đã có trong image frappe-vn:v16 qua nvm
RUN . /home/frappe/.nvm/nvm.sh && \
    for a in portal hr crm_ui tckt kho kinhdoanh quantri muahang duan; do \
      if [ -f "apps/$a/frontend/package.json" ]; then \
        echo "=== building frontend $a ==="; \
        cd apps/$a/frontend && \
        yarn install --frozen-lockfile --silent 2>/dev/null || yarn install --silent; \
        yarn build --silent; \
        cd /home/frappe/frappe-bench; \
      fi; \
    done
