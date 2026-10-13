# 📊 Weekly Memory Digest Cron Script
# 天龙引擎 V9.0 - 每周自动汇总记忆
#
# 调度建议：每周日 03:00 执行
# Windows 计划任务注册：
#   schtasks /create /tn "DragonEngine-WeeklyMemory" /tr "powershell -File C:\Users\li\.claude\projects\dragon-engine\scripts\cron_weekly_memory.ps1" /sc weekly /d SUN /st 03:00
#
# 失败处理：退出码 1 → 计划任务标记失败，可配邮件通知

$ErrorActionPreference = "Stop"

# 路径配置
$ProjectRoot = "C:\Users\li\.claude\projects\dragon-engine"
$DigestScript = Join-Path $ProjectRoot "hooks\utility\weekly-memory-digest.js"
$NodeExe = (Get-Command node.exe).Source

# 切到项目根（cwd 上下文）
Set-Location $ProjectRoot

Write-Host "📊 [Cron] Weekly Memory Digest 启动"
Write-Host "   ├─ 时间: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
Write-Host "   ├─ 脚本: $DigestScript"
Write-Host "   └─ Node: $NodeExe"

# 执行 Node 脚本（默认启用 --notify 失败通知）
$result = & $NodeExe $DigestScript --notify 2>&1
$exitCode = $LASTEXITCODE

Write-Host "`n📋 执行结果 (exit=$exitCode):"
Write-Host $result

if ($exitCode -ne 0) {
    Write-Host "`n❌ 周报生成失败，退出码: $exitCode"
    Write-Host "   错误日志: $env:USERPROFILE\.claude\memory\cron-error.log"
    exit 1
}

Write-Host "`n✅ 周报生成成功"
exit 0