"""test_02_import_chat · 导入 Claude JSONL + 幂等性"""
import sys
import tempfile
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from chat_import import import_chat, parse_session_file, scan_discover, ChatSession


def test_02_import_chat():
    # 创建 mock claude session
    with tempfile.TemporaryDirectory() as tmp:
        claude_file = Path(tmp) / "claude-test.jsonl"
        lines = [
            json.dumps({"role": "user", "content": "你好", "timestamp": "2026-08-26T10:00:00Z", "model": "sonnet"}),
            json.dumps({"role": "assistant", "content": "你好！", "timestamp": "2026-08-26T10:00:01Z", "model": "sonnet"}),
            json.dumps({"role": "user", "content": "DSH 是什么？", "timestamp": "2026-08-26T10:01:00Z", "model": "sonnet"}),
            json.dumps({"role": "assistant", "content": "DeepSeek Harness", "timestamp": "2026-08-26T10:01:05Z", "model": "sonnet"}),
        ]
        claude_file.write_text("\n".join(lines), encoding="utf-8")

        # import_chat
        result = import_chat("claude", str(claude_file))
        assert result["ok"], f"[FAIL] import_chat failed: {result}"
        assert result["imported_count"] == 1
        assert result["skipped_count"] == 0
        assert result["imported"][0]["messages_count"] == 4
        print(f"[PASS] import_chat(claude): {result['imported_count']} sessions, {result['imported'][0]['messages_count']} msgs")

        # 解析验证
        session = parse_session_file(claude_file, "claude")
        assert isinstance(session, ChatSession)
        assert session.source_format == "claude"
        assert len(session.messages) == 4
        assert session.messages[0].role == "user"
        assert session.messages[1].content == "你好！"
        assert session.messages[3].model == "sonnet"
        print(f"[PASS] parse_session_file: 4 messages parsed correctly")

        # Idempotency: expected_hash 错误应跳过
        result_skip = import_chat("claude", str(claude_file), expected_hash="sha256:wrong_hash")
        assert result_skip["imported_count"] == 0
        assert result_skip["skipped_count"] == 1
        print(f"[PASS] idempotency: wrong expected_hash → {result_skip['skipped_count']} skipped")

        # Idempotency: 正确 hash 应导入（short 16-char format）
        discovered_short = scan_discover(str(claude_file), "claude")
        real_hash_short = discovered_short[0]["source_hash"]  # scan_discover 用的就是短 hash
        result_ok = import_chat("claude", str(claude_file), expected_hash=real_hash_short)
        assert result_ok["imported_count"] == 1, f"[FAIL] correct hash 应导入，实际 {result_ok}"
        print(f"[PASS] idempotency: correct hash → {result_ok['imported_count']} imported")

        # 不支持的 format
        result_bad = import_chat("unknown_format", str(claude_file))
        assert not result_bad["ok"]
        assert result_bad["error"] == "UNSUPPORTED_FORMAT"
        print(f"[PASS] UNSUPPORTED_FORMAT rejected: {len(result_bad['supported'])} formats listed")

        # 路径不存在
        result_404 = import_chat("claude", "/nonexistent/path.jsonl")
        assert not result_404["ok"]
        assert result_404["error"] == "PATH_NOT_FOUND"
        print(f"[PASS] PATH_NOT_FOUND handled")


if __name__ == "__main__":
    test_02_import_chat()
