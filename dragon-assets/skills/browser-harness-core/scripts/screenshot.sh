#!/usr/bin/env bash
# screenshot.sh - Page screenshot capture
# Usage:
#   bash scripts/screenshot.sh --session <id> --url <url> --output <file> [--full-page]
#   bash scripts/screenshot.sh --session <id> --selector <sel> --output <file>

set -e

CDP_HOST="${CDP_HOST:-localhost}"
CDP_PORT="${CDP_PORT:-9222}"
SESSION_DIR="${BROWSER_SESSION_DIR:-$HOME/.claude/browser-harness/sessions}"

show_usage() {
    cat << EOF
Usage: bash scripts/screenshot.sh [options]

Options:
  --session <id>       会话 ID
  --url <url>           目标 URL (可选)
  --selector <sel>       元素选择器 (可选，截取特定元素)
  --output <file>       输出文件路径
  --full-page           截取整页

Examples:
  # 全页面截图
  bash scripts/screenshot.sh --session <id> --url "https://example.com" \\
    --full-page --output ./screenshots/page.png

  # 指定区域截图
  bash scripts/screenshot.sh --session <id> --selector ".content-area" \\
    --output ./screenshots/content.png

  # 快速截图 (当前页面)
  bash scripts/screenshot.sh --session <id> --output ./screenshots/quick.png
EOF
}

get_target() {
    local session_id="$1"
    local session_file="$SESSION_DIR/$session_id.json"

    if [ ! -f "$session_file" ]; then
        echo "❌ 会话不存在: $session_id" >&2
        return 1
    fi

    local target_id=$(command -v jq &> /dev/null && jq -r '.targetId // empty' "$session_file" 2>/dev/null)

    if [ -z "$target_id" ] || [ "$target_id" = "null" ]; then
        echo "❌ 会话无活跃 target: $session_id" >&2
        return 1
    fi

    echo "$target_id"
}

# Parse arguments
session_id=""
url=""
selector=""
output=""
full_page=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --session) session_id="$2"; shift 2 ;;
        --url) url="$2"; shift 2 ;;
        --selector) selector="$2"; shift 2 ;;
        --output) output="$2"; shift 2 ;;
        --full-page) full_page=true; shift ;;
        -h|--help) show_usage; exit 0 ;;
        *) shift ;;
    esac
done

if [ -z "$session_id" ]; then
    echo "❌ 缺少 --session 参数" >&2
    exit 1
fi

if [ -z "$output" ]; then
    echo "❌ 缺少 --output 参数" >&2
    exit 1
fi

mkdir -p "$(dirname "$output")"

target_id=$(get_target "$session_id")
if [ -z "$target_id" ]; then
    exit 1
fi

# Navigate if URL provided
if [ -n "$url" ]; then
    echo "🌐 导航到: $url" >&2
    curl -s "$CDP_HOST:$CDP_PORT/navigate?target=$target_id&url=$(echo "$url" | sed 's/ /%20/g; s/&/%26/g')" > /dev/null
    sleep 2
fi

# Screenshot mode
if [ -n "$selector" ]; then
    echo "📸 截取元素: $selector" >&2

    # Use eval to clip specific element
    local clip_js="(function(){
        var el = document.querySelector('$selector');
        if(el){
            var rect = el.getBoundingClientRect();
            return JSON.stringify({x: rect.left, y: rect.top, width: rect.width, height: rect.height});
        }
        return null;
    })()"

    local clip=$(curl -s -X POST "$CDP_HOST:$CDP_PORT/eval?target=$target_id" -d "$clip_js" 2>/dev/null)

    if [ -n "$clip" ] && [ "$clip" != "null" ]; then
        local x=$(echo "$clip" | command -v jq &> /dev/null && jq -r '.x' <<< "$clip" 2>/dev/null || echo "0")
        local y=$(echo "$clip" | command -v jq &> /dev/null && jq -r '.y' <<< "$clip" 2>/dev/null || echo "0")
        local w=$(echo "$clip" | command -v jq &> /dev/null && jq -r '.width' <<< "$clip" 2>/dev/null || echo "800")
        local h=$(echo "$clip" | command -v jq &> /dev/null && jq -r '.height' <<< "$clip" 2>/dev/null || echo "600")

        curl -s "$CDP_HOST:$CDP_PORT/screenshot?target=$target_id&file=$output&clip=true&x=$x&y=$y&width=$w&height=$h" > /dev/null
    else
        echo "❌ 未找到元素: $selector" >&2
        exit 1
    fi
elif [ "$full_page" = "true" ]; then
    echo "📸 截取整页: $output" >&2
    curl -s "$CDP_HOST:$CDP_PORT/screenshot?target=$target_id&file=$output&fullPage=true" > /dev/null
else
    echo "📸 截取视口: $output" >&2
    curl -s "$CDP_HOST:$CDP_PORT/screenshot?target=$target_id&file=$output" > /dev/null
fi

if [ -f "$output" ]; then
    local size=$(ls -lh "$output" 2>/dev/null | awk '{print $5}')
    echo "✅ 截图已保存: $output ($size)"
else
    echo "❌ 截图失败" >&2
    exit 1
fi
