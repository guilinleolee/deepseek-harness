"""
dsh-undo-savepoint-bridge V1.0 · Stage 54.1 借鉴档 · lire1131/dsh-undo-savepoint MIT 借鉴

================================================================================
  Stage 54.1 · 2026-08-26

设计：
  - 借鉴档模式（与 stage 41/45/46/48/49.1/49.2/49.4/50.1/50.2/51.1/53.1 同）
  - 5 类借鉴：undo config/plugin-code / secret-safe snapshots / one-click SAFE MODE /
    offline CLI when DSH won't boot / offline GUI when DSH won't boot
  - 不实跑 npm install（DSH Desktop 路径依赖 blocker）
  - 自研 15+ unittest PASS
  - 退出码契约：0=OK / 1=PARSE_ERR / 2=SNAPSHOT_ERR / 3=SECRET_ERR
================================================================================
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import hashlib
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

EXIT_OK = 0
EXIT_PARSE = 1
EXIT_SNAPSHOT = 2
EXIT_SECRET = 3


# ==============================================================================
# 1. Undo Change Set（借鉴 README · undo config & plugin-code changes）
# ==============================================================================

@dataclass
class UndoChange:
    """单条 undo 变更"""
    change_id: str
    timestamp: str
    change_type: str          # config / plugin-code / cordis-patch / etc.
    target_path: str
    before: str = ""
    after: str = ""


# ==============================================================================
# 2. Secret-safe Snapshot（借鉴 README · secret-safe snapshots）
# ==============================================================================

SECRET_PATTERNS = [
    r"(?i)api[_-]?key\s*[=:]\s*['\"]?[a-zA-Z0-9_\-]{20,}",
    r"(?i)token\s*[=:]\s*['\"]?[a-zA-Z0-9_\-]{20,}",
    r"(?i)password\s*[=:]\s*['\"]?[^\s'\"]{6,}",
    r"(?i)bearer\s+[a-zA-Z0-9_\-\.=]{20,}",
]


def redact_secrets(content: str) -> str:
    """secret-safe snapshot：自动 redact API key / token / password"""
    redacted = content
    for pat in SECRET_PATTERNS:
        redacted = re.sub(pat, "[REDACTED]", redacted)
    return redacted


# ==============================================================================
# 3. Snapshot 计算（借鉴 README · one-click SAFE MODE）
# ==============================================================================

@dataclass
class Snapshot:
    """secret-safe snapshot"""
    snapshot_id: str
    timestamp: str
    contents: Dict[str, str] = field(default_factory=dict)  # path → redacted content
    changes: List[UndoChange] = field(default_factory=list)
    sha256: str = ""

    def compute_sha256(self) -> str:
        """计算 snapshot 整体 SHA-256"""
        h = hashlib.sha256()
        for path in sorted(self.contents.keys()):
            h.update(path.encode("utf-8"))
            h.update(self.contents[path].encode("utf-8"))
        return h.hexdigest()

    def verify_integrity(self) -> bool:
        """校验完整性"""
        return self.sha256 == self.compute_sha256()


# ==============================================================================
# 4. One-click SAFE MODE（借鉴 README · one-click SAFE MODE）
# ==============================================================================

SAFE_MODE_LEVELS = ["minimal", "offline", "readonly"]


@dataclass
class SafeModeConfig:
    """SAFE MODE 配置（minimal / offline / readonly 3 档）"""
    level: str = "minimal"           # minimal / offline / readonly
    block_network: bool = True       # 阻断网络
    block_plugin_load: bool = True   # 阻断 plugin 加载
    readonly_mode: bool = False      # 只读模式


def validate_safe_mode(cfg: SafeModeConfig) -> List[str]:
    issues = []
    if cfg.level not in SAFE_MODE_LEVELS:
        issues.append(f"invalid level: {cfg.level} (allowed: {SAFE_MODE_LEVELS})")
    if cfg.level == "readonly" and not cfg.readonly_mode:
        issues.append("readonly level requires readonly_mode=True")
    return issues


# ==============================================================================
# 5. Offline CLI / GUI（借鉴 README · work even when DSH won't boot）
# ==============================================================================

@dataclass
class OfflineCommand:
    """offline CLI 命令（DSH 崩溃时仍可用）"""
    name: str
    description: str
    requires_network: bool = False


OFFLINE_COMMANDS = [
    OfflineCommand("rollback", "Undo last config change (offline)", False),
    OfflineCommand("restore", "Restore from snapshot (offline)", False),
    OfflineCommand("verify", "Verify snapshot integrity (offline)", False),
    OfflineCommand("doctor", "Run offline DSH doctor (offline)", False),
    OfflineCommand("safe-mode", "Enter SAFE MODE (offline)", False),
]


def list_offline_commands() -> List[Dict[str, str]]:
    return [{"name": c.name, "desc": c.description, "offline": not c.requires_network}
            for c in OFFLINE_COMMANDS]


# ==============================================================================
# CLI
# ==============================================================================

def cmd_redact(args: argparse.Namespace) -> int:
    """redact secrets demo"""
    redacted = redact_secrets(args.input)
    print(json.dumps({"original_len": len(args.input), "redacted_len": len(redacted), "redacted": redacted}, indent=2, ensure_ascii=False))
    return EXIT_OK


def cmd_safe_mode(args: argparse.Namespace) -> int:
    """校验 SAFE MODE 配置"""
    cfg = SafeModeConfig(
        level=args.level,
        block_network=args.block_network,
        block_plugin_load=args.block_plugin_load,
        readonly_mode=args.readonly_mode,
    )
    issues = validate_safe_mode(cfg)
    if issues:
        print(f"[validation issues] {issues}", file=sys.stderr)
        return EXIT_PARSE
    print(json.dumps({"safe_mode": asdict(cfg), "valid": True}, indent=2, ensure_ascii=False))
    return EXIT_OK


def cmd_offline_cmds(args: argparse.Namespace) -> int:
    """列出 offline CLI 命令"""
    print(json.dumps(list_offline_commands(), indent=2, ensure_ascii=False))
    return EXIT_OK


def cmd_snapshot_sha(args: argparse.Namespace) -> int:
    """snapshot SHA-256 demo"""
    h = hashlib.sha256(args.content.encode("utf-8")).hexdigest()
    print(json.dumps({"content_len": len(args.content), "sha256": h}, indent=2))
    return EXIT_OK


def cmd_secrets_patterns(args: argparse.Namespace) -> int:
    """列出 secret patterns"""
    print(json.dumps({"secret_patterns": SECRET_PATTERNS}, indent=2, ensure_ascii=False))
    return EXIT_OK


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="dsh_undo_savepoint_bridge",
        description="Stage 54.1 dsh-undo-savepoint-bridge V1.0 · lire1131/dsh-undo-savepoint MIT 借鉴档",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("redact", help="redact secrets demo")
    sp.add_argument("--input", required=True)
    sp.set_defaults(func=cmd_redact)

    sp = sub.add_parser("safe-mode", help="校验 SAFE MODE 配置")
    sp.add_argument("--level", choices=SAFE_MODE_LEVELS, default="minimal")
    sp.add_argument("--block-network", type=lambda x: x.lower() == "true", default=True)
    sp.add_argument("--block-plugin-load", type=lambda x: x.lower() == "true", default=True)
    sp.add_argument("--readonly-mode", type=lambda x: x.lower() == "true", default=False)
    sp.set_defaults(func=cmd_safe_mode)

    sp = sub.add_parser("offline-cmds", help="列出 offline CLI 命令")
    sp.set_defaults(func=cmd_offline_cmds)

    sp = sub.add_parser("snapshot-sha", help="snapshot SHA-256 demo")
    sp.add_argument("--content", required=True)
    sp.set_defaults(func=cmd_snapshot_sha)

    sp = sub.add_parser("secrets-patterns", help="列出 secret patterns")
    sp.set_defaults(func=cmd_secrets_patterns)

    return p


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
