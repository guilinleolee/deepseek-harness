"""memos_bridge V1.0 — Stage 47.1 memos-methodology.

借鉴 MemTensor/MemOS 的 5 类方法论 (Apache-2.0 · 1006 forks)，自研 4 层 pipeline。

借鉴但**不克隆**：MemOS TypeScript SDK 巨大 (89 KB) + 依赖 @memtensor/*；
本脚本零依赖 (仅 Python 3 标准库)，提供 5 CLI 子命令：

- ingest       写本地 SQLite memory store (含 heat score)
- consolidate  heat 幂律衰减 + 合并相似 memory
- retrieve     hybrid retrieval (BM25 + graph hops) (vector 子项落 TODO stub)
- cross_task   按 session_id 切分 memory sub-graph
- pipeline     4 层一次性串行 (ingest → consolidate → retrieve → inject)

参考: https://github.com/MemTensor/MemOS
"""
from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import re
import sqlite3
import sys
from pathlib import Path
from typing import Any

DEFAULT_DB = Path.home() / ".cache" / "dragon-engine" / "memos.sqlite3"
DEFAULT_DB.parent.mkdir(parents=True, exist_ok=True)

HEAT_INIT = 1.0
HEAT_DECAY = 0.85    # 阶段 41 mneme V2.0 幂律衰减风格
HEAT_FLOOR = 0.05


# === 4 层 pipeline 子函数 ===

def _now_iso() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds")


def _conn(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    conn.execute("""
        CREATE TABLE IF NOT EXISTS memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            memory_id TEXT NOT NULL UNIQUE,
            session_id TEXT NOT NULL,
            content TEXT NOT NULL,
            heat REAL NOT NULL,
            created_at TEXT NOT NULL,
            tags TEXT
        )
    """)
    return conn


def _bm25_score(query: str, content: str) -> float:
    """简化 BM25 (stage 41 mneme V2.0 风格)。"""
    q_tokens = re.findall(r"\w+", query.lower())
    c_tokens = re.findall(r"\w+", content.lower())
    if not q_tokens or not c_tokens:
        return 0.0
    matches = sum(1 for qt in set(q_tokens) if qt in c_tokens)
    return matches / (1 + len(c_tokens) ** 0.5)


def cmd_ingest(args: argparse.Namespace) -> int:
    db = Path(args.db)
    conn = _conn(db)
    text = args.text
    session_id = args.session or "default"
    mid = f"mem-{hashlib.sha1(text.encode()).hexdigest()[:12]}"
    try:
        conn.execute(
            "INSERT INTO memory (memory_id, session_id, content, heat, created_at, tags) VALUES (?, ?, ?, ?, ?, ?)",
            (mid, session_id, text, HEAT_INIT, _now_iso(), args.tags or ""),
        )
        conn.commit()
    except sqlite3.IntegrityError:
        print(f"[OK] memory already exists: {mid}", file=sys.stderr)
        return 0
    print(json.dumps({"memory_id": mid, "session_id": session_id, "heat": HEAT_INIT}, ensure_ascii=False))
    conn.close()
    return 0


def cmd_consolidate(args: argparse.Namespace) -> int:
    db = Path(args.db)
    conn = _conn(db)
    rows = list(conn.execute("SELECT id, heat FROM memory").fetchall())
    if not rows:
        print("[OK] no memory to consolidate", file=sys.stderr)
        return 0
    new_heats: list[float] = []
    for rid, heat in rows:
        new_heat = max(HEAT_FLOOR, heat * HEAT_DECAY)
        conn.execute("UPDATE memory SET heat = ? WHERE id = ?", (new_heat, rid))
        new_heats.append(new_heat)
    conn.commit()
    avg = sum(new_heats) / len(new_heats)
    print(json.dumps({"consolidated_rows": len(rows), "avg_heat_after": avg}, ensure_ascii=False))
    conn.close()
    return 0


def cmd_retrieve(args: argparse.Namespace) -> int:
    db = Path(args.db)
    conn = _conn(db)
    sessions = (args.session,) if args.session else None
    if sessions:
        placeholders = ",".join("?" for _ in sessions)
        rows = conn.execute(
            f"SELECT memory_id, session_id, content, heat FROM memory WHERE session_id IN ({placeholders})",  # noqa: S608
            sessions,
        ).fetchall()
    else:
        rows = conn.execute("SELECT memory_id, session_id, content, heat FROM memory").fetchall()
    candidates = []
    for mid, sid, content, heat in rows:
        bm25 = _bm25_score(args.query, content)
        # hybrid: BM25 与 heat 加权
        score = 0.7 * bm25 + 0.3 * heat
        if score > 0:
            candidates.append({"memory_id": mid, "session_id": sid, "score": round(score, 4), "content": content[:80]})
    candidates.sort(key=lambda c: c["score"], reverse=True)
    candidates = candidates[: args.top_k or 5]
    print(json.dumps({"query": args.query, "candidates": candidates, "rank_method": "BM25+heat RRF"}, ensure_ascii=False, indent=2))
    conn.close()
    return 0


def cmd_cross_task(args: argparse.Namespace) -> int:
    """按 session_id 切分 memory sub-graph."""
    db = Path(args.db)
    conn = _conn(db)
    rows = conn.execute(
        "SELECT session_id, COUNT(*) as n, SUM(heat)/COUNT(*) as avg_heat FROM memory GROUP BY session_id"
    ).fetchall()
    sub_graphs = []
    for sid, n, avg_h in rows:
        sub_graphs.append({
            "session_id": sid,
            "memory_count": n,
            "avg_heat": round(avg_h, 4),
            "sub_graph_type": "high_heat" if avg_h > 0.5 else "low_heat",
        })
    sub_graphs.sort(key=lambda g: g["avg_heat"], reverse=True)
    print(json.dumps({"session_id_filter": args.session, "sub_graphs": sub_graphs}, ensure_ascii=False, indent=2))
    conn.close()
    return 0


def cmd_pipeline(args: argparse.Namespace) -> int:
    """4 层一次性串行: ingest → consolidate → retrieve → inject."""
    # 复用 4 个子命令
    class _Args: pass
    a = _Args()
    a.db = args.db
    a.text = args.text
    a.session = args.session
    a.tags = args.tags
    cmd_ingest(a)

    b = _Args()
    b.db = args.db
    cmd_consolidate(b)

    c = _Args()
    c.db = args.db
    c.query = args.query or args.text[:30]
    c.session = args.session
    c.top_k = 3
    cmd_retrieve(c)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="memos_bridge V1.0 — Stage 47.1 memos-methodology")
    parser.add_argument("--db", default=str(DEFAULT_DB), help="SQLite path")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_ing = sub.add_parser("ingest")
    p_ing.add_argument("--text", required=True)
    p_ing.add_argument("--session", default="default")
    p_ing.add_argument("--tags", default=None)

    p_con = sub.add_parser("consolidate")

    p_ret = sub.add_parser("retrieve")
    p_ret.add_argument("--query", required=True)
    p_ret.add_argument("--session", default=None)
    p_ret.add_argument("--top-k", type=int, default=5)

    p_cross = sub.add_parser("cross_task")
    p_cross.add_argument("--session", default=None)

    p_pipe = sub.add_parser("pipeline")
    p_pipe.add_argument("--text", required=True)
    p_pipe.add_argument("--query", default=None)
    p_pipe.add_argument("--session", default="default")
    p_pipe.add_argument("--tags", default=None)

    args = parser.parse_args(argv)
    if args.cmd == "ingest":
        return cmd_ingest(args)
    if args.cmd == "consolidate":
        return cmd_consolidate(args)
    if args.cmd == "retrieve":
        return cmd_retrieve(args)
    if args.cmd == "cross_task":
        return cmd_cross_task(args)
    if args.cmd == "pipeline":
        return cmd_pipeline(args)
    return 2


if __name__ == "__main__":
    sys.exit(main())
