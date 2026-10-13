"""
dsh-chat-import-bridge V1.0 · Stage 53.1 借鉴档 · 18 unittest
"""
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))

import dsh_chat_import_bridge as ci  # noqa: E402


class TestSupportedFormats(unittest.TestCase):
    """#1 17+ agent 来源格式"""

    def test_unique_formats_count(self):
        # 去重后至少 17 种（README 写 17+）
        self.assertGreaterEqual(len(ci.UNIQUE_FORMATS), 17)

    def test_claude_present(self):
        names = [f["name"] for f in ci.UNIQUE_FORMATS]
        self.assertIn("claude", names)

    def test_dsh_present(self):
        names = [f["name"] for f in ci.UNIQUE_FORMATS]
        self.assertIn("dsh", names)

    def test_format_storage_patterns(self):
        for f in ci.UNIQUE_FORMATS:
            self.assertIn("storage", f)
            self.assertGreater(len(f["storage"]), 5)


class TestValidateImport(unittest.TestCase):
    """#2 import_chat 请求 schema 校验"""

    def test_valid_request(self):
        req = ci.ImportChatRequest(format="claude", path="~/.claude/projects/")
        issues = ci.validate_import_chat(req)
        self.assertEqual(issues, [])

    def test_invalid_format(self):
        req = ci.ImportChatRequest(format="rubbish", path="~/.foo/")
        issues = ci.validate_import_chat(req)
        self.assertEqual(len(issues), 1)
        self.assertIn("invalid format", issues[0])

    def test_missing_path(self):
        req = ci.ImportChatRequest(format="claude", path="")
        issues = ci.validate_import_chat(req)
        self.assertEqual(len(issues), 1)
        self.assertIn("missing 'path'", issues[0])

    def test_invalid_hash_format(self):
        req = ci.ImportChatRequest(format="dsh", path="~/.dsh/", expected_hash="not-hex!")
        issues = ci.validate_import_chat(req)
        self.assertEqual(len(issues), 1)

    def test_valid_hash_format(self):
        req = ci.ImportChatRequest(
            format="dsh", path="~/.dsh/", expected_hash="a1b2c3d4e5f67890"  # 16 chars
        )
        issues = ci.validate_import_chat(req)
        self.assertEqual(issues, [])


class TestExportFormats(unittest.TestCase):
    """#3 matrix export 3 格式"""

    def test_three_formats(self):
        self.assertEqual(len(ci.EXPORT_FORMATS), 3)
        self.assertEqual(ci.EXPORT_FORMATS, ["claude", "codex", "kimi"])


class TestSHA256Dedup(unittest.TestCase):
    """#4 SHA-256 dedup"""

    def test_consistent_hash(self):
        h1 = ci.sha256_dedup_content(b"hello world")
        h2 = ci.sha256_dedup_content(b"hello world")
        self.assertEqual(h1, h2)

    def test_diff_content_diff_hash(self):
        h1 = ci.sha256_dedup_content(b"hello")
        h2 = ci.sha256_dedup_content(b"world")
        self.assertNotEqual(h1, h2)

    def test_hash_length_16(self):
        h = ci.sha256_dedup_content(b"test")
        self.assertEqual(len(h), 16)


class TestIdempotency(unittest.TestCase):
    """#5 幂等性 3 状态"""

    def test_unchanged_skip(self):
        self.assertEqual(ci.check_idempotency("a1b2", "a1b2"), "skip")

    def test_first_import(self):
        self.assertEqual(ci.check_idempotency("a1b2", ""), "import")

    def test_grown_append(self):
        self.assertEqual(ci.check_idempotency("c3d4", "a1b2"), "append")


class TestInterchangeBundle(unittest.TestCase):
    """#6 portable interchange bundle"""

    def test_verify_integrity_match(self):
        content = b"hello world"
        sha = ci.sha256_dedup_content(content)  # 16 chars
        # actual full sha256
        full_sha = __import__("hashlib").sha256(content).hexdigest()
        bundle = ci.InterchangeBundle(
            primary_sha256=full_sha,
            secondary_sha256="metadata-sha",
            contents=content,
        )
        self.assertTrue(bundle.verify_integrity())

    def test_verify_integrity_mismatch(self):
        bundle = ci.InterchangeBundle(
            primary_sha256="wrong-sha",
            secondary_sha256="metadata-sha",
            contents=b"hello",
        )
        self.assertFalse(bundle.verify_integrity())


class TestEndToEnd(unittest.TestCase):
    """#7 end-to-end 集成"""

    def test_workflow(self):
        # 1. list formats
        self.assertGreaterEqual(len(ci.UNIQUE_FORMATS), 17)
        # 2. validate request
        req = ci.ImportChatRequest(format="dsh", path="~/.dsh/")
        self.assertEqual(ci.validate_import_chat(req), [])
        # 3. export format
        self.assertEqual(len(ci.EXPORT_FORMATS), 3)
        # 4. dedup + idempotency
        h1 = ci.sha256_dedup_content(b"test")
        h2 = ci.sha256_dedup_content(b"test")
        self.assertEqual(h1, h2)
        self.assertEqual(ci.check_idempotency(h1, h2), "skip")


if __name__ == "__main__":
    unittest.main(verbosity=2)
