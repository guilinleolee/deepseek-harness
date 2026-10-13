#!/usr/bin/env bash
#===============================================================================
# install-bundle.sh — 天龙引擎 Addon Bundle 安装脚本
#===============================================================================
# 功能：从 URL/路径/市场 ID 安装 Addon Bundle
# 用法：./install-bundle.sh <source> [--name NAME] [--force]
#===============================================================================

set -euo pipefail

BUNDLES_DIR="${HOME}/.claude/bundles"
INDEX_FILE="${HOME}/.claude/bundles/index.json"
SKILLS_DIR="${HOME}/.claude/skills"
AGENTS_DIR="${HOME}/.claude/agents"
NAME=""
FORCE=false

# --- 参数解析 ---
if [[ $# -lt 1 ]]; then
  echo "用法: $0 <source> [--name NAME] [--force]" >&2
  echo "示例: $0 https://github.com/owner/bundle-name" >&2
  echo "       $0 ./local-bundle --name custom-bundle" >&2
  echo "       $0 author/bundle-name@v1.0 --force" >&2
  exit 1
fi

SOURCE="$1"
shift

while [[ $# -gt 0 ]]; do
  case "$1" in
    --name) NAME="$2"; shift 2 ;;
    --force) FORCE=true ;;
    *) echo "未知参数: $1"; exit 1 ;;
  esac
done

# --- 依赖检查 ---
check_deps() {
  local missing=()
  command -v git >/dev/null 2>&1 || missing+=(git)
  command -v jq >/dev/null 2>&1 || missing+=(jq)
  if [[ ${#missing[@]} -gt 0 ]]; then
    echo "错误: 缺少依赖 ${missing[*]}，请先安装。" >&2
    exit 1
  fi
}

# --- 推断 Bundle ID ---
infer_bundle_id() {
  local source="$1"
  local name="$2"

  if [[ -n "$name" ]]; then
    # 用户指定名称：author-bundle-name 格式
    echo "$name" | tr '[:upper:]' '[:lower:]' | tr ' ' '-'
  else
    # 从路径推断
    local basename
    basename=$(basename "$source" .git)
    basename=$(basename "$basename")
    echo "$basename" | tr '[:upper:]' '[:lower:]' | tr ' ' '-'
  fi
}

# --- 解析来源类型 ---
parse_source() {
  local source="$1"

  if [[ "$source" =~ ^https?:// ]]; then
    echo "git-url"
  elif [[ "$source" =~ ^git@ ]]; then
    echo "git-ssh"
  elif [[ "$source" =~ ^([a-zA-Z0-9_-]+)/([a-zA-Z0-9_-]+)@(.+)$ ]]; then
    echo "marketplace"
  elif [[ -d "$source" ]]; then
    echo "local"
  else
    echo "unknown"
  fi
}

# --- 检查 Bundle 是否已安装 ---
check_installed() {
  local bundle_id="$1"

  if [[ -f "$INDEX_FILE" ]]; then
    if jq -e --arg id "$bundle_id" '.bundles[] | select(.id == $id)' "$INDEX_FILE" >/dev/null 2>&1; then
      return 0  # 已安装
    fi
  fi
  return 1  # 未安装
}

# --- 验证 Bundle 结构 ---
validate_structure() {
  local bundle_dir="$1"
  local bundle_id="$2"

  if [[ ! -f "$bundle_dir/SKILL.md" ]]; then
    echo "错误: Bundle 缺少必需的 SKILL.md 文件: $bundle_dir" >&2
    return 1
  fi

  local has_agents=false
  local has_skills=false
  [[ -d "$bundle_dir/agents" && -n "$(ls -A "$bundle_dir/agents" 2>/dev/null)" ]] && has_agents=true
  [[ -d "$bundle_dir/skills" && -n "$(ls -A "$bundle_dir/skills" 2>/dev/null)" ]] && has_skills=true

  if [[ "$has_agents" == "false" && "$has_skills" == "false" ]]; then
    echo "警告: Bundle 不包含 agents/ 或 skills/ 目录" >&2
    return 1
  fi

  echo "✅ Bundle 结构验证通过"
  [[ "$has_agents" == "true" ]] && echo "   包含: agents/ (${bundle_id}/agents/)"
  [[ "$has_skills" == "true" ]] && echo "   包含: skills/ (${bundle_id}/skills/)"
}

# --- 克隆或复制 Bundle ---
fetch_bundle() {
  local source="$1"
  local source_type="$2"
  local bundle_id="$3"
  local target_dir="${SKILLS_DIR}/${bundle_id}"

  if [[ -d "$target_dir" ]]; then
    if [[ "$FORCE" == "false" ]]; then
      echo "错误: Bundle 已存在: $bundle_id" >&2
      echo "使用 --force 强制覆盖，或先执行 uninstall-bundle.sh 移除。" >&2
      return 1
    else
      echo "⚠️  Bundle 已存在，--force 模式将覆盖: $bundle_id"
      rm -rf "$target_dir"
    fi
  fi

  mkdir -p "$(dirname "$target_dir")"

  case "$source_type" in
    git-url|git-ssh)
      echo "📥 克隆 Bundle: $source"
      git clone --depth 1 "$source" "$target_dir" 2>&1
      ;;
    marketplace)
      echo "📦 从市场安装: $source (Marketplace ID 解析需市场集成)"
      # 暂时不支持，留给后续市场集成
      echo "错误: Marketplace 安装暂未实现，请使用 Git URL 或本地路径。" >&2
      return 1
      ;;
    local)
      echo "📂 复制本地 Bundle: $source"
      cp -r "$source" "$target_dir"
      ;;
    *)
      echo "错误: 未知的来源类型: $source_type" >&2
      return 1
      ;;
  esac

  echo "✅ Bundle 已下载: $target_dir"
}

# --- 安装依赖 ---
install_dependencies() {
  local bundle_dir="$1"

  if [[ -f "$bundle_dir/setup.sh" ]]; then
    echo "🔧 执行安装脚本: $bundle_dir/setup.sh"
    pushd "$bundle_dir" >/dev/null 2>&1
    bash setup.sh
    local setup_result=$?
    popd >/dev/null 2>&1
    if [[ $setup_result -eq 0 ]]; then
      echo "✅ 安装脚本执行成功"
    else
      echo "⚠️  安装脚本执行失败 (exit $setup_result)，继续安装..."
    fi
  fi

  # 递归安装子 Bundle
  if [[ -d "$bundle_dir/skills" ]]; then
    for sub_dir in "$bundle_dir/skills"/*/; do
      if [[ -f "${sub_dir}setup.sh" ]]; then
        echo "🔧 执行子模块安装脚本: ${sub_dir}setup.sh"
        pushd "$sub_dir" >/dev/null 2>&1
        bash setup.sh 2>/dev/null || true
        popd >/dev/null 2>&1
      fi
    done
  fi
}

# --- 复制到 Agents 目录 ---
install_agents() {
  local bundle_dir="$1"
  local bundle_id="$2"

  if [[ -d "$bundle_dir/agents" && -n "$(ls -A "$bundle_dir/agents" 2>/dev/null)" ]]; then
    echo "📋 安装 Agent 配置到 $AGENTS_DIR/"
    mkdir -p "$AGENTS_DIR"

    for agent_file in "$bundle_dir/agents"/*.md; do
      [[ -f "$agent_file" ]] || continue
      local agent_basename
      agent_basename=$(basename "$agent_file")
      # 避免覆盖同名 Agent
      if [[ -f "${AGENTS_DIR}/${agent_basename}" && "$FORCE" == "false" ]]; then
        echo "   ⏭️  跳过已存在的 Agent: $agent_basename"
      else
        cp "$agent_file" "${AGENTS_DIR}/${agent_basename}"
        echo "   ✅ 安装 Agent: $agent_basename"
      fi
    done
  fi
}

# --- 更新 Bundle 索引 ---
update_index() {
  local bundle_id="$1"
  local bundle_dir="$2"
  local source="$3"
  local source_type="$4"

  mkdir -p "$(dirname "$INDEX_FILE")"

  # 提取元数据
  local name version author
  name=$(jq -r '.name // empty' "$bundle_dir/SKILL.md" 2>/dev/null || echo "$bundle_id")
  version=$(jq -r '.version // empty' "$bundle_dir/SKILL.md" 2>/dev/null || echo "1.0.0")
  author=$(jq -r '.author // empty' "$bundle_dir/SKILL.md" 2>/dev/null || echo "unknown")

  # 收集包含的组件
  local agents=()
  local skills=()
  if [[ -d "$bundle_dir/agents" ]]; then
    for f in "$bundle_dir/agents"/*.md; do
      [[ -f "$f" ]] || continue
      agents+=( "$(basename "$f" .md)" )
    done
  fi
  if [[ -d "$bundle_dir/skills" ]]; then
    for d in "$bundle_dir/skills"/*/; do
      [[ -d "$d" ]] || continue
      skills+=( "$(basename "$d")" )
    done
  fi

  local agents_json skills_json
  agents_json=$(printf '%s\n' "${agents[@]}" | jq -R . | jq -s .)
  skills_json=$(printf '%s\n' "${skills[@]}" | jq -R . | jq -s .)

  if [[ -f "$INDEX_FILE" ]]; then
    # 检查是否已在索引中
    if jq -e --arg id "$bundle_id" '.bundles[] | select(.id == $id)' "$INDEX_FILE" >/dev/null 2>&1; then
      # 更新已有条目
      local tmp
      tmp=$(mktemp)
      jq --arg id "$bundle_id" \
         --arg name "$name" \
         --arg version "$version" \
         --arg author "$author" \
         --arg source "$source" \
         --arg installed_at "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
         --argjson agents "$agents_json" \
         --argjson skills "$skills_json" \
         '.bundles |= map(
           if .id == $id then
             {id: $id, name: $name, version: $version, author: $author,
              source: $source, installed_at: $installed_at,
              status: "active", components: {agents: $agents, skills: $skills},
              dependencies: (if .dependencies then .dependencies else [] end)}
           else . end
         ) | .updated = (now | todate)' \
         "$INDEX_FILE" > "$tmp" && mv "$tmp" "$INDEX_FILE"
    else
      # 添加新条目
      local tmp
      tmp=$(mktemp)
      jq --arg id "$bundle_id" \
         --arg name "$name" \
         --arg version "$version" \
         --arg author "$author" \
         --arg source "$source" \
         --arg installed_at "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
         --argjson agents "$agents_json" \
         --argjson skills "$skills_json" \
         '. += {
           bundles: [.bundles + [{
             id: $id, name: $name, version: $version, author: $author,
             source: $source, installed_at: $installed_at,
             status: "active", components: {agents: $agents, skills: $skills},
             dependencies: []
           }]]
         } | .updated = (now | todate)' \
         "$INDEX_FILE" > "$tmp" && mv "$tmp" "$INDEX_FILE"
    fi
  else
    # 创建新索引
    cat > "$INDEX_FILE" <<EOF
{
  "version": "1.0",
  "updated": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "bundles": [
    {
      "id": "${bundle_id}",
      "name": "${name}",
      "version": "${version}",
      "author": "${author}",
      "source": "${source}",
      "installed_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
      "status": "active",
      "components": {
        "agents": $(echo "$agents_json"),
        "skills": $(echo "$skills_json")
      },
      "dependencies": []
    }
  ],
  "archives": []
}
EOF
  fi

  echo "✅ Bundle 索引已更新: $INDEX_FILE"
}

# --- 审计日志 ---
log_action() {
  local bundle_id="$1"
  local action="$2"
  local log_file="${HOME}/.claude/logs/bundle-lifecycle.log"
  mkdir -p "$(dirname "$log_file")"

  echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] ${action}: bundle_id=${bundle_id} source=${SOURCE} user=${USER:-unknown}" >> "$log_file"
}

# --- 主流程 ---
main() {
  echo ""
  echo "⚙️  Bundle 安装流程启动..."
  echo ""

  # 1. 检查依赖
  echo "📋 Step 1: 检查依赖"
  check_deps
  echo "✅ 依赖检查通过"

  # 2. 解析来源
  echo ""
  echo "📋 Step 2: 解析来源"
  local source_type
  source_type=$(parse_source "$SOURCE")
  echo "   来源类型: $source_type"
  echo "   来源: $SOURCE"
  if [[ "$source_type" == "unknown" ]]; then
    echo "错误: 无法识别的来源格式: $SOURCE" >&2
    exit 1
  fi

  # 3. 推断 Bundle ID
  echo ""
  echo "📋 Step 3: 确定 Bundle ID"
  local bundle_id
  bundle_id=$(infer_bundle_id "$SOURCE" "$NAME")
  echo "   Bundle ID: $bundle_id"

  # 4. 检查是否已安装
  echo ""
  echo "📋 Step 4: 检查安装状态"
  if check_installed "$bundle_id"; then
    if [[ "$FORCE" == "false" ]]; then
      echo "错误: Bundle 已安装: $bundle_id" >&2
      echo "使用 --force 强制覆盖。" >&2
      exit 1
    else
      echo "⚠️  Bundle 已安装，--force 模式将覆盖: $bundle_id"
    fi
  else
    echo "   Bundle 未安装，继续..."
  fi

  # 5. 获取 Bundle
  echo ""
  echo "📋 Step 5: 获取 Bundle"
  local bundle_dir="${SKILLS_DIR}/${bundle_id}"
  if ! fetch_bundle "$SOURCE" "$source_type" "$bundle_id"; then
    exit 1
  fi

  # 6. 验证结构
  echo ""
  echo "📋 Step 6: 验证 Bundle 结构"
  if ! validate_structure "$bundle_dir" "$bundle_id"; then
    exit 1
  fi

  # 7. 安装依赖
  echo ""
  echo "📋 Step 7: 安装依赖"
  install_dependencies "$bundle_dir"

  # 8. 安装 Agents
  echo ""
  echo "📋 Step 8: 安装 Agent 配置"
  install_agents "$bundle_dir" "$bundle_id"

  # 9. 更新索引
  echo ""
  echo "📋 Step 9: 更新 Bundle 索引"
  update_index "$bundle_id" "$bundle_dir" "$SOURCE" "$source_type"

  # 10. 审计日志
  log_action "$bundle_id" "install"

  echo ""
  echo "✅ Bundle 安装成功!"
  echo ""
  echo "📊 摘要:"
  echo "   Bundle ID:   $bundle_id"
  echo "   安装路径:    ${SKILLS_DIR}/${bundle_id}/"
  echo "   来源:       $SOURCE"
  echo "   索引文件:   $INDEX_FILE"
  echo ""
  echo "💡 提示: 使用 list-bundles.sh 查看已安装的 Bundle。"
  echo ""
}

main
