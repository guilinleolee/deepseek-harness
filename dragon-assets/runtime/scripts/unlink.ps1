# unlink.ps1 · 移除 dragon-engine 软链
# ======================================
#
# 反向操作：删除由 link-claude.ps1 / link-cursor.ps1 / link-continue.ps1
# 创建的所有 junction/symlink。仅删除 dragon-engine 相关的链接，
# 不会触碰任何真实目录或文件。

$Targets = @{
    "Claude Code" = @("$env:USERPROFILE\.claude\skills", "$env:USERPROFILE\.claude\agents", "$env:USERPROFILE\.claude\commands", "$env:USERPROFILE\.claude\hooks")
    "Cursor"      = @("$env:USERPROFILE\.cursor\dragon-engine")
    "Continue"    = @("$env:USERPROFILE\.continue\slash_commands\commands")
}

$removed = 0
$skipped = 0

foreach ($app in $Targets.Keys) {
    Write-Host "=== $app ==="
    foreach ($p in $Targets[$app]) {
        if (-not (Test-Path $p)) {
            continue
        }
        $item = Get-Item $p -Force
        if ($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint) {
            Write-Host "  [DEL ] $p  ($($item.LinkType))"
            Remove-Item $p -Force
            $removed++
        } else {
            Write-Host "  [SKIP] $p  (not a link, refusing to delete)"
            $skipped++
        }
    }
}

Write-Host ""
Write-Host "Summary: removed=$removed  skipped=$skipped"