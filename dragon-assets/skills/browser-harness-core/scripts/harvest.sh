#!/usr/bin/env bash
# harvest.sh - Data harvesting from web pages
# Usage:
#   bash scripts/harvest.sh --session <id> --url <url> --selector <selector> --fields '<json>' --output <file>
#   bash scripts/harvest.sh --session <id> --url <url> --selector <selector> --pagination '<json>' --output <file>

set -e

CDP_HOST="${CDP_HOST:-localhost}"
CDP_PORT="${CDP_PORT:-9222}"
SESSION_DIR="${BROWSER_SESSION_DIR:-$HOME/.claude/browser-harness/sessions}"

show_usage() {
    cat << EOF
Usage: bash scripts/harvest.sh [options]

Options:
  --session <id>        会话 ID
  --url <url>            目标 URL
  --selector <sel>       数据选择器
  --fields <json>        字段映射 JSON
  --pagination <json>    分页配置 JSON
  --output <file>        输出文件路径

Examples:
  # 采集单页数据
  bash scripts/harvest.sh --session <id> --url "https://example.com/products" \\
    --selector ".product-item" \\
    --fields '{"title":"h3","price":".price","rating":".stars"}' \\
    --output ./data/products.json

  # 采集多页数据
  bash scripts/harvest.sh --session <id> --url "https://example.com/products" \\
    --selector ".product-item" \\
    --pagination '{"next_button":".next-page","max_pages":10}' \\
    --output ./data/products-all.json
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

harvest_page() {
    local target_id="$1"
    local url="$2"
    local selector="$3"
    local fields="$4"

    # Navigate to URL
    echo "🌐 导航到: $url" >&2
    curl -s "$CDP_HOST:$CDP_PORT/navigate?target=$target_id&url=$(echo "$url" | sed 's/ /%20/g; s/&/%26/g')" > /dev/null
    sleep 2

    # Extract data using eval
    local extract_js=""
    if command -v jq &> /dev/null; then
        local fields_json="$fields"
        extract_js="(function(){
            var items = document.querySelectorAll('$selector');
            var fields = $fields_json;
            return JSON.stringify(Array.from(items).map(function(el){
                var result = {};
                Object.keys(fields).forEach(function(key){
                    var sel = fields[key];
                    var match = sel.match(/^([^@]+)(?:@(.+))?$/);
                    if(match){
                        var targetEl = el.querySelector(match[1]);
                        if(targetEl){
                            result[key] = match[2] ? targetEl.getAttribute(match[2]) : targetEl.textContent.trim();
                        }
                    }
                });
                return result;
            }));
        })()"
    else
        echo "❌ 需要 jq 来解析字段映射" >&2
        return 1
    fi

    local result=$(curl -s -X POST "$CDP_HOST:$CDP_PORT/eval?target=$target_id" -d "$extract_js" 2>/dev/null)
    echo "$result"
}

harvest_paginated() {
    local target_id="$1"
    local url="$2"
    local selector="$3"
    local fields="$4"
    local pagination="$5"
    local output="$6"

    local next_button=$(echo "$pagination" | command -v jq &> /dev/null && jq -r '.next_button // ".next"' <<< "$pagination" 2>/dev/null)
    local max_pages=$(echo "$pagination" | command -v jq &> /dev/null && jq -r '.max_pages // 10' <<< "$pagination" 2>/dev/null)

    echo "📦 开始分页采集 (最多 $max_pages 页)"

    local all_data="[]"
    local page=1

    while [ "$page" -le "$max_pages" ]; do
        echo "📄 采集第 $page/$max_pages 页..." >&2

        if [ "$page" -eq 1 ]; then
            curl -s "$CDP_HOST:$CDP_PORT/navigate?target=$target_id&url=$(echo "$url" | sed 's/ /%20/g; s/&/%26/g')" > /dev/null
        fi

        sleep 2

        local page_data=$(harvest_page "$target_id" "" "$selector" "$fields")
        if [ -n "$page_data" ] && [ "$page_data" != "null" ]; then
            if command -v jq &> /dev/null; then
                all_data=$(jq -n --argjson a "$all_data" --argjson b "$page_data" '$a + $b' 2>/dev/null)
            fi
        fi

        # Check if next button exists and click
        local has_next=$(curl -s -X POST "$CDP_HOST:$CDP_PORT/eval?target=$target_id" \
            -d "document.querySelector('$next_button') !== null" 2>/dev/null)

        if [ "$has_next" != "true" ]; then
            echo "✅ 无更多页面，停止采集" >&2
            break
        fi

        curl -s -X POST "$CDP_HOST:$CDP_PORT/click?target=$target_id" -d "$next_button" > /dev/null
        sleep 1

        page=$((page+1))
    done

    echo "$all_data"
}

# Parse arguments
session_id=""
url=""
selector=""
fields="{}"
pagination=""
output=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --session) session_id="$2"; shift 2 ;;
        --url) url="$2"; shift 2 ;;
        --selector) selector="$2"; shift 2 ;;
        --fields) fields="$2"; shift 2 ;;
        --pagination) pagination="$2"; shift 2 ;;
        --output) output="$2"; shift 2 ;;
        -h|--help) show_usage; exit 0 ;;
        *) shift ;;
    esac
done

if [ -z "$session_id" ]; then
    echo "❌ 缺少 --session 参数" >&2
    exit 1
fi

if [ -z "$selector" ]; then
    echo "❌ 缺少 --selector 参数" >&2
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

echo "🎯 开始数据采集..."
echo "   选择器: $selector"
echo "   字段: $fields"
echo "   输出: $output"

if [ -n "$pagination" ]; then
    data=$(harvest_paginated "$target_id" "$url" "$selector" "$fields" "$pagination" "$output")
else
    data=$(harvest_page "$target_id" "$url" "$selector" "$fields")
fi

if [ -n "$data" ] && [ "$data" != "null" ] && [ "$data" != "[]" ]; then
    echo "$data" > "$output"
    echo "✅ 数据已保存到: $output"

    if command -v jq &> /dev/null; then
        local count=$(echo "$data" | jq 'length' 2>/dev/null)
        echo "   采集记录数: $count"
    fi
else
    echo "⚠️  未采集到数据"
    echo "[]" > "$output"
fi
