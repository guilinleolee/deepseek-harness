#!/bin/bash
# MCP 懒加载管理器
# 动态启动和管理 MCP 服务器，减少 TOKEN 消耗
#
# 版本: 1.0.0
# 作者: 九部天龙

set -euo pipefail

# ============================================
# 配置
# ============================================

MCP_CACHE_DIR="${MCP_CACHE_DIR:-$HOME/.cache/mcp-servers}"
MCP_PID_FILE="$MCP_CACHE_DIR/pids.json"
MCP_CONFIG_FILE="$HOME/.claude/claude_desktop_config.json"

# 创建缓存目录
mkdir -p "$MCP_CACHE_DIR"

# ============================================
# MCP 服务器配置
# ============================================

# MCP 服务器启动命令
declare -A MCP_COMMANDS=(
  ["brave-search"]="npx -y @modelcontextprotocol/server-brave-search"
  ["exa"]="npx -y exa-mcp-server"
  ["relace"]="npx -y relace-mcp"
  ["github"]="npx -y @modelcontextprotocol/server-github"
  ["elasticsearch"]="npx -y elasticsearch-semantic-search-mcp-server"
  ["filesystem"]="npx -y @modelcontextprotocol/server-filesystem"
)

# MCP 服务器触发关键词（正则表达式）
declare -A MCP_TRIGGERS=(
  ["brave-search"]="web|search|news|general|新闻|搜索|通用|最新"
  ["exa"]="tech|code|programming|api|tutorial|编程|代码|技术|react|python|typescript|github|框架|开发"
  ["relace"]="explore|agentic|cloud|智能|探索|分析|架构|依赖"
  ["github"]="repo|pr|issue|仓库|github"
  ["elasticsearch"]="enterprise|large|semantic|企业|大规模"
  ["filesystem"]="file|local|文件"
)

# MCP 服务器空闲超时（分钟）
declare -A MCP_IDLE_TIMEOUT=(
  ["brave-search"]=30
  ["exa"]=20
  ["relace"]=15
  ["github"]=25
  ["elasticsearch"]=30
  ["filesystem"]=20
)

# ============================================
# 工具函数
# ============================================

# 日志函数
log_info() {
  echo "ℹ️  $*" >&2
}

log_success() {
  echo "✅ $*" >&2
}

log_warning() {
  echo "⚠️  $*" >&2
}

log_error() {
  echo "❌ $*" >&2
}

# 检查 MCP 是否运行
is_mcp_running() {
  local mcp_name=$1

  if [ ! -f "$MCP_PID_FILE" ]; then
    return 1
  fi

  local pid=$(jq -r ".\"$mcp_name\"" "$MCP_PID_FILE" 2>/dev/null)

  if [ -z "$pid" ] || [ "$pid" = "null" ]; then
    return 1
  fi

  # 检查进程是否存在
  if kill -0 "$pid" 2>/dev/null; then
    return 0
  fi

  # 进程不存在，清理 PID 文件
  jq "del(.\"$mcp_name\")" "$MCP_PID_FILE" > "$MCP_PID_FILE.tmp" 2>/dev/null
  mv "$MCP_PID_FILE.tmp" "$MCP_PID_FILE" 2>/dev/null || true

  return 1
}

# 获取 MCP 的 PID
get_mcp_pid() {
  local mcp_name=$1

  if [ ! -f "$MCP_PID_FILE" ]; then
    echo ""
    return
  fi

  jq -r ".\"$mcp_name\"" "$MCP_PID_FILE" 2>/dev/null || echo ""
}

# 更新 PID 文件
update_pid_file() {
  local mcp_name=$1
  local pid=$2

  if [ -f "$MCP_PID_FILE" ]; then
    jq ".\"$mcp_name\" = $pid" "$MCP_PID_FILE" > "$MCP_PID_FILE.tmp"
    mv "$MCP_PID_FILE.tmp" "$MCP_PID_FILE"
  else
    echo "{\"$mcp_name\": $pid}" > "$MCP_PID_FILE"
  fi
}

# 从 PID 文件中移除
remove_from_pid_file() {
  local mcp_name=$1

  if [ -f "$MCP_PID_FILE" ]; then
    jq "del(.\"$mcp_name\")" "$MCP_PID_FILE" > "$MCP_PID_FILE.tmp" 2>/dev/null
    mv "$MCP_PID_FILE.tmp" "$MCP_PID_FILE" 2>/dev/null || true
  fi
}

# ============================================
# MCP 管理函数
# ============================================

# 启动 MCP 服务器
start_mcp() {
  local mcp_name=$1
  local command=${MCP_COMMANDS[$mcp_name]:-}

  if [ -z "$command" ]; then
    log_error "未知的 MCP 服务器: $mcp_name"
    log_info "可用的 MCP 服务器:"
    for key in "${!MCP_COMMANDS[@]}"; do
      log_info "  - $key"
    done
    return 1
  fi

  # 检查是否已在运行
  if is_mcp_running "$mcp_name"; then
    local pid=$(get_mcp_pid "$mcp_name")
    log_success "$mcp_name 已在运行 (PID: $pid)"
    return 0
  fi

  log_info "正在启动 $mcp_name..."

  # 设置环境变量
  local env_vars=""
  case "$mcp_name" in
    "brave-search")
      if [ -n "${BRAVE_API_KEY:-}" ]; then
        env_vars="BRAVE_API_KEY=$BRAVE_API_KEY"
      fi
      ;;
    "exa")
      if [ -n "${EXA_API_KEY:-}" ]; then
        env_vars="EXA_API_KEY=$EXA_API_KEY"
      fi
      ;;
  esac

  # 启动 MCP 服务器（后台）
  local log_file="$MCP_CACHE_DIR/$mcp_name.log"

  if [ -n "$env_vars" ]; then
    nohup env $env_vars $command > "$log_file" 2>&1 &
  else
    nohup $command > "$log_file" 2>&1 &
  fi

  local pid=$!

  # 保存 PID
  update_pid_file "$mcp_name" "$pid"

  # 等待启动
  local max_wait=10
  local waited=0

  while [ $waited -lt $max_wait ]; do
    if is_mcp_running "$mcp_name"; then
      log_success "$mcp_name 启动成功 (PID: $pid)"
      return 0
    fi
    sleep 1
    waited=$((waited + 1))
  done

  # 启动失败
  log_error "$mcp_name 启动失败（超时）"
  log_info "查看日志: $log_file"
  remove_from_pid_file "$mcp_name"
  return 1
}

# 停止 MCP 服务器
stop_mcp() {
  local mcp_name=$1

  if ! is_mcp_running "$mcp_name"; then
    log_warning "$mcp_name 未运行"
    return 0
  fi

  local pid=$(get_mcp_pid "$mcp_name")

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
  remove_from_pid_file "$mcp_name"
  rm -f "$MCP_CACHE_DIR/$mcp_name.log"

  log_success "$mcp_name 已停止"
}

# 重启 MCP 服务器
restart_mcp() {
  local mcp_name=$1

  log_info "正在重启 $mcp_name..."
  stop_mcp "$mcp_name"
  sleep 1
  start_mcp "$mcp_name"
}

# 智能启动（基于触发词）
smart_start() {
  local query=$1

  log_info "分析查询: $query"

  for mcp_name in "${!MCP_TRIGGERS[@]}"; do
    local triggers=${MCP_TRIGGERS[$mcp_name]}

    if echo "$query" | grep -qiE "($triggers)"; then
      log_info "匹配到 MCP: $mcp_name"

      if is_mcp_running "$mcp_name"; then
        log_success "$mcp_name 已在运行"
      else
        start_mcp "$mcp_name"
      fi

      return 0
    fi
  done

  log_warning "查询不匹配任何 MCP 触发条件"
  return 1
}

# 确保 MCP 运行（用于脚本调用）
ensure_mcp() {
  local mcp_name=$1

  if is_mcp_running "$mcp_name"; then
    return 0
  fi

  # 尝试启动
  start_mcp "$mcp_name"

  # 等待启动完成
  sleep 2

  if is_mcp_running "$mcp_name"; then
    return 0
  else
    return 1
  fi
}

# 停止所有 MCP 服务器
stop_all_mcp() {
  local has_running=false

  for mcp_name in "${!MCP_COMMANDS[@]}"; do
    if is_mcp_running "$mcp_name"; then
      has_running=true
      stop_mcp "$mcp_name"
    fi
  done

  if [ "$has_running" = false ]; then
    log_info "没有运行中的 MCP 服务器"
  else
    log_success "所有 MCP 服务器已停止"
  fi
}

# 列出运行中的 MCP 服务器
list_mcp() {
  local has_running=false

  echo "运行中的 MCP 服务器:"
  echo ""

  for mcp_name in "${!MCP_COMMANDS[@]}"; do
    if is_mcp_running "$mcp_name"; then
      local pid=$(get_mcp_pid "$mcp_name")
      local memory=$(ps -p "$pid" -o rss= 2>/dev/null | awk '{print int($1/1024)"MB"}' || echo "N/A")
      echo "  ✅ $mcp_name"
      echo "     PID: $pid | 内存: $memory"
      has_running=true
    fi
  done

  if [ "$has_running" = false ]; then
    echo "  （无）"
  fi
}

# 显示所有 MCP 状态
status_mcp() {
  echo "MCP 服务器状态:"
  echo ""

  for mcp_name in "${!MCP_COMMANDS[@]}"; do
    if is_mcp_running "$mcp_name"; then
      local pid=$(get_mcp_pid "$mcp_name")
      local memory=$(ps -p "$pid" -o rss= 2>/dev/null | awk '{print int($1/1024)"MB"}' || echo "N/A")
      echo "  ✅ $mcp_name: 运行中 (PID: $pid, 内存: $memory)"
    else
      echo "  ⭕ $mcp_name: 未运行"
    fi
  done
}

# 清理空闲的 MCP 服务器
cleanup_idle_mcp() {
  local now=$(date +%s)
  local cleaned=false

  for mcp_name in "${!MCP_COMMANDS[@]}"; do
    if ! is_mcp_running "$mcp_name"; then
      continue
    fi

    local log_file="$MCP_CACHE_DIR/$mcp_name.log"

    if [ ! -f "$log_file" ]; then
      continue
    fi

    # 获取日志文件最后修改时间
    local last_modified=$(stat -c %Y "$log_file" 2>/dev/null || stat -f %m "$log_file" 2>/dev/null)
    local idle_minutes=$(( (now - last_modified) / 60 ))
    local timeout=${MCP_IDLE_TIMEOUT[$mcp_name]:-30}

    if [ "$idle_minutes" -gt "$timeout" ]; then
      log_info "$mcp_name 空闲超过 $idle_minutes 分钟，正在停止..."
      stop_mcp "$mcp_name"
      cleaned=true
    fi
  done

  if [ "$cleaned" = false ]; then
    log_info "没有需要清理的 MCP 服务器"
  fi
}

# 显示统计信息
stats_mcp() {
  echo "MCP 统计信息:"
  echo ""

  local running=0
  local total_memory=0

  for mcp_name in "${!MCP_COMMANDS[@]}"; do
    if is_mcp_running "$mcp_name"; then
      running=$((running + 1))
      local pid=$(get_mcp_pid "$mcp_name")
      local memory_kb=$(ps -p "$pid" -o rss= 2>/dev/null || echo "0")
      total_memory=$((total_memory + memory_kb))
    fi
  done

  echo "  运行中: $running / ${#MCP_COMMANDS[@]}"
  echo "  总内存: $((total_memory / 1024)) MB"
  echo "  缓存目录: $MCP_CACHE_DIR"
  echo ""
}

# ============================================
# 主命令
# ============================================

show_help() {
  cat << EOF
MCP 懒加载管理器 v1.0.0

用法: $(basename "$0") <command> [args]

命令:
  start <mcp_name>      启动指定的 MCP 服务器
  stop [mcp_name]       停止指定的 MCP 服务器（不指定则停止全部）
  restart <mcp_name>    重启指定的 MCP 服务器
  ensure <mcp_name>     确保 MCP 运行（用于脚本调用）
  smart <query>         智能启动（根据查询内容自动选择 MCP）
  list                  列出运行中的 MCP 服务器
  status                显示所有 MCP 服务器状态
  cleanup               清理空闲的 MCP 服务器
  stats                 显示统计信息

可用的 MCP 服务器:
EOF

  for mcp_name in "${!MCP_COMMANDS[@]}"; do
    local description="未知"
    case "$mcp_name" in
      "brave-search") description="Brave Search - 通用 Web 搜索" ;;
      "exa") description="Exa - 技术/代码搜索" ;;
      "relace") description="Relace - 智能代码探索" ;;
      "github") description="GitHub - 仓库搜索" ;;
      "elasticsearch") description="Elasticsearch - 企业级搜索" ;;
      "filesystem") description="Filesystem - 文件系统访问" ;;
    esac
    echo "  - $mcp_name: $description"
  done

  cat << EOF

环境变量:
  MCP_CACHE_DIR         MCP 缓存目录（默认: ~/.cache/mcp-servers）
  BRAVE_API_KEY         Brave Search API 密钥
  EXA_API_KEY           Exa API 密钥

示例:
  # 启动 Exa MCP
  $(basename "$0") start exa

  # 智能启动（基于查询）
  $(basename "$0") smart "React 教程"

  # 查看状态
  $(basename "$0") status

  # 清理空闲 MCP
  $(basename "$0") cleanup

EOF
}

# 主入口
main() {
  local command=${1:-}
  shift || true

  case "$command" in
    start)
      if [ -z "${1:-}" ]; then
        log_error "用法: $(basename "$0") start <mcp_name>"
        exit 1
      fi
      start_mcp "$1"
      ;;

    stop)
      if [ -z "${1:-}" ]; then
        stop_all_mcp
      else
        stop_mcp "$1"
      fi
      ;;

    restart)
      if [ -z "${1:-}" ]; then
        log_error "用法: $(basename "$0") restart <mcp_name>"
        exit 1
      fi
      restart_mcp "$1"
      ;;

    ensure)
      if [ -z "${1:-}" ]; then
        log_error "用法: $(basename "$0") ensure <mcp_name>"
        exit 1
      fi
      ensure_mcp "$1"
      ;;

    smart)
      if [ -z "${1:-}" ]; then
        log_error "用法: $(basename "$0") smart <query>"
        exit 1
      fi
      smart_start "$1"
      ;;

    list)
      list_mcp
      ;;

    status)
      status_mcp
      ;;

    cleanup)
      cleanup_idle_mcp
      ;;

    stats)
      stats_mcp
      ;;

    help|--help|-h)
      show_help
      ;;

    "")
      log_error "缺少命令"
      echo ""
      show_help
      exit 1
      ;;

    *)
      log_error "未知命令: $command"
      echo ""
      show_help
      exit 1
      ;;
  esac
}

# 运行主函数
main "$@"
