# =============================================================
# OpenClaw Zero-Polling Hook - PowerShell Version
# =============================================================
# Windows-compatible version of the OpenClaw zero-polling hook
# Triggered by Claude Code hooks when a task completes (Stop)
# or session ends (SessionEnd).
#
# Integration: Dragon Engine V7.1 + OpenClaw Protocol
# Author: Dragon Engine Team
# Created: 2026-02-25
# =============================================================

# Configuration
$Config = @{
    StateDir = Join-Path $env:USERPROFILE ".openclaw\workspace\state"
    TaskFile = "cc-task.json"
    ResultFile = "cc-result.json"
    LockFile = "cc-complete.lock"
    LogFile = "cc-hook.log"
    DedupWindow = 60000  # 60 seconds
    LockTimeout = 30000  # 30 seconds
}

# Logger function
function Log-Message {
    param([string]$Message)

    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "[$timestamp] $Message"
    $logPath = Join-Path $Config.StateDir $Config.LogFile

    try {
        Add-Content -Path $logPath -Value $logMessage -ErrorAction SilentlyContinue
    } catch {
        # Silently fail if logging fails
    }
}

# Ensure state directory exists
function Ensure-StateDir {
    try {
        if (-not (Test-Path $Config.StateDir)) {
            New-Item -Path $Config.StateDir -ItemType Directory -Force | Out-Null
        }
    } catch {
        Log-Message "ERROR: Failed to create state dir: $($_.Exception.Message)"
    }
}

# Check deduplication
function Test-ShouldSkip {
    $resultPath = Join-Path $Config.StateDir $Config.ResultFile

    try {
        if (Test-Path $resultPath) {
            $file = Get-Item $resultPath
            $age = (Get-Date) - $file.LastWriteTime
            $ageMs = $age.TotalMilliseconds

            if ($ageMs -lt $Config.DedupWindow) {
                $ageSec = [Math]::Floor($ageMs / 1000)
                $windowSec = $Config.DedupWindow / 1000
                Log-Message "Dedup: result file is ${ageSec}s old (< ${windowSec}s), skipping"
                return $true
            }
        }
    } catch {
        # File doesn't exist or error checking, proceed
    }

    return $false
}

# Acquire lock
function Acquire-Lock {
    $lockPath = Join-Path $Config.StateDir $Config.LockFile

    try {
        if (Test-Path $lockPath) {
            $file = Get-Item $lockPath
            $age = (Get-Date) - $file.LastWriteTime
            $ageMs = $age.TotalMilliseconds

            if ($ageMs -lt $Config.LockTimeout) {
                $ageSec = [Math]::Floor($ageMs / 1000)
                Log-Message "Lock exists and is ${ageSec}s old, skipping"
                return $false
            }
        }
    } catch {
        # Lock file doesn't exist
    }

    try {
        $pid | Out-File -FilePath $lockPath -Force
        return $true
    } catch {
        Log-Message "ERROR: Failed to acquire lock: $($_.Exception.Message)"
        return $false
    }
}

# Release lock
function Release-Lock {
    $lockPath = Join-Path $Config.StateDir $Config.LockFile

    try {
        if (Test-Path $lockPath) {
            Remove-Item $lockPath -Force -ErrorAction SilentlyContinue
        }
    } catch {
        # Lock file doesn't exist or can't be removed
    }
}

# Calculate duration
function Get-Duration {
    param([string]$DispatchedAt)

    if (-not $DispatchedAt) {
        return "unknown"
    }

    try {
        $start = [DateTime]::Parse($DispatchedAt)
        $end = Get-Date
        $elapsed = ($end - $start).TotalSeconds

        if ($elapsed -ge 3600) {
            $hours = [Math]::Floor($elapsed / 3600)
            $minutes = [Math]::Floor(($elapsed % 3600) / 60)
            $seconds = $elapsed % 60
            return "${hours}h${minutes}m${seconds}s"
        } elseif ($elapsed -ge 60) {
            $minutes = [Math]::Floor($elapsed / 60)
            $seconds = $elapsed % 60
            return "${minutes}m${seconds}s"
        } else {
            $seconds = [Math]::Floor($elapsed)
            return "${seconds}s"
        }
    } catch {
        return "unknown"
    }
}

# Collect file tree
function Get-FileTree {
    param([string]$WorkDir, [int]$MaxLines = 30)

    try {
        $files = Get-ChildItem -Path $WorkDir -Recurse -Depth 3 -File -ErrorAction SilentlyContinue |
            Where-Object {
                $_.FullName -notmatch "node_modules" -and
                $_.FullName -notmatch "\.git" -and
                $_.FullName -notmatch "dist" -and
                $_.FullName -notmatch "__pycache__" -and
                $_.Name -ne ".DS_Store"
            } |
            Select-Object -First $MaxLines |
            ForEach-Object {
                $_.FullName.Replace($WorkDir + "\", "")
            }

        return $files -join "`n"
    } catch {
        return ""
    }
}

# Main hook function
function Invoke-TaskComplete {
    param([string]$InputJson)

    Log-Message "Hook triggered: Invoke-TaskComplete"

    # Parse input
    $data = $InputJson | ConvertFrom-Json
    $sessionId = $data.sessionId
    $transcriptPath = $data.transcriptPath
    $cwd = $data.cwd
    $hookEventName = $data.hookEventName

    Log-Message "Event=$hookEventName SessionID=$sessionId CWD=$cwd"

    # Check deduplication
    if (Test-ShouldSkip) {
        return
    }

    # Acquire lock
    if (-not (Acquire-Lock)) {
        return
    }

    try {
        # Read task info
        $taskPath = Join-Path $Config.StateDir $Config.TaskFile
        $taskName = "unknown"
        $taskDispatched = ""
        $workDir = $cwd

        try {
            if (Test-Path $taskPath) {
                $taskData = Get-Content $taskPath -Raw | ConvertFrom-Json
                $taskName = $taskData.task
                if (-not $taskName) { $taskName = "unknown" }
                $taskDispatched = $taskData.dispatched_at
                $workDir = $taskData.work_dir
                if (-not $workDir) { $workDir = $cwd }
                Log-Message "Task file found: $taskName"
            }
        } catch {
            Log-Message "No task file found, using defaults"
        }

        # Calculate duration
        $duration = Get-Duration -DispatchedAt $taskDispatched
        $completedAt = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")

        # Collect file tree
        $fileTree = Get-FileTree -WorkDir $workDir

        # Build result object
        $result = [PSCustomObject]@{
            session_id = $sessionId
            hook_event = $hookEventName
            task = $taskName
            work_dir = $workDir
            status = "completed"
            completed_at = $completedAt
            duration = $duration
            transcript_path = $transcriptPath
            file_tree = $fileTree
        }

        # Write result JSON
        $resultPath = Join-Path $Config.StateDir $Config.ResultFile
        $result | ConvertTo-Json -Depth 10 | Out-File -FilePath $resultPath -Force
        Log-Message "Result written to $resultPath"

        # TODO: Send wake event to OpenClaw CLI
        # This would require OpenClaw CLI integration

        Log-Message "Hook completed successfully"
    } catch {
        Log-Message "ERROR: Hook failed: $($_.Exception.Message)"
    } finally {
        Release-Lock
    }
}

# Export for module usage
Export-ModuleMember -Function Invoke-TaskComplete

# Allow direct execution for testing
if ($MyInvocation.InvocationName -eq $MyInvocation.MyCommand.Name) {
    $testData = [PSCustomObject]@{
        sessionId = "test-session-123"
        transcriptPath = "C:\path\to\transcript"
        cwd = Get-Location
        hookEventName = "Stop"
    } | ConvertTo-Json -Depth 10

    Invoke-TaskComplete -InputJson $testData
}
