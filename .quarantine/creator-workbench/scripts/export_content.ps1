<#
.SYNOPSIS
    Export a verified Creator Workbench draft to per-platform copy-paste artifacts.

.DESCRIPTION
    This is a deterministic transformation from .work/<task_id>/drafts/<topic_id>/*-script.md
    into copy-paste-ready artifacts under $OutputDir/<Platform>/. It does NOT publish to
    any platform API — the user manually pastes each artifact into the target app.

    The function exports the platform set the caller passes. Unknown platforms are
    recorded in export_errors.json but do not abort the run. Approval must happen
    before this script is invoked; see sop/creator-workflow.md stage 5.

.PARAMETER TaskId
    The work-<id> folder name under CREATOR_WORKBENCH_CWD/.work/.

.PARAMETER TopicId
    The topic-<id> folder name inside .work/<TaskId>/drafts/.

.PARAMETER Platforms
    Comma-separated platform list: wechat,xiaohongshu,douyin,toutiao.

.PARAMETER WorkRoot
    The CREATOR_WORKBENCH_CWD root. Defaults to $env:CREATOR_WORKBENCH_CWD.

.PARAMETER OutputDir
    Final artifact root. Defaults to $env:CREATOR_WORKBENCH_OUTPUT_DIR.

.EXAMPLE
    pwsh -NoProfile -File scripts/export_content.ps1 `
        -TaskId work-20260828-0001 -TopicId topic-001 `
        -Platforms wechat,xiaohongshu `
        -WorkRoot $PWD `
        -OutputDir "D:\知识库\FDE\秉凌自媒体工作台\输出内容"
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$TaskId,

    [Parameter(Mandatory = $true)]
    [string]$TopicId,

    [Parameter(Mandatory = $true)]
    [string]$Platforms,

    [string]$WorkRoot = $env:CREATOR_WORKBENCH_CWD,

    [string]$OutputDir = $env:CREATOR_WORKBENCH_OUTPUT_DIR
)

$ErrorActionPreference = 'Stop'

if (-not $WorkRoot) {
    throw "WorkRoot missing: pass -WorkRoot or set CREATOR_WORKBENCH_CWD"
}
if (-not $OutputDir) {
    throw "OutputDir missing: pass -OutputDir or set CREATOR_WORKBENCH_OUTPUT_DIR"
}

$draftRoot = Join-Path $WorkRoot ".work/$TaskId/drafts/$TopicId"
if (-not (Test-Path $draftRoot)) {
    throw "draft root not found: $draftRoot"
}

$today = Get-Date -Format 'yyyy-MM-dd'
# Normalize separators and split. `[string[]]` typed parameters in external
# `pwsh -File` invocations drop the value on Windows; this script keeps
# `[string]` and parses it inline. Build an explicit `List<string>` under a
# fresh variable name to avoid PowerShell's variable-type-inference caching
# (assigning to `$platforms` here has been observed to leave the variable
# typed `string` on this host).
$normalized = ($Platforms -replace '[,\s;|]+', ',') -replace '^,|,$', ''
$rawParts = [regex]::Split($normalized, ',')
$plist = New-Object 'System.Collections.Generic.List[string]'
foreach ($entry in $rawParts) {
    $trimmed = "$entry".Trim()
    if ($trimmed) { $plist.Add($trimmed) | Out-Null }
}
$platforms = $plist

# Required platform → source script file mapping.
$sourceMap = @{
    'wechat'      = 'wechat-script.md'
    'xiaohongshu' = 'xhs-script.md'
    'douyin'      = 'douyin-script.md'
    'toutiao'     = 'toutiao-micro-post.md'
    'zhihu'       = 'zhihu-script.md'
    'bilibili'    = 'bilibili-script.md'
}

# Per-platform transform: produces <artifact> files under <OutputDir>/<Platform>/.
$transforms = @{
    'wechat' = {
        param($source, $targetDir, $meta)
        New-Item -ItemType Directory -Force -Path $targetDir | Out-Null
        $body = Get-Content -Raw -Encoding utf8 $source

        # Try shibazi-illustrator for placeholder images. Failures degrade
        # silently to <p>[图片位]</p> so the export never blocks on art.
        $imageDir = Join-Path $targetDir 'wechat-images'
        $illustrateScript = Join-Path $PSScriptRoot 'illustrate.ps1'
        $canIllustrate = (Test-Path $illustrateScript) -and $env:CREATOR_WORKBENCH_SKILLS_PATH
        $generatedImages = [ordered]@{}
        if ($canIllustrate -and ($body -match '<插入点')) {
            New-Item -ItemType Directory -Force -Path $imageDir | Out-Null
            try {
                pwsh -NoProfile -File $illustrateScript `
                    -InputPath $source `
                    -OutputDir $imageDir `
                    -Template kabager `
                    -Format html `
                    -Width 1200 `
                    -Height 512 | Out-Null
                Get-ChildItem -Path $imageDir -Filter '*.html' | ForEach-Object {
                    $generatedImages[$_.BaseName] = $_.FullName
                }
            } catch {
                Write-Warning "[illustrate] failed: $($_.Exception.Message)"
                $generatedImages = @{}
            }
        }

        # Convert headings to plain bold; keep paragraphs verbatim.
        $html = New-Object System.Text.StringBuilder
        [void]$html.AppendLine('<section style="font-family:-apple-system,sans-serif;line-height:1.7;">')
        $imageIndex = 0
        foreach ($line in ($body -split "`n")) {
            if ($line -match '^#\s+(.+)$') {
                [void]$html.AppendLine("<h1 style=`"font-size:20px;`">$($Matches[1])</h1>")
            } elseif ($line -match '^##\s+(.+)$') {
                [void]$html.AppendLine("<h2 style=`"font-size:17px;margin-top:24px;`">$($Matches[1])</h2>")
            } elseif ($line -match '^>\s+(.+)$') {
                [void]$html.AppendLine("<blockquote style=`"border-left:3px solid #ccc;padding-left:12px;color:#555;`">$($Matches[1])</blockquote>")
            } elseif ($line -match '^\s*[-*]\s+(.+)$') {
                [void]$html.AppendLine("<li>$($Matches[1])</li>")
            } elseif ($line -match '<插入点') {
                $imageIndex += 1
                $key = "wechat-script-poster"
                if ($generatedImages.Contains($key)) {
                    [void]$html.AppendLine("<p><img src=`"wechat-images/$key.html`" alt=`"配图 $imageIndex`" style=`"max-width:100%;`" /></p>")
                } else {
                    [void]$html.AppendLine("<p>[图片位 $imageIndex]</p>")
                }
            } elseif ($line.Trim() -eq '') {
                [void]$html.AppendLine('<br/>')
            } else {
                [void]$html.AppendLine("<p>$line</p>")
            }
        }
        [void]$html.AppendLine('</section>')

        $htmlFile = Join-Path $targetDir 'wechat-richtext.html'
        Set-Content -Path $htmlFile -Value $html.ToString() -Encoding utf8

        Copy-Item -Path $source -Destination (Join-Path $targetDir 'wechat-source.md') -Force

        $files = @($htmlFile, (Join-Path $targetDir 'wechat-source.md'))
        $imageDirRel = $null
        if ((Get-ChildItem -Path $imageDir -File -ErrorAction SilentlyContinue).Count -gt 0) {
            $imageDirRel = 'wechat-images'
        }

        return @{
            platform = 'wechat'
            files = $files
            image_dir = $imageDirRel
        }
    }

    'xiaohongshu' = {
        param($source, $targetDir, $meta)
        New-Item -ItemType Directory -Force -Path $targetDir | Out-Null

        $body = Get-Content -Raw -Encoding utf8 $source
        $lines = $body -split "`n"
        $titleLine = ($lines | Where-Object { $_ -match '^#\s+' } | Select-Object -First 1)
        $title = if ($titleLine) { ($titleLine -replace '^#\s+', '').Trim() } else { '' }

        $cover = ($lines | Where-Object { $_ -match '^\s*>\s*封面文案' } | Select-Object -First 1)
        $coverText = if ($cover) { ($cover -replace '^\s*>\s*封面文案[:：]?\s*', '').Trim() } else { '' }

        $tags = ($lines | Where-Object { $_ -match '^##\s*标签' } | ForEach-Object {
                $idx = [array]::IndexOf($lines, $_)
                for ($i = $idx + 1; $i -lt $lines.Count; $i++) {
                    $t = $lines[$i].Trim()
                    if ($t -eq '' -or $t.StartsWith('#')) { break }
                    $t
                }
            }) -join ' '

        $text = New-Object System.Text.StringBuilder
        [void]$text.AppendLine("【标题】$title")
        [void]$text.AppendLine('')
        [void]$text.AppendLine("【封面】$coverText")
        [void]$text.AppendLine('')
        # body: strip top heading + bottom auxiliary sections
        $bodyStart = ($lines | Where-Object { $_ -match '^##\s+正文' } | Select-Object -First 1)
        if ($bodyStart) {
            $startIdx = [array]::IndexOf($lines, $bodyStart) + 1
            for ($i = $startIdx; $i -lt $lines.Count; $i++) {
                $line = $lines[$i]
                if ($line -match '^##\s+') { break }
                [void]$text.AppendLine($line)
            }
        }
        if ($tags) {
            [void]$text.AppendLine('')
            [void]$text.AppendLine("【标签】$tags")
        }

        $textFile = Join-Path $targetDir 'xhs-text.txt'
        Set-Content -Path $textFile -Value $text.ToString() -Encoding utf8
        Copy-Item -Path $source -Destination (Join-Path $targetDir 'xhs-source.md') -Force

        # Image placeholder directory; user drops generated images here.
        $imgDir = Join-Path $targetDir 'xhs-images'
        New-Item -ItemType Directory -Force -Path $imgDir | Out-Null

        return @{
            platform = 'xiaohongshu'
            files = @($textFile, (Join-Path $targetDir 'xhs-source.md'))
            image_dir = $imgDir
        }
    }

    'douyin' = {
        param($source, $targetDir, $meta)
        New-Item -ItemType Directory -Force -Path $targetDir | Out-Null

        $body = Get-Content -Raw -Encoding utf8 $source
        $lines = $body -split "`n"
        $titleLine = ($lines | Where-Object { $_ -match '^#\s+' } | Select-Object -First 1)
        $title = if ($titleLine) { ($titleLine -replace '^#\s+', '').Trim() } else { '' }

        $text = New-Object System.Text.StringBuilder
        [void]$text.AppendLine("# $title")
        [void]$text.AppendLine('')
        [void]$text.AppendLine($body)

        $mdFile = Join-Path $targetDir 'douyin-script.md'
        Set-Content -Path $mdFile -Value $text.ToString() -Encoding utf8
        Copy-Item -Path $source -Destination (Join-Path $targetDir 'douyin-source.md') -Force

        $coverDir = Join-Path $targetDir 'douyin-cover'
        New-Item -ItemType Directory -Force -Path $coverDir | Out-Null

        return @{
            platform = 'douyin'
            files = @($mdFile, (Join-Path $targetDir 'douyin-source.md'))
            cover_dir = $coverDir
        }
    }

    'toutiao' = {
        param($source, $targetDir, $meta)
        New-Item -ItemType Directory -Force -Path $targetDir | Out-Null

        $body = Get-Content -Raw -Encoding utf8 $source
        $lines = $body -split "`n"
        $titleLine = ($lines | Where-Object { $_ -match '^#\s+' } | Select-Object -First 1)
        $title = if ($titleLine) { ($titleLine -replace '^#\s+', '').Trim() } else { '' }

        $text = New-Object System.Text.StringBuilder
        [void]$text.AppendLine("【微头条】$title")
        [void]$text.AppendLine('')
        # body is the first paragraph after the title; everything else is metadata.
        $inBody = $false
        foreach ($line in $lines) {
            if ($line -match '^#\s+') { $inBody = $true; continue }
            if (-not $inBody) { continue }
            if ($line.Trim() -eq '') { [void]$text.AppendLine(''); continue }
            if ($line -match '^```') { break }
            [void]$text.AppendLine($line)
        }

        $mdFile = Join-Path $targetDir 'toutiao-micro-post.md'
        Set-Content -Path $mdFile -Value $text.ToString() -Encoding utf8
        Copy-Item -Path $source -Destination (Join-Path $targetDir 'toutiao-source.md') -Force

        return @{
            platform = 'toutiao'
            files = @($mdFile, (Join-Path $targetDir 'toutiao-source.md'))
        }
    }

    'zhihu' = {
        param($source, $targetDir, $meta)
        New-Item -ItemType Directory -Force -Path $targetDir | Out-Null

        $body = Get-Content -Raw -Encoding utf8 $source
        $lines = $body -split "`n"
        $titleLine = ($lines | Where-Object { $_ -match '^#\s+' } | Select-Object -First 1)
        $title = if ($titleLine) { ($titleLine -replace '^#\s+', '').Trim() } else { '' }

        # Extract 参考文献 block at the end (if present) so the answer body
        # excludes it from the main paste.
        $refs = New-Object System.Text.StringBuilder
        $main = New-Object System.Text.StringBuilder
        $inRefs = $false
        foreach ($line in $lines) {
            if ($line -match '^##\s*参考文献') { $inRefs = $true; continue }
            if ($inRefs) {
                [void]$refs.AppendLine($line)
            } else {
                [void]$main.AppendLine($line)
            }
        }

        $text = New-Object System.Text.StringBuilder
        [void]$text.AppendLine("【知乎问题】$title")
        [void]$text.AppendLine('')
        [void]$text.AppendLine($main.ToString())
        if ($refs.Length -gt 0) {
            [void]$text.AppendLine('')
            [void]$text.AppendLine('--- 参考文献 ---')
            [void]$text.AppendLine($refs.ToString())
        }

        $textFile = Join-Path $targetDir 'zhihu-answer.md'
        Set-Content -Path $textFile -Value $text.ToString() -Encoding utf8
        Copy-Item -Path $source -Destination (Join-Path $targetDir 'zhihu-source.md') -Force

        return @{
            platform = 'zhihu'
            files = @($textFile, (Join-Path $targetDir 'zhihu-source.md'))
        }
    }

    'bilibili' = {
        param($source, $targetDir, $meta)
        New-Item -ItemType Directory -Force -Path $targetDir | Out-Null

        $body = Get-Content -Raw -Encoding utf8 $source
        $lines = $body -split "`n"
        $titleLine = ($lines | Where-Object { $_ -match '^#\s+' } | Select-Object -First 1)
        $title = if ($titleLine) { ($titleLine -replace '^#\s+', '').Trim() } else { '' }

        # B 站视频脚本：保留镜头/字幕/口播结构，直接作为可读剧本分发。
        $text = New-Object System.Text.StringBuilder
        [void]$text.AppendLine("# B 站视频脚本")
        [void]$text.AppendLine('')
        [void]$text.AppendLine("【标题】$title")
        [void]$text.AppendLine('')
        [void]$text.AppendLine($body)

        $mdFile = Join-Path $targetDir 'bilibili-script.md'
        Set-Content -Path $mdFile -Value $text.ToString() -Encoding utf8
        Copy-Item -Path $source -Destination (Join-Path $targetDir 'bilibili-source.md') -Force

        $coverDir = Join-Path $targetDir 'bilibili-cover'
        New-Item -ItemType Directory -Force -Path $coverDir | Out-Null

        return @{
            platform = 'bilibili'
            files = @($mdFile, (Join-Path $targetDir 'bilibili-source.md'))
            cover_dir = $coverDir
        }
    }
}

$results = @()
$errors  = @()
$results_list = New-Object 'System.Collections.Generic.List[object]'
$errors_list = New-Object 'System.Collections.Generic.List[object]'
$manifest = @{
    task_id   = $TaskId
    topic_id  = $TopicId
    exported_at = (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ')
    work_root = $WorkRoot
    output_dir = $OutputDir
    platforms = @()
}

foreach ($platform in $plist) {
    if (-not $sourceMap.ContainsKey($platform)) {
        $errors_list.Add([ordered]@{
            platform = $platform
            reason   = 'unknown_platform'
            message  = "no source mapping for $platform"
        }) | Out-Null
        continue
    }

    $source = Join-Path $draftRoot $sourceMap[$platform]
    if (-not (Test-Path $source)) {
        $errors_list.Add([ordered]@{
            platform = $platform
            reason   = 'missing_source'
            path     = $source
        }) | Out-Null
        continue
    }

    $platformOutDir = Join-Path $OutputDir "$platform/$today/$TaskId-$TopicId"
    $metaPath = Join-Path $draftRoot 'meta.json'
    $meta = $null
    if (Test-Path $metaPath) {
        try { $meta = Get-Content -Raw -Encoding utf8 $metaPath | ConvertFrom-Json } catch { $meta = $null }
    }

    try {
        $transform = $transforms[$platform]
        $result = & $transform $source $platformOutDir $meta
        $results_list.Add($result) | Out-Null
        $results += $result
        $manifest.platforms += [ordered]@{
            platform = $platform
            output_dir = $platformOutDir
            files = $result.files
        }
        Write-Host "[ok] $platform -> $platformOutDir"
    } catch {
        $errors_list.Add([ordered]@{
            platform = $platform
            reason   = 'transform_failed'
            message  = $_.Exception.Message
        }) | Out-Null
        Write-Warning "[fail] $platform : $($_.Exception.Message)"
    }
}

$errors = $errors_list.ToArray()
$manifest.errors = $errors

$manifestDir = Join-Path $OutputDir "$today/$TaskId-$TopicId"
New-Item -ItemType Directory -Force -Path $manifestDir | Out-Null
$manifestPath = Join-Path $manifestDir 'export_manifest.json'
$manifest | ConvertTo-Json -Depth 8 | Set-Content -Path $manifestPath -Encoding utf8

if ($errors.Count -gt 0) {
    $errorPath = Join-Path $manifestDir 'export_errors.json'
    $errors | ConvertTo-Json -Depth 5 | Set-Content -Path $errorPath -Encoding utf8
}

Write-Host ''
Write-Host "manifest: $manifestPath"
if ($errors.Count -gt 0) {
    Write-Host "errors:   $errorPath"
    exit 1
}
exit 0