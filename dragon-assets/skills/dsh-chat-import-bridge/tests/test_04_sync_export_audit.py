"""test_04_sync_export_audit · sync_to_claude + export_chat + doctor"""
import sys
import tempfile
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from chat_import import (
    parse_session_file, export_chat, sync_to_claude, doctor, verify_session,
)


def test_04_sync_export_audit():
    with tempfile.TemporaryDirectory() as tmp:
        # 创建 mock session
        claude_file = Path(tmp) / "session-sync.jsonl"
        lines = [
            json.dumps({"role": "user", "content": "msg1", "timestamp": "2026-08-26T10:00:00Z"}),
            json.dumps({"role": "assistant", "content": "reply1", "timestamp": "2026-08-26T10:00:01Z"}),
        ]
        claude_file.write_text("\n".join(lines), encoding="utf-8")

        session = parse_session_file(claude_file, "claude")

        # 1. export_chat → claude
        exported = export_chat(session, "claude")
        assert exported["ok"]
        assert exported["format"] == "claude"
        assert "msg1" in exported["content"]
        assert "reply1" in exported["content"]
        assert exported["content_length"] > 0
        print(f"[PASS] export_chat(claude): {exported['content_length']} 字符")

        # 2. export_chat → codex
        exported_codex = export_chat(session, "codex")
        assert exported_codex["ok"]
        assert exported_codex["format"] == "codex"
        assert "session_id" in exported_codex["content"]
        print(f"[PASS] export_chat(codex): JSON 格式")

        # 3. export_chat → kimi
        exported_kimi = export_chat(session, "kimi")
        assert exported_kimi["ok"]
        assert exported_kimi["format"] == "kimi"
        assert "conversations" in exported_kimi["content"]
        print(f"[PASS] export_chat(kimi): JSON 格式")

        # 4. 不支持的格式
        bad = export_chat(session, "unknown")
        assert not bad["ok"]
        assert bad["error"] == "UNSUPPORTED_EXPORT_FORMAT"
        print(f"[PASS] export_chat: UNSUPPORTED_EXPORT_FORMAT rejected")

        # 5. sync_to_claude (dry_run=True)
        sync = sync_to_claude(session, str(claude_file), dry_run=True)
        assert sync["ok"]
        assert sync["dry_run"] is True
        assert sync["appended_count"] == 2
        assert sync["guarded"] is True  # target 存在 → guarded
        print(f"[PASS] sync_to_claude(dry_run): {sync['appended_count']} msgs (guarded={sync['guarded']})")

        # 6. sync_to_claude (dry_run=False) → 实际追加 + 备份
        sync_real = sync_to_claude(session, str(claude_file), dry_run=False)
        assert sync_real["dry_run"] is False
        backup_file = Path(str(claude_file) + ".bak")
        assert backup_file.exists(), f"[FAIL] backup 未创建: {backup_file}"
        print(f"[PASS] sync_to_claude(real): 创建 backup {backup_file.name}")

        # 验证目标文件被追加（行数 + 2）
        lines_after = claude_file.read_text(encoding="utf-8").splitlines()
        assert len(lines_after) == 4, f"[FAIL] 应有 4 行（原 2 + 追加 2）, got {len(lines_after)}"
        print(f"[PASS] sync_to_claude 追加: 文件行数 2 → 4")

        # 7. doctor
        d = doctor([session])
        assert d["ok"]
        assert d["stats"]["total_sessions"] == 1
        assert d["stats"]["by_format"]["claude"] == 1
        assert d["stats"]["empty_sessions"] == 0
        assert len(d["issues"]) == 0
        print(f"[PASS] doctor: ok={d['ok']}, {d['stats']}")

        # doctor 检测 empty session
        from chat_import import ChatSession
        empty_session = ChatSession(
            session_id="empty", source_format="claude", source_path="",
            messages=[], source_hash="sha256:empty",
        )
        d_empty = doctor([empty_session])
        assert not d_empty["ok"]
        assert d_empty["stats"]["empty_sessions"] == 1
        print(f"[PASS] doctor: 检测 empty session")

        # 8. verify_session
        v = verify_session(session)
        assert v["ok"]
        assert v["checks"]["messages_count"] == 2
        assert v["checks"]["first_message_at"] == "2026-08-26T10:00:00Z"
        print(f"[PASS] verify_session: {v['checks']['messages_count']} messages verified")


if __name__ == "__main__":
    test_04_sync_export_audit()
