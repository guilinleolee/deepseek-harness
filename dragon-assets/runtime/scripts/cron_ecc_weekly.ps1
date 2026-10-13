# cron_ecc_weekly.ps1 - Stage 47.2 ECC 7 天观察期 Windows 计划任务脚本
#
# 用法 (管理员):
#   1. 在 PowerShell (管理员) 中执行此脚本: `.\cron_ecc_weekly.ps1 -Install`
#   2. 在任务计划程序 → 任务计划库 → \DragonEngine\ECC-Observe 可看到注册成功的任务
#   3. 立即跑一次测试: `.\cron_ecc_weekly.ps1 -RunNow`
#   4. 卸载: `.\cron_ecc_weekly.ps1 -Uninstall`
#
# 任务设置:
#   - 触发器: 每天 00:00 UTC (Asia/Shanghai = 08:00) 触发
#   - 命令:   python scripts/ecc_7day.py single
#   - 失败:   单日失败不影响 7 天观察期 (Day 0-6 累计)

[CmdletBinding()]
param(
    [switch]$Install,
    [switch]$Uninstall,
    [switch]$RunNow
)

$TaskName = "ECC-Observe"
$TaskPath = "\DragonEngine"
$ScriptPath = Join-Path (Get-Location) "scripts\ecc_7day.py"
$PythonExe = (Get-Command python -ErrorAction Stop).Source

if (-not (Test-Path $ScriptPath)) {
    Write-Error "ecс_7day.py 不存在: $ScriptPath"
    exit 1
}

if ($Install) {
    $Action = New-ScheduledTaskAction `
        -Execute $PythonExe `
        -Argument "`"$ScriptPath`" single" `
        -WorkingDirectory (Get-Location)
    $Trigger = New-ScheduledTaskTrigger `
        -Daily `
        -At "00:00"

    $Settings = New-ScheduledTaskSettingsSet `
        -StartWhenAvailable `
        -DontStopIfGoingOnBatteries `
        -ExecutionTimeLimit (New-TimeSpan -Minutes 5)

    Register-ScheduledTask `
        -TaskName $TaskName `
        -TaskPath $TaskPath `
        -Action $Action `
        -Trigger $Trigger `
        -Settings $Settings `
        -Description "Stage 47.2 ECC 7 天观察期 — 每天 0:00 UTC 跑一次 snapshot" `
        -User "SYSTEM" `
        -RunLevel Highest `
        -Force

    Write-Host "[OK] Task '$TaskName\$TaskPath' 已安装 (Daily 00:00 UTC)"
    Write-Host "    测试: & $PSCommandPath -RunNow"
    exit 0
}

if ($Uninstall) {
    Unregister-ScheduledTask -TaskName $TaskName -TaskPath $TaskPath -Confirm:$false
    Write-Host "[OK] Task '$TaskName\$TaskPath' 已卸载"
    exit 0
}

if ($RunNow) {
    Write-Host "==> 手动跑一次 Day snapshot ..."
    $env:PYTHONIOENCODING = "utf-8"
    & $PythonExe $ScriptPath single
    Write-Host "`n==> 当前进度:"
    & $PythonExe $ScriptPath status
    exit $LASTEXITCODE
}

# 默认: 打印用法
@"
用法:
  .\$($MyInvocation.MyCommand.Name) -Install    # 注册 Windows 计划任务
  .\$($MyInvocation.MyCommand.Name) -Uninstall  # 卸载
  .\$($MyInvocation.MyCommand.Name) -RunNow      # 手动跑 1 次

任务名: $TaskName\$TaskPath
触发: 每日 00:00 UTC (Asia/Shanghai = 08:00)
脚本: $ScriptPath
Python: $PythonExe
"@
