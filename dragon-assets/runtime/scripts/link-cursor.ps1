# link-cursor.ps1 · 天龙引擎 -> Cursor 软链挂载
# =================================================
#
# Cursor 用 .cursorrules 文件 + .cursor/ 目录。
# 这里 junction 整个 dragon-engine 仓库到 ~/.cursor/dragon-engine/，
# 然后在用户项目里加一行 "Include ~/.cursor/dragon-engine/" 即可。
#
# 注：Cursor 现阶段对 junction 支持有限（rules 仍以 .cursorrules 为主），
# 这个 link 主要用于在 Cursor 侧浏览天龙引擎资源。
#
# 调用：
#   powershell -ExecutionPolicy Bypass -File scripts/link-cursor.ps1
#   powershell -ExecutionPolicy Bypass -File scripts/link-cursor.ps1 -DryRun

param(
    [switch]$DryRun,
    [string]$CursorHome = "$env:USERPROFILE\.cursor",
    [string]$LinkName = "dragon-engine",
    [string]$DragonRoot = (Split-Path -Parent $PSScriptRoot)
)

if (-not (Test-Path $DragonRoot)) {
    Write-Error "Dragon root not found: $DragonRoot"
    exit 1
}

if (-not (Test-Path $CursorHome)) {
    Write-Host "Creating $CursorHome ..."
    if (-not $DryRun) {
        New-Item -ItemType Directory -Path $CursorHome | Out-Null
    }
}

$target = Join-Path $CursorHome $LinkName
$source = $DragonRoot

Write-Host "Junction-linking dragon-engine to $target ..."
Write-Host "  DragonRoot: $DragonRoot"
Write-Host ""

if (Test-Path $target) {
    $item = Get-Item $target -Force
    if ($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint) {
        Write-Host "  [SKIP] $target is already a $($item.LinkType)"
        exit 0
    } else {
        Write-Host "  [WARN] $target exists but is NOT a junction/symlink. Refusing to overwrite."
        exit 1
    }
}

if ($DryRun) {
    Write-Host "  [DRY ] New-Item Junction $target -> $source"
    exit 0
}

try {
    New-Item -ItemType Junction -Path $target -Target $source | Out-Null
    Write-Host "  [OK ] Junction created: $target -> $source"
    Write-Host ""
    Write-Host "In your Cursor project, create .cursorrules containing:"
    Write-Host "    @~/.cursor/dragon-engine/CLAUDE.md"
} catch {
    Write-Error "  [ERR] Failed to create junction: $_"
    exit 1
}