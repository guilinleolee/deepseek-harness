#!/usr/bin/env python3
"""
Website Change Detector - 网页变化检测
借鉴 Huginn Change Detector Agent 设计
"""

import os
import sys
import sqlite3
import argparse
import hashlib
import re
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    import urllib.request as requests


# 配置
WATCH_DIR = Path(os.path.expanduser("~/.claude/watch"))
WATCH_DB = WATCH_DIR / "watch.db"
SNAPSHOT_DIR = WATCH_DIR / "snapshots"


def init_db():
    """初始化数据库"""
    WATCH_DIR.mkdir(parents=True, exist_ok=True)
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    WATCH_DIR.chmod(0o700)

    conn = sqlite3.connect(str(WATCH_DB))
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS watches (
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
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            watch_id INTEGER,
            content TEXT,
            hash TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (watch_id) REFERENCES watches(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS changes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            watch_id INTEGER,
            change_type TEXT,
            old_value TEXT,
            new_value TEXT,
            detected_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            notified INTEGER DEFAULT 0,
            FOREIGN KEY (watch_id) REFERENCES watches(id)
        )
    """)

    conn.commit()
    conn.close()


def compute_hash(content):
    """计算内容哈希"""
    return hashlib.sha256(content.encode()).hexdigest()


def fetch_content(url, selector=None):
    """获取页面内容"""
    try:
        if REQUESTS_AVAILABLE:
            response = requests.get(url, timeout=30)
            content = response.text
        else:
            with urllib.request.urlopen(url, timeout=30) as response:
                content = response.read().decode()

        if selector:
            # 简单的 CSS 选择器模拟
            match = re.search(f'<{selector}[^>]*>([^<]+)</{selector}>', content)
            if match:
                return match.group(1)
            # 尝试提取标签内容
            match = re.search(f'class="?{selector}"?[^>]*>([^<]+)', content)
            if match:
                return match.group(1)

        return content
    except Exception as e:
        print(f"[ERROR] 获取内容失败: {e}")
        return None


def check_keywords(content, keywords):
    """检查关键词"""
    found = []
    for keyword in keywords.split(','):
        keyword = keyword.strip()
        if keyword.lower() in content.lower():
            found.append(keyword)
    return found


def cmd_add(args):
    """添加监控"""
    init_db()

    name = args.name or urlparse(args.url).netloc

    conn = sqlite3.connect(str(WATCH_DB))
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO watches (name, url, selector, keywords, interval) VALUES (?, ?, ?, ?, ?)",
            (name, args.url, args.selector, args.keywords, args.interval)
        )
        conn.commit()
        watch_id = cursor.lastrowid
        print(f"[OK] 添加监控: {name} (ID: {watch_id})")

        # 立即执行首次检查
        check_watch(watch_id)

    except Exception as e:
        print(f"[ERROR] 添加失败: {e}")
    finally:
        conn.close()

    return 0


def check_watch(watch_id):
    """检查监控"""
    conn = sqlite3.connect(str(WATCH_DB))
    cursor = conn.cursor()

    cursor.execute(
        "SELECT url, selector, keywords, last_hash FROM watches WHERE id=?",
        (watch_id,)
    )
    row = cursor.fetchone()

    if not row:
        print(f"[ERROR] 监控 {watch_id} 不存在")
        conn.close()
        return 1

    url, selector, keywords, last_hash = row

    print(f"[INFO] 检查: {url}")

    content = fetch_content(url, selector)

    if content is None:
        conn.close()
        return 1

    new_hash = compute_hash(content)

    # 保存快照
    cursor.execute(
        "INSERT INTO snapshots (watch_id, content, hash) VALUES (?, ?, ?)",
        (watch_id, content[:10000], new_hash)
    )

    # 检测变化
    if new_hash != last_hash:
        print(f"[CHANGED] 检测到变化: {url}")

        if last_hash:
            change_type = "keywords_detected" if keywords else "hash_changed"
            cursor.execute(
                "INSERT INTO changes (watch_id, change_type, old_value, new_value) VALUES (?, ?, ?, ?)",
                (watch_id, change_type, last_hash, new_hash)
            )

            # 检查关键词
            if keywords:
                found = check_keywords(content, keywords)
                for kw in found:
                    print(f"[CHANGED] 关键词匹配: {kw}")
                    trigger_notification(watch_id, kw, content)

        # 更新哈希
        cursor.execute(
            "UPDATE watches SET last_hash=?, last_check=CURRENT_TIMESTAMP WHERE id=?",
            (new_hash, watch_id)
        )
    else:
        print(f"[SAME] 内容无变化: {url}")

    conn.commit()
    conn.close()

    return 0


def cmd_check(args):
    """立即检查"""
    init_db()
    return check_watch(args.id)


def cmd_list(args):
    """列出监控"""
    init_db()

    conn = sqlite3.connect(str(WATCH_DB))
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, name, url, interval, status, last_check FROM watches ORDER BY created_at DESC"
    )

    print(f"{'ID':<5} {'名称':<20} {'URL':<40} {'状态':<10} {'最后检查':<20}")
    print("-" * 100)
    for row in cursor.fetchall():
        print(f"{row[0]:<5} {row[1] or '':<20} {row[2][:40]:<40} {row[4]:<10} {row[5] or '':<20}")

    conn.close()
    return 0


def cmd_delete(args):
    """删除监控"""
    init_db()

    conn = sqlite3.connect(str(WATCH_DB))
    cursor = conn.cursor()
    cursor.execute("DELETE FROM snapshots WHERE watch_id=?", (args.id,))
    cursor.execute("DELETE FROM changes WHERE watch_id=?", (args.id,))
    cursor.execute("DELETE FROM watches WHERE id=?", (args.id,))
    conn.commit()
    deleted = cursor.rowcount
    conn.close()

    if deleted:
        print(f"[OK] 监控 {args.id} 已删除")
    else:
        print(f"[ERROR] 监控 {args.id} 不存在")

    return 0


def trigger_notification(watch_id, keyword, content):
    """触发通知"""
    conn = sqlite3.connect(str(WATCH_DB))
    cursor = conn.cursor()
    cursor.execute("SELECT notification_config FROM watches WHERE id=?", (watch_id,))
    row = cursor.fetchone()
    conn.close()

    if row and row[0]:
        webhook_url = row[0]
        try:
            data = {
                "event": "change_detected",
                "watch_id": watch_id,
                "keyword": keyword,
                "content": content[:500]
            }
            if REQUESTS_AVAILABLE:
                requests.post(webhook_url, json=data, timeout=10)
            print(f"[OK] 通知已发送")
        except Exception as e:
            print(f"[ERROR] 通知发送失败: {e}")


def cmd_notify(args):
    """设置通知"""
    init_db()

    conn = sqlite3.connect(str(WATCH_DB))
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE watches SET notification_config=? WHERE id=?",
        (args.webhook, args.id)
    )
    conn.commit()
    updated = cursor.rowcount
    conn.close()

    if updated:
        print(f"[OK] 通知已设置")
    else:
        print(f"[ERROR] 监控 {args.id} 不存在")

    return 0


def cmd_history(args):
    """查看变化历史"""
    init_db()

    conn = sqlite3.connect(str(WATCH_DB))
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, change_type, detected_at FROM changes WHERE watch_id=? ORDER BY detected_at DESC LIMIT ?",
        (args.id, args.limit)
    )

    print(f"{'ID':<5} {'变化类型':<20} {'时间':<20}")
    print("-" * 50)
    for row in cursor.fetchall():
        print(f"{row[0]:<5} {row[1]:<20} {row[2]:<20}")

    conn.close()
    return 0


def cmd_doctor(args):
    """诊断检查"""
    print("=== Website Change Detector Diagnosis ===")
    print()

    print("[1] Directory Check")
    if WATCH_DIR.exists():
        print(f"  [OK] Directory: {WATCH_DIR}")
    else:
        print("  [X] Directory not exists")

    print()
    print("[2] Database Check")
    if WATCH_DB.exists():
        conn = sqlite3.connect(str(WATCH_DB))
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM watches")
        watch_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM snapshots")
        snapshot_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM changes")
        change_count = cursor.fetchone()[0]
        conn.close()
        print(f"  Watches: {watch_count}")
        print(f"  Snapshots: {snapshot_count}")
        print(f"  Changes: {change_count}")
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
    parser = argparse.ArgumentParser(description="Website Change Detector - 网页变化检测")
    subparsers = parser.add_subparsers(dest='cmd', help='命令')

    # add
    p_add = subparsers.add_parser('add', help='添加监控')
    p_add.add_argument('url', help='URL')
    p_add.add_argument('--selector', help='CSS 选择器')
    p_add.add_argument('--interval', default='1h', help='检查间隔')
    p_add.add_argument('--keywords', help='关键词（逗号分隔）')
    p_add.add_argument('--name', help='名称')
    p_add.set_defaults(func=cmd_add)

    # check
    p_check = subparsers.add_parser('check', help='立即检查')
    p_check.add_argument('id', type=int, help='监控 ID')
    p_check.set_defaults(func=cmd_check)

    # list
    p_list = subparsers.add_parser('list', help='列出监控')
    p_list.set_defaults(func=cmd_list)

    # delete
    p_del = subparsers.add_parser('delete', help='删除监控')
    p_del.add_argument('id', type=int, help='监控 ID')
    p_del.set_defaults(func=cmd_delete)

    # notify
    p_not = subparsers.add_parser('notify', help='设置通知')
    p_not.add_argument('id', type=int, help='监控 ID')
    p_not.add_argument('--webhook', required=True, help='Webhook URL')
    p_not.set_defaults(func=cmd_notify)

    # history
    p_hist = subparsers.add_parser('history', help='查看历史')
    p_hist.add_argument('id', type=int, help='监控 ID')
    p_hist.add_argument('--limit', type=int, default=10, help='限制')
    p_hist.set_defaults(func=cmd_history)

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
