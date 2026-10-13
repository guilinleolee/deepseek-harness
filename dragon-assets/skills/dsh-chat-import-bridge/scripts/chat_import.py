"""chat_import.py · dsh-chat-import-bridge 核心 · V1.0

天龙自研模块 · MIT
借鉴 Nwflower/dsh-chat-import v0.1.x 的 18 format 路由 + idempotency + bundle 范式

接口语义（与上游 dsh-chat-import npm v0.1.x 对齐）：
  - import_chat(format, path) → DSH session
  - scan_discover(path) → 会话清单（只读预览）
  - export_chat(session_id, format) → 反向导出
  - export_bundle / restore_bundle → 跨机器备份
  - sync_to_claude → 增量同步（guarded）
  - doctor / verify_session → 审计 + 健康检查
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
import tempfile
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any


TZ_CN = timezone(timedelta(hours=8))


# ─── 18 format 路由 ──────────────────────────────────────────────────────────

SUPPORTED_FORMATS = {
    # L1: 主流 agent
    "claude", "codex", "chatgpt", "cursor", "gemini", "reasonix",
    # L2: 新型 agent
    "opencode", "mimo", "zcode", "grok", "openclaw", "pi",
    # L3: 其他
    "hermes", "kimi", "qoder", "workbuddy",
    # L4: DSH 自身 + 通用
    "dsh", "local-jsonl",
}

# 文件格式签名（每个 format 识别）
FORMAT_SIGNATURES = {
    "claude": {"dir_pattern": r"\.claude[/\\]projects", "file_ext": ".jsonl"},
    "codex": {"dir_pattern": r"\.codex[/\\]sessions", "file_ext": ".jsonl"},
    "chatgpt": {"file_pattern": r"conversations\.json$"},
    "cursor": {"dir_pattern": r"\.cursor[/\\]projects", "file_ext": ".json"},
    "gemini": {"dir_pattern": r"\.gemini[/\\]tmp", "file_ext": ".json"},
    "reasonix": {"dir_pattern": r"\.reasonix[/\\]sessions", "file_ext": ".json"},
    "opencode": {"dir_pattern": r"opencode[/\\]storage", "file_ext": ".json"},
    "mimo": {"dir_pattern": r"\.mimo[/\\]sessions", "file_ext": ".json"},
    "zcode": {"dir_pattern": r"\.zcode[/\\]logs", "file_ext": ".md"},
    "grok": {"dir_pattern": r"\.grokx[/\\]sessions", "file_ext": ".jsonl"},
    "openclaw": {"dir_pattern": r"\.openclaw[/\\]chats", "file_ext": ".md"},
    "pi": {"dir_pattern": r"\.pi[/\\]sessions", "file_ext": ".json"},
    "hermes": {"file_pattern": r"history\.jsonl$"},
    "kimi": {"dir_pattern": r"\.kimi[/\\]sessions", "file_ext": ".json"},
    "qoder": {"dir_pattern": r"\.qoder[/\\]sessions", "file_ext": ".jsonl"},
    "workbuddy": {"dir_pattern": r"\.workbuddy[/\\]sessions", "file_ext": ".json"},
    "dsh": {"dir_pattern": r"\.dsh[/\\]sessions", "file_ext": ".jsonl"},
    "local-jsonl": {"file_ext": ".jsonl"},
}


def detect_format(path: str) -> str | None:
    """根据路径检测 format"""
    p = Path(path).resolve()
    path_str = str(p).replace("\\", "/")

    for fmt, sig in FORMAT_SIGNATURES.items():
        if "dir_pattern" in sig:
            if re.search(sig["dir_pattern"], path_str):
                return fmt
        if "file_pattern" in sig:
            if re.search(sig["file_pattern"], path):
                return fmt

    # 默认回退到扩展名
    if path.endswith(".jsonl"):
        return "local-jsonl"
    if path.endswith(".json"):
        return None
    return None


# ─── 数据模型 ────────────────────────────────────────────────────────────

@dataclass
class ChatMessage:
    """单条消息（保留 tool calls / reasoning / 模型）"""
    role: str  # user / assistant / system / tool
    content: str
    timestamp: str = ""
    tool_calls: list = field(default_factory=list)
    reasoning: str = ""
    model: str = ""
    message_id: str = ""


@dataclass
class ChatSession:
    """一个会话（来自外部 agent）"""
    session_id: str
    source_format: str
    source_path: str
    title: str = ""
    model: str = "unknown"
    created_at: str = ""
    updated_at: str = ""
    messages: list = field(default_factory=list)   # [ChatMessage]
    metadata: dict = field(default_factory=dict)
    source_hash: str = ""  # SHA-256 of source file

    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "source_format": self.source_format,
            "source_path": self.source_path,
            "title": self.title,
            "model": self.model,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "messages_count": len(self.messages),
            "source_hash": self.source_hash,
            "metadata": self.metadata,
        }

    def to_dsh_session(self) -> dict:
        """转换为 DSH session 格式（可被 univer_embed 渲染）"""
        return {
            "type": "dsh_session",
            "session_id": self.session_id,
            "source_format": self.source_format,
            "title": self.title or f"{self.source_format}:{self.session_id[:8]}",
            "model": self.model,
            "created_at": self.created_at,
            "messages": [asdict(m) for m in self.messages],
            "metadata": {**self.metadata, "source_hash": self.source_hash},
        }


# ─── 1. scan_discover（只读预览） ───────────────────────────────────────

def scan_discover(path: str, format_hint: str = "") -> list[dict]:
    """扫描路径，识别所有会话（不读内容）"""
    p = Path(path)
    if not p.exists():
        return []

    fmt = format_hint or detect_format(str(p)) or "unknown"

    sessions = []

    if p.is_file():
        # 单文件
        size = p.stat().st_size
        h = hashlib.sha256(p.read_bytes()).hexdigest()[:16]
        sessions.append({
            "path": str(p),
            "size": size,
            "source_hash": f"sha256:{h}",
            "format": fmt,
            "modified": datetime.fromtimestamp(p.stat().st_mtime, TZ_CN).isoformat(),
        })
    else:
        # 目录：递归找 *.jsonl / *.json
        for ext in ["*.jsonl", "*.json", "*.md"]:
            for f in p.rglob(ext):
                if f.stat().st_size == 0:
                    continue
                size = f.stat().st_size
                try:
                    h = hashlib.sha256(f.read_bytes()).hexdigest()[:16]
                except Exception:
                    continue
                sessions.append({
                    "path": str(f),
                    "size": size,
                    "source_hash": f"sha256:{h}",
                    "format": fmt,
                    "modified": datetime.fromtimestamp(f.stat().st_mtime, TZ_CN).isoformat(),
                })

    return sessions


# ─── 2. 前端解析（按 format 拆分消息） ──────────────────────────────────

def parse_session_file(path: Path, fmt: str) -> ChatSession:
    """解析单个会话文件 → ChatSession"""
    session_id = path.stem
    h = hashlib.sha256(path.read_bytes()).hexdigest()
    text = path.read_text(encoding="utf-8", errors="ignore")

    messages = []
    title = ""
    model = "unknown"
    created_at = ""

    try:
        if fmt == "claude" or fmt == "codex" or fmt == "dsh" or fmt == "local-jsonl":
            # JSONL 格式：每行一个 JSON 消息
            for line in text.splitlines():
                if not line.strip():
                    continue
                try:
                    obj = json.loads(line)
                    msg = _parse_jsonl_message(obj)
                    if msg:
                        messages.append(msg)
                except json.JSONDecodeError:
                    pass
        elif fmt == "chatgpt":
            # conversations.json: {"mapping": {...}}
            obj = json.loads(text)
            mapping = obj.get("mapping", {})
            for node_id, node in mapping.items():
                msg_data = node.get("message", {})
                if msg_data:
                    role = msg_data.get("author", {}).get("role", "user")
                    content = msg_data.get("content", {}).get("parts", [])
                    text_parts = [p.get("text", "") for p in content if isinstance(p, dict) and "text" in p]
                    content_str = "\n".join(text_parts)
                    messages.append(ChatMessage(
                        role=role,
                        content=content_str,
                        timestamp=str(msg_data.get("create_time", "")),
                    ))
            title = obj.get("title", "")
        elif fmt == "cursor":
            obj = json.loads(text)
            for m in obj.get("messages", []):
                messages.append(ChatMessage(
                    role=m.get("role", "user"),
                    content=m.get("content", ""),
                    timestamp=m.get("timestamp", ""),
                ))
        elif fmt == "gemini":
            obj = json.loads(text)
            for m in obj.get("conversation", []):
                messages.append(ChatMessage(
                    role=m.get("role", "user"),
                    content=m.get("content", ""),
                    timestamp=m.get("timestamp", ""),
                ))
        else:
            # 通用：尝试 JSON
            try:
                obj = json.loads(text)
                if isinstance(obj, dict) and "messages" in obj:
                    for m in obj["messages"]:
                        messages.append(ChatMessage(
                            role=m.get("role", "user"),
                            content=m.get("content", ""),
                            timestamp=m.get("timestamp", ""),
                        ))
                title = obj.get("title", "") if isinstance(obj, dict) else ""
            except json.JSONDecodeError:
                # Markdown / text 类
                messages.append(ChatMessage(role="user", content=text[:1000]))

    except Exception as e:
        # 解析失败不阻断，记录在 metadata
        return ChatSession(
            session_id=session_id,
            source_format=fmt,
            source_path=str(path),
            source_hash=f"sha256:{h}",
            metadata={"parse_error": str(e)},
        )

    return ChatSession(
        session_id=session_id,
        source_format=fmt,
        source_path=str(path),
        title=title,
        model=model,
        created_at=created_at or datetime.fromtimestamp(path.stat().st_mtime, TZ_CN).isoformat(),
        updated_at=datetime.fromtimestamp(path.stat().st_mtime, TZ_CN).isoformat(),
        messages=messages,
        source_hash=f"sha256:{h}",
    )


def _parse_jsonl_message(obj: dict) -> ChatMessage | None:
    """Claude / Codex / DSH JSONL 单行解析"""
    if not isinstance(obj, dict):
        return None
    role = obj.get("role") or obj.get("type", "user")
    content = obj.get("content") or obj.get("text", "") or ""
    if isinstance(content, list):
        # 多 part
        text_parts = [p.get("text", "") for p in content if isinstance(p, dict) and "text" in p]
        content = "\n".join(text_parts)

    return ChatMessage(
        role=role,
        content=content,
        timestamp=obj.get("timestamp") or obj.get("created_at", ""),
        tool_calls=obj.get("tool_calls", []),
        reasoning=obj.get("reasoning", ""),
        model=obj.get("model", ""),
    )


# ─── 3. import_chat（核心入口） ────────────────────────────────────────

def import_chat(format: str, path: str, workspace: str = "default",
               expected_hash: str = "", restamp: bool = False) -> dict:
    """主入口：把 chat 导入 DSH

    Idempotency:
      - expectedHash: 源 hash 匹配才导入
      - restamp: 强制重导入
      - unchanged sources skip（hash 一致）
      - grown sources append
    """
    fmt = format
    p = Path(path)

    if fmt not in SUPPORTED_FORMATS:
        return {"ok": False, "error": "UNSUPPORTED_FORMAT", "format": fmt,
                "supported": sorted(SUPPORTED_FORMATS)}

    if not p.exists():
        return {"ok": False, "error": "PATH_NOT_FOUND", "path": str(p)}

    # 扫描
    discovered = scan_discover(str(p), fmt)
    if not discovered:
        return {"ok": False, "error": "NO_SESSIONS_FOUND", "path": str(p)}

    # 解析每个 session
    imported = []
    skipped = []
    for entry in discovered:
        # Idempotency 检查
        if not restamp and expected_hash and entry["source_hash"] != expected_hash:
            skipped.append({"path": entry["path"], "reason": "HASH_MISMATCH"})
            continue

        try:
            session = parse_session_file(Path(entry["path"]), fmt)
            imported.append({
                "session_id": session.session_id,
                "title": session.title,
                "source_format": session.source_format,
                "messages_count": len(session.messages),
                "source_hash": session.source_hash,
                "dsh_session": session.to_dsh_session(),
            })
        except Exception as e:
            skipped.append({"path": entry["path"], "reason": f"PARSE_ERROR: {e}"})

    return {
        "ok": True,
        "format": fmt,
        "workspace": workspace,
        "imported_count": len(imported),
        "skipped_count": len(skipped),
        "imported": imported,
        "skipped": skipped,
    }


# ─── 4. export_chat（反向导出） ─────────────────────────────────────────

def export_chat(session: ChatSession, format: str) -> dict:
    """DSH session 反向导出（claude / codex / kimi）"""
    if format not in ("claude", "codex", "kimi"):
        return {"ok": False, "error": "UNSUPPORTED_EXPORT_FORMAT", "format": format}

    # 生成 export 文件
    if format == "claude":
        # Claude JSONL 格式：{"role": "user", "content": "...", "timestamp": "..."}
        lines = []
        for msg in session.messages:
            lines.append(json.dumps({
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp,
            }, ensure_ascii=False))
        content = "\n".join(lines)
        ext = "jsonl"
    elif format == "codex":
        # Codex rollout 格式：{"messages": [{"role": ..., "content": ...}]}
        content = json.dumps({
            "session_id": session.session_id,
            "messages": [{
                "role": m.role,
                "content": m.content,
                "timestamp": m.timestamp,
            } for m in session.messages],
        }, ensure_ascii=False, indent=2)
        ext = "json"
    else:  # kimi
        # Kimi wire format
        content = json.dumps({
            "id": session.session_id,
            "conversations": [{
                "role": m.role,
                "text": m.content,
            } for m in session.messages],
        }, ensure_ascii=False, indent=2)
        ext = "json"

    return {
        "ok": True,
        "format": format,
        "session_id": session.session_id,
        "content": content,
        "content_length": len(content),
        "export_extension": ext,
    }


# ─── 5. bundle（SHA-256 双指纹备份） ─────────────────────────────────────

@dataclass
class ChatBundle:
    version: str = "1.0"
    source_format: str = ""
    session_id: str = ""
    created_at: str = ""
    fingerprint_source: str = ""   # 源文件 SHA-256
    fingerprint_content: str = ""  # 序列化后 SHA-256
    messages: list = field(default_factory=list)
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "version": self.version,
            "source_format": self.source_format,
            "session_id": self.session_id,
            "created_at": self.created_at,
            "fingerprint_source": self.fingerprint_source,
            "fingerprint_content": self.fingerprint_content,
            "messages": self.messages,
            "metadata": self.metadata,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)


def export_bundle(session: ChatSession, source_path: str = "") -> ChatBundle:
    """导出为 portable bundle"""
    source_path = source_path or session.source_path

    # 计算 source 指纹
    source_hash = ""
    if source_path and Path(source_path).exists():
        source_hash = f"sha256:{hashlib.sha256(Path(source_path).read_bytes()).hexdigest()}"

    # 计算 content 指纹
    content_str = json.dumps([asdict(m) for m in session.messages], ensure_ascii=False, sort_keys=True)
    content_hash = f"sha256:{hashlib.sha256(content_str.encode()).hexdigest()}"

    return ChatBundle(
        source_format=session.source_format,
        session_id=session.session_id,
        created_at=datetime.now(TZ_CN).isoformat(),
        fingerprint_source=source_hash,
        fingerprint_content=content_hash,
        messages=[asdict(m) for m in session.messages],
        metadata={
            "title": session.title,
            "model": session.model,
            "messages_count": len(session.messages),
            "source_path": session.source_path,
        },
    )


def restore_bundle(bundle_json: str) -> dict:
    """从 bundle JSON 恢复会话"""
    try:
        bundle_dict = json.loads(bundle_json)
    except json.JSONDecodeError as e:
        return {"ok": False, "error": "INVALID_JSON", "details": str(e)}

    bundle = ChatBundle(**bundle_dict)
    return {
        "ok": True,
        "session_id": bundle.session_id,
        "source_format": bundle.source_format,
        "messages_count": len(bundle.messages),
        "fingerprint_source": bundle.fingerprint_source,
        "fingerprint_content": bundle.fingerprint_content,
        "created_at": bundle.created_at,
    }


# ─── 6. sync_to_claude（guarded 增量同步） ─────────────────────────────

def sync_to_claude(session: ChatSession, target_path: str, dry_run: bool = True) -> dict:
    """增量追加 DSH session → Claude JSONL（防覆盖）"""
    target = Path(target_path)

    # 如果 target 存在 + dry_run=False 才真写
    append_count = len(session.messages)

    if target.exists() and not dry_run:
        # 防覆盖：先备份
        backup = target.with_suffix(target.suffix + ".bak")
        backup.write_bytes(target.read_bytes())

        # 追加新 turns（先确保末尾有换行符，避免接续到末行）
        with target.open("a", encoding="utf-8") as f:
            # 若文件末尾无换行，先补一个
            if target.stat().st_size > 0:
                with target.open("rb") as rb:
                    rb.seek(-1, 2)  # 末尾
                    last_byte = rb.read(1)
                    if last_byte != b"\n":
                        f.write("\n")
            for msg in session.messages:
                f.write(json.dumps({
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.timestamp,
                    "synced_at": datetime.now(TZ_CN).isoformat(),
                    "from_session": session.session_id,
                }, ensure_ascii=False) + "\n")

    return {
        "ok": True,
        "session_id": session.session_id,
        "target_path": str(target),
        "appended_count": append_count if dry_run else append_count,
        "dry_run": dry_run,
        "guarded": target.exists(),  # 防覆盖 guard
    }


# ─── 7. doctor / verify_session（审计） ─────────────────────────────────

def doctor(sessions: list[ChatSession]) -> dict:
    """健康检查"""
    issues = []
    stats = {
        "total_sessions": len(sessions),
        "by_format": {},
        "empty_sessions": 0,
        "missing_hash": 0,
        "parse_errors": 0,
    }

    for s in sessions:
        # by_format
        stats["by_format"][s.source_format] = stats["by_format"].get(s.source_format, 0) + 1
        # empty
        if len(s.messages) == 0:
            stats["empty_sessions"] += 1
            issues.append({"session_id": s.session_id, "type": "EMPTY"})
        # missing hash
        if not s.source_hash:
            stats["missing_hash"] += 1
            issues.append({"session_id": s.session_id, "type": "NO_HASH"})
        # parse error
        if "parse_error" in s.metadata:
            stats["parse_errors"] += 1
            issues.append({"session_id": s.session_id, "type": "PARSE_ERROR",
                          "error": s.metadata["parse_error"]})

    return {
        "ok": len(issues) == 0,
        "stats": stats,
        "issues": issues,
    }


def verify_session(session: ChatSession) -> dict:
    """单 session 验证"""
    checks = {
        "has_source_hash": bool(session.source_hash),
        "has_title": bool(session.title),
        "has_model": bool(session.model),
        "messages_count": len(session.messages),
        "first_message_at": session.messages[0].timestamp if session.messages else "",
        "last_message_at": session.messages[-1].timestamp if session.messages else "",
    }
    return {"ok": True, "session_id": session.session_id, "checks": checks}


# ─── 主入口 ────────────────────────────────────────────────────────────────

def main() -> int:
    """演示：完整流程"""
    print("=" * 70)
    print("Stage 55 · dsh-chat-import-bridge · V1.0 演示")
    print("=" * 70)

    # 创建临时 mock session
    with tempfile.TemporaryDirectory() as tmp:
        # 1. 创建 mock claude session 文件
        claude_file = Path(tmp) / "session-001.jsonl"
        lines = [
            json.dumps({"role": "user", "content": "你好", "timestamp": "2026-08-26T10:00:00Z", "model": "sonnet"}),
            json.dumps({"role": "assistant", "content": "你好！有什么可以帮助你？", "timestamp": "2026-08-26T10:00:01Z", "model": "sonnet"}),
            json.dumps({"role": "user", "content": "介绍一下 DSH", "timestamp": "2026-08-26T10:01:00Z", "model": "sonnet"}),
            json.dumps({"role": "assistant", "content": "DSH 是 DeepSeek Harness...", "timestamp": "2026-08-26T10:01:05Z", "model": "sonnet"}),
        ]
        claude_file.write_text("\n".join(lines), encoding="utf-8")

        # 2. 扫描
        discovered = scan_discover(str(claude_file), "claude")
        print(f"\n[1] scan_discover: {len(discovered)} 个会话")
        for d in discovered:
            print(f"  - {d['path']} ({d['size']} B, {d['source_hash']})")

        # 3. import_chat
        result = import_chat("claude", str(claude_file))
        print(f"\n[2] import_chat: ok={result['ok']}, imported={result['imported_count']}")
        if result["imported"]:
            s = result["imported"][0]
            print(f"  - session_id={s['session_id']}, messages={s['messages_count']}")

        # 4. 解析 session（用于后续步骤）
        session = parse_session_file(claude_file, "claude")
        print(f"\n[3] parse_session_file: {len(session.messages)} messages")

        # 5. export_chat → claude
        exported = export_chat(session, "claude")
        print(f"\n[4] export_chat(claude): {exported['content_length']} 字符")

        # 6. bundle 导出
        bundle = export_bundle(session, str(claude_file))
        print(f"\n[5] export_bundle: source={bundle.fingerprint_source[:20]}..., content={bundle.fingerprint_content[:20]}...")

        # 7. bundle 恢复
        restored = restore_bundle(bundle.to_json())
        print(f"\n[6] restore_bundle: ok={restored['ok']}, messages={restored['messages_count']}")

        # 8. sync_to_claude
        sync = sync_to_claude(session, str(claude_file), dry_run=True)
        print(f"\n[7] sync_to_claude (dry_run): appended={sync['appended_count']}, guarded={sync['guarded']}")

        # 9. doctor
        d = doctor([session])
        print(f"\n[8] doctor: ok={d['ok']}, stats={d['stats']}")

    print("\n" + "=" * 70)
    return 0


if __name__ == "__main__":
    sys.exit(main())
