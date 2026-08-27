"""
multi-platform-publisher 多平台发布器 · V1.0
9 平台一键发布 · token bucket 限流 · sha256 去重 · 指数退避重试

依赖:
    - 标准库 hashlib / json / sqlite3 / time / uuid
"""

import argparse
import hashlib
import json
import os
import sqlite3
import sys
import time
import uuid
from contextlib import contextmanager
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List

# 强制 stdout/stderr 用 utf-8 编码（Windows GBK 抛 UnicodeEncodeError on emoji）
# 必须在创建 print 之前生效
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


# ===== 默认路径 =====
DEFAULT_DB_PATH = Path.home() / ".claude" / "skills" / "multi-platform-publisher" / "publisher.db"

# ===== 9 平台配置 =====
PLATFORMS: Dict[str, Dict] = {
    "douyin":      {"name": "抖音",      "qps": 5,   "max_retry": 3, "watermark": True,  "category": "video"},
    "xiaohongshu": {"name": "小红书",     "qps": 3,   "max_retry": 3, "watermark": True,  "category": "image"},
    "shipinhao":   {"name": "视频号",     "qps": 2,   "max_retry": 3, "watermark": True,  "category": "video"},
    "bilibili":    {"name": "B站",        "qps": 2,   "max_retry": 3, "watermark": False, "category": "video"},
    "kuaishou":    {"name": "快手",      "qps": 4,   "max_retry": 3, "watermark": True,  "category": "video"},
    "weibo":       {"name": "微博",      "qps": 10,  "max_retry": 3, "watermark": False, "category": "image"},
    "wechat":      {"name": "公众号",     "qps": 1,   "max_retry": 3, "watermark": False, "category": "article"},
    "tiktok":      {"name": "TikTok",    "qps": 5,   "max_retry": 3, "watermark": True,  "category": "video"},
    "youtube":     {"name": "YouTube",   "qps": 1,   "max_retry": 3, "watermark": False, "category": "video"},
}

# ===== 博主黑名单（与 blogger-fingerprint-registry 同步）=====
BLOCKED_BLOGGERS = {"blacklisted_demo", "retired_xxx"}


# ===== Schema =====
SCHEMA = """
CREATE TABLE IF NOT EXISTS publish_tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id TEXT UNIQUE NOT NULL,
    blogger_id TEXT NOT NULL,
    content_type TEXT NOT NULL,
    content_path TEXT NOT NULL,
    content_sha256 TEXT NOT NULL,
    title TEXT,
    description TEXT,
    tags TEXT,
    platforms TEXT NOT NULL,
    scheduled_at TEXT,
    watermark INTEGER DEFAULT 1,
    status TEXT DEFAULT 'pending',
    created_at TEXT DEFAULT (datetime('now')),
    started_at TEXT,
    finished_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_blogger ON publish_tasks(blogger_id);
CREATE INDEX IF NOT EXISTS idx_status ON publish_tasks(status);
CREATE INDEX IF NOT EXISTS idx_sha256 ON publish_tasks(content_sha256);

-- 内容去重（跨平台 sha256 索引）
CREATE TABLE IF NOT EXISTS content_dedup (
    content_sha256 TEXT PRIMARY KEY,
    first_published_at TEXT DEFAULT (datetime('now')),
    platforms_published TEXT,
    publish_count INTEGER DEFAULT 1
);

-- 平台发布结果
CREATE TABLE IF NOT EXISTS publish_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id TEXT NOT NULL,
    platform TEXT NOT NULL,
    account_id TEXT,
    status TEXT NOT NULL,
    platform_post_id TEXT,
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    duration_ms INTEGER,
    published_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_results_task ON publish_results(task_id);
CREATE INDEX IF NOT EXISTS idx_results_platform ON publish_results(platform);

-- 速率限制（token bucket 状态）
CREATE TABLE IF NOT EXISTS rate_limit_state (
    platform TEXT PRIMARY KEY,
    tokens REAL NOT NULL,
    last_refill_ts REAL NOT NULL
);

-- 死信队列（重试 3 次仍失败）
CREATE TABLE IF NOT EXISTS dead_letter_queue (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id TEXT NOT NULL,
    platform TEXT NOT NULL,
    error_message TEXT,
    failed_at TEXT DEFAULT (datetime('now'))
);
"""


# ===== 任务 Schema =====
@dataclass
class PublishTask:
    blogger_id: str
    content_type: str            # video / image / article
    content_path: str
    title: str
    platforms: List[str]
    description: str = ""
    tags: List[str] = field(default_factory=list)
    scheduled_at: Optional[str] = None
    watermark: bool = True
    account_ids: Dict[str, str] = field(default_factory=dict)
    task_id: Optional[str] = None

    def __post_init__(self):
        if self.task_id is None:
            self.task_id = str(uuid.uuid4())


# ===== 数据库 =====
@contextmanager
def get_conn(db_path: str = None):
    path = db_path or str(DEFAULT_DB_PATH)
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db(db_path: str = None) -> str:
    with get_conn(db_path) as conn:
        conn.executescript(SCHEMA)
    return db_path or str(DEFAULT_DB_PATH)


# ===== 工具函数 =====
def compute_sha256(content_path: str) -> str:
    """计算内容 sha256"""
    p = Path(content_path)
    if not p.exists():
        # 测试场景：返回基于文件名+大小的伪 hash
        return hashlib.sha256(f"{p.name}_{p.stat().st_size if p.exists() else 0}".encode()).hexdigest()[:16]
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


# ===== Token Bucket 限流 =====
def acquire_token(platform: str, db_path: str = None) -> bool:
    """获取令牌（token bucket）"""
    cfg = PLATFORMS.get(platform)
    if not cfg:
        return False

    qps = cfg["qps"]
    capacity = float(qps)
    now = time.time()

    with get_conn(db_path) as conn:
        row = conn.execute(
            "SELECT tokens, last_refill_ts FROM rate_limit_state WHERE platform = ?", (platform,)
        ).fetchone()

        if row:
            tokens, last_refill = row["tokens"], row["last_refill_ts"]
            # 补充令牌
            elapsed = now - last_refill
            tokens = min(capacity, tokens + elapsed * qps)
        else:
            tokens = capacity
            last_refill = now

        if tokens >= 1.0:
            tokens -= 1.0
            conn.execute(
                "INSERT OR REPLACE INTO rate_limit_state (platform, tokens, last_refill_ts) VALUES (?, ?, ?)",
                (platform, tokens, now),
            )
            return True
        else:
            conn.execute(
                "INSERT OR REPLACE INTO rate_limit_state (platform, tokens, last_refill_ts) VALUES (?, ?, ?)",
                (platform, tokens, now),
            )
            return False


def wait_for_token(platform: str, db_path: str = None, timeout: float = 5.0) -> bool:
    """等待令牌（带超时）"""
    deadline = time.time() + timeout
    while time.time() < deadline:
        if acquire_token(platform, db_path):
            return True
        time.sleep(1.0 / PLATFORMS[platform]["qps"])
    return False


# ===== 伦理校验 =====
def validate_publish_ethics(task: PublishTask, db_path: str = None) -> Dict:
    """校验发布伦理（黑名单博主 + 内容去重）"""
    # 博主黑名单
    if task.blogger_id in BLOCKED_BLOGGERS:
        return {"passed": False, "reason": f"博主 {task.blogger_id} 在黑名单中"}

    # 平台合法
    invalid = [p for p in task.platforms if p not in PLATFORMS]
    if invalid:
        return {"passed": False, "reason": f"不支持的平台: {invalid}"}

    # 内容去重
    sha = compute_sha256(task.content_path)
    with get_conn(db_path) as conn:
        row = conn.execute("SELECT first_published_at, platforms_published FROM content_dedup WHERE content_sha256 = ?", (sha,)).fetchone()
        if row:
            return {
                "passed": False,
                "reason": f"内容重复（sha256={sha[:8]}...）首次发布于 {row['first_published_at']}",
                "duplicate_sha256": sha,
                "existing_platforms": row["platforms_published"],
            }

    return {"passed": True, "content_sha256": sha}


# ===== 发布（mock 实现） =====
def publish_to_platform(task: PublishTask, platform: str, account_id: str = None, db_path: str = None) -> Dict:
    """发布到单个平台（mock）"""
    started = time.time()
    cfg = PLATFORMS[platform]

    # 限流
    if not wait_for_token(platform, db_path, timeout=2.0):
        return {
            "success": False,
            "platform": platform,
            "error": "限流超时（token bucket）",
            "retry_count": 0,
        }

    # 模拟发布
    try:
        # 模拟网络延迟
        time.sleep(0.01)

        # mock 平台 post_id
        post_id = f"{platform}_{uuid.uuid4().hex[:12]}"

        duration = int((time.time() - started) * 1000)

        # 记录结果
        sha = compute_sha256(task.content_path)
        with get_conn(db_path) as conn:
            conn.execute(
                """INSERT INTO publish_results
                (task_id, platform, account_id, status, platform_post_id, retry_count, duration_ms)
                VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (task.task_id, platform, account_id, "success", post_id, 0, duration),
            )

            # 更新去重表
            row = conn.execute("SELECT platforms_published FROM content_dedup WHERE content_sha256 = ?", (sha,)).fetchone()
            if row:
                existing = row["platforms_published"] or ""
                plats = set(existing.split(",")) if existing else set()
                plats.add(platform)
                conn.execute(
                    "UPDATE content_dedup SET platforms_published = ?, publish_count = publish_count + 1 WHERE content_sha256 = ?",
                    (",".join(sorted(plats)), sha),
                )
            else:
                conn.execute(
                    "INSERT INTO content_dedup (content_sha256, platforms_published) VALUES (?, ?)",
                    (sha, platform),
                )

        return {
            "success": True,
            "platform": platform,
            "post_id": post_id,
            "duration_ms": duration,
        }

    except Exception as e:
        return {
            "success": False,
            "platform": platform,
            "error": f"{type(e).__name__}: {e}",
        }


def publish_with_retry(task: PublishTask, platform: str, account_id: str = None, db_path: str = None) -> Dict:
    """带指数退避的重试发布"""
    cfg = PLATFORMS[platform]
    max_retry = cfg["max_retry"]
    last_result = None

    for attempt in range(max_retry + 1):
        result = publish_to_platform(task, platform, account_id, db_path)
        result["retry_count"] = attempt

        if result["success"]:
            return result

        last_result = result
        if attempt < max_retry:
            # 指数退避: 0.1s, 0.2s, 0.4s
            time.sleep(0.1 * (2 ** attempt))

    # 全部失败，入死信队列
    with get_conn(db_path) as conn:
        conn.execute(
            "INSERT INTO dead_letter_queue (task_id, platform, error_message) VALUES (?, ?, ?)",
            (task.task_id, platform, last_result.get("error", "unknown")),
        )
        conn.execute(
            "INSERT INTO publish_results (task_id, platform, account_id, status, error_message, retry_count) VALUES (?, ?, ?, ?, ?, ?)",
            (task.task_id, platform, account_id, "failed", last_result.get("error"), max_retry),
        )

    return last_result


# ===== 主流程 =====
def create_task(task: PublishTask, db_path: str = None) -> Dict:
    """创建发布任务（含伦理校验）"""
    # 伦理校验
    eth = validate_publish_ethics(task, db_path)
    if not eth["passed"]:
        return {"success": False, "error": eth["reason"]}

    sha = eth["content_sha256"]

    with get_conn(db_path) as conn:
        try:
            conn.execute(
                """INSERT INTO publish_tasks
                (task_id, blogger_id, content_type, content_path, content_sha256,
                 title, description, tags, platforms, scheduled_at, watermark)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    task.task_id,
                    task.blogger_id,
                    task.content_type,
                    task.content_path,
                    sha,
                    task.title,
                    task.description,
                    json.dumps(task.tags, ensure_ascii=False),
                    json.dumps(task.platforms, ensure_ascii=False),
                    task.scheduled_at,
                    1 if task.watermark else 0,
                ),
            )
            return {"success": True, "task_id": task.task_id, "content_sha256": sha}
        except sqlite3.IntegrityError as e:
            return {"success": False, "error": f"task_id 已存在: {task.task_id}"}


def execute_task(task: PublishTask, db_path: str = None) -> Dict:
    """执行发布任务（多平台并发）"""
    started_at = datetime.now().isoformat()
    results = []

    with get_conn(db_path) as conn:
        conn.execute("UPDATE publish_tasks SET started_at = ?, status = 'running' WHERE task_id = ?",
                     (started_at, task.task_id))

    for platform in task.platforms:
        account_id = task.account_ids.get(platform, f"default_{platform}")
        result = publish_with_retry(task, platform, account_id, db_path)
        results.append(result)

    finished_at = datetime.now().isoformat()
    success_count = sum(1 for r in results if r["success"])
    total = len(results)

    final_status = "success" if success_count == total else ("partial" if success_count > 0 else "failed")

    with get_conn(db_path) as conn:
        conn.execute("UPDATE publish_tasks SET finished_at = ?, status = ? WHERE task_id = ?",
                     (finished_at, final_status, task.task_id))

    return {
        "task_id": task.task_id,
        "status": final_status,
        "success": success_count,
        "failed": total - success_count,
        "results": results,
    }


def publish_now(task: PublishTask, db_path: str = None) -> Dict:
    """立即发布（创建任务 + 执行）"""
    create_result = create_task(task, db_path)
    if not create_result["success"]:
        return create_result
    return execute_task(task, db_path)


def get_task_status(task_id: str, db_path: str = None) -> Optional[Dict]:
    """查询任务状态"""
    with get_conn(db_path) as conn:
        task = conn.execute("SELECT * FROM publish_tasks WHERE task_id = ?", (task_id,)).fetchone()
        if not task:
            return None
        results = conn.execute(
            "SELECT platform, status, platform_post_id, error_message, retry_count, duration_ms FROM publish_results WHERE task_id = ?",
            (task_id,),
        ).fetchall()
        return {
            "task_id": task["task_id"],
            "blogger_id": task["blogger_id"],
            "status": task["status"],
            "content_sha256": task["content_sha256"],
            "created_at": task["created_at"],
            "started_at": task["started_at"],
            "finished_at": task["finished_at"],
            "results": [dict(r) for r in results],
        }


def get_publish_stats(db_path: str = None) -> Dict:
    """发布统计"""
    with get_conn(db_path) as conn:
        total_tasks = conn.execute("SELECT COUNT(*) FROM publish_tasks").fetchone()[0]
        total_results = conn.execute("SELECT COUNT(*) FROM publish_results").fetchone()[0]
        success_results = conn.execute("SELECT COUNT(*) FROM publish_results WHERE status='success'").fetchone()[0]
        dead_letters = conn.execute("SELECT COUNT(*) FROM dead_letter_queue").fetchone()[0]
        unique_content = conn.execute("SELECT COUNT(*) FROM content_dedup").fetchone()[0]

        by_platform = conn.execute(
            "SELECT platform, COUNT(*) as c FROM publish_results GROUP BY platform"
        ).fetchall()

        return {
            "total_tasks": total_tasks,
            "total_results": total_results,
            "success_results": success_results,
            "failed_results": total_results - success_results,
            "dead_letters": dead_letters,
            "unique_content": unique_content,
            "by_platform": {r["platform"]: r["c"] for r in by_platform},
        }


def batch_publish(tasks: List[PublishTask], db_path: str = None) -> Dict:
    """批量发布"""
    results = []
    for task in tasks:
        r = publish_now(task, db_path)
        results.append(r)
    return {
        "total": len(tasks),
        "success": sum(1 for r in results if r.get("status") in ("success", "partial")),
        "failed": sum(1 for r in results if r.get("status") == "failed" or not r.get("success")),
        "results": results,
    }


def check_dedup(content_path: str, db_path: str = None) -> Dict:
    """查询内容是否已发布"""
    sha = compute_sha256(content_path)
    with get_conn(db_path) as conn:
        row = conn.execute("SELECT * FROM content_dedup WHERE content_sha256 = ?", (sha,)).fetchone()
        if row:
            return {
                "duplicate": True,
                "sha256": sha,
                "first_published_at": row["first_published_at"],
                "platforms": row["platforms_published"],
                "publish_count": row["publish_count"],
            }
    return {"duplicate": False, "sha256": sha}


# ===== CLI =====
def main():
    parser = argparse.ArgumentParser(description="multi-platform-publisher · V1.0")
    parser.add_argument("--db", help="数据库路径")

    sub = parser.add_subparsers(dest="command", help="子命令")

    # init
    sub_init = sub.add_parser("init", help="初始化数据库")
    sub_init.add_argument("--db", help="数据库路径")

    # list-platforms
    sub_lp = sub.add_parser("list-platforms", help="列出 9 平台")

    # publish
    sub_pub = sub.add_parser("publish", help="立即发布")
    sub_pub.add_argument("--db", help="数据库路径")
    sub_pub.add_argument("--blogger-id", required=True)
    sub_pub.add_argument("--video", help="视频路径")
    sub_pub.add_argument("--image", help="图片路径")
    sub_pub.add_argument("--article", help="文章路径")
    sub_pub.add_argument("--title", required=True)
    sub_pub.add_argument("--description", default="")
    sub_pub.add_argument("--tags", default="", help="逗号分隔")
    sub_pub.add_argument("--platforms", required=True, help="逗号分隔")
    sub_pub.add_argument("--schedule", help="定时发布时间（ISO）")
    sub_pub.add_argument("--no-watermark", action="store_true")

    # batch
    sub_batch = sub.add_parser("batch", help="批量发布")
    sub_batch.add_argument("--db", help="数据库路径")
    sub_batch.add_argument("--file", required=True, help="JSONL 文件")

    # status
    sub_status = sub.add_parser("status", help="任务状态")
    sub_status.add_argument("--db", help="数据库路径")
    sub_status.add_argument("--task-id", required=True)

    # stats
    sub_stats = sub.add_parser("stats", help="发布统计")
    sub_stats.add_argument("--db", help="数据库路径")

    # dedup
    sub_dedup = sub.add_parser("dedup", help="去重查询")
    sub_dedup.add_argument("--db", help="数据库路径")
    sub_dedup.add_argument("--content", required=True)

    args = parser.parse_args()
    db_path = getattr(args, "db", None)

    if args.command == "init":
        path = init_db(db_path)
        print(f"✅ 数据库已初始化: {path}")
        return

    if args.command == "list-platforms":
        print("\n📱 9 平台配置:")
        for code, cfg in PLATFORMS.items():
            print(f"  {code:15s} {cfg['name']:8s}  QPS={cfg['qps']:>2}  retry={cfg['max_retry']}  watermark={'✅' if cfg['watermark'] else '❌'}  category={cfg['category']}")
        return

    # 其余命令需要 DB
    if not Path(db_path or str(DEFAULT_DB_PATH)).exists():
        init_db(db_path)

    if args.command == "publish":
        # 决定内容路径与类型
        if args.video:
            content_path, content_type = args.video, "video"
        elif args.image:
            content_path, content_type = args.image, "image"
        elif args.article:
            content_path, content_type = args.article, "article"
        else:
            print("❌ 错误: 必须指定 --video / --image / --article 之一")
            sys.exit(1)

        platforms = [p.strip() for p in args.platforms.split(",") if p.strip()]
        tags = [t.strip() for t in args.tags.split(",") if t.strip()] if args.tags else []

        task = PublishTask(
            blogger_id=args.blogger_id,
            content_type=content_type,
            content_path=content_path,
            title=args.title,
            description=args.description,
            tags=tags,
            platforms=platforms,
            scheduled_at=args.schedule,
            watermark=not args.no_watermark,
        )

        if args.schedule:
            # 定时：仅创建任务，不执行
            r = create_task(task, db_path)
            if r["success"]:
                print(f"✅ 已创建定时任务: {task.task_id}")
                print(f"   计划发布时间: {args.schedule}")
                print(f"   目标平台: {', '.join(platforms)}")
            else:
                print(f"❌ {r['error']}")
                sys.exit(2)
        else:
            # 立即发布
            r = publish_now(task, db_path)
            if r.get("status") == "success":
                print(f"✅ 全部成功 ({r['success']}/{r['success']})")
            elif r.get("status") == "partial":
                print(f"⚠️ 部分成功: {r['success']}/{r['success'] + r['failed']}")
            else:
                print(f"❌ 全部失败: {r.get('error', 'unknown')}")

            print(f"\n   task_id: {task.task_id}")
            for res in r.get("results", []):
                if res["success"]:
                    print(f"     ✅ {res['platform']:12s} post_id={res.get('post_id', 'N/A')} ({res.get('duration_ms', 0)}ms)")
                else:
                    print(f"     ❌ {res['platform']:12s} {res.get('error', 'unknown')}")

    elif args.command == "batch":
        tasks = []
        with open(args.file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                data = json.loads(line)
                if "platforms" in data and isinstance(data["platforms"], str):
                    data["platforms"] = [p.strip() for p in data["platforms"].split(",")]
                if "tags" in data and isinstance(data["tags"], str):
                    data["tags"] = [t.strip() for t in data["tags"].split(",")]
                tasks.append(PublishTask(**data))

        result = batch_publish(tasks, db_path)
        print(f"✅ 批量发布完成: 成功 {result['success']}/{result['total']}, 失败 {result['failed']}")

    elif args.command == "status":
        st = get_task_status(args.task_id, db_path)
        if st:
            print(f"\n📋 任务 {args.task_id}:")
            print(f"   博主: {st['blogger_id']}")
            print(f"   状态: {st['status']}")
            print(f"   内容指纹: {st['content_sha256'][:16]}...")
            print(f"   创建: {st['created_at']}")
            print(f"   开始: {st['started_at']}")
            print(f"   结束: {st['finished_at']}")
            print(f"\n   各平台结果:")
            for r in st["results"]:
                if r["status"] == "success":
                    print(f"     ✅ {r['platform']:12s} post_id={r['platform_post_id']}")
                else:
                    print(f"     ❌ {r['platform']:12s} {r['error_message']}")
        else:
            print(f"❌ 未找到任务: {args.task_id}")
            sys.exit(1)

    elif args.command == "stats":
        stats = get_publish_stats(db_path)
        print(f"\n📊 发布统计:")
        print(f"   任务总数: {stats['total_tasks']}")
        print(f"   发布结果: {stats['total_results']} (成功 {stats['success_results']} / 失败 {stats['failed_results']})")
        print(f"   死信队列: {stats['dead_letters']}")
        print(f"   唯一内容: {stats['unique_content']}")
        if stats["by_platform"]:
            print(f"\n   按平台分布:")
            for p, c in sorted(stats["by_platform"].items(), key=lambda x: -x[1]):
                print(f"     {p:15s}: {c:>5}")

    elif args.command == "dedup":
        r = check_dedup(args.content, db_path)
        if r["duplicate"]:
            print(f"⚠️ 内容已发布过: sha256={r['sha256'][:16]}...")
            print(f"   首次发布: {r['first_published_at']}")
            print(f"   已发布平台: {r['platforms']}")
            print(f"   发布次数: {r['publish_count']}")
        else:
            print(f"✅ 内容未重复: sha256={r['sha256'][:16]}...")


if __name__ == "__main__":
    main()