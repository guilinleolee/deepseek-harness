<#
.SYNOPSIS
    Scan CREATOR_WORKBENCH_INPUT_DIR for the current creation task and emit a
    JSON inventory the agent reads in stage 1 of sop/creator-workflow.md.

.DESCRIPTION
    Walks the input directory, groups files by first-level subfolder (treated
    as a topic or campaign), and emits one JSON object per group. Each entry
    carries the relative paths, total bytes, and the most recent mtime.

    The script does NOT read file contents — it only inventories them so the
    agent decides which files are worth reading with read_file.

.PARAMETER InputDir
    Input root. Defaults to $env:CREATOR_WORKBENCH_INPUT_DIR.

.PARAMETER OutputPath
    Where to write the inventory JSON. Defaults to stdout.
#>
[CmdletBinding()]
param(
    [string]$InputDir = $env:CREATOR_WORKBENCH_INPUT_DIR,
    [string]$OutputPath
)

$ErrorActionPreference = 'Stop'

if (-not $InputDir) {
    throw "InputDir missing: pass -InputDir or set CREATOR_WORKBENCH_INPUT_DIR"
}
if (-not (Test-Path $InputDir)) {
    throw "InputDir does not exist: $InputDir"
}

$groups = @{}
Get-ChildItem -Path $InputDir -Recurse -File -ErrorAction SilentlyContinue | ForEach-Object {
    $rel = $_.FullName.Substring((Resolve-Path $InputDir).Path.Length).TrimStart('\', '/')
    $top = $rel.Split('\', '/')[0]
    if (-not $groups.ContainsKey($top)) {
        $groups[$top] = [ordered]@{
            group = $top
            file_count = 0
            total_bytes = 0L
            last_modified = $null
            files = @()
        }
    }
    $g = $groups[$top]
    $g.file_count += 1
    $g.total_bytes += $_.Length
    if (-not $g.last_modified -or $_.LastWriteTimeUtc -gt $g.last_modified) {
        $g.last_modified = $_.LastWriteTimeUtc.ToString('yyyy-MM-ddTHH:mm:ssZ')
    }
    $g.files += [ordered]@{
        path = $rel
        bytes = $_.Length
        modified = $_.LastWriteTimeUtc.ToString('yyyy-MM-ddTHH:mm:ssZ')
    }
}

$payload = [ordered]@{
    input_dir = $InputDir
    scanned_at = (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ')
    group_count = $groups.Count
    groups = @($groups.Values)
}

$json = $payload | ConvertTo-Json -Depth 6
if ($OutputPath) {
    $parent = Split-Path -Parent $OutputPath
    if ($parent -and -not (Test-Path $parent)) { New-Item -ItemType Directory -Force -Path $parent | Out-Null }
    Set-Content -Path $OutputPath -Value $json -Encoding utf8
    Write-Host "wrote: $OutputPath"
} else {
    Write-Output $json
}