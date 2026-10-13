#!/usr/bin/env python3
"""
RSS Aggregator - RSS/Atom 订阅聚合
借鉴 Huginn RSS Agent 设计
"""

import os
import sys
import sqlite3
import argparse
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime, timedelta
from urllib.parse import urlparse

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    import urllib.request as requests


# 配置
RSS_DIR = Path(os.path.expanduser("~/.claude/rss"))
RSS_DB = RSS_DIR / "rss.db"
CACHE_DIR = RSS_DIR / "cache"


def init_db():
    """初始化数据库"""
    RSS_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    RSS_DIR.chmod(0o700)

    conn = sqlite3.connect(str(RSS_DB))
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS feeds (
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
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS items (
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
        )
    """)

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_items_pub_date ON items(pub_date DESC)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_items_feed_id ON items(feed_id)")

    conn.commit()
    conn.close()


def parse_feed(url):
    """解析 RSS/Atom 源"""
    try:
        if REQUESTS_AVAILABLE:
            response = requests.get(url, timeout=30)
            content = response.text
        else:
            with urllib.request.urlopen(url, timeout=30) as resp:
                content = resp.read().decode()

        root = ET.fromstring(content)

        items = []

        # RSS 2.0
        if root.tag == 'rss' or root.tag.endswith('rss'):
            channel = root.find('channel')
            if channel is not None:
                for item in channel.findall('item'):
                    title = item.findtext('title', '')
                    link = item.findtext('link', '')
                    description = item.findtext('description', '')
                    pub_date = item.findtext('pubDate', '')
                    guid = item.findtext('guid', link)

                    items.append({
                        'title': title,
                        'link': link,
                        'description': description,
                        'pub_date': pub_date,
                        'guid': guid
                    })

        # Atom
        elif root.tag == 'feed' or root.tag.endswith('feed'):
            for entry in root.findall('entry'):
                title = entry.findtext('title', '')
                link = entry.find('link')
                link_href = link.get('href') if link is not None else ''
                summary = entry.findtext('summary', '')
                published = entry.findtext('published', '') or entry.findtext('updated', '')
                guid = entry.findtext('id', link_href)

                items.append({
                    'title': title,
                    'link': link_href,
                    'description': summary,
                    'pub_date': published,
                    'guid': guid
                })

        return items

    except Exception as e:
        print(f"[ERROR] 解析失败: {e}")
        return []


def fetch_feed(feed_id, url, name):
    """拉取订阅"""
    print(f"[INFO] 拉取: {name}")

    items = parse_feed(url)

    if not items:
        print(f"[WARN] 无内容: {name}")
        return 0

    conn = sqlite3.connect(str(RSS_DB))
    cursor = conn.cursor()

    count = 0
    for item in items:
        guid = item.get('guid', item.get('link', ''))

        if not guid:
            continue

        # 去重检查
        cursor.execute("SELECT 1 FROM items WHERE guid=?", (guid,))
        if cursor.fetchone():
            continue

        cursor.execute("""
            INSERT INTO items (feed_id, guid, title, link, description, pub_date)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            feed_id,
            guid,
            item.get('title', ''),
            item.get('link', ''),
            item.get('description', ''),
            item.get('pub_date', '')
        ))
        count += 1

    cursor.execute(
        "UPDATE feeds SET last_fetch=CURRENT_TIMESTAMP WHERE id=?",
        (feed_id,)
    )
    conn.commit()
    conn.close()

    if count > 0:
        print(f"[OK] 新增 {count} 条: {name}")
    else:
        print(f"[SAME] 无新内容: {name}")

    return count


def cmd_add(args):
    """添加订阅"""
    init_db()

    # 验证 URL
    try:
        if REQUESTS_AVAILABLE:
            requests.head(args.url, timeout=10)
        else:
            with urllib.request.urlopen(args.url, timeout=10) as resp:
                pass
    except Exception as e:
        print(f"[ERROR] 无法访问: {e}")
        return 1

    conn = sqlite3.connect(str(RSS_DB))
    cursor = conn.cursor()

    try:
        name = args.name or urlparse(args.url).netloc
        cursor.execute(
            "INSERT INTO feeds (name, url, tag, category, interval) VALUES (?, ?, ?, ?, ?)",
            (name, args.url, args.tag, args.category, args.interval)
        )
        conn.commit()
        feed_id = cursor.lastrowid
        print(f"[OK] 添加订阅: {name} (ID: {feed_id})")

        # 立即拉取
        fetch_feed(feed_id, args.url, name)

    except sqlite3.IntegrityError:
        print(f"[WARN] 订阅已存在: {args.url}")
    finally:
        conn.close()

    return 0


def cmd_fetch(args):
    """拉取更新"""
    init_db()

    conn = sqlite3.connect(str(RSS_DB))
    cursor = conn.cursor()

    if args.feed_id:
        cursor.execute("SELECT id, url, name FROM feeds WHERE id=?", (args.feed_id,))
        row = cursor.fetchone()
        if row:
            fetch_feed(row[0], row[1], row[2])
    else:
        tag_filter = f" WHERE tag='{args.tag}'" if args.tag else ""
        cursor.execute(f"SELECT id, url, name FROM feeds{tag_filter}")

        for row in cursor.fetchall():
            if args.parallel > 1:
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor(max_workers=args.parallel) as executor:
                    executor.submit(fetch_feed, row[0], row[1], row[2])
            else:
                fetch_feed(row[0], row[1], row[2])

    conn.close()
    return 0


def cmd_list(args):
    """列出订阅"""
    init_db()

    conn = sqlite3.connect(str(RSS_DB))
    cursor = conn.cursor()

    if args.tag:
        cursor.execute(
            "SELECT id, name, url, tag, last_fetch FROM feeds WHERE tag=? ORDER BY name",
            (args.tag,)
        )
    else:
        cursor.execute("SELECT id, name, url, tag, last_fetch FROM feeds ORDER BY name")

    print(f"{'ID':<5} {'名称':<25} {'URL':<40} {'标签':<15} {'最后拉取':<20}")
    print("-" * 110)
    for row in cursor.fetchall():
        print(f"{row[0]:<5} {row[1]:<25} {row[2][:40]:<40} {row[3] or '':<15} {row[4] or '':<20}")

    conn.close()
    return 0


def cmd_items(args):
    """列出内容"""
    init_db()

    conn = sqlite3.connect(str(RSS_DB))
    cursor = conn.cursor()

    conditions = []
    params = []

    if args.feed_id:
        conditions.append("i.feed_id=?")
        params.append(args.feed_id)

    if args.tag:
        conditions.append("f.tag=?")
        params.append(args.tag)

    where = " AND ".join(conditions) if conditions else "1=1"
    query = f"""
        SELECT i.id, i.title, f.name, i.pub_date, i.read
        FROM items i
        JOIN feeds f ON i.feed_id=f.id
        WHERE {where}
        ORDER BY i.pub_date DESC
        LIMIT ?
    """
    params.append(args.limit)

    cursor.execute(query, params)

    print(f"{'ID':<5} {'标题':<50} {'来源':<20} {'发布时间':<20}")
    print("-" * 100)
    for row in cursor.fetchall():
        title = (row[1] or '')[:50]
        feed = (row[2] or '')[:20]
        print(f"{row[0]:<5} {title:<50} {feed:<20} {row[3] or '':<20}")

    conn.close()
    return 0


def cmd_search(args):
    """搜索内容"""
    init_db()

    conn = sqlite3.connect(str(RSS_DB))
    cursor = conn.cursor()

    cursor.execute("""
        SELECT i.id, i.title, f.name, i.pub_date
        FROM items i
        JOIN feeds f ON i.feed_id=f.id
        WHERE i.title LIKE ? OR i.description LIKE ?
        ORDER BY i.pub_date DESC
        LIMIT ?
    """, (f'%{args.keyword}%', f'%{args.keyword}%', args.limit))

    print(f"{'ID':<5} {'标题':<60} {'来源':<20}")
    print("-" * 90)
    for row in cursor.fetchall():
        title = (row[1] or '')[:60]
        feed = (row[2] or '')[:20]
        print(f"{row[0]:<5} {title:<60} {feed:<20}")

    conn.close()
    return 0


def cmd_digest(args):
    """生成摘要"""
    init_db()

    hours = args.hours
    tag = args.tag

    conn = sqlite3.connect(str(RSS_DB))
    cursor = conn.cursor()

    conditions = ["i.fetched_at > datetime('now', ?)", f"-{hours} hours"]
    params = [f"-{hours} hours"]

    if tag:
        conditions.append("f.tag=?")
        params.append(tag)

    where = " AND ".join(conditions)

    cursor.execute(f"""
        SELECT i.title, i.link, i.description, f.name, i.pub_date
        FROM items i
        JOIN feeds f ON i.feed_id=f.id
        WHERE {where}
        ORDER BY i.pub_date DESC
    """, params)

    items = cursor.fetchall()
    conn.close()

    if args.format == 'markdown':
        print(f"# RSS 摘要 ({datetime.now().strftime('%Y-%m-%d %H:%M')})")
        print()
        print(f"## 过去 {hours} 小时内容")
        print()

        for title, link, desc, feed, pub in items:
            print(f"- **{feed}: {title}**")
            if desc:
                print(f"  {desc[:200]}...")
            print(f"  [原文链接]({link})")
            print()

    elif args.format == 'html':
        print("<h1>RSS 摘要</h1>")
        for title, link, desc, feed, pub in items:
            print(f"<article><h2>[{feed}] {title}</h2><p>{desc or ''}</p><a href='{link}'>原文</a></article>")

    else:
        for title, link, desc, feed, pub in items:
            print(f"[{feed}] {title}")
            print(f"  {link}")
            print()

    return 0


def cmd_doctor(args):
    """诊断检查"""
    print("=== RSS Aggregator Diagnosis ===")
    print()

    print("[1] Directory Check")
    if RSS_DIR.exists():
        print(f"  [OK] Directory: {RSS_DIR}")
    else:
        print("  [X] Directory not exists")

    print()
    print("[2] Database Check")
    if RSS_DB.exists():
        conn = sqlite3.connect(str(RSS_DB))
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM feeds")
        feed_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM items")
        item_count = cursor.fetchone()[0]
        conn.close()
        print(f"  Feeds: {feed_count}")
        print(f"  Items: {item_count}")
        print("  [OK] Database normal")
    else:
        print("  [X] Database not exists")

    print()
    print("[3] requests Check")
    if REQUESTS_AVAILABLE:
        print("  [OK] requests installed")
    else:
        print("  [!] requests not installed, using urllib")


def main():
    parser = argparse.ArgumentParser(description="RSS Aggregator - RSS/Atom 订阅聚合")
    subparsers = parser.add_subparsers(dest='cmd', help='命令')

    # add
    p_add = subparsers.add_parser('add', help='添加订阅')
    p_add.add_argument('url', help='RSS URL')
    p_add.add_argument('--tag', help='标签')
    p_add.add_argument('--category', help='分类')
    p_add.add_argument('--interval', default='1h', help='拉取间隔')
    p_add.add_argument('--name', help='名称')
    p_add.set_defaults(func=cmd_add)

    # fetch
    p_fetch = subparsers.add_parser('fetch', help='拉取更新')
    p_fetch.add_argument('--feed-id', type=int, help='订阅 ID')
    p_fetch.add_argument('--tag', help='标签')
    p_fetch.add_argument('--parallel', type=int, default=1, help='并行数')
    p_fetch.set_defaults(func=cmd_fetch)

    # list
    p_list = subparsers.add_parser('list', help='列出订阅')
    p_list.add_argument('--tag', help='标签')
    p_list.set_defaults(func=cmd_list)

    # items
    p_items = subparsers.add_parser('items', help='列出内容')
    p_items.add_argument('--feed-id', type=int, help='订阅 ID')
    p_items.add_argument('--tag', help='标签')
    p_items.add_argument('--limit', type=int, default=20, help='限制')
    p_items.set_defaults(func=cmd_items)

    # search
    p_search = subparsers.add_parser('search', help='搜索内容')
    p_search.add_argument('keyword', help='关键词')
    p_search.add_argument('--limit', type=int, default=20, help='限制')
    p_search.set_defaults(func=cmd_search)

    # digest
    p_digest = subparsers.add_parser('digest', help='生成摘要')
    p_digest.add_argument('--hours', type=int, default=24, help='过去小时数')
    p_digest.add_argument('--format', choices=['markdown', 'html', 'text'], default='markdown', help='格式')
    p_digest.add_argument('--tag', help='标签')
    p_digest.set_defaults(func=cmd_digest)

    # doctor
    p_doc = subparsers.add_parser('doctor', help='诊断检查')
    p_doc.set_defaults(func=cmd_doctor)

    # init
    p_init = subparsers.add_parser('init', help='初始化')
    p_init.set_defaults(func=lambda args: init_db() or print("[OK] 初始化完成"))

    args = parser.parse_args()

    if hasattr(args, 'func'):
        return args.func(args)
    else:
        parser.print_help()
        return 0


if __name__ == '__main__':
    sys.exit(main())
