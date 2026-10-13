"""
memsearch-bridge V1.0 · Stage 49.2 borrowed-bridge · 15+ unittest
"""
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))

import memsearch_bridge as mb  # noqa: E402


class TestSHA256Dedup(unittest.TestCase):
    """#1 SHA-256 dedup"""

    def test_consistent_hash(self):
        h1 = mb.sha256_dedup("hello world")
        h2 = mb.sha256_dedup("hello world")
        self.assertEqual(h1, h2)

    def test_diff_input_diff_hash(self):
        h1 = mb.sha256_dedup("hello")
        h2 = mb.sha256_dedup("world")
        self.assertNotEqual(h1, h2)


class TestParseMarkdown(unittest.TestCase):
    """#2 Markdown memory parse"""

    def test_basic_parse(self):
        # ASCII-only content to avoid encoding issues
        content = "redis #redis\ncaching #caching\ndeploy #k8s"
        m = mb.parse_markdown_memory("2026-08-26.md", content)
        self.assertEqual(m.sha256, mb.sha256_dedup(content))
        self.assertIn("redis", m.tags)
        self.assertIn("caching", m.tags)
        self.assertIn("k8s", m.tags)

    def test_no_tags(self):
        content = "this is plain text without tags"
        m = mb.parse_markdown_memory("x.md", content)
        self.assertEqual(m.tags, [])

    def test_empty_content(self):
        with self.assertRaises(ValueError):
            mb.parse_markdown_memory("x.md", "")

    def test_multiple_inline_tags(self):
        content = "redis #redis caching #caching deploy #k8s #devops"
        m = mb.parse_markdown_memory("x.md", content)
        self.assertEqual(set(m.tags), {"redis", "caching", "k8s", "devops"})

    def test_path_preserved(self):
        m = mb.parse_markdown_memory("/path/to/mem.md", "tag #test")
        self.assertEqual(m.path, "/path/to/mem.md")
        self.assertIn("test", m.tags)


class TestProgressiveRetrieve(unittest.TestCase):
    """#3 Progressive 3-layer retrieval"""

    def _mems(self):
        return [
            mb.MarkdownMemory("a.md", "abc123", "2026-08-26T10:00:00Z",
                              "Redis caching 60s TTL strategy", tags=["redis"]),
            mb.MarkdownMemory("b.md", "def456", "2026-08-25T10:00:00Z",
                              "K8s deploy via ArgoCD GitOps", tags=["k8s"]),
            mb.MarkdownMemory("c.md", "ghi789", "2026-08-24T10:00:00Z",
                              "Python typing generics PEP 484", tags=["python"]),
        ]

    def test_search_layer_keyword_match(self):
        r = mb.progressive_retrieve("redis", self._mems())
        search = [l for l in r.layers if l.layer == "search"]
        self.assertGreater(len(search), 0)
        # a.md 应有命中
        a_matches = [l for l in search if l.memory_path == "a.md"]
        self.assertGreater(len(a_matches), 0)

    def test_empty_query_no_match(self):
        r = mb.progressive_retrieve("nonexistent_keyword_xyzzy", self._mems())
        search = [l for l in r.layers if l.layer == "search"]
        self.assertEqual(len(search), 0)

    def test_empty_mems(self):
        r = mb.progressive_retrieve("anything", [])
        self.assertEqual(r.layers, [])

    def test_sorted_by_score(self):
        r = mb.progressive_retrieve("redis", self._mems())
        scores = [l.score for l in r.layers]
        self.assertEqual(scores, sorted(scores, reverse=True))

    def test_expand_layer_tag_match(self):
        r = mb.progressive_retrieve("redis", self._mems())
        expand = [l for l in r.layers if l.layer == "expand"]
        # a.md tags=[redis] → expand 应有命中
        self.assertGreater(len(expand), 0)


class TestRRFRerank(unittest.TestCase):
    """#4 RRF reranking"""

    def test_basic_rrf(self):
        dense = [("doc1", 0.9), ("doc2", 0.7)]
        sparse = [("doc2", 0.95), ("doc1", 0.6)]
        fused = mb.rrf_rerank(dense, sparse)
        # RRF 数学：doc1 = 1/61+1/62, doc2 = 1/62+1/61 → 相等
        self.assertEqual(len(fused), 2)
        self.assertIn(fused[0][0], ["doc1", "doc2"])

    def test_disjoint_results(self):
        dense = [("doc1", 0.9)]
        sparse = [("doc2", 0.95)]
        fused = mb.rrf_rerank(dense, sparse)
        self.assertEqual(len(fused), 2)
        self.assertIn("doc1", [d for d, _ in fused])
        self.assertIn("doc2", [d for d, _ in fused])

    def test_empty_inputs(self):
        fused = mb.rrf_rerank([], [])
        self.assertEqual(fused, [])

    def test_one_side_empty(self):
        dense = [("doc1", 0.9), ("doc2", 0.5)]
        fused = mb.rrf_rerank(dense, [])
        self.assertEqual(len(fused), 2)
        top_doc, top_score = fused[0]
        self.assertEqual(top_doc, "doc1")


class TestSkillExtract(unittest.TestCase):
    """#5 Skills from memory extraction"""

    def test_extract_with_steps(self):
        content = "Procedure:\n1. find the key\n2. rotate it\n3. test\n4. deploy"
        mem = mb.MarkdownMemory("p.md", "p", "2026-08-26T10:00:00Z", content, tags=[])
        cand = mb.extract_skill_candidate(mem)
        self.assertIsNotNone(cand)
        self.assertGreaterEqual(len(cand.workflow_steps), 3)

    def test_extract_no_steps(self):
        mem = mb.MarkdownMemory("p.md", "p", "2026-08-26T10:00:00Z", "no steps here", tags=[])
        cand = mb.extract_skill_candidate(mem)
        self.assertIsNone(cand)

    def test_extract_exactly_3_steps(self):
        content = "Steps:\n1. one\n2. two\n3. three"
        mem = mb.MarkdownMemory("p.md", "p", "2026-08-26T10:00:00Z", content, tags=[])
        cand = mb.extract_skill_candidate(mem)
        self.assertIsNotNone(cand)
        self.assertEqual(len(cand.workflow_steps), 3)


class TestMemsearchEndToEnd(unittest.TestCase):
    """#6 end-to-end integration"""

    def test_workflow(self):
        # 1. parse memory
        mem = mb.parse_markdown_memory(
            "e2e.md",
            "Procedure:\n1. grep the code\n2. edit\n3. test"
        )
        # 2. retrieve
        r = mb.progressive_retrieve("edit code", [mem])
        self.assertGreater(len(r.layers), 0)
        # 3. extract skill
        cand = mb.extract_skill_candidate(mem)
        self.assertIsNotNone(cand)
        self.assertEqual(len(cand.workflow_steps), 3)


if __name__ == "__main__":
    unittest.main(verbosity=2)
