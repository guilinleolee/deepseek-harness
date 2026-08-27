#!/usr/bin/env bash
# session.sh - Browser session management
# Usage:
#   bash scripts/session.sh create --name "session-name" [--type persistent]
#   bash scripts/session.sh list
#   bash scripts/session.sh status --id <session-id>
#   bash scripts/session.sh resume --id <session-id>
#   bash scripts/session.sh checkpoint --id <session-id> --name "checkpoint-name"
#   bash scripts/session.sh close --id <session-id>

set -e

SESSION_DIR="${BROWSER_SESSION_DIR:-$HOME/.claude/browser-harness/sessions}"
mkdir -p "$SESSION_DIR"

show_usage() {
    cat << EOF
Usage: bash scripts/session.sh <command> [options]

Commands:
  create      创建新会话
  list        列出所有会话
  status      查看会话状态
  resume      恢复会话
  checkpoint 保存检查点
  restore     恢复检查点
  close       关闭会话

Examples:
  bash scripts/session.sh create --name "research-001"
  bash scripts/session.sh list
  bash scripts/session.sh status --id abc123
  bash scripts/session.sh checkpoint --id abc123 --name "step-3-done"
EOF
}

cmd_create() {
    local name="session-$(date +%Y%m%d-%H%M%S)"
    local type="persistent"

    while [[ $# -gt 0 ]]; do
        case $1 in
            --name) name="$2"; shift 2 ;;
            --type) type="$2"; shift 2 ;;
            *) shift ;;
        esac
    done

    local id=$(uuidgen 2>/dev/null || cat /proc/sys/kernel/random/uuid 2>/dev/null || echo "s-$(date +%s)")
    local session_file="$SESSION_DIR/$id.json"

    cat > "$session_file" << EOF
{
  "id": "$id",
  "name": "$name",
  "type": "$type",
  "created": "$(date -Iseconds 2>/dev/null || date +%Y-%m-%dT%H:%M:%S)",
  "lastActive": "$(date -Iseconds 2>/dev/null || date +%Y-%m-%dT%H:%M:%S)",
  "status": "active",
  "targetId": null,
  "checkpoints": []
}
EOF

    echo "✅ 会话已创建: $id"
    echo "   名称: $name"
    echo "   类型: $type"
    echo "   文件: $session_file"
    echo ""
    echo "💡 使用 --session $id 执行任务"
}

cmd_list() {
    echo "📋 浏览器会话列表"
    echo "===================="

    if [ ! -d "$SESSION_DIR" ] || [ -z "$(ls -A "$SESSION_DIR" 2>/dev/null)" ]; then
        echo "暂无会话"
        return
    fi

    for f in "$SESSION_DIR"/*.json; do
        [ -f "$f" ] || continue
        if command -v jq &> /dev/null; then
            local name=$(jq -r '.name' "$f" 2>/dev/null || echo "未知")
            local status=$(jq -r '.status' "$f" 2>/dev/null || echo "未知")
            local last=$(jq -r '.lastActive' "$f" 2>/dev/null || echo "未知")
            local id=$(jq -r '.id' "$f" 2>/dev/null || echo "未知")
            echo "• $id"
            echo "  名称: $name | 状态: $status | 最后活动: $last"
            echo ""
        else
            echo "• $(basename "$f")"
        fi
    done
}

cmd_status() {
    local id=""

    while [[ $# -gt 0 ]]; do
        case $1 in
            --id) id="$2"; shift 2 ;;
            *) shift ;;
        esac
    done

    if [ -z "$id" ]; then
        echo "❌ 缺少 --id 参数"
        exit 1
    fi

    local session_file="$SESSION_DIR/$id.json"
    if [ ! -f "$session_file" ]; then
        echo "❌ 会话不存在: $id"
        exit 1
    fi

    if command -v jq &> /dev/null; then
        echo "📊 会话状态: $id"
        jq '.' "$session_file"
    else
        cat "$session_file"
    fi
}

cmd_checkpoint() {
    local id=""
    local checkpoint_name="checkpoint-$(date +%Y%m%d-%H%M%S)"

    while [[ $# -gt 0 ]]; do
        case $1 in
            --id) id="$2"; shift 2 ;;
            --name) checkpoint_name="$2"; shift 2 ;;
            *) shift ;;
        esac
    done

    if [ -z "$id" ]; then
        echo "❌ 缺少 --id 参数"
        exit 1
    fi

    local session_file="$SESSION_DIR/$id.json"
    if [ ! -f "$session_file" ]; then
        echo "❌ 会话不存在: $id"
        exit 1
    fi

    local cp_id="cp-$(date +%s)"
    local cp_file="$SESSION_DIR/checkpoints/$id-$cp_id.json"
    mkdir -p "$SESSION_DIR/checkpoints"

    # Copy current session state
    cp "$session_file" "$cp_file"

    # Update session checkpoints array
    if command -v jq &> /dev/null; then
        local checkpoints=$(jq -c '.checkpoints += [{"id": "'$cp_id'", "name": "'$checkpoint_name'", "created": "'$(date -Iseconds 2>/dev/null || date +%Y-%m-%dT%H:%M:%S)'"}]' "$session_file")
        echo "$checkpoints" > "$session_file"
    fi

    echo "✅ 检查点已保存: $cp_id"
    echo "   名称: $checkpoint_name"
    echo "   文件: $cp_file"
}

cmd_close() {
    local id=""

    while [[ $# -gt 0 ]]; do
        case $1 in
            --id) id="$2"; shift 2 ;;
            *) shift ;;
        esac
    done

    if [ -z "$id" ]; then
        echo "❌ 缺少 --id 参数"
        exit 1
    fi

    local session_file="$SESSION_DIR/$id.json"
    if [ ! -f "$session_file" ]; then
        echo "❌ 会话不存在: $id"
        exit 1
    fi

    # Mark as closed
    if command -v jq &> /dev/null; then
        local updated=$(jq '.status = "closed" | .closedAt = "'$(date -Iseconds 2>/dev/null || date +%Y-%m-%dT%H:%M:%S)'"' "$session_file")
        echo "$updated" > "$session_file"
    fi

    echo "✅ 会话已关闭: $id"
}

# Main dispatcher
case "${1:-}" in
    create) shift; cmd_create "$@" ;;
    list) cmd_list ;;
    status) shift; cmd_status "$@" ;;
    checkpoint) shift; cmd_checkpoint "$@" ;;
    close) shift; cmd_close "$@" ;;
    *) show_usage ;;
esac
