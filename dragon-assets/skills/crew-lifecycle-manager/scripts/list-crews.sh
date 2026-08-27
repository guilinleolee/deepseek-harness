#!/usr/bin/env bash
#===============================================================================
# list-crews.sh — 天龙引擎 Crew 团队列表查询脚本
#===============================================================================
# 功能：扫描 ~/.claude/agents/ 目录，解析 Agent 元数据，按域名分组展示
# 用法：./list-crews.sh [--format table|json|yaml] [--domain DOMAIN]
#===============================================================================

set -euo pipefail

AGENTS_DIR="${HOME}/.claude/agents"
INDEX_FILE="${HOME}/.claude/agents/index.json"
OUTPUT_FORMAT="table"
FILTER_DOMAIN=""

# --- 参数解析 ---
while [[ $# -gt 0 ]]; do
  case "$1" in
    --format)
      OUTPUT_FORMAT="$2"; shift 2 ;;
    --domain)
      FILTER_DOMAIN="$2"; shift 2 ;;
    --help|-h)
      echo "用法: $0 [--format table|json|yaml] [--domain DOMAIN]"
      exit 0 ;;
    *)
      echo "未知参数: $1"; exit 1 ;;
  esac
done

# --- 依赖检查 ---
check_deps() {
  local missing=()
  command -v jq >/dev/null 2>&1 || missing+=(jq)
  if [[ ${#missing[@]} -gt 0 ]]; then
    echo "错误: 缺少依赖 ${missing[*]}，请先安装。" >&2
    exit 1
  fi
}

# --- 从 YAML frontmatter 解析 Agent 元数据 ---
parse_agent() {
  local file="$1"
  local id name domain status version

  # 从文件名推断 ID（去掉 .md 后缀，取目录前缀）
  id=$(basename "$file" .md)

  # 解析 YAML frontmatter
  if [[ -f "$file" ]]; then
    # 提取 name（第一行 # 后的内容或 name 字段）
    name=$(awk '/^---$/ && !done { found=1; next }
               found && /^---$/ { exit }
               found && /^name:/ { sub(/^name: */,""); print; exit }
               found && /^#/ { sub(/^#+/,""); gsub(/^ +/,""); if(NF) print; exit }
               BEGIN { FS="\n"; RS="" } { print "" }' "$file" 2>/dev/null || echo "$id")

    # 提取 domain
    domain=$(awk '/^---$/ && !done { found=1; next }
               found && /^---$/ { exit }
               found && /^domain:/ { sub(/^domain: */,""); print; exit }' "$file" 2>/dev/null || echo "未分类")

    # 提取 status
    status=$(awk '/^---$/ && !done { found=1; next }
              found && /^---$/ { exit }
              found && /^status:/ { sub(/^status: */,""); print; exit }' "$file" 2>/dev/null || echo "active")

    # 提取 version
    version=$(awk '/^---$/ && !done { found=1; next }
              found && /^---$/ { exit }
              found && /^version:/ { sub(/^version: */,""); print; exit }' "$file" 2>/dev/null || echo "unknown")
  else
    name="$id"; domain="未分类"; status="unknown"; version="unknown"
  fi

  echo "${id}|${name}|${domain}|${status}|${version}"
}

# --- 构建 Agent 列表 ---
build_crew_list() {
  local tmp_json
  tmp_json=$(mktemp)

  echo '[]' > "$tmp_json"
  local count=0

  # 扫描所有 .md 文件（排除 README）
  while IFS= read -r -d '' file; do
    [[ "$(basename "$file")" == "README"* ]] && continue

    local parsed
    parsed=$(parse_agent "$file")
    IFS='|' read -r id name domain status version <<< "$parsed"

    # 过滤域名
    if [[ -n "$FILTER_DOMAIN" && "$domain" != *"$FILTER_DOMAIN"* ]]; then
      continue
    fi

    local entry
    entry=$(jq -n \
      --arg id "$id" \
      --arg name "$name" \
      --arg domain "$domain" \
      --arg status "$status" \
      --arg version "$version" \
      --arg file "$file" \
      '{id: $id, name: $name, domain: $domain, status: $status, version: $version, file: $file}')

    tmp=$(mktemp)
    jq -s ".[0] + [$entry]" "$tmp_json" > "$tmp" && mv "$tmp" "$tmp_json"
    ((count++))
  done < <(find "$AGENTS_DIR" -maxdepth 3 -name "*.md" -type f 2>/dev/null | sort)

  cat "$tmp_json"
  rm -f "$tmp_json"
  echo "$count"
}

# --- 表格输出 ---
output_table() {
  local count
  local data
  data=$(build_crew_list)
  count=$(tail -n1 <<< "$data" | grep -oE '[0-9]+$')
  data=$(sed '$d' <<< "$data")

  echo ""
  echo "┌─────────────────────────────────────────────────────────────┐"
  echo "│              天龙引擎 Crew 团队全景                            │"
  echo "├─────────────────────────────────────────────────────────────┤"

  if [[ -z "$FILTER_DOMAIN" ]]; then
    # 按域名分组
    local domains
    domains=$(echo "$data" | jq -r '[.[].domain] | unique | .[]' 2>/dev/null || echo "未分类")
    for d in $domains; do
      local agents_in_domain
      agents_in_domain=$(echo "$data" | jq -r --arg dom "$d" '.[] | select(.domain == $dom) | .name' 2>/dev/null | tr '\n' ', ' | sed 's/,$//')
      local cnt
      cnt=$(echo "$data" | jq --arg dom "$d" '[.[] | select(.domain == $dom)] | length' 2>/dev/null || echo 0)
      echo "│ ${d} (${cnt})                                             │"
      echo "│   ${agents_in_domain}  │"
      echo "├─────────────────────────────────────────────────────────────┤"
    done
  else
    echo "$data" | jq -r '.[] | "│ \(.id) │ \(.name) │ \(.domain) │ \(.status)"' 2>/dev/null
  fi

  echo "├─────────────────────────────────────────────────────────────┤"
  echo "│ 总计: ${count} 个 Agent                                    │"
  echo "└─────────────────────────────────────────────────────────────┘"
  echo ""
}

# --- JSON 输出 ---
output_json() {
  local count
  local data
  data=$(build_crew_list)
  count=$(tail -n1 <<< "$data" | grep -oE '[0-9]+$')
  data=$(sed '$d' <<< "$data")

  jq -n \
    --argjson timestamp "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
    --argjson total "$count" \
    --argjson agents "$data" \
    '{timestamp: $timestamp, total_agents: $total, agents: $agents}'
}

# --- YAML 输出 ---
output_yaml() {
  local count
  local data
  data=$(build_crew_list)
  count=$(tail -n1 <<< "$data" | grep -oE '[0-9]+$')
  data=$(sed '$d' <<< "$data")

  echo "timestamp: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "total_agents: $count"
  echo "agents:"
  echo "$data" | jq -r '.[] | "  - id: \(.id)\n    name: \(.name)\n    domain: \(.domain)\n    status: \(.status)\n    version: \(.version)"' 2>/dev/null
}

# --- 主流程 ---
main() {
  check_deps

  if [[ ! -d "$AGENTS_DIR" ]]; then
    echo "错误: Agent 目录不存在: $AGENTS_DIR" >&2
    exit 1
  fi

  case "$OUTPUT_FORMAT" in
    json) output_json ;;
    yaml) output_yaml ;;
    table) output_table ;;
    *)
      echo "错误: 不支持的格式: $OUTPUT_FORMAT (支持: table, json, yaml)" >&2
      exit 1 ;;
  esac
}

main
