import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parent.parent
SPEC = importlib.util.spec_from_file_location("account_memory", ROOT / "scripts" / "account_memory.py")
MEMORY = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MEMORY)


class AccountMemoryTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.account = "creator-a"
        MEMORY.main([
            "--root", str(self.root), "init", "--account", self.account, "--platforms", "douyin,xiaohongshu"
        ])

    def tearDown(self):
        self.temporary.cleanup()

    def run_command(self, *arguments):
        return MEMORY.main(["--root", str(self.root), *arguments])

    def cases(self):
        path = self.root / "accounts" / self.account / "cases.json"
        return json.loads(path.read_text(encoding="utf-8"))

    def test_init_stays_outside_skill_and_sets_local_only_defaults(self):
        profile = json.loads((self.root / "accounts" / self.account / "profile.json").read_text(encoding="utf-8"))
        self.assertTrue(profile["local_only"])
        self.assertFalse(profile["remote_sync"])
        self.assertFalse(profile["raw_media_stored_by_default"])

    def test_empty_codex_home_falls_back_to_the_users_local_codex_directory(self):
        with mock.patch.dict(MEMORY.os.environ, {"CODEX_HOME": ""}, clear=False):
            self.assertEqual(Path.home() / ".codex" / "data" / "media-publish-check", MEMORY.default_root())

    def test_local_utility_has_no_network_client(self):
        source = (ROOT / "scripts" / "account_memory.py").read_text(encoding="utf-8")
        for forbidden in ("import requests", "import urllib", "import socket", "http.client"):
            self.assertNotIn(forbidden, source)

    def test_feedback_creates_only_a_draft_until_explicit_activation(self):
        self.run_command(
            "save-review", "--account", self.account, "--platform", "douyin", "--content-type", "video",
            "--risk-tags", "external-action", "--predicted-risk", "R2"
        )
        case_id = self.cases()[0]["case_id"]
        self.run_command(
            "feedback", "--account", self.account, "--case-id", case_id,
            "--outcome", "platform-notice", "--notice-summary", "redacted notice"
        )
        self.run_command("rebuild-candidates", "--account", self.account)
        active_path = self.root / "accounts" / self.account / "active-rules.json"
        self.assertEqual([], json.loads(active_path.read_text(encoding="utf-8")))
        candidate = json.loads(
            (self.root / "accounts" / self.account / "candidate-updates.json").read_text(encoding="utf-8")
        )[0]
        self.run_command("activate", "--account", self.account, "--candidate-id", candidate["candidate_id"])
        self.assertEqual("active", json.loads(active_path.read_text(encoding="utf-8"))[0]["status"])

    def test_normal_feedback_does_not_create_a_risk_rule(self):
        self.run_command(
            "save-review", "--account", self.account, "--platform", "xiaohongshu", "--content-type", "image-post",
            "--risk-tags", "ai-label", "--predicted-risk", "R1"
        )
        case_id = self.cases()[0]["case_id"]
        self.run_command("feedback", "--account", self.account, "--case-id", case_id, "--outcome", "normal")
        self.run_command("rebuild-candidates", "--account", self.account)
        candidates = json.loads(
            (self.root / "accounts" / self.account / "candidate-updates.json").read_text(encoding="utf-8")
        )
        self.assertEqual([], candidates)

    def test_disabling_memory_stops_context_retrieval_without_deleting_data(self):
        self.run_command("disable", "--account", self.account)
        self.run_command(
            "save-review", "--account", self.account, "--platform", "douyin", "--content-type", "video",
            "--risk-tags", "external-action", "--predicted-risk", "R2"
        )
        self.assertEqual(1, len(self.cases()))
        self.run_command("context", "--account", self.account, "--platform", "douyin", "--risk-tags", "external-action")


if __name__ == "__main__":
    unittest.main()
