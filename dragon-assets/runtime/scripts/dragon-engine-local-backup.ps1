#天龙引擎本地备份脚本
# 功能：打包备份整个天龙引擎目录，保留最近 7 天版本
#
# 用法：
#   .\dragon-engine-local-backup.ps1          # 执行备份
#   .\dragon-engine-local-backup.ps1 -DryRun  # 预览（不实际备份）

param(
    [switch]$DryRun
)

# ============ 配置 ============
$SOURCE_DIR = "C:\Users\li\.claude\projects\dragon-engine"
$BACKUP_DIR = "D:\天龙引擎"
$DAYS_TO_KEEP = 7
$BACKUP_PREFIX = "dragon-engine-backup"

# 日志函数
function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $levelStr = switch ($Level) {
        "INFO"    { "[+]" }
        "WARN"    { "[!]" }
        "ERROR"   { "[X]" }
        "SUCCESS" { "[OK]" }
        default   { "[*]" }
    }
    Write-Host "$timestamp $levelStr $Message"
}

# ============ 主程序 ============
Write-Host ""
Write-Host "=== Tianlong Engine Local Backup ==="
Write-Host "===================================="

# 检查源目录
if (-not (Test-Path $SOURCE_DIR)) {
    Write-Log "Source directory not found: $SOURCE_DIR" "ERROR"
    exit 1
}

# 创建备份目录
if (-not (Test-Path $BACKUP_DIR)) {
    Write-Log "Creating backup directory: $BACKUP_DIR" "WARN"
    if (-not $DryRun) {
        New-Item -ItemType Directory -Path $BACKUP_DIR -Force | Out-Null
    }
}

# 生成备份文件名
$date = Get-Date -Format "yyyy-MM-dd"
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupName = "${BACKUP_PREFIX}_${date}_${timestamp}"
$backupFile = Join-Path $BACKUP_DIR "${backupName}.zip"
$linkFile = Join-Path $BACKUP_DIR "${BACKUP_PREFIX}_latest.zip"

Write-Log "Source: $SOURCE_DIR"
Write-Log "Backup: $BACKUP_DIR"
Write-Log "File: ${backupName}.zip"

if ($DryRun) {
    Write-Log "[DRY-RUN] Simulation mode, no actual backup" "WARN"
} else {
    Write-Host ""
    Write-Log "Starting compression..."

    try {
        # 使用 Compress-Archive 压缩目录
        Compress-Archive -Path "$SOURCE_DIR\*" -DestinationPath "$backupFile" -CompressionLevel Optimal -Force

        $fileSize = (Get-Item $backupFile).Length / 1MB
        Write-Log "Backup created: ${backupName}.zip ($(('{0:N2}' -f $fileSize)) MB)" "SUCCESS"

        # 更新 latest 链接
        if (Test-Path $linkFile) {
            Remove-Item $linkFile -Force
        }
        Copy-Item $backupFile $linkFile -Force
        Write-Log "Updated latest link" "SUCCESS"

    } catch {
        Write-Log "Backup failed: $_" "ERROR"
        exit 1
    }
}

# 清理旧备份（保留最近 7 天）
Write-Host ""
Write-Log "Cleaning old backups (keep last $DAYS_TO_KEEP days)..."

$allBackups = Get-ChildItem -Path $BACKUP_DIR -Filter "${BACKUP_PREFIX}_*.zip" | Sort-Object LastWriteTime -Descending
$backupsToDelete = $allBackups | Select-Object -Skip $DAYS_TO_KEEP

if ($backupsToDelete.Count -eq 0) {
    Write-Log "No old backups to clean" "INFO"
} else {
    foreach ($backup in $backupsToDelete) {
        if ($DryRun) {
            Write-Log "[DRY-RUN] Will delete: $($backup.Name)" "WARN"
        } else {
            Remove-Item $backup.FullName -Force
            Write-Log "Deleted: $($backup.Name)" "INFO"
        }
    }
}

# 显示备份统计
Write-Host ""
Write-Log "Backup Summary:" "INFO"
Write-Host "  Total backups: $($allBackups.Count)"
if ($allBackups.Count -gt 0) {
    Write-Host "  Latest backup: $($allBackups[0].Name) ($(('{0:N2}' -f ($allBackups[0].Length / 1MB)) + ' MB'))"
}
Write-Host "  Backup dir: $BACKUP_DIR"

Write-Host ""
Write-Host "===================================="
if ($DryRun) {
    Write-Log "Simulation complete" "SUCCESS"
} else {
    Write-Log "Backup complete" "SUCCESS"
}

exit 0
