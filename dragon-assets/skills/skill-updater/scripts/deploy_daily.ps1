# deploy_daily.ps1 · skill-updater V1.1 增量 · Windows 调度脚本
# 部署方式（任选其一）：
#   1. Windows Task Scheduler（推荐）：
#      - 打开"任务计划程序" → 创建任务
#      - 触发器：每天 09:00
#      - 操作：powershell -ExecutionPolicy Bypass -File C:\...\deploy_daily.ps1
#   2. 手动跑：双击 deploy_daily.bat（配套）
#   3. Git Bash: bash scripts/cron_daily.sh
#
# 行为：
#   1. 调用 Git Bash 跑 cron_daily.sh
#   2. 失败时写 Windows Event Log（可选）
#   3. 日志输出到 logs/deploy-daily-YYYYMMDD.log
#
# 退出码：0=全 PASS / 1=有 FAILED / 2=配置错

$ErrorActionPreference = "Continue"

# 路径常量
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$SkillDir = Split-Path -Parent $ScriptDir
$DragonRoot = $env:DRAGON_ROOT
if (-not $DragonRoot) {
    $DragonRoot = "C:\Users\li\.claude\projects\dragon-engine"
}
$LogsDir = Join-Path $SkillDir "logs"
$DateStamp = Get-Date -Format "yyyyMMdd-HHmmss"
$DateDay = Get-Date -Format "yyyyMMdd"
$LogFile = Join-Path $LogsDir "deploy-daily-$DateDay.log"

# Git Bash 路径（Windows 自带 Git for Windows）
$GitBash = "C:\Program Files\Git\bin\bash.exe"
if (-not (Test-Path $GitBash)) {
    $GitBash = "C:\Program Files (x86)\Git\bin\bash.exe"
}
if (-not (Test-Path $GitBash)) {
    Write-Error "❌ 未找到 Git Bash（请安装 Git for Windows）"
    exit 3
}

# 准备日志目录
if (-not (Test-Path $LogsDir)) {
    New-Item -ItemType Directory -Path $LogsDir -Force | Out-Null
}

function Log($msg) {
    $ts = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    $line = "[$ts] $msg"
    Write-Host $line
    Add-Content -Path $LogFile -Value $line -Encoding UTF8
}

Log "═══ skill-updater · deploy_daily · $DateStamp ═══"
Log "天龙根: $DragonRoot"
Log "Git Bash: $GitBash"
Log "日志: $LogFile"

# ────────────────────────────────────────
# Step 1 · 跑 cron_daily.sh
# ────────────────────────────────────────
Log ""
Log "── Step 1 · 调用 cron_daily.sh ──"

$CronScript = Join-Path $ScriptDir "cron_daily.sh"
$env:DRAGON_ROOT = $DragonRoot

$Process = Start-Process -FilePath $GitBash `
    -ArgumentList "-c", "`"$CronScript`" 2>&1" `
    -NoNewWindow -Wait -PassThru `
    -RedirectStandardOutput (Join-Path $LogsDir "deploy-stdout-$DateDay.log") `
    -RedirectStandardError (Join-Path $LogsDir "deploy-stderr-$DateDay.log")

$ExitCode = $Process.ExitCode
Log "cron_daily.sh exit=${ExitCode}"

# ────────────────────────────────────────
# Step 2 · 失败时发 Windows 桌面通知
# ────────────────────────────────────────
if ($ExitCode -ne 0) {
    Log ""
    Log "── Step 2 · 失败处理 ──"

    # Windows 桌面通知
    [System.Reflection.Assembly]::LoadWithPartialName('System.Windows.Forms') | Out-Null
    [System.Reflection.Assembly]::LoadWithPartialName('System.Drawing') | Out-Null
    $Balloon = New-Object System.Windows.Forms.NotifyIcon
    $Balloon.Icon = [System.Drawing.SystemIcons]::Warning
    $Balloon.BalloonTipIcon = [System.Windows.Forms.ToolTipIcon]::Warning
    $Balloon.BalloonTipTitle = "⚠️ skill-updater apply 失败"
    $Balloon.BalloonTipText = "exit=$ExitCode，详情见日志: $LogFile"
    $Balloon.Visible = $true
    $Balloon.ShowBalloonTip(10000)
    Start-Sleep -Seconds 3
    $Balloon.Dispose()

    Log "📢 Windows 桌面通知已发"
    exit 1
}

Log ""
Log "✅ deploy_daily 完成，全部 PASS"
exit 0
