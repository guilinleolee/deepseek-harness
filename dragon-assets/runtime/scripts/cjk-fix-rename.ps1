# cjk-fix-rename.ps1
# Auto-generated 2026-08-05 · 修正 5 个 rename 后内容名不贴切的文件

# 用法：在 dragon-engine 根目录下运行
#   powershell -ExecutionPolicy Bypass -File scripts\cjk-fix-rename.ps1

$ErrorActionPreference = "Stop"
Set-Location "C:\Users\li\.claude\projects\dragon-engine"

function ConvertFrom-HexPath {
    param([string]$hex)
    $bytes = for ($i = 0; $i -lt $hex.Length; $i += 2) {
        [Convert]::ToInt32($hex.Substring($i, 2), 16)
    }
    return [System.Text.Encoding]::UTF8.GetString($bytes)
}

# --- pair 1: commands\评审师.md -> commands\评论分析.md ---
$src = ConvertFrom-HexPath "636f6d6d616e64735ce8af84e5aea1e5b8882e6d64"
$dst = ConvertFrom-HexPath "636f6d6d616e64735ce8af84e8aebae58886e69e902e6d64"
if (Test-Path -LiteralPath $src) {
    Write-Host "[MOVE] $src -> $dst" -ForegroundColor Cyan
    if ((Get-Item -LiteralPath $src) -is [System.IO.DirectoryInfo]) {
        # 目录改名（git 不直接支持 dir rename, 先 mv 后 add）
        Move-Item -LiteralPath $src -Destination $dst
        git add -A
    } else {
        git mv $src $dst
    }
} else {
    Write-Host "[SKIP] not found: $src" -ForegroundColor Yellow
}

# --- pair 2: skills\learned-patterns\09编排调度师_ -> skills\learned-patterns\09编排协调师_ ---
$src = ConvertFrom-HexPath "736b696c6c735c6c6561726e65642d7061747465726e735c3039e7bc96e68e92e8b083e5baa6e5b8885f"
$dst = ConvertFrom-HexPath "736b696c6c735c6c6561726e65642d7061747465726e735c3039e7bc96e68e92e58d8fe8b083e5b8885f"
if (Test-Path -LiteralPath $src) {
    Write-Host "[MOVE] $src -> $dst" -ForegroundColor Cyan
    if ((Get-Item -LiteralPath $src) -is [System.IO.DirectoryInfo]) {
        # 目录改名（git 不直接支持 dir rename, 先 mv 后 add）
        Move-Item -LiteralPath $src -Destination $dst
        git add -A
    } else {
        git mv $src $dst
    }
} else {
    Write-Host "[SKIP] not found: $src" -ForegroundColor Yellow
}

# --- pair 3: skills\learned-patterns\09编排调度师_learned-patterns.md -> skills\learned-patterns\09编排协调师_learned-patterns.md ---
$src = ConvertFrom-HexPath "736b696c6c735c6c6561726e65642d7061747465726e735c3039e7bc96e68e92e8b083e5baa6e5b8885f6c6561726e65642d7061747465726e732e6d64"
$dst = ConvertFrom-HexPath "736b696c6c735c6c6561726e65642d7061747465726e735c3039e7bc96e68e92e58d8fe8b083e5b8885f6c6561726e65642d7061747465726e732e6d64"
if (Test-Path -LiteralPath $src) {
    Write-Host "[MOVE] $src -> $dst" -ForegroundColor Cyan
    if ((Get-Item -LiteralPath $src) -is [System.IO.DirectoryInfo]) {
        # 目录改名（git 不直接支持 dir rename, 先 mv 后 add）
        Move-Item -LiteralPath $src -Destination $dst
        git add -A
    } else {
        git mv $src $dst
    }
} else {
    Write-Host "[SKIP] not found: $src" -ForegroundColor Yellow
}

# --- pair 4: skills\opc-methodology\sk-conversion-loop\examples\转化归因计划模板.md -> skills\opc-methodology\sk-conversion-loop\examples\转化漏斗设计模板.md ---
$src = ConvertFrom-HexPath "736b696c6c735c6f70632d6d6574686f646f6c6f67795c736b2d636f6e76657273696f6e2d6c6f6f705c6578616d706c65735ce8bdace58c96e5bd92e59ba0e8aea1e58892e6a8a1e69dbf2e6d64"
$dst = ConvertFrom-HexPath "736b696c6c735c6f70632d6d6574686f646f6c6f67795c736b2d636f6e76657273696f6e2d6c6f6f705c6578616d706c65735ce8bdace58c96e6bc8fe69697e8aebee8aea1e6a8a1e69dbf2e6d64"
if (Test-Path -LiteralPath $src) {
    Write-Host "[MOVE] $src -> $dst" -ForegroundColor Cyan
    if ((Get-Item -LiteralPath $src) -is [System.IO.DirectoryInfo]) {
        # 目录改名（git 不直接支持 dir rename, 先 mv 后 add）
        Move-Item -LiteralPath $src -Destination $dst
        git add -A
    } else {
        git mv $src $dst
    }
} else {
    Write-Host "[SKIP] not found: $src" -ForegroundColor Yellow
}

# --- pair 5: skills\opc-methodology\sk-mvp-design\examples\MVP验证计划模板.md -> skills\opc-methodology\sk-mvp-design\examples\MVP验证设计模板.md ---
$src = ConvertFrom-HexPath "736b696c6c735c6f70632d6d6574686f646f6c6f67795c736b2d6d76702d64657369676e5c6578616d706c65735c4d5650e9aa8ce8af81e8aea1e58892e6a8a1e69dbf2e6d64"
$dst = ConvertFrom-HexPath "736b696c6c735c6f70632d6d6574686f646f6c6f67795c736b2d6d76702d64657369676e5c6578616d706c65735c4d5650e9aa8ce8af81e8aebee8aea1e6a8a1e69dbf2e6d64"
if (Test-Path -LiteralPath $src) {
    Write-Host "[MOVE] $src -> $dst" -ForegroundColor Cyan
    if ((Get-Item -LiteralPath $src) -is [System.IO.DirectoryInfo]) {
        # 目录改名（git 不直接支持 dir rename, 先 mv 后 add）
        Move-Item -LiteralPath $src -Destination $dst
        git add -A
    } else {
        git mv $src $dst
    }
} else {
    Write-Host "[SKIP] not found: $src" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "[DONE] 跑完后请 Claude 跑：" -ForegroundColor Green
Write-Host "   python scripts/build-index.py --include-library"
Write-Host "   python scripts/check-cjk-filenames.py    # expect 0"
Write-Host "   python scripts/skill-admin.py"
