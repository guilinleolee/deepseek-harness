#!/usr/bin/env bash
#===============================================================================
# list-bundles.sh — 天龙引擎 Addon Bundle 列表查询脚本
#===============================================================================
# 功能：扫描 ~/.claude/skills/ 目录，解析 Bundle 元数据，按状态分组展示
# 用法：./list-bundles.sh [--format table|json|yaml] [--status active|archived|all]
#===============================================================================

set -euo pipefail

SKILLS_DIR="${HOME}/.claude/skills"
INDEX_FILE="${HOME}/.claude/bundles/index.json"
ARCHIVE_DIR="${HOME}/.claude/bundles/archive"
OUTPUT_FORMAT="table"
FILTER_STATUS="active"

# --- 参数解析 ---
while [[ $# -gt 0 ]]; do
  case "$1" in
    --format)
      OUTPUT_FORMAT="$2"; shift 2 ;;
    --status)
      FILTER_STATUS="$2"; shift 2 ;;
    --help|-h)
      echo "用法: $0 [--format table|json|yaml] [--status active|archived|all]"
      exit 0 ;;
    *) echo "未知参数: $1"; exit 1 ;;
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

# --- 从 SKILL.md 解析 Bundle 元数据 ---
parse_bundle() {
  local dir="$1"
  local id="$2"

  # 从 SKILL.md 提取 YAML frontmatter
  local name version author description
  name=$(awk '/^---$/ && !done { found=1; next }
             found && /^---$/ { exit }
             found && /^name:/ { sub(/^name: */,""); print; exit }
             BEGIN { FS="\n"; RS="" } { print "" }' "$dir/SKILL.md" 2>/dev/null || echo "$id")

  version=$(awk '/^---$/ && !done { found=1; next }
            found && /^---$/ { exit }
            found && /^version:/ { sub(/^version: */,""); print; exit }
            BEGIN { FS="\n"; RS="" } { print "" }' "$dir/SKILL.md" 2>/dev/null || echo "unknown")

  author=$(awk '/^---$/ && !done { found=1; next }
           found && /^---$/ { exit }
           found && /^author:/ { sub(/^author: */,""); print; exit }
           BEGIN { FS="\n"; RS="" } { print "" }' "$dir/SKILL.md" 2>/dev/null || echo "unknown")

  description=$(awk '/^---$/ && !done { found=1; next }
                found && /^---$/ { exit }
                found && /^description[:|]/ { sub(/^description: */,""); sub(/\|$/,""); print; exit }
                BEGIN { FS="\n"; RS="" } { print "" }' "$dir/SKILL.md" 2>/dev/null | head -c 100 || echo "")

  # 统计组件
  local agents_count=0 skills_count=0
  if [[ -d "$dir/agents" ]]; then
    agents_count=$(find "$dir/agents" -maxdepth 1 -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
  fi
  if [[ -d "$dir/skills" ]]; then
    skills_count=$(find "$dir/skills" -maxdepth 1 -mindepth 1 -type d 2>/dev/null | wc -l | tr -d ' ')
  fi

  # 从索引获取状态
  local status="active"
  local installed_at="unknown"
  if [[ -f "$INDEX_FILE" ]]; then
    status=$(jq -r --arg id "$id" '.bundles[] | select(.id == $id) | .status // "active"' "$INDEX_FILE" 2>/dev/null || echo "active")
    installed_at=$(jq -r --arg id "$id" '.bundles[] | select(.id == $id) | .installed_at // "unknown"' "$INDEX_FILE" 2>/dev/null || echo "unknown")
  fi

  echo "${id}|${name}|${version}|${author}|${status}|${installed_at}|${agents_count}|${skills_count}"
}

# --- 构建 Bundle 列表 ---
build_bundle_list() {
  local tmp_json
  tmp_json=$(mktemp)
  echo '[]' > "$tmp_json"
  local count=0

  # 扫描 skills/ 目录下的子目录
  if [[ -d "$SKILLS_DIR" ]]; then
    for dir in "$SKILLS_DIR"/*/; do
      [[ -d "$dir" ]] || continue
      [[ -f "${dir}SKILL.md" ]] || continue

      local id
      id=$(basename "$dir")
      [[ "$id" == "bundle-manager" ]] && continue  # 跳过自身

      local parsed
      parsed=$(parse_bundle "$dir" "$id")
      IFS='|' read -r bid bname bversion bauthor bstatus binstalled_at bagents_count bskills_count <<< "$parsed"

      # 过滤状态
      if [[ "$FILTER_STATUS" != "all" && "$bstatus" != "$FILTER_STATUS" ]]; then
        continue
      fi

      local entry
      entry=$(jq -n \
        --arg id "$bid" \
        --arg name "$bname" \
        --arg version "$bversion" \
        --arg author "$bauthor" \
        --arg status "$bstatus" \
        --arg installed_at "$binstalled_at" \
        --argjson agents_count "$bagents_count" \
        --argjson skills_count "$bskills_count" \
        --arg dir "$dir" \
        '{id: $id, name: $name, version: $version, author: $author,
          status: $status, installed_at: $installed_at,
          agents_count: $agents_count, skills_count: $skills_count, dir: $dir}')

      local tmp
      tmp=$(mktemp)
      jq -s ".[0] + [$entry]" "$tmp_json" > "$tmp" && mv "$tmp" "$tmp_json"
      ((count++))
    done
  fi

  # 添加已归档的 Bundle
  if [[ "$FILTER_STATUS" == "archived" || "$FILTER_STATUS" == "all" ]] && [[ -f "$INDEX_FILE" ]]; then
    while IFS= read -r meta_file; do
      [[ -f "$meta_file" ]] || continue
      [[ "$meta_file" == *.meta.json ]] || continue

      local bid bname bversion bauthor
      bid=$(jq -r '.original_id // empty' "$meta_file" 2>/dev/null || echo "")
      [[ -z "$bid" ]] && continue

      bname=$(jq -r '.name // empty' "$meta_file" 2>/dev/null || echo "$bid")
      bversion=$(jq -r '.version // empty' "$meta_file" 2>/dev/null || echo "unknown")
      bauthor=$(jq -r '.author // empty' "$meta_file" 2>/dev/null || echo "unknown")

      local archived_at reason archive_file
      archived_at=$(jq -r '.archived_at // empty' "$meta_file" 2>/dev/null || echo "unknown")
      reason=$(jq -r '.reason // empty' "$meta_file" 2>/dev/null || echo "unknown")
      archive_file=$(jq -r '.archive_file // empty' "$meta_file" 2>/dev/null || echo "unknown")

      local entry
      entry=$(jq -n \
        --arg id "$bid" \
        --arg name "$bname" \
        --arg version "$bversion" \
        --arg author "$bauthor" \
        --arg status "archived" \
        --arg archived_at "$archived_at" \
        --arg reason "$reason" \
        --arg archive_file "$archive_file" \
        '{id: $id, name: $name, version: $version, author: $bauthor,
          status: $status, archived_at: $archived_at,
          reason: $reason, archive_file: $archive_file,
          agents_count: 0, skills_count: 0, dir: ""}')

      local tmp
      tmp=$(mktemp)
      jq -s ".[0] + [$entry]" "$tmp_json" > "$tmp" && mv "$tmp" "$tmp_json"
      ((count++))
    done < <(find "$ARCHIVE_DIR" -maxdepth 1 -name "*.meta.json" 2>/dev/null)
  fi

  cat "$tmp_json"
  rm -f "$tmp_json"
  echo "$count"
}

# --- 表格输出 ---
output_table() {
  local count
  local data
  data=$(build_bundle_list)
  count=$(tail -n1 <<< "$data" | grep -oE '[0-9]+$')
  data=$(sed '$d' <<< "$data")

  echo ""
  echo "┌─────────────────────────────────────────────────────────────────────┐"
  echo "│              天龙引擎 Addon Bundle 全景                               │"
  echo "├─────────────────────────────────────────────────────────────────────┤"

  local active_count archived_count
  active_count=$(echo "$data" | jq '[.[] | select(.status == "active")] | length' 2>/dev/null || echo 0)
  archived_count=$(echo "$data" | jq '[.[] | select(.status == "archived")] | length' 2>/dev/null || echo 0)

  # 活跃 Bundle
  if [[ "$FILTER_STATUS" != "archived" ]]; then
    echo "│ installed ($active_count)                                              │"
    echo "├─────────────────────────────────────────────────────────────────────┤"
    echo "$data" | jq -r 'select(.status == "active") | "│ \(.id) │ v\(.version) │ \(.status) │ \(.agents_count) agents / \(.skills_count) skills │"' 2>/dev/null || echo "│ (无活跃 Bundle)                                                    │"
  fi

  # 已归档 Bundle
  if [[ "$FILTER_STATUS" != "active" ]]; then
    if [[ "$FILTER_STATUS" != "archived" ]]; then
      echo "├─────────────────────────────────────────────────────────────────────┤"
    fi
    echo "│ archived ($archived_count)                                            │"
    echo "├─────────────────────────────────────────────────────────────────────┤"
    echo "$data" | jq -r 'select(.status == "archived") | "│ \(.id) │ v\(.version) │ archived │ reason: \(.reason) │"' 2>/dev/null || echo "│ (无已归档 Bundle)                                                   │"
  fi

  echo "├─────────────────────────────────────────────────────────────────────┤"
  echo "│ 总计: ${count} 个 Bundle │ 活跃: ${active_count} │ 已归档: ${archived_count}  │"
  echo "└─────────────────────────────────────────────────────────────────────┘"
  echo ""
}

# --- JSON 输出 ---
output_json() {
  local count
  local data
  data=$(build_bundle_list)
  count=$(tail -n1 <<< "$data" | grep -oE '[0-9]+$')
  data=$(sed '$d' <<< "$data")

  jq -n \
    --argjson timestamp "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
    --argjson total "$count" \
    --argjson bundles "$data" \
    '{timestamp: $timestamp, total_bundles: $total, bundles: $bundles}'
}

# --- YAML 输出 ---
output_yaml() {
  local count
  local data
  data=$(build_bundle_list)
  count=$(tail -n1 <<< "$data" | grep -oE '[0-9]+$')
  data=$(sed '$d' <<< "$data")

  echo "timestamp: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "total_bundles: $count"
  echo "bundles:"
  echo "$data" | jq -r '.[] | "  - id: \(.id)\n    name: \(.name)\n    version: \(.version)\n    author: \(.author)\n    status: \(.status)"' 2>/dev/null
}

# --- 主流程 ---
main() {
  check_deps

  if [[ ! -d "$SKILLS_DIR" ]]; then
    echo "错误: Skills 目录不存在: $SKILLS_DIR" >&2
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
