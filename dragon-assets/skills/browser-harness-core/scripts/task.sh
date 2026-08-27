#!/usr/bin/env bash
# task.sh - Multi-step task execution
# Usage:
#   bash scripts/task.sh execute --session <id> --steps '[...]'
#   bash scripts/task.sh execute-file --session <id> --file ./tasks/flow.yaml
#   bash scripts/task.sh execute-file --session <id> --file ./tasks/flow.yaml --retry

set -e

CDP_HOST="${CDP_HOST:-localhost}"
CDP_PORT="${CDP_PORT:-9222}"
SESSION_DIR="${BROWSER_SESSION_DIR:-$HOME/.claude/browser-harness/sessions}"

show_usage() {
    cat << EOF
Usage: bash scripts/task.sh <command> [options]

Commands:
  execute        执行任务序列 (JSON 格式)
  execute-file  从文件执行任务 (YAML/JSON)

Examples:
  # 执行 JSON 步骤
  bash scripts/task.sh execute --session <id> \\
    --steps '[{"action":"navigate","url":"https://example.com"}]'

  # 从文件执行
  bash scripts/task.sh execute-file --session <id> --file ./tasks/login.yaml

  # 带检查点的重试
  bash scripts/task.sh execute-file --session <id> --file ./tasks/flow.yaml \\
    --retry --checkpoint ./checkpoints/flow.cpt
EOF
}

# Get CDP target for session
get_target() {
    local session_id="$1"
    local session_file="$SESSION_DIR/$session_id.json"

    if [ ! -f "$session_file" ]; then
        echo "❌ 会话不存在: $session_id" >&2
        return 1
    fi

    # Update lastActive
    if command -v jq &> /dev/null; then
        local updated=$(jq '.lastActive = "'$(date -Iseconds 2>/dev/null || date +%Y-%m-%dT%H:%M:%S)'"' "$session_file")
        echo "$updated" > "$session_file"
    fi

    # Get or create target
    local target_id=$(command -v jq &> /dev/null && jq -r '.targetId // empty' "$session_file" 2>/dev/null)

    if [ -z "$target_id" ] || [ "$target_id" = "null" ]; then
        # Create new tab
        local new_target=$(curl -s "http://$CDP_HOST:$CDP_PORT/new?url=about:blank" 2>/dev/null)
        target_id=$(echo "$new_target" | command -v jq &> /dev/null && jq -r '.targetId // empty' <<< "$new_target" 2>/dev/null)

        if [ -n "$target_id" ] && [ "$target_id" != "null" ]; then
            # Save targetId to session
            if command -v jq &> /dev/null; then
                local updated=$(jq ".targetId = \"$target_id\"" "$session_file")
                echo "$updated" > "$session_file"
            fi
        else
            echo "❌ 无法创建新标签页" >&2
            return 1
        fi
    fi

    echo "$target_id"
}

# Execute single action
execute_action() {
    local target_id="$1"
    local action="$2"

    local action_type=$(echo "$action" | command -v jq &> /dev/null && jq -r '.action' <<< "$action" 2>/dev/null || echo "")
    local selector=$(echo "$action" | command -v jq &> /dev/null && jq -r '.selector // empty' <<< "$action" 2>/dev/null)
    local url=$(echo "$action" | command -v jq &> /dev/null && jq -r '.url // empty' <<< "$action" 2>/dev/null)
    local value=$(echo "$action" | command -v jq &> /dev/null && jq -r '.value // empty' <<< "$action" 2>/dev/null)
    local wait=$(echo "$action" | command -v jq &> /dev/null && jq -r '.wait // empty' <<< "$action" 2>/dev/null)
    local output=$(echo "$action" | command -v jq &> /dev/null && jq -r '.output // empty' <<< "$action" 2>/dev/null)

    echo "   ▶️  执行: $action_type" >&2

    case "$action_type" in
        navigate)
            curl -s "$CDP_HOST:$CDP_PORT/navigate?target=$target_id&url=$(echo "$url" | sed 's/ /%20/g; s/&/%26/g')" > /dev/null
            [ "$wait" = "networkidle" ] && sleep 2
            ;;
        click)
            [ -n "$selector" ] && curl -s -X POST "$CDP_HOST:$CDP_PORT/click?target=$target_id" -d "$selector" > /dev/null
            ;;
        fill)
            local escaped_value=$(echo "$value" | sed 's/"/\\"/g' | sed "s/'/'\\\''/g")
            if [ -n "$selector" ] && [ -n "$escaped_value" ]; then
                curl -s -X POST "$CDP_HOST:$CDP_PORT/eval?target=$target_id" \
                    -d "document.querySelector('$selector').value='$escaped_value'" > /dev/null
            fi
            ;;
        screenshot)
            if [ -n "$output" ]; then
                curl -s "$CDP_HOST:$CDP_PORT/screenshot?target=$target_id&file=$output" > /dev/null
                echo "   📸 截图已保存: $output" >&2
            fi
            ;;
        scroll)
            local distance=$(echo "$action" | command -v jq &> /dev/null && jq -r '.distance // 300' <<< "$action" 2>/dev/null)
            curl -s "$CDP_HOST:$CDP_PORT/scroll?target=$target_id&y=$distance" > /dev/null
            ;;
        wait)
            local condition=$(echo "$action" | command -v jq &> /dev/null && jq -r '.condition // empty' <<< "$action" 2>/dev/null)
            local cond_value=$(echo "$action" | command -v jq &> /dev/null && jq -r '.value // empty' <<< "$action" 2>/dev/null)
            [ -n "$condition" ] && sleep 2
            ;;
        eval)
            [ -n "$value" ] && curl -s -X POST "$CDP_HOST:$CDP_PORT/eval?target=$target_id" -d "$value" > /dev/null
            ;;
        *)
            echo "   ⚠️  未知动作: $action_type" >&2
            ;;
    esac

    # Wait if specified
    case "$wait" in
        visible|stable|networkidle) sleep 1 ;;
        *) [ -n "$wait" ] && sleep "$wait" ;;
    esac
}

cmd_execute() {
    local session_id=""
    local steps="[]"
    local retry=false
    local checkpoint=""

    while [[ $# -gt 0 ]]; do
        case $1 in
            --session) session_id="$2"; shift 2 ;;
            --steps) steps="$2"; shift 2 ;;
            --retry) retry=true; shift ;;
            --checkpoint) checkpoint="$2"; shift 2 ;;
            *) shift ;;
        esac
    done

    if [ -z "$session_id" ]; then
        echo "❌ 缺少 --session 参数" >&2
        exit 1
    fi

    local target_id=$(get_target "$session_id")
    if [ -z "$target_id" ]; then
        exit 1
    fi

    echo "🚀 开始执行任务 (session: $session_id, target: $target_id)"

    local steps_count=$(echo "$steps" | command -v jq &> /dev/null && jq 'length' <<< "$steps" 2>/dev/null || echo "0")
    echo "📋 步骤数: $steps_count"

    local i=0
    local total=$(echo "$steps" | command -v jq &> /dev/null && jq 'length' <<< "$steps" 2>/dev/null || echo "0")

    if command -v jq &> /dev/null; then
        while [ "$i" -lt "$total" ]; do
            local step=$(jq ".[$i]" <<< "$steps" 2>/dev/null)
            echo "📌 步骤 $((i+1))/$total" >&2
            execute_action "$target_id" "$step"
            i=$((i+1))
        done
    fi

    echo ""
    echo "✅ 任务执行完成"
}

cmd_execute_file() {
    local session_id=""
    local file=""
    local retry=false
    local checkpoint=""

    while [[ $# -gt 0 ]]; do
        case $1 in
            --session) session_id="$2"; shift 2 ;;
            --file) file="$2"; shift 2 ;;
            --retry) retry=true; shift ;;
            --checkpoint) checkpoint="$2"; shift 2 ;;
            *) shift ;;
        esac
    done

    if [ -z "$session_id" ]; then
        echo "❌ 缺少 --session 参数" >&2
        exit 1
    fi

    if [ -z "$file" ]; then
        echo "❌ 缺少 --file 参数" >&2
        exit 1
    fi

    if [ ! -f "$file" ]; then
        echo "❌ 文件不存在: $file" >&2
        exit 1
    fi

    # Parse YAML or JSON
    local ext="${file##*.}"
    local steps="[]"

    case "$ext" in
        yaml|yml)
            # Simple YAML to JSON conversion for steps array
            # This is a basic implementation - for full YAML support, install yq
            echo "⚠️  YAML 解析需要 yq 工具" >&2
            echo "   安装: https://github.com/mikefarah/yq/" >&2
            echo "   或使用 JSON 格式" >&2
            exit 1
            ;;
        json)
            steps=$(cat "$file")
            ;;
        *)
            echo "❌ 不支持的格式: $ext (仅支持 yaml/json)" >&2
            exit 1
            ;;
    esac

    cmd_execute --session "$session_id" --steps "$steps" ${retry:+--retry} ${checkpoint:+--checkpoint "$checkpoint"}
}

# Main dispatcher
case "${1:-}" in
    execute) shift; cmd_execute "$@" ;;
    execute-file) shift; cmd_execute_file "$@" ;;
    *) show_usage ;;
esac
