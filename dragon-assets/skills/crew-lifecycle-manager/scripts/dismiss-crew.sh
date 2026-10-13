#!/usr/bin/env bash
#===============================================================================
# dismiss-crew.sh — 天龙引擎 Crew 成员解散脚本
#===============================================================================
# 功能：归档 Agent 配置，清理依赖，更新团队索引
# 用法：./dismiss-crew.sh <agent-id> [--reason REASON] [--archive] [--force]
#===============================================================================

set -euo pipefail

AGENTS_DIR="${HOME}/.claude/agents"
INDEX_FILE="${HOME}/.claude/agents/index.json"
ARCHIVE_DIR="${HOME}/.claude/agents/archive"
REASON="manual"
FORCE=false
DO_ARCHIVE=true

# --- 参数解析 ---
if [[ $# -lt 1 ]]; then
  echo "用法: $0 <agent-id> [--reason REASON] [--no-archive] [--force]" >&2
  echo "示例: $0 35-02 --reason 'upgraded'" >&2
  echo "       $0 17-01 --no-archive" >&2
  exit 1
fi

AGENT_ID="$1"
shift

while [[ $# -gt 0 ]]; do
  case "$1" in
    --reason)
      REASON="$2"; shift 2 ;;
    --no-archive)
      DO_ARCHIVE=false; shift ;;
    --force)
      FORCE=true ;;
    *)
      echo "未知参数: $1"; exit 1 ;;
  esac
done

# --- Agent ID 格式验证 ---
validate_agent_id() {
  local id="$1"
  if [[ ! "$id" =~ ^[0-9]{1,2}-[0-9]{1,2}$ ]]; then
    echo "错误: Agent ID 格式无效: $id" >&2
    return 1
  fi
  return 0
}

# --- 核心九部保护 ---
check_core_protection() {
  local id="$1"
  local prefix="${id%%-*}"

  if [[ "$prefix" =~ ^(00|01|02|03|04|05|06|07|08)$ ]]; then
    echo "错误: 核心九部 Agent 不可解散: $id" >&2
    echo "核心九部 (00-08) 是系统内置岗位，受安全规则保护。" >&2
    return 1
  fi
  return 0
}

# --- 检查是否存在 ---
check_exists() {
  local id="$1"
  local file="${AGENTS_DIR}/${id}.md"

  if [[ ! -f "$file" ]]; then
    echo "错误: Agent 不存在: $id" >&2
    return 1
  fi

  echo "$file"
}

# --- 查找依赖关系 ---
find_dependencies() {
  local id="$1"
  local deps=()

  # 在 index.json 中查找依赖此 Agent 的其他 Agent
  if [[ -f "$INDEX_FILE" ]]; then
    while IFS= read -r line; do
      [[ -z "$line" ]] && continue
      # 检查是否有其他 Agent 依赖此 ID
      if jq -e --argjson id "$id" '.[].depends_on // [] | contains([$id])' "$INDEX_FILE" >/dev/null 2>&1; then
        deps+=( "$(jq -r --argjson id "$id" '.agents[] | select(.depends_on // [] | contains([$id])) | .id' "$INDEX_FILE" 2>/dev/null)" )
      fi
    done < <(jq -c '.agents[]' "$INDEX_FILE" 2>/dev/null || echo "")
  fi

  printf '%s\n' "${deps[@]:-}"
}

# --- 确认操作 ---
confirm_dismissal() {
  local id="$1"
  local file="$2"
  local deps_count="$3"

  echo ""
  echo "⚠️  确认解散 Agent: $id"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "  配置文件: $file"
  echo "  解散原因: $REASON"
  echo "  依赖清理: $deps_count 个 Agent 可能受影响"
  echo "  归档操作: $([ "$DO_ARCHIVE" == "true" ] && echo "是" || echo "否")"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

  if [[ "$FORCE" == "false" ]]; then
    read -rp "确认解散? (y/n): " confirm
    if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
      echo "操作已取消。"
      exit 0
    fi
  else
    echo "⚠️  --force 模式，跳过确认。"
  fi
}

# --- 归档 Agent 文件 ---
archive_agent() {
  local id="$1"
  local file="$2"
  local timestamp
  timestamp=$(date +%Y%m%d%H%M%S)
  local archive_file="${ARCHIVE_DIR}/${id}-${timestamp}.md"

  mkdir -p "$ARCHIVE_DIR"

  if [[ -f "$file" ]]; then
    cp "$file" "$archive_file"

    # 添加归档元数据
    local meta_file="${ARCHIVE_DIR}/${id}-${timestamp}.meta.json"
    cat > "$meta_file" <<EOF
{
  "original_id": "${id}",
  "archived_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "archive_file": "$(basename "$archive_file")",
  "reason": "${REASON}",
  "restored_at": null,
  "status": "archived"
}
EOF

    echo "✅ 已归档: $archive_file"
    echo "$archive_file"
  fi
}

# --- 删除原文件 ---
remove_original() {
  local id="$1"
  local file="$2"

  rm -f "$file"
  echo "✅ 已删除原配置: $file"
}

# --- 更新团队索引 ---
update_index() {
  local id="$1"

  if [[ -f "$INDEX_FILE" ]]; then
    local tmp
    tmp=$(mktemp)

    # 从索引中移除
    jq --arg id "$id" \
       --arg reason "$REASON" \
       --argjson archived_at "$(date -u +%s)" \
       '{
         version: .version,
         updated: (now | todate),
         agents: .agents | map(select(.id != $id)),
         archived: (.archived // []) + [{
           id: $id,
           archived_at: $archived_at,
           reason: $reason,
           status: "archived"
         }]
       }' \
       "$INDEX_FILE" > "$tmp" && mv "$tmp" "$INDEX_FILE"

    echo "✅ 团队索引已更新: $INDEX_FILE"
  fi
}

# --- 清理依赖关系 ---
clean_dependencies() {
  local id="$1"

  # 更新引用此 Agent 的其他 Agent
  if [[ -f "$INDEX_FILE" ]]; then
    local tmp
    tmp=$(mktemp)

    jq --arg id "$id" \
       '.agents |= map(
         if (.depends_on // []) | contains([$id]) then
           .depends_on = (.depends_on // []) | map(if . == $id then null else . end) | map(select(. != null))
         else . end
       )' \
       "$INDEX_FILE" > "$tmp" && mv "$tmp" "$INDEX_FILE"

    echo "✅ 依赖关系已清理"
  fi
}

# --- 审计日志 ---
log_action() {
  local id="$1"
  local action="$2"
  local log_file="${HOME}/.claude/logs/crew-lifecycle.log"
  mkdir -p "$(dirname "$log_file")"

  echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] ${action}: agent_id=${id} reason=${REASON} user=${USER:-unknown}" >> "$log_file"
}

# --- 主流程 ---
main() {
  echo ""
  echo "⚙️  Crew 成员解散流程启动..."
  echo ""

  # 1. 验证 Agent ID
  echo "📋 Step 1: 验证 Agent ID"
  if ! validate_agent_id "$AGENT_ID"; then
    exit 1
  fi
  echo "✅ Agent ID 格式正确: $AGENT_ID"

  # 2. 核心九部保护检查
  echo ""
  echo "📋 Step 2: 安全规则检查"
  if ! check_core_protection "$AGENT_ID"; then
    exit 1
  fi
  echo "✅ 安全规则检查通过"

  # 3. 检查是否存在
  echo ""
  echo "📋 Step 3: 检查 Agent 状态"
  local agent_file
  agent_file=$(check_exists "$AGENT_ID")
  echo "✅ Agent 存在: $agent_file"

  # 4. 查找依赖
  echo ""
  echo "📋 Step 4: 分析影响范围"
  local deps
  mapfile -t deps < <(find_dependencies "$AGENT_ID")
  local deps_count=${#deps[@]}
  echo "   受影响依赖: $deps_count 个"
  if [[ $deps_count -gt 0 ]]; then
    echo "   依赖列表: ${deps[*]}"
  fi

  # 5. 确认操作
  echo ""
  confirm_dismissal "$AGENT_ID" "$agent_file" "$deps_count"

  # 6. 归档（原文件保留）
  local archive_file=""
  if [[ "$DO_ARCHIVE" == "true" ]]; then
    echo ""
    echo "📋 Step 5: 归档 Agent 配置"
    archive_file=$(archive_agent "$AGENT_ID" "$agent_file")
  fi

  # 7. 删除原文件
  echo ""
  echo "📋 Step 6: 清理 Agent 配置"
  remove_original "$AGENT_ID" "$agent_file"

  # 8. 清理依赖关系
  echo ""
  echo "📋 Step 7: 清理依赖关系"
  clean_dependencies "$AGENT_ID"

  # 9. 更新团队索引
  echo ""
  echo "📋 Step 8: 更新团队索引"
  update_index "$AGENT_ID"

  # 10. 审计日志
  log_action "$AGENT_ID" "dismiss"

  echo ""
  echo "✅ 解散完成!"
  echo ""
  echo "📊 摘要:"
  echo "  Agent ID:     $AGENT_ID"
  echo "  解散原因:     $REASON"
  echo "  归档文件:     ${archive_file:-未归档}"
  echo "  依赖清理:     ${deps_count} 个"
  echo ""
  echo "💡 提示: 已归档的 Agent 可在 90 天内通过恢复脚本还原。"
  echo ""
}

main
