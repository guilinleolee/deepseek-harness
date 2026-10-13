"""test_03_bundle · SHA-256 双指纹 bundle"""
import sys
import tempfile
import json
import hashlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from chat_import import (
    parse_session_file, export_bundle, restore_bundle, ChatBundle,
)


def test_03_bundle():
    with tempfile.TemporaryDirectory() as tmp:
        # 创建 mock session 文件
        claude_file = Path(tmp) / "session-bundle.jsonl"
        lines = [
            json.dumps({"role": "user", "content": "hello", "timestamp": "2026-08-26T10:00:00Z"}),
            json.dumps({"role": "assistant", "content": "hi!", "timestamp": "2026-08-26T10:00:01Z"}),
        ]
        claude_file.write_text("\n".join(lines), encoding="utf-8")

        session = parse_session_file(claude_file, "claude")

        # export_bundle
        bundle = export_bundle(session, str(claude_file))
        assert isinstance(bundle, ChatBundle)
        assert bundle.source_format == "claude"
        assert bundle.session_id == "session-bundle"
        assert len(bundle.fingerprint_source) > 20  # sha256:xxx 格式
        assert len(bundle.fingerprint_content) > 20
        assert bundle.fingerprint_source != bundle.fingerprint_content  # 双指纹不同
        assert len(bundle.messages) == 2
        print(f"[PASS] export_bundle: source={bundle.fingerprint_source[:30]}..., content={bundle.fingerprint_content[:30]}...")

        # 验证 source_hash 正确
        expected_source_hash = f"sha256:{hashlib.sha256(claude_file.read_bytes()).hexdigest()}"
        assert bundle.fingerprint_source == expected_source_hash
        print(f"[PASS] source_hash matches: {bundle.fingerprint_source[:40]}")

        # 序列化为 JSON
        bundle_json = bundle.to_json()
        assert isinstance(bundle_json, str)
        # 重新解析能拿回
        reparsed = json.loads(bundle_json)
        assert reparsed["session_id"] == bundle.session_id
        assert reparsed["metadata"]["messages_count"] == bundle.metadata["messages_count"]
        print(f"[PASS] bundle JSON 序列化 + 解析 ({len(bundle_json)} 字符)")

        # restore_bundle
        restored = restore_bundle(bundle_json)
        assert restored["ok"]
        assert restored["session_id"] == "session-bundle"
        assert restored["source_format"] == "claude"
        assert restored["messages_count"] == 2
        print(f"[PASS] restore_bundle: ok={restored['ok']}, {restored['messages_count']} msgs recovered")

        # 双指纹跨机器持久化（fingerprint 不变）
        assert restored["fingerprint_source"] == bundle.fingerprint_source
        assert restored["fingerprint_content"] == bundle.fingerprint_content
        print(f"[PASS] 双指纹跨机器持久化: source/content hash 一致")

        # 无效 JSON
        invalid = restore_bundle("not valid json {")
        assert not invalid["ok"]
        assert invalid["error"] == "INVALID_JSON"
        print(f"[PASS] restore_bundle: invalid JSON rejected")


if __name__ == "__main__":
    test_03_bundle()
