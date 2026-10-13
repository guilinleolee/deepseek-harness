# link-continue.ps1 · 天龙引擎 -> Continue 软链挂载
# =====================================================
#
# Continue (https://continue.dev) 的资源目录结构：
#   ~/.continue/
#     config.json
#     rules/         (类似 .cursorrules 的规则)
#     slash_commands/ (类似 Claude Code commands)
#
# Continue 对 commands 加载机制与 Claude Code 不完全相同（需要 config.json
# 注册），所以这里只挂载 rules/ + slash_commands/，并提示用户手动补 config。
#
# 调用：
#   powershell -ExecutionPolicy Bypass -File scripts/link-continue.ps1
#   powershell -ExecutionPolicy Bypass -File scripts/link-continue.ps1 -DryRun

param(
    [switch]$DryRun,
    [string]$ContinueHome = "$env:USERPROFILE\.continue",
    [string]$DragonRoot = (Split-Path -Parent $PSScriptRoot)
)

$Dirs = @("commands")  # Continue 主要用 slash_commands，对应 commands/

if (-not (Test-Path $DragonRoot)) {
    Write-Error "Dragon root not found: $DragonRoot"
    exit 1
}
foreach ($d in $Dirs) {
    if (-not (Test-Path (Join-Path $DragonRoot $d))) {
        Write-Error "Required dir missing in dragon root: $d"
        exit 1
    }
}

if (-not (Test-Path $ContinueHome)) {
    Write-Host "Creating $ContinueHome ..."
    if (-not $DryRun) {
        New-Item -ItemType Directory -Path $ContinueHome | Out-Null
    }
}

$slashDir = Join-Path $ContinueHome "slash_commands"

if (-not (Test-Path $slashDir)) {
    if (-not $DryRun) {
        New-Item -ItemType Directory -Path $slashDir | Out-Null
    }
}

Write-Host "Junction-linking dragon-engine to $slashDir ..."
Write-Host ""

foreach ($d in $Dirs) {
    $target = Join-Path $slashDir $d
    $source = Join-Path $DragonRoot $d

    if (Test-Path $target) {
        $item = Get-Item $target -Force
        if ($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint) {
            Write-Host "  [SKIP] $target is already a $($item.LinkType)"
        } else {
            Write-Host "  [WARN] $target exists but is NOT a junction/symlink. Refusing to overwrite."
        }
        continue
    }

    if ($DryRun) {
        Write-Host "  [DRY ] New-Item Junction $target -> $source"
        continue
    }

    try {
        New-Item -ItemType Junction -Path $target -Target $source | Out-Null
        Write-Host "  [OK ] Junction created: $target -> $source"
    } catch {
        Write-Error "  [ERR] Failed to create junction for ${d}: $_"
    }
}

Write-Host ""
Write-Host "Continue's config.json still needs to register the slash commands."
Write-Host "See: docs/integration.md (Continue section)"