# link-claude.ps1 · 天龙引擎 -> Claude Code 软链挂载
# =================================================
#
# 把天龙引擎的 4 类资源（skills / agents / commands / hooks）通过
# NTFS Junction 挂载到 Claude Code 家目录，Claude Code 会自动识别。
#
# Junction vs Symlink:
#   - Junction 不需要开发者模式或 admin（普通 NTFS 即可）
#   - Junction 仅用于目录；天龙引擎 4 类资源恰好都是目录
#   - 删除 junction 不会影响源目录
#
# 调用：
#   powershell -ExecutionPolicy Bypass -File scripts/link-claude.ps1
#   powershell -ExecutionPolicy Bypass -File scripts/link-claude.ps1 -DryRun

param(
    [switch]$DryRun,
    [string]$ClaudeHome = "$env:USERPROFILE\.claude",
    [string]$DragonRoot = (Split-Path -Parent $PSScriptRoot)
)

$Dirs = @("skills", "agents", "commands", "hooks")

# Sanity checks
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

if (-not (Test-Path $ClaudeHome)) {
    Write-Host "Creating $ClaudeHome ..."
    if (-not $DryRun) {
        New-Item -ItemType Directory -Path $ClaudeHome | Out-Null
    }
}

Write-Host "Junction-linking dragon-engine to $ClaudeHome ..."
Write-Host "  DragonRoot: $DragonRoot"
Write-Host "  Target dirs: $($Dirs -join ', ')"
Write-Host ""

$linked = 0
$skipped = 0
$warned = 0

foreach ($d in $Dirs) {
    $target = Join-Path $ClaudeHome $d
    $source = Join-Path $DragonRoot $d

    if (Test-Path $target) {
        $item = Get-Item $target -Force
        if ($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint) {
            $linkType = $item.LinkType  # "Junction" or "SymbolicLink"
            Write-Host "  [SKIP] $target is already a $linkType"
            $skipped++
        } else {
            Write-Host "  [WARN] $target exists but is NOT a junction/symlink. Refusing to overwrite."
            Write-Host "         Back it up first, then run this script again."
            $warned++
        }
        continue
    }

    if ($DryRun) {
        Write-Host "  [DRY ] New-Item Junction $target -> $source"
        $linked++
        continue
    }

    try {
        New-Item -ItemType Junction -Path $target -Target $source | Out-Null
        Write-Host "  [OK ] Junction created: $target -> $source"
        $linked++
    } catch {
        Write-Error "  [ERR] Failed to create junction for ${d}: $_"
    }
}

Write-Host ""
Write-Host "Summary: linked=$linked  skipped=$skipped  warned=$warned"
Write-Host ""
if ($linked -gt 0 -or $skipped -gt 0) {
    Write-Host "Verify with: powershell -File scripts/link-status.ps1"
    Write-Host "Undo with:   powershell -File scripts/unlink.ps1"
}