# ============================================
# 客服工作台 V0.1 · PowerShell 启动脚本
# 用法:右键 → 使用 PowerShell 运行
# ============================================

$ErrorActionPreference = "Stop"

# 1. Docker Desktop
Write-Host "=== [1/5] 检查 Docker Desktop ===" -ForegroundColor Cyan
$d = Get-Process "Docker Desktop" -ErrorAction SilentlyContinue
if (-not $d) {
    Write-Host "启动 Docker Desktop..." -ForegroundColor Yellow
    Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    Write-Host "等待 30 秒..." -ForegroundColor Yellow
    Start-Sleep -Seconds 30
} else {
    Write-Host "Docker Desktop 已在运行" -ForegroundColor Green
}

# 2. daemon
Write-Host ""
Write-Host "=== [2/5] 等待 Docker daemon ===" -ForegroundColor Cyan
$retry = 0
while ($retry -lt 12) {
    try {
        docker info 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Docker daemon 就绪" -ForegroundColor Green
            break
        }
    } catch {}
    $retry++
    Write-Host "  等待中 ($retry/12)..."
    Start-Sleep -Seconds 5
}

# 3. 切目录
Write-Host ""
Write-Host "=== [3/5] 进入部署目录 ===" -ForegroundColor Cyan
Set-Location $PSScriptRoot
Write-Host "当前: $(Get-Location)"

# 4. .env
Write-Host ""
Write-Host "=== [4/5] 准备 .env ===" -ForegroundColor Cyan
if (-not (Test-Path .env.example)) {
    Write-Host "ERROR: .env.example 缺失" -ForegroundColor Red
    exit 1
}
if (Test-Path .env) {
    Write-Host ".env 已存在" -ForegroundColor Yellow
} else {
    Copy-Item .env.example .env
    Write-Host ".env 创建成功 - 请填入 OPENAI_API_KEY" -ForegroundColor Yellow
}

# 5. compose
Write-Host ""
Write-Host "=== [5/5] 启动所有服务 ===" -ForegroundColor Cyan
$composeCmd = "docker compose"
try {
    docker compose version 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) { $composeCmd = "docker-compose" }
} catch {
    $composeCmd = "docker-compose"
}
Write-Host "使用: $composeCmd" -ForegroundColor Green

Invoke-Expression "$composeCmd up -d"

Write-Host ""
Write-Host "=== 启动完成 ===" -ForegroundColor Green
Write-Host "状态: $composeCmd ps"
Write-Host "日志: $composeCmd logs -f backend"
Write-Host "健康: curl http://localhost:8080/health"
