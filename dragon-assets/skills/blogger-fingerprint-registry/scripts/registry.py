"""
blogger-fingerprint-registry 指纹库核心 · V1.0
SQLite 后端 · CRUD + 全文搜索 + 伦理护栏

依赖:
    - 标准库 sqlite3
"""

import argparse
import csv
import json
import sqlite3
import sys
import time
from contextlib import contextmanager
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional, Dict, List, Iterable


# ===== 默认路径 =====
DEFAULT_DB_PATH = Path.home() / ".claude" / "skills" / "blogger-fingerprint-registry" / "registry.db"

# ===== 10 套博主模板（继承自 voxcpm-voice-distillery）=====
PRESET_TEMPLATES = [
    "治愈系", "知识区", "搞笑博主", "带货主播", "影视解说",
    "美食博主", "科技评测", "二次元", "母婴", "古风",
]

# ===== 30 语言 + 9 方言 =====
SUPPORTED_LANGUAGES = ["zh", "en", "ja", "ko", "es", "fr", "de", "ru", "ar", "hi", "pt", "it", "th", "vi", "id", "ms", "tl", "nl", "pl", "tr", "uk", "cs", "el", "sv", "no", "da", "fi", "he", "hu", "bn"]
SUPPORTED_DIALECTS_ZH = ["普通话", "粤语", "川话", "东北话", "上海话", "闽南语", "湖南话", "山东话", "陕西话"]

# ===== 黑名单关键词（撤回/政治人物）=====
BLOCKED_KEYWORDS = ["习近平", "Trump 特朗普", "Biden 拜登", "马英九", "蔡英文"]

# ===== 默认 consent 有效期 =====
DEFAULT_CONSENT_DAYS = 365


# ===== Schema =====
SCHEMA = """
CREATE TABLE IF NOT EXISTS fingerprints (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    blogger_id TEXT UNIQUE NOT NULL,
    blogger_name TEXT NOT NULL,
    owner_id TEXT NOT NULL,
    matched_template TEXT,
    language TEXT DEFAULT 'zh',
    dialect TEXT,
    -- 6 维指纹
    timbre_label TEXT,
    speed_label TEXT,
    speed_chars_per_sec REAL,
    dialect_detected TEXT,
    emotion_label TEXT,
    prosody_f0_mean REAL,
    vocabulary_top TEXT,
    -- 文件路径
    audio_path TEXT,
    fingerprint_path TEXT,
    lora_path TEXT,
    -- 伦理
    consent_file TEXT NOT NULL,
    consent_expires_at TEXT,
    watermark_enabled INTEGER DEFAULT 1,
    -- 元数据
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    retired_at TEXT,
    retire_reason TEXT
);

CREATE INDEX IF NOT EXISTS idx_blogger_name ON fingerprints(blogger_name);
CREATE INDEX IF NOT EXISTS idx_template ON fingerprints(matched_template);
CREATE INDEX IF NOT EXISTS idx_language ON fingerprints(language);
CREATE INDEX IF NOT EXISTS idx_owner ON fingerprints(owner_id);
CREATE INDEX IF NOT EXISTS idx_active ON fingerprints(retired_at);

-- 全文搜索（FTS5）
CREATE VIRTUAL TABLE IF NOT EXISTS fingerprints_fts USING fts5(
    blogger_id, blogger_name, matched_template,
    content='fingerprints', content_rowid='id'
);

-- 审计日志
CREATE TABLE IF NOT EXISTS audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    action TEXT NOT NULL,        -- add / get / retire / search
    blogger_id TEXT,
    actor TEXT,
    timestamp TEXT DEFAULT (datetime('now')),
    details TEXT
);
"""


# ===== 指纹记录 =====
@dataclass
class Fingerprint:
    blogger_id: str
    blogger_name: str
    owner_id: str
    consent_file: str
    matched_template: Optional[str] = None
    language: str = "zh"
    dialect: Optional[str] = None
    timbre_label: Optional[str] = None
    speed_label: Optional[str] = None
    speed_chars_per_sec: Optional[float] = None
    dialect_detected: Optional[str] = None
    emotion_label: Optional[str] = None
    prosody_f0_mean: Optional[float] = None
    vocabulary_top: Optional[str] = None
    audio_path: Optional[str] = None
    fingerprint_path: Optional[str] = None
    lora_path: Optional[str] = None
    consent_expires_at: Optional[str] = None
    watermark_enabled: bool = True


# ===== 伦理校验 =====
def validate_consent_file(consent_file: str) -> Dict:
    """校验同意书（必须存在 + 含同意关键词）"""
    p = Path(consent_file)
    if not p.exists():
        return {"passed": False, "reason": f"同意书不存在: {consent_file}"}

    try:
        content = p.read_text(encoding="utf-8")
    except Exception as e:
        return {"passed": False, "reason": f"无法读取: {e}"}

    if not content.strip():
        return {"passed": False, "reason": "同意书为空"}

    # 至少含一个同意关键词（中/英）
    consent_keywords = ["I consent", "i consent", "我同意", "已授权", "consent"]
    if not any(kw in content for kw in consent_keywords):
        return {"passed": False, "reason": f"同意书未含 consent 关键词"}

    return {"passed": True, "reason": "OK"}


def check_blacklist(text: str) -> List[str]:
    """检查黑名单关键词"""
    found = []
    for kw in BLOCKED_KEYWORDS:
        if kw in text:
            found.append(kw)
    return found


# ===== 数据库连接 =====
@contextmanager
def get_conn(db_path: str = None):
    """获取数据库连接（自动 commit/close）"""
    path = db_path or str(DEFAULT_DB_PATH)
    # 确保父目录存在
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db(db_path: str = None) -> str:
    """初始化数据库"""
    with get_conn(db_path) as conn:
        conn.executescript(SCHEMA)
    return db_path or str(DEFAULT_DB_PATH)


def log_audit(conn: sqlite3.Connection, action: str, blogger_id: str, actor: str = "system", details: str = ""):
    """写审计日志"""
    conn.execute(
        "INSERT INTO audit_log (action, blogger_id, actor, details) VALUES (?, ?, ?, ?)",
        (action, blogger_id, actor, details),
    )


# ===== CRUD =====
def add_fingerprint(fp: Fingerprint, db_path: str = None) -> Dict:
    """添加指纹"""
    # 伦理校验
    eth = validate_consent_file(fp.consent_file)
    if not eth["passed"]:
        return {"success": False, "error": f"伦理校验失败: {eth['reason']}"}

    # 黑名单
    bl = check_blacklist(fp.blogger_name) + check_blacklist(fp.owner_id)
    if bl:
        return {"success": False, "error": f"博主名/持有者含黑名单关键词: {bl}"}

    # 模板校验
    if fp.matched_template and fp.matched_template not in PRESET_TEMPLATES:
        return {"success": False, "error": f"未知模板: {fp.matched_template}（可选: {PRESET_TEMPLATES}）"}

    # 默认 consent 过期时间
    if not fp.consent_expires_at:
        from datetime import datetime, timedelta
        fp.consent_expires_at = (datetime.now() + timedelta(days=DEFAULT_CONSENT_DAYS)).isoformat()

    with get_conn(db_path) as conn:
        try:
            conn.execute(
                """INSERT INTO fingerprints
                (blogger_id, blogger_name, owner_id, matched_template, language, dialect,
                 timbre_label, speed_label, speed_chars_per_sec, dialect_detected, emotion_label,
                 prosody_f0_mean, vocabulary_top, audio_path, fingerprint_path, lora_path,
                 consent_file, consent_expires_at, watermark_enabled)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (fp.blogger_id, fp.blogger_name, fp.owner_id, fp.matched_template, fp.language, fp.dialect,
                 fp.timbre_label, fp.speed_label, fp.speed_chars_per_sec, fp.dialect_detected, fp.emotion_label,
                 fp.prosody_f0_mean, fp.vocabulary_top, fp.audio_path, fp.fingerprint_path, fp.lora_path,
                 fp.consent_file, fp.consent_expires_at, 1 if fp.watermark_enabled else 0),
            )
            # FTS 索引
            conn.execute(
                "INSERT INTO fingerprints_fts (rowid, blogger_id, blogger_name, matched_template) VALUES (last_insert_rowid(), ?, ?, ?)",
                (fp.blogger_id, fp.blogger_name, fp.matched_template or ""),
            )
            log_audit(conn, "add", fp.blogger_id, details=f"template={fp.matched_template}")
            return {"success": True, "blogger_id": fp.blogger_id}
        except sqlite3.IntegrityError as e:
            return {"success": False, "error": f"blogger_id 已存在: {fp.blogger_id} ({e})"}


def get_fingerprint(blogger_id: str, db_path: str = None) -> Optional[Dict]:
    """获取指纹（不含已撤回）"""
    with get_conn(db_path) as conn:
        row = conn.execute(
            "SELECT * FROM fingerprints WHERE blogger_id = ? AND retired_at IS NULL",
            (blogger_id,),
        ).fetchone()
        if row:
            log_audit(conn, "get", blogger_id)
            return dict(row)
        return None


def search_fingerprints(
    keyword: Optional[str] = None,
    template: Optional[str] = None,
    language: Optional[str] = None,
    dialect: Optional[str] = None,
    owner_id: Optional[str] = None,
    include_retired: bool = False,
    limit: int = 20,
    db_path: str = None,
) -> List[Dict]:
    """搜索指纹"""
    sql = "SELECT * FROM fingerprints WHERE 1=1"
    params = []

    if not include_retired:
        sql += " AND retired_at IS NULL"

    if keyword:
        sql += " AND (blogger_name LIKE ? OR blogger_id LIKE ?)"
        params.extend([f"%{keyword}%", f"%{keyword}%"])

    if template:
        sql += " AND matched_template = ?"
        params.append(template)

    if language:
        sql += " AND language = ?"
        params.append(language)

    if dialect:
        sql += " AND dialect = ?"
        params.append(dialect)

    if owner_id:
        sql += " AND owner_id = ?"
        params.append(owner_id)

    sql += f" ORDER BY created_at DESC LIMIT {limit}"

    with get_conn(db_path) as conn:
        rows = conn.execute(sql, params).fetchall()
        log_audit(conn, "search", "?", details=f"keyword={keyword}, template={template}, found={len(rows)}")
        return [dict(r) for r in rows]


def retire_fingerprint(blogger_id: str, reason: str, db_path: str = None) -> Dict:
    """撤回（标记黑名单）"""
    with get_conn(db_path) as conn:
        row = conn.execute("SELECT id FROM fingerprints WHERE blogger_id = ?", (blogger_id,)).fetchone()
        if not row:
            return {"success": False, "error": f"博主不存在: {blogger_id}"}

        conn.execute(
            "UPDATE fingerprints SET retired_at = datetime('now'), retire_reason = ?, updated_at = datetime('now') WHERE blogger_id = ?",
            (reason, blogger_id),
        )
        log_audit(conn, "retire", blogger_id, details=f"reason={reason}")
        return {"success": True, "blogger_id": blogger_id, "reason": reason}


def get_stats(db_path: str = None) -> Dict:
    """统计信息"""
    with get_conn(db_path) as conn:
        total = conn.execute("SELECT COUNT(*) FROM fingerprints").fetchone()[0]
        active = conn.execute("SELECT COUNT(*) FROM fingerprints WHERE retired_at IS NULL").fetchone()[0]
        retired = total - active

        by_template = conn.execute(
            "SELECT matched_template, COUNT(*) as c FROM fingerprints WHERE retired_at IS NULL GROUP BY matched_template"
        ).fetchall()

        by_language = conn.execute(
            "SELECT language, COUNT(*) as c FROM fingerprints WHERE retired_at IS NULL GROUP BY language"
        ).fetchall()

        return {
            "total": total,
            "active": active,
            "retired": retired,
            "by_template": {r["matched_template"] or "未分类": r["c"] for r in by_template},
            "by_language": {r["language"]: r["c"] for r in by_language},
        }


def import_from_jsonl(file_path: str, db_path: str = None) -> Dict:
    """从 JSONL 批量导入"""
    added = 0
    skipped = 0
    errors = []

    with open(file_path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                fp = Fingerprint(**data)
                result = add_fingerprint(fp, db_path)
                if result["success"]:
                    added += 1
                else:
                    skipped += 1
                    errors.append(f"line {line_num}: {result['error']}")
            except Exception as e:
                skipped += 1
                errors.append(f"line {line_num}: {type(e).__name__}: {e}")

    return {"added": added, "skipped": skipped, "errors": errors[:10]}


# ===== CLI =====
def main():
    parser = argparse.ArgumentParser(description="blogger-fingerprint-registry · V1.0")
    parser.add_argument("--db", help="数据库路径")

    sub = parser.add_subparsers(dest="command", help="子命令")

    # init
    sub_init = sub.add_parser("init", help="初始化数据库")
    sub_init.add_argument("--db", help="数据库路径")

    # add
    sub_add = sub.add_parser("add", help="添加博主")
    sub_add.add_argument("--db", help="数据库路径")
    sub_add.add_argument("--blogger-id", required=True)
    sub_add.add_argument("--blogger-name", required=True)
    sub_add.add_argument("--owner-id", required=True)
    sub_add.add_argument("--consent-file", required=True)
    sub_add.add_argument("--matched-template", choices=PRESET_TEMPLATES)
    sub_add.add_argument("--language", default="zh")
    sub_add.add_argument("--dialect")
    sub_add.add_argument("--timbre-label")
    sub_add.add_argument("--speed-label")
    sub_add.add_argument("--emotion-label")
    sub_add.add_argument("--audio")
    sub_add.add_argument("--fingerprint")
    sub_add.add_argument("--lora")

    # get
    sub_get = sub.add_parser("get", help="获取博主")
    sub_get.add_argument("--db", help="数据库路径")
    sub_get.add_argument("--blogger-id", required=True)

    # search
    sub_search = sub.add_parser("search", help="搜索博主")
    sub_search.add_argument("--db", help="数据库路径")
    sub_search.add_argument("--keyword")
    sub_search.add_argument("--template", choices=PRESET_TEMPLATES)
    sub_search.add_argument("--language")
    sub_search.add_argument("--dialect")
    sub_search.add_argument("--owner-id")
    sub_search.add_argument("--limit", type=int, default=20)
    sub_search.add_argument("--include-retired", action="store_true")

    # retire
    sub_retire = sub.add_parser("retire", help="撤回博主")
    sub_retire.add_argument("--db", help="数据库路径")
    sub_retire.add_argument("--blogger-id", required=True)
    sub_retire.add_argument("--reason", default="revoked_consent")

    # stats
    sub_stats = sub.add_parser("stats", help="统计")
    sub_stats.add_argument("--db", help="数据库路径")

    # import
    sub_import = sub.add_parser("import", help="批量导入")
    sub_import.add_argument("--db", help="数据库路径")
    sub_import.add_argument("--file", required=True, help="JSONL 文件")

    # list-presets
    sub_presets = sub.add_parser("list-presets", help="列出模板")

    args = parser.parse_args()

    if args.command == "list-presets":
        print("\n🎨 10 套博主音色模板:")
        for p in PRESET_TEMPLATES:
            print(f"  - {p}")
        return

    if not args.command:
        parser.print_help()
        return

    # 初始化
    if args.command == "init":
        path = init_db(args.db)
        print(f"✅ 数据库已初始化: {path}")
        return

    # 其余命令需要 DB
    if not Path(args.db or str(DEFAULT_DB_PATH)).exists():
        init_db(args.db)

    if args.command == "add":
        fp = Fingerprint(
            blogger_id=args.blogger_id,
            blogger_name=args.blogger_name,
            owner_id=args.owner_id,
            consent_file=args.consent_file,
            matched_template=args.matched_template,
            language=args.language,
            dialect=args.dialect,
            timbre_label=args.timbre_label,
            speed_label=args.speed_label,
            emotion_label=args.emotion_label,
            audio_path=args.audio,
            fingerprint_path=args.fingerprint,
            lora_path=args.lora,
        )
        result = add_fingerprint(fp, args.db)
        if result["success"]:
            print(f"✅ 已添加: {args.blogger_id} ({args.blogger_name})")
        else:
            print(f"❌ {result['error']}")
            sys.exit(2)

    elif args.command == "get":
        row = get_fingerprint(args.blogger_id, args.db)
        if row:
            print(json.dumps(row, ensure_ascii=False, indent=2))
        else:
            print(f"❌ 未找到或已撤回: {args.blogger_id}")
            sys.exit(1)

    elif args.command == "search":
        results = search_fingerprints(
            keyword=args.keyword,
            template=args.template,
            language=args.language,
            dialect=args.dialect,
            owner_id=args.owner_id,
            include_retired=args.include_retired,
            limit=args.limit,
            db_path=args.db,
        )
        print(f"🔍 找到 {len(results)} 条结果:")
        for r in results:
            print(f"  - {r['blogger_id']:30s} | {r['blogger_name']:20s} | {r['matched_template'] or '未分类':8s} | {r['language']}")

    elif args.command == "retire":
        result = retire_fingerprint(args.blogger_id, args.reason, args.db)
        if result["success"]:
            print(f"✅ 已撤回: {args.blogger_id} (原因: {args.reason})")
        else:
            print(f"❌ {result['error']}")

    elif args.command == "stats":
        stats = get_stats(args.db)
        print(f"\n📊 指纹库统计:")
        print(f"   总数: {stats['total']:,} | 活跃: {stats['active']:,} | 撤回: {stats['retired']:,}")
        print(f"\n   按模板分布:")
        for tmpl, count in sorted(stats["by_template"].items(), key=lambda x: -x[1]):
            print(f"     {tmpl:8s}: {count:>6,}")
        print(f"\n   按语言分布 (top 10):")
        for lang, count in sorted(stats["by_language"].items(), key=lambda x: -x[1])[:10]:
            print(f"     {lang:6s}: {count:>6,}")

    elif args.command == "import":
        result = import_from_jsonl(args.file, args.db)
        print(f"✅ 导入完成: 新增 {result['added']} 条, 跳过 {result['skipped']} 条")
        if result["errors"]:
            print(f"   错误样例:")
            for e in result["errors"][:5]:
                print(f"     - {e}")


if __name__ == "__main__":
    main()
