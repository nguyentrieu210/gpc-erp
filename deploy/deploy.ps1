# GPC ERP — Deploy to bare-metal server 171.244.140.133 (gpcds.site)
# Usage: powershell -File deploy.ps1

$ErrorActionPreference = "Stop"
$Server = "171.244.140.133"
$User = "root"
$Pass = "Letdoit1@"
$BenchPath = "/home/frappe/frappe-bench"
$Site = "hoangdat.gpcds.site"

# ── 1. Package source ───────────────────────────────────────────────────────
Write-Host "=== Packaging source ===" -ForegroundColor Cyan
$TempDir = "$PSScriptRoot\..\temp_deploy"
Remove-Item -Recurse -Force $TempDir -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force -Path "$TempDir\apps","$TempDir\shared" | Out-Null

$Apps = @("portal","hr","crm_ui","tckt","kho","kinhdoanh","quantri","muahang","duan","taisan")
foreach ($a in $Apps) {
    $src = "$PSScriptRoot\..\apps\$a"
    $dst = "$TempDir\apps\$a"
    New-Item -ItemType Directory -Force -Path "$dst" | Out-Null
    robocopy $src $dst /E /XF *.pyc /XD __pycache__ node_modules .git /NFL /NDL /NJH /NJS | Out-Null
    # Copy frontend build output (pre-built dist)
    if (Test-Path "$src\$a\public\frontend") {
        Write-Host "  $a: frontend pre-built" -ForegroundColor Green
    }
}
# Shared
robocopy "$PSScriptRoot\..\shared" "$TempDir\shared" /E /NFL /NDL /NJH /NJS | Out-Null
Write-Host "Packaged OK" -ForegroundColor Green

# ── 2. Upload to server ─────────────────────────────────────────────────────
Write-Host "=== Uploading to server ===" -ForegroundColor Cyan
try {
    Import-Module Posh-SSH -ErrorAction Stop
    $Pwd = ConvertTo-SecureString $Pass -AsPlainText -Force
    $Cred = New-Object System.Management.Automation.PSCredential($User, $Pwd)
    $Session = New-SSHSession -ComputerName $Server -Credential $Cred -AcceptKey -Force -ConnectionTimeout 10
    $Sid = $Session.SessionId

    # Create target dirs
    Invoke-SSHCommand -SessionId $Sid -Command "mkdir -p $BenchPath/apps $BenchPath/shared" | Out-Null

    # Upload each app
    foreach ($a in $Apps) {
        Write-Host "  Uploading $a..." -ForegroundColor Yellow
        Set-SFTPItem -SessionId $Sid -Path "$TempDir\apps\$a" -Destination "$BenchPath/apps/" -Recursive -Force
    }
    Write-Host "  Uploading shared..." -ForegroundColor Yellow
    Set-SFTPItem -SessionId $Sid -Path "$TempDir\shared" -Destination "$BenchPath/" -Recursive -Force

    # ── 3. Install & Build on Server ─────────────────────────────────────────
    Write-Host "=== Installing & Building ===" -ForegroundColor Cyan

    $SetupScript = @"
set -e
cd $BenchPath
export PATH="/home/frappe/.nvm/versions/node/v24.12.0/bin:/home/frappe/.nvm/nvm.sh:\$PATH"
. /home/frappe/.nvm/nvm.sh 2>/dev/null

echo "--- pip install ---"
for a in portal hr crm_ui tckt kho kinhdoanh quantri muahang duan taisan; do
  ./env/bin/pip install -e apps/\$a -q 2>/dev/null
  mkdir -p sites/assets
  ln -sfn $BenchPath/apps/\$a/\$a/public $BenchPath/sites/assets/\$a 2>/dev/null || true
done
echo "pip ok"

echo "--- build frontend ---"
for a in portal hr crm_ui tckt kho kinhdoanh quantri muahang duan taisan; do
  if [ -f "apps/\$a/frontend/package.json" ]; then
    echo "Building \$a..."
    cd apps/\$a/frontend
    if [ ! -d node_modules ]; then
      yarn install --silent 2>/dev/null || yarn install 2>/dev/null
    fi
    yarn build --silent 2>/dev/null || yarn build 2>/dev/null
    cd $BenchPath
  fi
done
echo "build ok"

echo "--- listing apps ---"
bench --site $Site list-apps 2>/dev/null || true
echo "DONE"
"@

    $ScriptFile = "/tmp/deploy_setup.sh"
    # Write script via SFTP
    $ScriptBytes = [System.Text.Encoding]::UTF8.GetBytes($SetupScript)
    $ScriptPath = "$PSScriptRoot\..\temp_deploy\setup.sh"
    [System.IO.File]::WriteAllBytes($ScriptPath, $ScriptBytes)
    Set-SFTPItem -SessionId $Sid -Path $ScriptPath -Destination $ScriptFile -Force

    Invoke-SSHCommand -SessionId $Sid -Command "bash $ScriptFile 2>&1" -TimeOut 600

    # ── 4. bench install-app ─────────────────────────────────────────────────
    Write-Host "=== bench install-app ===" -ForegroundColor Cyan
    foreach ($a in $Apps) {
        Write-Host "  install-app $a..." -ForegroundColor Yellow
        $result = Invoke-SSHCommand -SessionId $Sid -Command "cd $BenchPath && bench --site $Site install-app $a 2>&1" -TimeOut 60
        Write-Host "    $($result.Output -join ' ')" -ForegroundColor DarkGray
    }

    # ── 5. Seed portal modules + setup ───────────────────────────────────────
    Write-Host "=== Seeding ===" -ForegroundColor Cyan
    Invoke-SSHCommand -SessionId $Sid -Command "cd $BenchPath && bench --site $Site execute portal.setup.setup_portal 2>&1" -TimeOut 30
    Invoke-SSHCommand -SessionId $Sid -Command "cd $BenchPath && bench --site $Site execute taisan.api.setup_taisan 2>&1" -TimeOut 30

    # ── 6. Rebuild JS/CSS bundles ────────────────────────────────────────────
    Write-Host "=== bench build ===" -ForegroundColor Cyan
    Invoke-SSHCommand -SessionId $Sid -Command "cd $BenchPath && bench build 2>&1" -TimeOut 120

    Remove-SSHSession -SessionId $Sid | Out-Null

} finally {
    # Cleanup
    Remove-Item -Recurse -Force $TempDir -ErrorAction SilentlyContinue
    if ($Session) { Remove-SSHSession -SessionId $Sid -ErrorAction SilentlyContinue | Out-Null }
}

Write-Host "=== DEPLOY COMPLETE ===" -ForegroundColor Green
Write-Host "URL: https://hoangdat.gpcds.site" -ForegroundColor Cyan
Write-Host "Portal: https://hoangdat.gpcds.site/portal_app" -ForegroundColor Cyan
