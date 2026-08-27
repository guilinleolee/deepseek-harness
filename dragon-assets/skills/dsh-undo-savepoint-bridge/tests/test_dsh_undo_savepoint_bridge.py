"""
dsh-undo-savepoint-bridge V1.0 · Stage 54.1 借鉴档 · 15 unittest
"""
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))

import dsh_undo_savepoint_bridge as us  # noqa: E402


class TestRedactSecrets(unittest.TestCase):
    """#1 secret-safe redact"""

    def test_redact_api_key(self):
        input_s = "api_key = 'sk-1234567890abcdefghij'"
        out = us.redact_secrets(input_s)
        self.assertIn("[REDACTED]", out)
        self.assertNotIn("sk-1234567890", out)

    def test_redact_bearer_token(self):
        input_s = "Authorization: Bearer abc123def456ghi789jkl012"
        out = us.redact_secrets(input_s)
        self.assertIn("[REDACTED]", out)

    def test_redact_password(self):
        input_s = "password = mysecretpass123"
        out = us.redact_secrets(input_s)
        self.assertIn("[REDACTED]", out)

    def test_no_secret_unchanged(self):
        input_s = "this is just normal text"
        out = us.redact_secrets(input_s)
        self.assertEqual(out, input_s)


class TestSafeMode(unittest.TestCase):
    """#2 SAFE MODE 3 档校验"""

    def test_minimal_valid(self):
        cfg = us.SafeModeConfig(level="minimal")
        self.assertEqual(us.validate_safe_mode(cfg), [])

    def test_offline_valid(self):
        cfg = us.SafeModeConfig(level="offline")
        self.assertEqual(us.validate_safe_mode(cfg), [])

    def test_readonly_requires_flag(self):
        cfg = us.SafeModeConfig(level="readonly", readonly_mode=False)
        issues = us.validate_safe_mode(cfg)
        self.assertEqual(len(issues), 1)

    def test_readonly_with_flag_valid(self):
        cfg = us.SafeModeConfig(level="readonly", readonly_mode=True)
        self.assertEqual(us.validate_safe_mode(cfg), [])

    def test_invalid_level(self):
        cfg = us.SafeModeConfig(level="bogus")
        issues = us.validate_safe_mode(cfg)
        self.assertEqual(len(issues), 1)


class TestOfflineCommands(unittest.TestCase):
    """#3 offline CLI 命令"""

    def test_five_commands(self):
        cmds = us.list_offline_commands()
        self.assertEqual(len(cmds), 5)

    def test_all_offline(self):
        cmds = us.list_offline_commands()
        for c in cmds:
            self.assertTrue(c["offline"], f"{c['name']} should be offline")

    def test_command_names(self):
        cmds = us.list_offline_commands()
        names = [c["name"] for c in cmds]
        self.assertEqual(names, ["rollback", "restore", "verify", "doctor", "safe-mode"])


class TestSnapshotSHA(unittest.TestCase):
    """#4 Snapshot SHA-256"""

    def test_compute_sha256(self):
        s = us.Snapshot(snapshot_id="s1", timestamp="2026-08-26T00:00:00Z")
        s.contents = {"a.txt": "hello", "b.txt": "world"}
        s.sha256 = s.compute_sha256()
        self.assertEqual(len(s.sha256), 64)  # SHA-256 hex

    def test_verify_integrity_match(self):
        s = us.Snapshot(snapshot_id="s1", timestamp="2026-08-26T00:00:00Z")
        s.contents = {"a.txt": "hello"}
        s.sha256 = s.compute_sha256()
        self.assertTrue(s.verify_integrity())

    def test_verify_integrity_tampered(self):
        s = us.Snapshot(snapshot_id="s1", timestamp="2026-08-26T00:00:00Z")
        s.contents = {"a.txt": "hello"}
        s.sha256 = s.compute_sha256()
        # 内容被篡改
        s.contents["a.txt"] = "TAMPERED"
        self.assertFalse(s.verify_integrity())


class TestEndToEnd(unittest.TestCase):
    """#5 end-to-end 集成"""

    def test_workflow(self):
        # 1. redact secrets
        input_s = "api_key = 'sk-1234567890abcdefghij'"  # 22 chars API key
        self.assertIn("[REDACTED]", us.redact_secrets(input_s))
        # 2. validate SAFE MODE
        cfg = us.SafeModeConfig(level="minimal")
        self.assertEqual(us.validate_safe_mode(cfg), [])
        # 3. snapshot integrity
        s = us.Snapshot(snapshot_id="e2e", timestamp="2026-08-26T00:00:00Z")
        s.contents = {"x": "y"}
        s.sha256 = s.compute_sha256()
        self.assertTrue(s.verify_integrity())
        # 4. offline commands
        self.assertEqual(len(us.list_offline_commands()), 5)


if __name__ == "__main__":
    unittest.main(verbosity=2)
