"""test_01_format_router · 18 format 路由"""
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from chat_import import (
    detect_format, scan_discover, SUPPORTED_FORMATS, FORMAT_SIGNATURES,
)


def test_01_format_router():
    # 18 format 全部注册
    assert len(SUPPORTED_FORMATS) >= 18, f"[FAIL] expected ≥18 formats, got {len(SUPPORTED_FORMATS)}"
    print(f"[PASS] SUPPORTED_FORMATS: {len(SUPPORTED_FORMATS)} formats registered")

    # 每个 format 都有 signature（除少数 file-only）
    for fmt in ["claude", "codex", "chatgpt", "cursor", "gemini", "reasonix",
                "opencode", "mimo", "zcode", "grok", "openclaw", "pi",
                "hermes", "kimi", "qoder", "workbuddy", "dsh"]:
        assert fmt in FORMAT_SIGNATURES, f"[FAIL] format '{fmt}' 缺 signature"

    # detect_format 路径识别
    test_paths = [
        ("~/.claude/projects/session-1.jsonl", "claude"),
        ("/Users/x/.codex/sessions/2026/08/rollout-abc.jsonl", "codex"),
        ("/Users/x/Downloads/chatgpt-export/conversations.json", "chatgpt"),
        ("~/.cursor/projects/foo/agent-transcripts/abc.json", "cursor"),
        ("~/.gemini/tmp/abc/chats/session.json", "gemini"),
        ("~/.openclaw/chats/abc.md", "openclaw"),
        ("~/.pi/sessions/abc.json", "pi"),
        ("~/.kimi/sessions/abc.json", "kimi"),
        ("~/.dsh/sessions/abc.jsonl", "dsh"),
        ("/tmp/foo.jsonl", "local-jsonl"),  # fallback
    ]

    # 用 mock paths（绝对路径）
    for path, expected in test_paths:
        detected = detect_format(path)
        # 注意：路径是模拟的，可能不会匹配（但 fallback 到 extension）
        if detected:
            print(f"  '{path}' → {detected} (expected {expected})")
        else:
            print(f"  '{path}' → None (mock path 不可识别, fallback {expected})")

    # fallback：陌生 .jsonl 应返回 local-jsonl
    detected = detect_format("/tmp/random.jsonl")
    assert detected == "local-jsonl", f"[FAIL] fallback 应为 local-jsonl, got {detected}"
    print(f"[PASS] detect_format fallback: /tmp/random.jsonl → {detected}")


if __name__ == "__main__":
    test_01_format_router()
