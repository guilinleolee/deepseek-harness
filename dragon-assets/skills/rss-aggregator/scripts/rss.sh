#!/usr/bin/env bash
#==============================================================================
# RSS Aggregator - RSS/Atom 订阅聚合
# 借鉴 Huginn RSS Agent 设计
#==============================================================================

set -euo pipefail

# 配置
RSS_DIR="${RSS_DIR:-$HOME/.claude/rss}"
RSS_DB="$RSS_DIR/rss.db"
CACHE_DIR="$RSS_DIR/cache"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[OK]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# 初始化
init() {
    mkdir -p "$RSS_DIR" "$CACHE_DIR"
    chmod 700 "$RSS_DIR"

    if [[ ! -f "$RSS_DB" ]]; then
        sqlite3 "$RSS_DB" "CREATE TABLE feeds (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            url TEXT UNIQUE NOT NULL,
            tag TEXT,
            category TEXT,
            interval TEXT DEFAULT '1h',
            last_fetch DATETIME,
            last_hash TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'active'
        );"

        sqlite3 "$RSS_DB" "CREATE TABLE items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            feed_id INTEGER,
            guid TEXT UNIQUE,
            title TEXT,
            link TEXT,
            description TEXT,
            content TEXT,
            author TEXT,
            pub_date DATETIME,
            fetched_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            read INTEGER DEFAULT 0,
            FOREIGN KEY (feed_id) REFERENCES feeds(id)
        );"

        sqlite3 "$RSS_DB" "CREATE INDEX idx_items_pub_date ON items(pub_date DESC);"
        sqlite3 "$RSS_DB" "CREATE INDEX idx_items_feed_id ON items(feed_id);"

        log_success "数据库初始化完成: $RSS_DB"
    fi
}

# 解析 RSS/Atom
parse_feed() {
    local url="$1"
    local xml
    xml=$(curl -sL "$url" --max-time 30)

    if echo "$xml" | grep -q "<rss"; then
        # RSS 2.0
        echo "$xml" | grep -oP '(?<=<item>)[\s\S]*?(?=</item>)' | while read -r item; do
            local title link description pub_date guid
            title=$(echo "$item" | grep -oP '(?<=<title>)[^<]+' | sed 's/&lt;/</g; s/&gt;/>/g; s/&amp;/\&/g; s/&quot;/"/g')
            link=$(echo "$item" | grep -oP '(?<=<link>)[^<]+')
            description=$(echo "$item" | grep -oP '(?<=<description>)[^<]+' | head -c 1000)
            pub_date=$(echo "$item" | grep -oP '(?<=<pubDate>)[^<]+')
            guid=$(echo "$item" | grep -oP '(?<=<guid>)[^<]+' || echo "$link")

            echo "$title|$link|$description|$pub_date|$guid"
        done
    elif echo "$xml" | grep -q "<feed"; then
        # Atom
        echo "$xml" | grep -oP '(?<=<entry>)[\s\S]*?(?=</entry>)' | while read -r entry; do
            local title link summary published guid
            title=$(echo "$entry" | grep -oP '(?<=<title[^>]*>)[^<]+' | sed 's/&lt;/</g; s/&gt;/>/g; s/&amp;/\&/g')
            link=$(echo "$entry" | grep -oP '(?<=<link[^>]*href=["\x27])[^"\x27]+')
            summary=$(echo "$entry" | grep -oP '(?<=<summary>)[^<]+' | head -c 1000)
            published=$(echo "$entry" | grep -oP '(?<=<published>)[^<]+' || echo "$entry" | grep -oP '(?<=<updated>)[^<]+')
            guid=$(echo "$entry" | grep -oP '(?<=<id>)[^<]+' || echo "$link")

            echo "$title|$link|$summary|$published|$guid"
        done
    else
        log_error "无法解析 RSS/Atom: $url"
        return 1
    fi
}

# 添加订阅
add_feed() {
    local url="$1"
    local tag="${2:-}"
    local category="${3:-}"
    local interval="${4:-1h}"
    local name="${5:-$(basename "$url")}"

    init

    # 验证 URL
    curl -sL --max-time 10 -o /dev/null "$url" || { log_error "无法访问: $url"; return 1; }

    if sqlite3 "$RSS_DB" "SELECT 1 FROM feeds WHERE url='$url'" 2>/dev/null | grep -q 1; then
        log_warn "订阅已存在: $url"
        return 1
    fi

    sqlite3 "$RSS_DB" "INSERT INTO feeds (name, url, tag, category, interval)
        VALUES ('$name', '$url', '$tag', '$category', '$interval')"

    local feed_id
    feed_id=$(sqlite3 "$RSS_DB" "SELECT last_insert_rowid()")

    log_success "添加订阅: $name (ID: $feed_id)"

    # 立即拉取
    fetch_feed "$feed_id"
}

# 拉取订阅
fetch_feed() {
    local feed_id="${1:-}"
    local parallel="${PARALLEL:-1}"

    init

    if [[ -n "$feed_id" ]]; then
        fetch_single_feed "$feed_id"
    else
        local feeds
        feeds=$(sqlite3 "$RSS_DB" "SELECT id FROM feeds WHERE status='active'")
        for fid in $feeds; do
            fetch_single_feed "$fid" &
            [[ $parallel -gt 1 ]] && wait
        done
        wait
    fi
}

fetch_single_feed() {
    local feed_id="$1"

    local url name
    read -r url name < <(sqlite3 "$RSS_DB" "SELECT url, name FROM feeds WHERE id=$feed_id")

    log_info "拉取: $name"

    local items
    items=$(parse_feed "$url") || return 1

    local count=0
    while IFS='|' read -r title link description pub_date guid; do
        [[ -z "$guid" ]] && continue

        # 去重检查
        if ! sqlite3 "$RSS_DB" "SELECT 1 FROM items WHERE guid='$guid'" 2>/dev/null | grep -q 1; then
            sqlite3 "$RSS_DB" "INSERT INTO items (feed_id, guid, title, link, description, pub_date)
                VALUES ($feed_id, '$(echo "$guid" | sqlite3Escape)', '$(echo "$title" | sqlite3Escape)',
                        '$(echo "$link" | sqlite3Escape)', '$(echo "$description" | sqlite3Escape)',
                        '$(echo "$pub_date" | sqlite3Escape)')"
            ((count++))
        fi
    done <<< "$items"

    sqlite3 "$RSS_DB" "UPDATE feeds SET last_fetch=CURRENT_TIMESTAMP WHERE id=$feed_id"

    [[ $count -gt 0 ]] && log_success "新增 $count 条: $name" || log_warn "无新内容: $name"
}

# SQLite 转义
sqlite3Escape() {
    sed "s/'/''/g"
}

# 列出订阅
list_feeds() {
    local tag="${1:-}"
    init

    if [[ -n "$tag" ]]; then
        sqlite3 -header -column "$RSS_DB" \
            "SELECT id, name, url, tag, last_fetch FROM feeds WHERE tag='$tag' ORDER BY name"
    else
        sqlite3 -header -column "$RSS_DB" \
            "SELECT id, name, url, tag, last_fetch FROM feeds ORDER BY name"
    fi
}

# 列出内容
list_items() {
    local feed_id="${1:-}"
    local limit="${2:-20}"
    local tag="${3:-}"

    init

    local query="SELECT i.id, i.title, f.name as feed, i.pub_date, i.read
                 FROM items i JOIN feeds f ON i.feed_id=f.id"

    local conditions=""
    [[ -n "$feed_id" ]] && conditions=" WHERE i.feed_id=$feed_id"
    [[ -n "$tag" ]] && conditions=" WHERE f.tag='$tag'"

    query="$query$conditions ORDER BY i.pub_date DESC LIMIT $limit"

    sqlite3 -header -column "$RSS_DB" "$query"
}

# 搜索内容
search_items() {
    local keyword="$1"
    local limit="${2:-20}"
    init

    sqlite3 -header -column "$RSS_DB" \
        "SELECT id, title, f.name as feed, pub_date
         FROM items i JOIN feeds f ON i.feed_id=f.id
         WHERE i.title LIKE '%$keyword%' OR i.description LIKE '%$keyword%'
         ORDER BY i.pub_date DESC LIMIT $limit"
}

# 读取内容
read_item() {
    local item_id="$1"
    init

    sqlite3 -header -column "$RSS_DB" \
        "SELECT title, link, description, content, author, pub_date
         FROM items WHERE id=$item_id" | sed 's/|/\n/g'
}

# 生成摘要
generate_digest() {
    local hours="${1:-24}"
    local format="${2:-markdown}"
    local tag="${3:-}"

    init

    local items
    local query="SELECT i.title, i.link, i.description, f.name, i.pub_date
                 FROM items i JOIN feeds f ON i.feed_id=f.id
                 WHERE i.fetched_at > datetime('now', '-$hours hours')"

    [[ -n "$tag" ]] && query="$query AND f.tag='$tag'"
    query="$query ORDER BY i.pub_date DESC"

    items=$(sqlite3 "$RSS_DB" "$query")

    if [[ "$format" == "markdown" ]]; then
        echo "# RSS 摘要 ($(date '+%Y-%m-%d %H:%M'))"
        echo
        echo "## 过去 $hours 小时内容"
        echo

        while IFS='|' read -r title link desc feed pub; do
            echo "- **[$feed] $title**"
            echo "  $desc"
            echo "  [原文链接]($link)"
            echo
        done <<< "$items"
    elif [[ "$format" == "html" ]]; then
        echo "<h1>RSS 摘要 ($(date '+%Y-%m-%d %H:%M'))</h1>"
        while IFS='|' read -r title link desc feed pub; do
            echo "<article><h2>[$feed] $title</h2><p>$desc</p><a href='$link'>原文</a></article>"
        done <<< "$items"
    fi
}

# 导出 OPML
export_opml() {
    local output="${1:-subscriptions.opml}"
    init

    echo '<?xml version="1.0" encoding="UTF-8"?>'
    echo '<opml version="2.0">'
    echo '<head><title>RSS Subscriptions</title></head>'
    echo '<body>'

    sqlite3 "$RSS_DB" "SELECT name, url, tag FROM feeds" | while IFS='|' read -r name url tag; do
        echo "  <outline text=\"$name\" title=\"$name\" type=\"rss\" xmlUrl=\"$url\"/>"
    done

    echo '</body>'
    echo '</opml>' > "$output"

    log_success "已导出: $output"
}

# 导入 OPML
import_opml() {
    local file="$1"

    grep -oP '(?<=xmlUrl=")[^"]+' "$file" | while read -r url; do
        add_feed "$url"
    done
}

# 删除订阅
delete_feed() {
    local feed_id="$1"
    init
    sqlite3 "$RSS_DB" "DELETE FROM items WHERE feed_id=$feed_id"
    sqlite3 "$RSS_DB" "DELETE FROM feeds WHERE id=$feed_id"
    log_success "订阅 $feed_id 已删除"
}

# 诊断
doctor() {
    echo "=== RSS Aggregator 诊断 ==="
    echo

    echo "[1] 目录检查"
    [[ -d "$RSS_DIR" ]] && echo "  ✓ 目录: $RSS_DIR" || echo "  ✗ 目录不存在"

    echo
    echo "[2] 数据库检查"
    if [[ -f "$RSS_DB" ]]; then
        feed_count=$(sqlite3 "$RSS_DB" "SELECT COUNT(*) FROM feeds")
        item_count=$(sqlite3 "$RSS_DB" "SELECT COUNT(*) FROM items")
        echo "  订阅数: $feed_count"
        echo "  内容数: $item_count"
        echo "  ✓ 数据库正常"
    else
        echo "  ✗ 数据库不存在"
    fi

    echo
    echo "[3] curl 检查"
    command -v curl &>/dev/null && echo "  ✓ curl 已安装" || echo "  ✗ curl 未安装"

    echo
    echo "[4] SQLite 检查"
    command -v sqlite3 &>/dev/null && echo "  ✓ sqlite3 已安装" || echo "  ⚠ sqlite3 未安装"
}

# 帮助
usage() {
    cat << EOF
RSS Aggregator - RSS/Atom 订阅聚合

用法: rss <命令> [参数]

订阅管理:
  add <url> [--tag] [--category] [--interval] [--name]
      添加订阅
  list [--tag]
      列出订阅
  delete <id>
      删除订阅
  import <file.opml>
      导入 OPML
  export [output.opml]
      导出 OPML

内容操作:
  fetch [--all] [--tag] [--parallel N]
      拉取更新
  items [--feed-id] [--tag] [--limit N]
      列出内容
  search <keyword> [--limit N]
      搜索内容
  read <item_id>
      阅读内容

摘要生成:
  digest [--hours N] [--format markdown|html] [--tag]
      生成摘要

示例:
  rss add "https://blog.example.com/feed.xml" --tag tech
  rss list --tag tech
  rss fetch --all --parallel 5
  rss digest --hours 24 --format markdown
  rss search "AI" --limit 20
  rss export subscriptions.opml

EOF
}

main() {
    local cmd="${1:-}"
    shift || true

    case "$cmd" in
        add)
            add_feed "$@"
            ;;
        list)
            list_feeds "$@"
            ;;
        delete)
            delete_feed "$@"
            ;;
        fetch)
            fetch_feed "$@"
            ;;
        items)
            list_items "$@"
            ;;
        search)
            search_items "$@"
            ;;
        read)
            read_item "$@"
            ;;
        digest)
            generate_digest "$@"
            ;;
        import)
            import_opml "$@"
            ;;
        export)
            export_opml "$@"
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

main "$@"
