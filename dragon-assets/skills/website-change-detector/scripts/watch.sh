#!/usr/bin/env bash
#==============================================================================
# Website Change Detector - 网页变化检测
# 借鉴 Huginn Change Detector Agent 设计
#==============================================================================

set -euo pipefail

# 配置
WATCH_DIR="${WATCH_DIR:-$HOME/.claude/watch}"
WATCH_DB="$WATCH_DIR/watch.db"
SNAPSHOT_DIR="$WATCH_DIR/snapshots"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[CHANGED]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[SAME]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# 初始化
init() {
    mkdir -p "$WATCH_DIR" "$SNAPSHOT_DIR"
    chmod 700 "$WATCH_DIR"

    if [[ ! -f "$WATCH_DB" ]]; then
        sqlite3 "$WATCH_DB" "CREATE TABLE watches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            url TEXT NOT NULL,
            selector TEXT,
            keywords TEXT,
            interval TEXT DEFAULT '1h',
            last_hash TEXT,
            last_check DATETIME,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'active'
        );"

        sqlite3 "$WATCH_DB" "CREATE TABLE snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            watch_id INTEGER,
            content TEXT,
            hash TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (watch_id) REFERENCES watches(id)
        );"

        sqlite3 "$WATCH_DB" "CREATE TABLE changes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            watch_id INTEGER,
            change_type TEXT,
            old_value TEXT,
            new_value TEXT,
            detected_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            notified INTEGER DEFAULT 0,
            FOREIGN KEY (watch_id) REFERENCES watches(id)
        );"

        log_success "数据库初始化完成: $WATCH_DB"
    fi
}

# 获取页面内容
fetch_content() {
    local url="$1"
    local selector="$2"

    if [[ -n "$selector" ]]; then
        curl -sL "$url" | grep -oP "(?<=<${selector%% *}[^>]*>)[^<]+" | head -1 || \
        curl -sL "$url" | sed -n "/$selector/,/<\/$selector/p" | head -50
    else
        curl -sL "$url"
    fi
}

# 计算哈希
compute_hash() {
    echo -n "$1" | md5sum | cut -d' ' -f1 || \
    echo -n "$1" | shasum -a 256 | cut -d' ' -f1
}

# 添加监控
add_watch() {
    local url="$1"
    local selector="${2:-}"
    local interval="${3:-1h}"
    local keywords="${4:-}"
    local name="${5:-$(basename "$url")}"

    init

    # 检测变化模式
    local mode="hash"
    if [[ -n "$keywords" ]]; then
        mode="keywords"
    elif [[ -n "$selector" ]]; then
        mode="selector"
    fi

    sqlite3 "$WATCH_DB" "INSERT INTO watches (name, url, selector, keywords, interval, status)
        VALUES ('$name', '$url', '$selector', '$keywords', '$interval', 'active')"

    local watch_id
    watch_id=$(sqlite3 "$WATCH_DB" "SELECT last_insert_rowid()")

    log_success "添加监控: $name (ID: $watch_id)"

    # 立即执行首次检查
    check_watch "$watch_id"
}

# 检查监控
check_watch() {
    local watch_id="$1"

    init

    local url selector keywords last_hash
    read -r url selector keywords last_hash < <(sqlite3 "$WATCH_DB" \
        "SELECT url, selector, keywords, last_hash FROM watches WHERE id=$watch_id")

    [[ -z "$url" ]] && { log_error "监控 $watch_id 不存在"; return 1; }

    log_info "检查: $url"

    # 获取内容
    local content
    content=$(fetch_content "$url" "$selector") || { log_error "获取内容失败"; return 1; }

    local new_hash
    new_hash=$(compute_hash "$content")

    # 保存快照
    sqlite3 "$WATCH_DB" "INSERT INTO snapshots (watch_id, content, hash)
        VALUES ($watch_id, '$(echo "$content" | sqlite3Escape)', '$new_hash')"

    # 检测变化
    if [[ "$new_hash" != "$last_hash" ]]; then
        log_success "检测到变化: $url"

        if [[ -n "$last_hash" ]]; then
            # 记录变化
            local change_type="hash_changed"
            [[ -n "$keywords" ]] && change_type="keywords_detected"

            sqlite3 "$WATCH_DB" "INSERT INTO changes (watch_id, change_type, old_value, new_value)
                VALUES ($watch_id, '$change_type', '$last_hash', '$new_hash')"

            # 检查关键词
            if [[ -n "$keywords" ]]; then
                for keyword in $(echo "$keywords" | tr ',' ' '); do
                    if echo "$content" | grep -qi "$keyword"; then
                        log_success "关键词匹配: $keyword"
                        trigger_notification "$watch_id" "$keyword" "$content"
                    fi
                done
            fi
        fi

        # 更新哈希
        sqlite3 "$WATCH_DB" "UPDATE watches SET last_hash='$new_hash', last_check=CURRENT_TIMESTAMP WHERE id=$watch_id"
    else
        log_warn "内容无变化: $url"
    fi
}

# 触发通知
trigger_notification() {
    local watch_id="$1"
    local keyword="$2"
    local content="$3"

    local webhook_url
    webhook_url=$(sqlite3 "$WATCH_DB" "SELECT notification_config FROM watches WHERE id=$watch_id" 2>/dev/null)

    if [[ -n "$webhook_url" ]]; then
        curl -sL -X POST "$webhook_url" \
            -H "Content-Type: application/json" \
            -d "{\"event\":\"change_detected\",\"watch_id\":$watch_id,\"keyword\":\"$keyword\",\"content\":\"$(echo "$content" | head -c 500 | sqlite3Escape)\"}" \
            && log_success "通知已发送" || log_error "通知发送失败"
    fi
}

# SQLite 转义
sqlite3Escape() {
    sed "s/'/''/g"
}

# 列出监控
list_watches() {
    init
    sqlite3 -header -column "$WATCH_DB" \
        "SELECT id, name, url, interval, status, last_check FROM watches ORDER BY created_at DESC"
}

# 删除监控
delete_watch() {
    local watch_id="$1"
    init
    sqlite3 "$WATCH_DB" "DELETE FROM watches WHERE id=$watch_id" && \
        log_success "监控 $watch_id 已删除"
}

# 查看变化历史
history() {
    local watch_id="$1"
    local limit="${2:-10}"
    init
    sqlite3 -header -column "$WATCH_DB" \
        "SELECT id, change_type, detected_at FROM changes WHERE watch_id=$watch_id ORDER BY detected_at DESC LIMIT $limit"
}

# 查看快照
snapshots() {
    local watch_id="$1"
    local limit="${2:-5}"
    init
    sqlite3 -header -column "$WATCH_DB" \
        "SELECT id, hash, created_at FROM snapshots WHERE watch_id=$watch_id ORDER BY created_at DESC LIMIT $limit"
}

# 诊断
doctor() {
    echo "=== Website Change Detector 诊断 ==="
    echo

    echo "[1] 目录检查"
    [[ -d "$WATCH_DIR" ]] && echo "  ✓ 目录: $WATCH_DIR" || echo "  ✗ 目录不存在"
    [[ -d "$SNAPSHOT_DIR" ]] && echo "  ✓ 快照目录: $SNAPSHOT_DIR" || echo "  ✗ 快照目录不存在"

    echo
    echo "[2] 数据库检查"
    if [[ -f "$WATCH_DB" ]]; then
        watch_count=$(sqlite3 "$WATCH_DB" "SELECT COUNT(*) FROM watches")
        snapshot_count=$(sqlite3 "$WATCH_DB" "SELECT COUNT(*) FROM snapshots")
        change_count=$(sqlite3 "$WATCH_DB" "SELECT COUNT(*) FROM changes")
        echo "  监控数: $watch_count"
        echo "  快照数: $snapshot_count"
        echo "  变化记录: $change_count"
        echo "  ✓ 数据库正常"
    else
        echo "  ✗ 数据库不存在"
    fi

    echo
    echo "[3] curl 检查"
    command -v curl &>/dev/null && echo "  ✓ curl 已安装" || echo "  ✗ curl 未安装"

    echo
    echo "[4] 并行处理检查"
    command -v xargs &>/dev/null && echo "  ✓ xargs 已安装" || echo "  ⚠ xargs 未安装"
}

# 帮助
usage() {
    cat << EOF
Website Change Detector - 网页变化检测

用法: watch <命令> [参数]

命令:
  add <url> [--selector] [--interval] [--keywords] [--name]
      添加监控
  check <id>                   立即检查
  list                         列出所有监控
  delete <id>                  删除监控
  history <id> [N]             查看变化历史
  snapshots <id> [N]           查看快照
  notify <id> --webhook <url> 设置通知
  doctor                       诊断检查
  init                         初始化

示例:
  watch add "https://news.site" --keywords "AI,LLM"
  watch add "https://example.com" --selector ".price" --interval 30m
  watch list
  watch history 1 --last 10
  watch notify 1 --webhook "https://hook.site/notify"
  watch check 1

EOF
}

main() {
    local cmd="${1:-}"
    shift || true

    case "$cmd" in
        add)
            add_watch "$@"
            ;;
        check)
            check_watch "$@"
            ;;
        list)
            list_watches
            ;;
        delete)
            delete_watch "$@"
            ;;
        history)
            history "$@"
            ;;
        snapshots)
            snapshots "$@"
            ;;
        notify)
            notify_watch "$@"
            ;;
        doctor)
            doctor
            ;;
        init)
            init
            ;;
        help|--help|-h)
            usage
            ;;
        *)
            usage
            ;;
    esac
}

notify_watch() {
    local watch_id="$1"
    local webhook_url="${2:-}"
    init
    [[ -z "$webhook_url" ]] && { log_error "需要 webhook URL"; return 1; }
    sqlite3 "$WATCH_DB" "UPDATE watches SET notification_config='$webhook_url' WHERE id=$watch_id"
    log_success "通知已设置"
}

main "$@"
