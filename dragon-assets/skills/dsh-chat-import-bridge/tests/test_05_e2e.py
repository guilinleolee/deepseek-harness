"""test_05_e2e · 端到端：scan → import → export → bundle → restore → sync → audit"""
import sys
import tempfile
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from chat_import import (
    scan_discover, import_chat, parse_session_file, export_chat,
    export_bundle, restore_bundle, sync_to_claude, doctor,
)


def test_05_e2e():
    """完整链路：3 个 claude sessions → import → bundle → restore → sync → audit"""
    with tempfile.TemporaryDirectory() as tmp:
        # 创建 3 个 mock claude sessions
        for i in range(3):
            f = Path(tmp) / f"session-{i:03d}.jsonl"
            msgs = [
                json.dumps({"role": "user", "content": f"Q{i+1}", "timestamp": f"2026-08-26T10:0{i}:00Z"}),
                json.dumps({"role": "assistant", "content": f"A{i+1}", "timestamp": f"2026-08-26T10:0{i}:01Z"}),
            ]
            f.write_text("\n".join(msgs), encoding="utf-8")

        # 1. scan
        discovered = scan_discover(tmp, "claude")
        assert len(discovered) >= 3, f"[FAIL] 应发现 ≥3 个，实际 {len(discovered)}"
        print(f"[STEP 1] scan_discover: {len(discovered)} sessions found")

        # 2. import（模拟整体目录）
        result = import_chat("claude", tmp)
        assert result["ok"]
        assert result["imported_count"] >= 3
        print(f"[STEP 2] import_chat: {result['imported_count']} imported, {result['skipped_count']} skipped")

        # 3. 解析第一个 session
        first_path = Path(discovered[0]["path"])
        session = parse_session_file(first_path, "claude")
        print(f"[STEP 3] parse_session: {session.session_id}, {len(session.messages)} msgs")

        # 4. export_chat 反向
        exported = export_chat(session, "claude")
        assert exported["ok"]
        print(f"[STEP 4] export_chat(claude): {exported['content_length']} 字符")

        # 5. bundle 导出
        bundle = export_bundle(session, str(first_path))
        assert bundle.fingerprint_source.startswith("sha256:")
        assert bundle.fingerprint_content.startswith("sha256:")
        print(f"[STEP 5] export_bundle: 2 个 fingerprint OK")

        # 6. bundle 跨机器恢复（JSON 序列化后）
        bundle_json = bundle.to_json()
        bundle_size = len(bundle_json)
        restored = restore_bundle(bundle_json)
        assert restored["ok"]
        print(f"[STEP 6] restore_bundle: {bundle_size} B JSON → {restored['messages_count']} msgs")

        # 7. sync_to_claude
        sync = sync_to_claude(session, str(first_path), dry_run=True)
        assert sync["ok"]
        print(f"[STEP 7] sync_to_claude: {sync['appended_count']} msgs (dry_run)")

        # 8. doctor 健康检查
        all_sessions = [parse_session_file(Path(d["path"]), "claude") for d in discovered[:3]]
        d = doctor(all_sessions)
        assert d["stats"]["total_sessions"] >= 3
        assert d["stats"]["by_format"]["claude"] >= 3
        print(f"[STEP 8] doctor: {d['stats']}")

        # 9. 端到端：聚合验证
        print(f"\n{'=' * 60}")
        print(f"端到端完整链路 PASS:")
        print(f"  scan: {len(discovered)} sessions")
        print(f"  import: {result['imported_count']} imported")
        print(f"  parse: {len(session.messages)} msgs in first session")
        print(f"  export: {exported['content_length']} chars")
        print(f"  bundle: {bundle_size} B (双指纹)")
        print(f"  restore: {restored['messages_count']} msgs")
        print(f"  sync: {sync['appended_count']} msgs (dry_run)")
        print(f"  doctor: {d['stats']['total_sessions']} sessions healthy")
        print(f"{'=' * 60}")


if __name__ == "__main__":
    test_05_e2e()
