<#
.SYNOPSIS
    Generate wechat / xhs / article illustrations for the Creator Workbench.

.DESCRIPTION
    Tries the Tianlong Engine `shibazi-illustrator` HTML engine first. When
    that skill is unavailable, fails silently, or produces no output, falls
    back to a built-in minimal HTML card template so the export pipeline
    never blocks on art.

    Engines (auto-selected):
        shibazi  when $env:CREATOR_WORKBENCH_SKILLS_PATH points at a working
                 install of shibazi-illustrator AND its CLI produces output.
        builtin  always-available minimal HTML card; identical layout family
                 (`kabager` / `minimal` / `dramatic`) but no Playwright PNG.

    The fallback matters: shibazi-illustrator ships with a `main()` gate that
    depends on `process.argv[1]` matching `import.meta.url`. Some `bun` /
    `npx bun` invocations on Windows break that equality, so the CLI exits
    0 without ever running `main()`. We detect "no output after success" and
    quietly switch to the builtin template.

.PARAMETER InputPath
    Article / script Markdown to illustrate.

.PARAMETER OutputDir
    Directory to receive generated HTML files. Created if missing.

.PARAMETER Template
    kabager / minimal / dramatic. Affects the fallback card style; shibazi
    passes it through.

.PARAMETER Format
    html (default) | png | both. PNG requires shibazi's Playwright pipeline;
    the builtin engine always emits html.

.PARAMETER Width
    Pixel width for the rendered card.

.PARAMETER Height
    Pixel height for the rendered card.

.PARAMETER SkillsPath
    Path to the Tianlong Engine skills root. Default:
    $env:CREATOR_WORKBENCH_SKILLS_PATH.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$InputPath,

    [Parameter(Mandatory = $true)]
    [string]$OutputDir,

    [ValidateSet('kabager', 'minimal', 'dramatic')]
    [string]$Template = 'kabager',

    [ValidateSet('html', 'png', 'both')]
    [string]$Format = 'html',

    [int]$Width = 1200,

    [int]$Height = 512,

    [string]$SkillsPath = $env:CREATOR_WORKBENCH_SKILLS_PATH
)

$ErrorActionPreference = 'Stop'

if (-not (Test-Path $InputPath)) {
    throw "input not found: $InputPath"
}
New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null

function New-BuiltinCard {
    param(
        [string]$Title,
        [string]$Subtitle,
        [string]$Style,
        [string]$OutFile,
        [int]$Width,
        [int]$Height
    )

    $bg = switch ($Style) {
        'dramatic' { '#0e0d0c'; $fg = '#f5f5f5'; $accent = '#FF6B35' }
        'minimal'  { '#ffffff'; $fg = '#1a1a1a'; $accent = '#2D5BFF' }
        default    { '#1f2937'; $fg = '#f5f5f5'; $accent = '#2D5BFF' }
    }

    $html = @"
<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>
  body { margin: 0; font-family: -apple-system, 'PingFang SC', 'Microsoft YaHei', sans-serif; }
  .card { width: ${Width}px; height: ${Height}px; background: $bg; color: $fg;
          display: flex; flex-direction: column; justify-content: center;
          padding: 48px 72px; box-sizing: border-box; position: relative; }
  .accent { position: absolute; top: 32px; left: 72px; width: 56px; height: 4px; background: $accent; }
  .title { font-size: 38px; font-weight: 700; line-height: 1.3; margin: 24px 0 16px; max-width: 80%; }
  .subtitle { font-size: 18px; opacity: 0.75; line-height: 1.6; max-width: 70%; }
  .brand { position: absolute; bottom: 32px; right: 72px; font-size: 14px; opacity: 0.6; }
</style></head>
<body>
  <div class="card">
    <div class="accent"></div>
    <div class="title">$Title</div>
    <div class="subtitle">$Subtitle</div>
    <div class="brand">Creator Workbench · $([datetime]::Now.ToString('yyyy-MM-dd'))</div>
  </div>
</body></html>
"@
    Set-Content -Path $OutFile -Value $html -Encoding utf8
}

function Get-ArticleMeta {
    param([string]$Path)
    $lines = Get-Content -Path $Path -Encoding utf8
    $title = ''
    $subtitle = ''
    foreach ($line in $lines) {
        $trimmed = $line.Trim()
        if (-not $title -and $trimmed -match '^#\s+(.+)$') {
            $title = $Matches[1]
            continue
        }
        if (-not $subtitle -and $trimmed -match '^>\s+(.+)$') {
            $subtitle = $Matches[1]
            continue
        }
        if ($title -and $subtitle) { break }
    }
    if (-not $title) { $title = [System.IO.Path]::GetFileNameWithoutExtension($Path) }
    if (-not $subtitle) { $subtitle = '由 Creator Workbench 生成' }
    return @{ Title = $title; Subtitle = $subtitle }
}

$meta = Get-ArticleMeta -Path $InputPath
$articleBase = [System.IO.Path]::GetFileNameWithoutExtension($InputPath)

# Step 1: try shibazi if configured.
$shibaziProduced = $false
if ($SkillsPath -and (Test-Path (Join-Path $SkillsPath 'shibazi-illustrator/scripts/html-export.ts'))) {
    Write-Host "[illustrate] engine=shibazi template=$Template format=$Format"
    $scriptPath = Join-Path $SkillsPath 'shibazi-illustrator/scripts/html-export.ts'
    $bun = (Get-Command bun -ErrorAction SilentlyContinue)?.Source
    $bunArgs = if ($bun) { @() } else { @('-y', 'bun') }
    $bunCmd = if ($bun) { $bun } else { 'npx' }
    $baseOut = Join-Path $OutputDir "$articleBase-poster"
    $cliArgs = @($scriptPath, $InputPath, '-t', $Template, '-f', $Format,
                 '-o', $baseOut, '-w', "$Width", '-h', "$Height")
    try {
        & $bunCmd @bunArgs @cliArgs 2>&1 | Out-Null
        if ($LASTEXITCODE -ne 0) {
            Write-Warning "[illustrate] shibazi exited $LASTEXITCODE; falling back to builtin"
        } else {
            # Did shibazi actually produce output?
            $shibaziProduced = ($null -ne (Get-ChildItem -Path $OutputDir -Filter '*.html' -ErrorAction SilentlyContinue | Select-Object -First 1))
            if (-not $shibaziProduced) {
                Write-Warning "[illustrate] shibazi returned 0 but produced no HTML; falling back to builtin"
            }
        }
    } catch {
        Write-Warning "[illustrate] shibazi invocation failed: $($_.Exception.Message)"
    }
}

# Step 2: ensure we have at least one HTML file. Fall back to the builtin card.
$existing = Get-ChildItem -Path $OutputDir -Filter '*.html' -ErrorAction SilentlyContinue
if (-not $shibaziProduced -or $existing.Count -eq 0) {
    Write-Host "[illustrate] engine=builtin template=$Template"
    New-BuiltinCard -Title $meta.Title -Subtitle $meta.Subtitle -Style $Template `
        -OutFile (Join-Path $OutputDir "$articleBase-poster.html") `
        -Width $Width -Height $Height
}

Get-ChildItem -Path $OutputDir -File | ForEach-Object {
    Write-Host "[ok] $($_.FullName)"
}