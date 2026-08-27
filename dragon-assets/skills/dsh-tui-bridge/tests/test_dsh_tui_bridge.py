"""
dsh-tui-bridge V1.0 · 14 unittest (Stage 47)
"""
import os
import sys
import json
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))

import dsh_tui_bridge as tb  # noqa: E402


class TestTUIStateSnapshot(unittest.TestCase):
    """#1 TUI 状态机 dataclass（6 字段）"""

    def test_basic_parse(self):
        snap = tb.parse_state_snapshot(json.dumps({
            "state_id": "abc",
            "current_scene": "main",
            "input_buffer": "hello",
            "thinking_buffer": "thinking...",
            "working_status": "thinking",
            "context_progress": 0.42,
        }))
        self.assertEqual(snap.state_id, "abc")
        self.assertEqual(snap.current_scene, "main")
        self.assertEqual(snap.working_status, "thinking")
        self.assertEqual(snap.context_progress, 0.42)

    def test_default_values(self):
        snap = tb.parse_state_snapshot(json.dumps({
            "state_id": "x",
            "current_scene": "settings",
        }))
        self.assertEqual(snap.input_buffer, "")
        self.assertEqual(snap.thinking_buffer, "")
        self.assertEqual(snap.working_status, "idle")
        self.assertEqual(snap.context_progress, 0.0)

    def test_invalid_json(self):
        with self.assertRaises(ValueError):
            tb.parse_state_snapshot("not json")

    def test_missing_required_field(self):
        with self.assertRaises(ValueError):
            tb.parse_state_snapshot(json.dumps({"current_scene": "main"}))


class TestChannelProtocol(unittest.TestCase):
    """#2 DSH TUI Channel Protocol（6 类消息 parser）"""

    def test_user_input(self):
        msg = tb.parse_channel_message(json.dumps({
            "type": "user_input", "content": "hello", "seq": 42,
        }))
        self.assertEqual(msg.type, "user_input")
        self.assertEqual(msg.payload["content"], "hello")
        self.assertEqual(msg.seq, 42)

    def test_assistant_thought(self):
        msg = tb.parse_channel_message(json.dumps({
            "type": "assistant_thought", "delta": "思考中...", "done": False,
        }))
        self.assertEqual(msg.type, "assistant_thought")
        self.assertEqual(msg.payload["delta"], "思考中...")
        self.assertFalse(msg.payload["done"])

    def test_tool_call(self):
        msg = tb.parse_channel_message(json.dumps({
            "type": "tool_call", "tool": "bash", "args": {"command": "ls"},
        }))
        self.assertEqual(msg.type, "tool_call")
        self.assertEqual(msg.payload["tool"], "bash")

    def test_tool_result(self):
        msg = tb.parse_channel_message(json.dumps({
            "type": "tool_result", "tool": "bash", "status": "ok", "output": "file1\nfile2",
        }))
        self.assertEqual(msg.type, "tool_result")

    def test_working_activity(self):
        msg = tb.parse_channel_message(json.dumps({
            "type": "working_activity", "type_subtype": "search", "msg": "searching...",
        }))
        self.assertEqual(msg.type, "working_activity")

    def test_approval_request(self):
        msg = tb.parse_channel_message(json.dumps({
            "type": "approval_request", "tool": "write_file",
            "args": {"path": "/tmp/x"}, "deadline": "2026-08-30T00:00:00Z",
        }))
        self.assertEqual(msg.type, "approval_request")

    def test_unknown_type(self):
        with self.assertRaises(ValueError):
            tb.parse_channel_message(json.dumps({"type": "rubbish_msg"}))

    def test_missing_type(self):
        with self.assertRaises(ValueError):
            tb.parse_channel_message(json.dumps({"content": "no type"}))


class TestCordisPatch(unittest.TestCase):
    """#3 cordis patch 生成"""

    def test_default_patch(self):
        patch = tb.generate_cordis_patch()
        self.assertIn("patch", patch)
        self.assertEqual(patch["patch"][0]["insert"][0]["id"], "dsh-tui-bridge")
        self.assertTrue(patch["patch"][0]["insert"][0]["config"]["borrowed"])

    def test_custom_upstream(self):
        patch = tb.generate_cordis_patch(upstream="custom-vendor/foo")
        self.assertEqual(patch["patch"][0]["insert"][0]["config"]["upstream"], "custom-vendor/foo")


class TestAutoSaveSimulator(unittest.TestCase):
    """#4 settings auto-save simulator（借鉴 commit #575）"""

    def test_initial_empty(self):
        result = tb.settings_autosave_simulator({}, [])
        self.assertEqual(result, {})

    def test_single_modification(self):
        result = tb.settings_autosave_simulator(
            {"theme": "dark"},
            [{"language": "zh"}],
        )
        self.assertEqual(result["theme"], "dark")
        self.assertEqual(result["language"], "zh")

    def test_last_write_wins(self):
        result = tb.settings_autosave_simulator(
            {"brightness": "50"},
            [
                {"brightness": "60"},
                {"brightness": "70"},
                {"brightness": "100"},
            ],
        )
        self.assertEqual(result["brightness"], "100")

    def test_complex_changes(self):
        result = tb.settings_autosave_simulator(
            {"a": 1, "b": 2, "c": 3},
            [
                {"b": 20},
                {"c": 30, "d": 4},  # 新增 d
            ],
        )
        self.assertEqual(result, {"a": 1, "b": 20, "c": 30, "d": 4})


if __name__ == "__main__":
    unittest.main(verbosity=2)
