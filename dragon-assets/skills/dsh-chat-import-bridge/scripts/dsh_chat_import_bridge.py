"""
dsh-chat-import-bridge V1.0 · Stage 53.1 借鉴档 · Nwflower/dsh-chat-import MIT 借鉴

================================================================================
  Stage 53.1 · 2026-08-26

设计：
  - 借鉴档模式（与 stage 41/45/46/48/49.1/49.2/49.4/50.1/50.2/51.1 同）
  - 5 类借鉴：17+ agent 来源格式 parser / 单 import_chat 工具协议 /
    matrix export 3 格式 (claude/codex/kimi) / portable interchange bundle /
    SHA-256 dedup + idempotency
  - 不实跑 npm install（DSH Desktop 0.1.x peer 依赖 blocker）
  - 自研 15+ unittest PASS
  - 退出码契约：0=OK / 1=PARSE_ERR / 2=SCHEMA_ERR / 3=CHECKSUM_ERR
================================================================================
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

EXIT_OK = 0
EXIT_PARSE = 1
EXIT_SCHEMA = 2
EXIT_CHECKSUM = 3


# ==============================================================================
# 1. 17+ Agent 来源格式（借鉴 README §Supported sources）
# ==============================================================================

SUPPORTED_FORMATS = [
    # 8 大类 18 个 format 值（参考 README 表格）
    {"name": "claude",   "display": "Claude Code",       "storage": "~/.claude/projects/<slug>/<sessionId>.jsonl"},
    {"name": "claude",   "display": "Claude-3p",          "storage": "%LOCALAPPDATA%/Claude-3p/claude-code-sessions", "note": "metadata → JSONL via cliSessionId"},
    {"name": "codex",    "display": "Codex / ChatGPT CLI","storage": "~/.codex/sessions/YYYY/MM/DD/rollout-*.jsonl"},
    {"name": "chatgpt",  "display": "ChatGPT (web export)","storage": "anywhere you saved export · conversations.json"},
    {"name": "cursor",   "display": "Cursor",             "storage": "~/.cursor/projects/<slug>/agent-transcripts/<id>/<id>.jsonl"},
    {"name": "gemini",   "display": "Gemini CLI",          "storage": "~/.gemini/history/<slot>/chats/session-*.json"},
    {"name": "reasonix", "display": "Reasonix (CLI+desktop)","storage": "~/.reasonix/sessions/desktop-*.jsonl"},
    {"name": "opencode", "display": "opencode",           "storage": "~/.local/share/opencode/opencode.db"},
    {"name": "mimocode", "display": "MiMo Code",          "storage": "~/.local/share/mimocode/mimocode.db"},
    {"name": "zcode",    "display": "ZCode (z.ai CLI)",   "storage": "~/.zcode/cli/db/db.sqlite"},
    {"name": "grokbuild","display": "Grok Build",         "storage": "~/.grok/sessions/<project>/<session_id>/"},
    {"name": "openclaw", "display": "OpenClaw",           "storage": "~/.openclaw/agents/<agent>/sessions/*.jsonl"},
    {"name": "pi",       "display": "Pi Coding Agent",    "storage": "~/.pi/agent/sessions/--<cwd>--/<timestamp>_<uuid>.jsonl"},
    {"name": "hermes",   "display": "Hermes",             "storage": "~/.hermes/ (Windows %LOCALAPPDATA%/hermes)"},
    {"name": "kimi",     "display": "Kimi CLI / Kimi Code","storage": "~/.kimi/sessions/<workdir-md5>/<sessionId>/wire.jsonl"},
    {"name": "qoder",    "display": "Qoder CLI",          "storage": "~/.qoder/projects/<encoded-project>/<sessionId>.jsonl"},
    {"name": "workbuddy","display": "WorkBuddy (Tencent)","storage": "~/.workbuddy/projects/<project-hash>/<session-uuid>.jsonl"},
    {"name": "dsh",      "display": "DSH session logs",   "storage": "~/.dsh/sessions/<encoded-workspace>/<sessionId>/session.jsonl(.zstd)"},
    {"name": "local-jsonl","display": "Any local JSONL",   "storage": "any .jsonl file/dir (auto-detected)"},
]

# 去重（claude 出现 2 次：Claude Code + Claude-3p）
UNIQUE_FORMATS = []
seen = set()
for f in SUPPORTED_FORMATS:
    if f["name"] not in seen:
        UNIQUE_FORMATS.append(f)
        seen.add(f["name"])


# ==============================================================================
# 2. 单 import_chat 工具协议（借鉴 stage 47 dsh-univer-office 单工具协议）
# ==============================================================================

@dataclass
class ImportChatRequest:
    """import_chat 工具请求"""
    format: str                    # 17+ supported formats
    path: str
    preview: bool = False          # 零副作用
    force: bool = False            # 新完整副本
    session_id: Optional[str] = None
    expected_hash: Optional[str] = None
    restamp: bool = False
    workspace: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {k: v for k, v in asdict(self).items() if v is not None}


def validate_import_chat(req: ImportChatRequest) -> List[str]:
    """校验 import_chat 请求（schema 校验）"""
    issues = []
    format_names = [f["name"] for f in SUPPORTED_FORMATS]
    if req.format not in format_names:
        issues.append(f"invalid format: {req.format} (allowed: {set(format_names)})")
    if not req.path:
        issues.append("missing 'path' field")
    if req.expected_hash and not re.match(r"^[a-f0-9]{16,64}$", req.expected_hash):
        issues.append("invalid expected_hash format (hex 16-64 chars)")
    return issues


# ==============================================================================
# 3. matrix export 3 格式（借鉴 README §matrix export）
# ==============================================================================

EXPORT_FORMATS = ["claude", "codex", "kimi"]


@dataclass
class ExportChatResult:
    """export_chat 工具结果"""
    format: str                     # claude / codex / kimi
    output_path: str
    lossy_items: List[str] = field(default_factory=list)
    success: bool = True


# ==============================================================================
# 4. portable interchange bundle（借鉴 export_bundle / restore_bundle + SHA-256）
# ==============================================================================

@dataclass
class InterchangeBundle:
    """interchange bundle（借鉴 export_bundle）"""
    primary_sha256: str       # 内容 SHA-256
    secondary_sha256: str     # metadata SHA-256
    contents: bytes = b""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def verify_integrity(self) -> bool:
        """校验 bundle 完整性"""
        actual = hashlib.sha256(self.contents).hexdigest()
        return actual == self.primary_sha256


# ==============================================================================
# 5. SHA-256 dedup + idempotency（借鉴 README §Idempotency & protection）
# ==============================================================================

def sha256_dedup_content(content: bytes) -> str:
    """借鉴 README：unchanged sources skip, grown sources append"""
    return hashlib.sha256(content).hexdigest()[:16]


def check_idempotency(current_sha: str, stored_sha: str) -> str:
    """检查幂等性：3 种状态"""
    if current_sha == stored_sha:
        return "skip"            # unchanged → skip
    if not stored_sha:
        return "import"         # 首次 → import
    return "append"             # grown → append


# ==============================================================================
# CLI
# ==============================================================================

def cmd_list_formats(args: argparse.Namespace) -> int:
    """列出 17+ agent 来源格式"""
    print("=== dsh-chat-import 17+ supported formats ===")
    unique_seen = set()
    for f in SUPPORTED_FORMATS:
        if f["name"] not in unique_seen:
            unique_seen.add(f["name"])
            print(f"  [{f['name']:<14}] {f['display']:<28} {f['storage']}")
    print(f"\n  unique formats: {len(unique_seen)}")
    return EXIT_OK


def cmd_validate_import(args: argparse.Namespace) -> int:
    """校验 import_chat 请求 schema"""
    try:
        req = ImportChatRequest(
            format=args.format,
            path=args.path,
            preview=args.preview,
            force=args.force,
            session_id=args.session_id,
            expected_hash=args.expected_hash,
        )
    except Exception as e:
        print(f"[parse error] {e}", file=sys.stderr)
        return EXIT_PARSE
    issues = validate_import_chat(req)
    if issues:
        print(f"[validation issues] {issues}", file=sys.stderr)
        return EXIT_SCHEMA
    print(json.dumps({"validated": True, "request": req.to_dict()}, indent=2, ensure_ascii=False))
    return EXIT_OK


def cmd_check_idempotency(args: argparse.Namespace) -> int:
    """检查幂等性"""
    if not args.current or not args.stored:
        print("error: both --current and --stored required", file=sys.stderr)
        return EXIT_PARSE
    result = check_idempotency(args.current, args.stored)
    print(json.dumps({"current": args.current, "stored": args.stored, "action": result}, indent=2))
    return EXIT_OK


def cmd_sha256_dedup(args: argparse.Namespace) -> int:
    """SHA-256 dedup demo"""
    h = sha256_dedup_content(args.input.encode("utf-8"))
    print(json.dumps({"input_len": len(args.input), "sha256_short": h}, indent=2))
    return EXIT_OK


def cmd_list_export_formats(args: argparse.Namespace) -> int:
    """列出 3 类 matrix export 格式"""
    print("=== matrix export 3 formats ===")
    for f in EXPORT_FORMATS:
        print(f"  - {f}")
    print(f"\n  total: {len(EXPORT_FORMATS)}")
    return EXIT_OK


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="dsh_chat_import_bridge",
        description="Stage 53.1 dsh-chat-import-bridge V1.0 · Nwflower/dsh-chat-import MIT 借鉴档",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("list-formats", help="列出 17+ agent 来源格式")
    sp.set_defaults(func=cmd_list_formats)

    sp = sub.add_parser("validate-import", help="校验 import_chat 请求 schema")
    sp.add_argument("--format", required=True, help="format value")
    sp.add_argument("--path", required=True)
    sp.add_argument("--preview", action="store_true")
    sp.add_argument("--force", action="store_true")
    sp.add_argument("--session-id")
    sp.add_argument("--expected-hash")
    sp.set_defaults(func=cmd_validate_import)

    sp = sub.add_parser("check-idempotency", help="检查幂等性 3 状态")
    sp.add_argument("--current", required=True, help="current SHA-256 short")
    sp.add_argument("--stored", required=True, help="stored SHA-256 short (空字符串表示无)")
    sp.set_defaults(func=cmd_check_idempotency)

    sp = sub.add_parser("sha256-dedup", help="SHA-256 dedup demo")
    sp.add_argument("--input", required=True)
    sp.set_defaults(func=cmd_sha256_dedup)

    sp = sub.add_parser("list-export-formats", help="列出 matrix export 3 格式")
    sp.set_defaults(func=cmd_list_export_formats)

    return p


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
