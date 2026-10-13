"""
dsh-desktop-bridge V1.0 · Stage 49.1 借鉴档 · 12+ unittest
"""
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))

import dsh_desktop_bridge as db  # noqa: E402


class TestDSHDesktopState(unittest.TestCase):
    """#1 DSH 桌面状态 dataclass"""

    def test_default_state(self):
        s = db.DSHDesktopState()
        self.assertEqual(s.active_workspace, "default")
        self.assertEqual(s.theme, "auto")
        self.assertEqual(s.language, "zh-CN")
        self.assertEqual(s.recent_workspaces, [])


class TestManifestParser(unittest.TestCase):
    """#2 DSH 插件 manifest 解析"""

    def test_basic_parse(self):
        yml = """id: tui-bridge
name: TUI Bridge
version: 1.0.0
entry: ./lib/index.js
manifest: dsh.plugin/v1
borrowed: true
borrowed_from: ccch1mneyyy/dsh-TUI
"""
        m = db.parse_manifest(yml)
        self.assertEqual(m.id, "tui-bridge")
        self.assertEqual(m.version, "1.0.0")
        self.assertTrue(m.borrowed)

    def test_missing_required_key(self):
        with self.assertRaises(ValueError):
            db.parse_manifest("id: x\nname: y\nversion: 1.0.0\nentry: a")


class TestComposerCommands(unittest.TestCase):
    """#3 Composer Dock 命令"""

    def test_list_all(self):
        cmds = db.list_composer_commands()
        self.assertGreaterEqual(len(cmds), 4)
        self.assertIn("/workspace", [c["cmd"] for c in cmds])

    def test_parse_valid(self):
        r = db.parse_composer_command("/workspace default")
        self.assertTrue(r["ok"])
        self.assertEqual(r["cmd"], "/workspace")
        self.assertEqual(r["args"], "default")

    def test_parse_unknown(self):
        r = db.parse_composer_command("/nonsense arg")
        self.assertFalse(r["ok"])
        self.assertIn("unknown command", r["error"])

    def test_parse_no_slash(self):
        r = db.parse_composer_command("workspace default")
        self.assertFalse(r["ok"])


class TestWorkspaceRoute(unittest.TestCase):
    """#4 多 workspace 路由"""

    def test_route_by_id(self):
        wss = [db.Workspace(id="default", name="Default", path="/home/x/dsh"),
               db.Workspace(id="work", name="Work", path="/home/x/work")]
        ws = db.route_workspace("work", wss)
        self.assertEqual(ws.id, "work")

    def test_route_by_name(self):
        wss = [db.Workspace(id="default", name="Default", path="/home/x/dsh")]
        ws = db.route_workspace("Default", wss)
        self.assertEqual(ws.id, "default")

    def test_route_not_found(self):
        wss = [db.Workspace(id="x", name="X", path="/")]
        with self.assertRaises(KeyError):
            db.route_workspace("nonexistent", wss)


class TestAgentDispatch(unittest.TestCase):
    """#5 Agent task 派发"""

    def test_captain_round_robin(self):
        t = db.AgentTask(id="t1", description="test", assignee="captain")
        r = db.dispatch_task(t, ["alice", "bob"])
        self.assertEqual(r["assignee"], "alice")

    def test_named_assignee(self):
        t = db.AgentTask(id="t2", description="test", assignee="bob")
        r = db.dispatch_task(t, ["alice", "bob"])
        self.assertEqual(r["assignee"], "bob")

    def test_no_members(self):
        t = db.AgentTask(id="t3", description="test", assignee="captain")
        r = db.dispatch_task(t, [])
        self.assertEqual(r["assignee"], "captain")  # 保持


if __name__ == "__main__":
    unittest.main(verbosity=2)
