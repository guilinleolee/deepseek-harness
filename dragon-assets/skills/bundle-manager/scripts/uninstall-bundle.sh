#!/usr/bin/env bash
#===============================================================================
# uninstall-bundle.sh — 天龙引擎 Addon Bundle 卸载脚本
#===============================================================================
# 功能：归档 Bundle 文件，清理索引，更新依赖
# 用法：./uninstall-bundle.sh <bundle-id> [--reason REASON] [--archive] [--force]
#===============================================================================

set -euo pipefail

BUNDLES_DIR="${HOME}/.claude/bundles"
INDEX_FILE="${HOME}/.claude/bundles/index.json"
SKILLS_DIR="${HOME}/.claude/skills"
AGENTS_DIR="${HOME}/.claude/agents"
ARCHIVE_DIR="${HOME}/.claude/bundles/archive"
REASON="manual"
DO_ARCHIVE=true
FORCE=false

# --- 参数解析 ---
if [[ $# -lt 1 ]]; then
  echo "用法: $0 <bundle-id> [--reason REASON] [--no-archive] [--force]" >&2
  echo "示例: $0 wiseflow-crew-lifecycle --reason 'upgraded'" >&2
  echo "       $0 my-bundle --no-archive" >&2
  exit 1
fi

BUNDLE_ID="$1"
shift

while [[ $# -gt 0 ]]; do
  case "$1" in
    --reason) REASON="$2"; shift 2 ;;
    --no-archive) DO_ARCHIVE=false; shift ;;
    --force) FORCE=true ;;
    *) echo "未知参数: $1"; exit 1 ;;
  esac
done

# --- Bundle ID 格式验证 ---
validate_bundle_id() {
  local id="$1"
  if [[ ! "$id" =~ ^[a-zA-Z0-9_-]+$ ]]; then
    echo "错误: Bundle ID 格式无效: $id" >&2
    echo "期望格式: author-bundle-name (字母、数字、连字符)" >&2
    return 1
  fi
  return 0
}

# --- 核心 Bundle 保护 ---
check_core_protection() {
  local id="$1"

  if [[ "$id" == system* ]]; then
    echo "错误: 系统 Bundle 不可卸载: $id" >&2
    echo "系统 Bundle (system 前缀) 是系统内置组件，受安全规则保护。" >&2
    return 1
  fi
  return 0
}

# --- 检查是否存在 ---
check_exists() {
  local id="$1"
  local bundle_dir="${SKILLS_DIR}/${id}"

  if [[ ! -d "$bundle_dir" ]]; then
    echo "错误: Bundle 不存在: $id" >&2
    return 1
  fi

  echo "$bundle_dir"
}

# --- 从索引获取信息 ---
get_bundle_info() {
  local id="$1"

  if [[ -f "$INDEX_FILE" ]]; then
    jq -r --arg id "$id" '.bundles[] | select(.id == $id)' "$INDEX_FILE" 2>/dev/null || echo "{}"
  else
    echo "{}"
  fi
}

# --- 查找依赖此 Bundle 的其他 Bundle ---
find_dependents() {
  local bundle_id="$1"
  local dependents=()

  if [[ -f "$INDEX_FILE" ]]; then
    while IFS= read -r line; do
      [[ -z "$line" ]] && continue
      local dep_check
      dep_check=$(jq -r --argjson bid "$bundle_id" 'select(.dependencies // [] | contains([$bid])) | .id' <<< "$line" 2>/dev/null)
      [[ -n "$dep_check" ]] && dependents+=( "$dep_check" )
    done < <(jq -c '.bundles[]' "$INDEX_FILE" 2>/dev/null || echo "")
  fi

  printf '%s\n' "${dependents[@]:-}"
}

# --- 确认操作 ---
confirm_uninstall() {
  local id="$1"
  local bundle_dir="$2"
  local info="$3"
  local dependents_count="$4"

  local name version
  name=$(jq -r '.name // empty' <<< "$info" 2>/dev/null || echo "$id")
  version=$(jq -r '.version // empty' <<< "$info" 2>/dev/null || echo "unknown")

  echo ""
  echo "⚠️  确认卸载 Bundle: $id"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "   Bundle 名称: $name"
  echo "   Bundle 版本: $version"
  echo "   安装路径:   $bundle_dir"
  echo "   卸载原因:   $REASON"
  echo "   依赖清理:   $dependents_count 个 Bundle 可能受影响"
  echo "   归档操作:   $([ "$DO_ARCHIVE" == "true" ] && echo "是" || echo "否")"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

  if [[ "$FORCE" == "false" ]]; then
    read -rp "确认卸载? (y/n): " confirm
    if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
      echo "操作已取消。"
      exit 0
    fi
  else
    echo "⚠️  --force 模式，跳过确认。"
  fi
}

# --- 归档 Bundle ---
archive_bundle() {
  local id="$1"
  local bundle_dir="$2"
  local timestamp
  timestamp=$(date +%Y%m%d%H%M%S)
  local archive_file="${ARCHIVE_DIR}/${id}-${timestamp}.tar.gz"

  mkdir -p "$ARCHIVE_DIR"

  if [[ -d "$bundle_dir" ]]; then
    tar -czf "$archive_file" -C "$(dirname "$bundle_dir")" "$(basename "$bundle_dir")" 2>/dev/null

    # 添加归档元数据
    local info
    info=$(get_bundle_info "$id")
    local name version author
    name=$(jq -r '.name // empty' <<< "$info" 2>/dev/null || echo "$id")
    version=$(jq -r '.version // empty' <<< "$info" 2>/dev/null || echo "unknown")
    author=$(jq -r '.author // empty' <<< "$info" 2>/dev/null || echo "unknown")

    local meta_file="${ARCHIVE_DIR}/${id}-${timestamp}.meta.json"
    cat > "$meta_file" <<EOF
{
  "original_id": "${id}",
  "archived_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "archive_file": "$(basename "$archive_file")",
  "reason": "${REASON}",
  "name": "${name}",
  "version": "${version}",
  "author": "${author}",
  "restored_at": null,
  "status": "archived"
}
EOF

    echo "✅ 已归档: $archive_file"
    echo "$archive_file"
  fi
}

# --- 删除 Bundle 目录 ---
remove_bundle() {
  local id="$1"
  local bundle_dir="$2"

  rm -rf "$bundle_dir"
  echo "✅ 已删除 Bundle 目录: $bundle_dir"
}

# --- 移除 Agents ---
remove_agents() {
  local bundle_id="$1"
  local bundle_dir="${SKILLS_DIR}/${bundle_id}"
  local removed=0

  if [[ -d "$bundle_dir/agents" ]]; then
    for agent_file in "$bundle_dir/agents"/*.md; do
      [[ -f "$agent_file" ]] || continue
      local agent_basename
      agent_basename=$(basename "$agent_file")
      if [[ -f "${AGENTS_DIR}/${agent_basename}" ]]; then
        rm -f "${AGENTS_DIR}/${agent_basename}"
        echo "   ✅ 移除 Agent: $agent_basename"
        ((removed++))
      fi
    done
    echo "   共移除 $removed 个 Agent 配置"
  fi
}

# --- 执行卸载脚本 ---
run_teardown() {
  local bundle_dir="$1"

  if [[ -f "$bundle_dir/teardown.sh" ]]; then
    echo "🔧 执行卸载脚本: $bundle_dir/teardown.sh"
    pushd "$bundle_dir" >/dev/null 2>&1
    bash teardown.sh 2>/dev/null || true
    popd >/dev/null 2>&1
    echo "✅ 卸载脚本执行完成"
  fi
}

# --- 更新 Bundle 索引 ---
update_index() {
  local id="$1"

  if [[ -f "$INDEX_FILE" ]]; then
    local tmp
    tmp=$(mktemp)

    jq --arg id "$id" \
       --arg reason "$REASON" \
       --argjson archived_at "$(date -u +%s)" \
       '{
         version: .version,
         updated: (now | todate),
         bundles: .bundles | map(select(.id != $id)),
         archives: (.archives // []) + [{
           id: $id,
           archived_at: $archived_at,
           reason: $reason,
           status: "archived"
         }]
       }' \
       "$INDEX_FILE" > "$tmp" && mv "$tmp" "$INDEX_FILE"

    echo "✅ Bundle 索引已更新: $INDEX_FILE"
  fi
}

# --- 清理依赖关系 ---
clean_dependencies() {
  local id="$1"

  if [[ -f "$INDEX_FILE" ]]; then
    local tmp
    tmp=$(mktemp)

    jq --arg id "$id" \
       '.bundles |= map(
         if (.dependencies // []) | contains([$id]) then
           .dependencies = (.dependencies // []) | map(if . == $id then null else . end) | map(select(. != null))
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
  local log_file="${HOME}/.claude/logs/bundle-lifecycle.log"
  mkdir -p "$(dirname "$log_file")"

  echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] ${action}: bundle_id=${id} reason=${REASON} user=${USER:-unknown}" >> "$log_file"
}

# --- 主流程 ---
main() {
  echo ""
  echo "⚙️  Bundle 卸载流程启动..."
  echo ""

  # 1. 验证 Bundle ID
  echo "📋 Step 1: 验证 Bundle ID"
  if ! validate_bundle_id "$BUNDLE_ID"; then
    exit 1
  fi
  echo "✅ Bundle ID 格式正确: $BUNDLE_ID"

  # 2. 核心保护检查
  echo ""
  echo "📋 Step 2: 安全规则检查"
  if ! check_core_protection "$BUNDLE_ID"; then
    exit 1
  fi
  echo "✅ 安全规则检查通过"

  # 3. 检查是否存在
  echo ""
  echo "📋 Step 3: 检查 Bundle 状态"
  local bundle_dir
  bundle_dir=$(check_exists "$BUNDLE_ID")
  echo "✅ Bundle 存在: $bundle_dir"

  # 4. 获取 Bundle 信息
  echo ""
  echo "📋 Step 4: 获取 Bundle 信息"
  local bundle_info
  bundle_info=$(get_bundle_info "$BUNDLE_ID")

  # 5. 查找依赖
  echo ""
  echo "📋 Step 5: 分析影响范围"
  local dependents
  mapfile -t dependents < <(find_dependents "$BUNDLE_ID")
  local dependents_count=${#dependents[@]}
  echo "   受影响 Bundle: $dependents_count 个"
  if [[ $dependents_count -gt 0 ]]; then
    echo "   依赖列表: ${dependents[*]}"
  fi

  # 6. 确认操作
  echo ""
  confirm_uninstall "$BUNDLE_ID" "$bundle_dir" "$bundle_info" "$dependents_count"

  # 7. 执行卸载脚本
  local archive_file=""
  if [[ "$DO_ARCHIVE" == "true" ]]; then
    echo ""
    echo "📋 Step 7: 执行卸载脚本"
    run_teardown "$bundle_dir"
  fi

  # 8. 归档
  echo ""
  echo "📋 Step 8: 归档 Bundle"
  if [[ "$DO_ARCHIVE" == "true" ]]; then
    archive_file=$(archive_bundle "$BUNDLE_ID" "$bundle_dir")
  fi

  # 9. 移除 Agents
  echo ""
  echo "📋 Step 9: 清理 Agent 配置"
  remove_agents "$BUNDLE_ID"

  # 10. 删除 Bundle 目录
  echo ""
  echo "📋 Step 10: 清理 Bundle 目录"
  remove_bundle "$BUNDLE_ID" "$bundle_dir"

  # 11. 清理依赖关系
  echo ""
  echo "📋 Step 11: 清理依赖关系"
  clean_dependencies "$BUNDLE_ID"

  # 12. 更新索引
  echo ""
  echo "📋 Step 12: 更新 Bundle 索引"
  update_index "$BUNDLE_ID"

  # 13. 审计日志
  log_action "$BUNDLE_ID" "uninstall"

  echo ""
  echo "✅ 卸载完成!"
  echo ""
  echo "📊 摘要:"
  echo "   Bundle ID:    $BUNDLE_ID"
  echo "   卸载原因:    $REASON"
  echo "   归档文件:    ${archive_file:-未归档}"
  echo "   依赖清理:    ${dependents_count} 个"
  echo ""
  echo "💡 提示: 已归档的 Bundle 可在 90 天内通过恢复脚本还原。"
  echo ""
}

main
