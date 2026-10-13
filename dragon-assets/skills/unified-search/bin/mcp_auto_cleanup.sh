#!/bin/bash
# ============================================================================
# MCP 自动清理脚本
# 自动停止空闲的 MCP 服务器，释放资源
# ============================================================================

set -euo pipefail

# 获取脚本目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 配置
MCP_CACHE_DIR="${MCP_CACHE_DIR:-$HOME/.cache/mcp-servers}"
MCP_IDLE_TIMEOUT="${MCP_IDLE_TIMEOUT:-30}"  # 默认 30 分钟

# 日志函数
log_info() {
  echo "ℹ️  $(date '+%Y-%m-%d %H:%M:%S') - $*" >&2
}

log_success() {
  echo "✅ $(date '+%Y-%m-%d %H:%M:%S') - $*" >&2
}

log_warning() {
  echo "⚠️  $(date '+%Y-%m-%d %H:%M:%S') - $*" >&2
}

# MCP 服务器空闲超时（分钟）- 可覆盖默认值
declare -A MCP_IDLE_TIMEOUT=(
  ["brave-search"]=30
  ["exa"]=20
  ["relace"]=15
  ["github"]=25
  ["elasticsearch"]=30
  ["filesystem"]=20
)

# 检查 MCP 是否运行
is_mcp_running() {
  local mcp_name=$1

  if [ ! -f "$MCP_CACHE_DIR/pids.json" ]; then
    return 1
  fi

  local pid=$(jq -r ".\"$mcp_name\"" "$MCP_CACHE_DIR/pids.json" 2>/dev/null)

  if [ -z "$pid" ] || [ "$pid" = "null" ]; then
    return 1
  fi

  # 检查进程是否存在
  if kill -0 "$pid" 2>/dev/null; then
    return 0
  fi

  # 进程不存在，清理 PID 文件
  jq "del(.\"$mcp_name\")" "$MCP_CACHE_DIR/pids.json" > "$MCP_CACHE_DIR/pids.json.tmp" 2>/dev/null
  mv "$MCP_CACHE_DIR/pids.json.tmp" "$MCP_CACHE_DIR/pids.json" 2>/dev/null || true

  return 1
}

# 停止 MCP 服务器
stop_mcp() {
  local mcp_name=$1

  if ! is_mcp_running "$mcp_name"; then
    return 0
  fi

  local pid=$(jq -r ".\"$mcp_name\"" "$MCP_CACHE_DIR/pids.json" 2>/dev/null)

  log_info "正在停止 $mcp_name (PID: $pid)..."

  # 尝试优雅停止
  kill "$pid" 2>/dev/null || true

  # 等待进程结束
  local max_wait=5
  local waited=0

  while [ $waited -lt $max_wait ]; do
    if ! kill -0 "$pid" 2>/dev/null; then
      break
    fi
    sleep 1
    waited=$((waited + 1))
  done

  # 如果还在运行，强制终止
  if kill -0 "$pid" 2>/dev/null; then
    log_warning "$mcp_name 未响应，强制终止..."
    kill -9 "$pid" 2>/dev/null || true
  fi

  # 清理
  jq "del(.\"$mcp_name\")" "$MCP_CACHE_DIR/pids.json" > "$MCP_CACHE_DIR/pids.json.tmp" 2>/dev/null
  mv "$MCP_CACHE_DIR/pids.json.tmp" "$MCP_CACHE_DIR/pids.json" 2>/dev/null || true
  rm -f "$MCP_CACHE_DIR/$mcp_name.log"

  log_success "$mcp_name 已停止"
}

# 获取 MCP 最后活动时间
get_mcp_last_activity() {
  local mcp_name=$1
  local log_file="$MCP_CACHE_DIR/$mcp_name.log"

  if [ ! -f "$log_file" ]; then
    echo "0"
    return
  fi

  # 获取日志文件最后修改时间
  stat -c %Y "$log_file" 2>/dev/null || stat -f %m "$log_file" 2>/dev/null || echo "0"
}

# 清理空闲的 MCP 服务器
cleanup_idle_mcp() {
  local now=$(date +%s)
  local cleaned=false
  local cleaned_count=0

  log_info "开始清理空闲的 MCP 服务器..."

  for mcp_name in brave-search exa relace github elasticsearch filesystem; do
    if ! is_mcp_running "$mcp_name"; then
      continue
    fi

    local last_activity=$(get_mcp_last_activity "$mcp_name")

    if [ "$last_activity" -eq 0 ]; then
      continue
    fi

    local idle_seconds=$((now - last_activity))
    local idle_minutes=$((idle_seconds / 60))
    local timeout=${MCP_IDLE_TIMEOUT[$mcp_name]:-30}

    if [ "$idle_minutes" -gt "$timeout" ]; then
      log_info "$mcp_name 空闲超过 $idle_minutes 分钟（阈值: $timeout 分钟），正在停止..."
      stop_mcp "$mcp_name"
      cleaned=true
      cleaned_count=$((cleaned_count + 1))
    fi
  done

  if [ "$cleaned" = false ]; then
    log_info "没有需要清理的 MCP 服务器"
  else
    log_success "已清理 $cleaned_count 个空闲的 MCP 服务器"
  fi
}

# 显示清理统计
show_cleanup_stats() {
  local now=$(date +%s)

  echo ""
  echo "MCP 服务器活动状态:"
  echo "===================="
  echo ""

  for mcp_name in brave-search exa relace github elasticsearch filesystem; do
    if ! is_mcp_running "$mcp_name"; then
      continue
    fi

    local last_activity=$(get_mcp_last_activity "$mcp_name")

    if [ "$last_activity" -eq 0 ]; then
      echo "  ⭕ $mcp_name: 无活动记录"
      continue
    fi

    local idle_seconds=$((now - last_activity))
    local idle_minutes=$((idle_seconds / 60))
    local timeout=${MCP_IDLE_TIMEOUT[$mcp_name]:-30}

    if [ "$idle_minutes" -gt "$timeout" ]; then
      echo "  🟡 $mcp_name: 空闲 $idle_minutes 分钟（建议清理）"
    else
      echo "  🟢 $mcp_name: 活跃中（空闲 $idle_minutes 分钟）"
    fi
  done

  echo ""
}

# 主函数
main() {
  local action=${1:-cleanup}

  case "$action" in
    cleanup)
      cleanup_idle_mcp
      ;;

    stats)
      show_cleanup_stats
      ;;

    dry-run)
      log_info "模拟运行（不会实际停止 MCP）"
      show_cleanup_stats
      ;;

    help|--help|-h)
      cat << EOF
MCP 自动清理脚本

用法: $(basename "$0") <command>

命令:
  cleanup    清理空闲的 MCP 服务器（默认）
  stats      显示所有 MCP 服务器的活动状态
  dry-run    模拟运行，显示哪些 MCP 会被清理

环境变量:
  MCP_CACHE_DIR      MCP 缓存目录（默认: ~/.cache/mcp-servers）
  MCP_IDLE_TIMEOUT   默认空闲超时（分钟，默认: 30）

示例:
  # 清理空闲 MCP
  $(basename "$0") cleanup

  # 查看状态
  $(basename "$0") stats

  # 模拟运行
  $(basename "$0") dry-run

集成到 cron:
  # 每 10 分钟清理一次
  */10 * * * * /path/to/mcp_auto_cleanup.sh cleanup

  # 每小时清理一次
  0 * * * * /path/to/mcp_auto_cleanup.sh cleanup

EOF
      ;;

    *)
      log_error "未知命令: $action"
      echo ""
      echo "用法: $(basename "$0") {cleanup|stats|dry-run|help}"
      exit 1
      ;;
  esac
}

# 运行主函数
main "$@"
