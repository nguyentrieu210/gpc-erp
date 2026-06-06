#!/usr/bin/env bash
# GPC SHARED — đồng bộ shared/ui -> apps/<app>/frontend/src/_shared
# Dùng được cả trên Windows (Git Bash) lẫn trong container Linux/Docker.
#   bash shared/sync.sh            # đồng bộ tất cả app có frontend/
#   bash shared/sync.sh kinhdoanh  # chỉ 1 app
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SRC="$ROOT/shared/ui"
APPS=${*:-"portal hr crm_ui tckt kho kinhdoanh quantri muahang duan"}

for a in $APPS; do
  fe="$ROOT/apps/$a/frontend"
  [ -d "$fe" ] || continue
  dest="$fe/src/_shared"
  rm -rf "$dest"
  mkdir -p "$dest"
  cp -r "$SRC/." "$dest/"
  echo "synced -> apps/$a/frontend/src/_shared"
done
echo "DONE"
