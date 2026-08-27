# link-status.ps1 · 查看 dragon-engine 软链挂载状态
# =====================================================
#
# 检查 4 个 AI 应用目录（Claude Code / Cursor / Continue）下是否存在
# dragon-engine 相关 junction/symlink，并报告类型。

$Targets = @{
    "Claude Code" = @{
        Home = "$env:USERPROFILE\.claude"
        Dirs = @("skills", "agents", "commands", "hooks")
    }
    "Cursor" = @{
        Home = "$env:USERPROFILE\.cursor"
        Dirs = @("dragon-engine")
    }
    "Continue" = @{
        Home = "$env:USERPROFILE\.continue"
        Dirs = @("slash_commands\commands")
    }
}

Write-Host "Dragon-engine link status:"
Write-Host ""

$totalLinked = 0
$totalMiss = 0

foreach ($app in $Targets.Keys) {
    $cfg = $Targets[$app]
    Write-Host "=== $app ($($cfg.Home)) ==="
    if (-not (Test-Path $cfg.Home)) {
        Write-Host "  (home dir not exist)"
        Write-Host ""
        continue
    }
    foreach ($d in $cfg.Dirs) {
        $p = Join-Path $cfg.Home $d
        if (-not (Test-Path $p)) {
            Write-Host "  [MISS] $p  (not linked)"
            $totalMiss++
            continue
        }
        $item = Get-Item $p -Force
        if ($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint) {
            Write-Host "  [LINK] $p  ($($item.LinkType) -> $($item.Target))"
            $totalLinked++
        } else {
            Write-Host "  [FILE] $p  (real directory, not a link)"
        }
    }
    Write-Host ""
}

Write-Host "Summary: $totalLinked linked, $totalMiss missing"
if ($totalMiss -gt 0) {
    Write-Host ""
    Write-Host "To link: powershell -File scripts/link-<app>.ps1"
}