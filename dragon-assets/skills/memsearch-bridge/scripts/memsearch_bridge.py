"""
memsearch-bridge V1.0 · Stage 49.2 借鉴档 · zilliztech/memsearch MIT 借鉴

================================================================================
  Stage 49.2 · 2026-08-26

设计：
  - 借鉴档模式（与 stage 45 dsh-eval / 46 dsh-peak-gate / 48 dsh-TUI / 49.1 dsh-desktop 同）
  - 5 类借鉴：Markdown is source of truth / Milvus shadow index / progressive retrieval /
    hybrid search (dense + BM25 + RRF) / skills from memory (procedural)
  - 不实跑 memsearch CLI（DSH Desktop 路径依赖 + ONNX 模型 1GB+ 下载）
  - 自研 14/14 unittest PASS
  - 退出码契约：0=OK / 1=PARSE_ERR / 2=QUERY_ERR / 3=CMD_ERR
================================================================================
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

EXIT_OK = 0
EXIT_PARSE = 1
EXIT_QUERY = 2
EXIT_CMD = 3


# ==============================================================================
# 1. Markdown 源真 + SHA-256 内容 hash（smart dedup 借鉴）
# ==============================================================================

@dataclass
class MarkdownMemory:
    """Markdown 记忆条目（与上游一致）"""
    path: str                          # .memsearch/memory/2026-08-26.md
    sha256: str                        # smart dedup
    created_at: str                    # ISO timestamp
    content: str = ""
    tags: List[str] = field(default_factory=list)


def sha256_dedup(content: str) -> str:
    """与上游一致：SHA-256 内容 hash · 跳过未变更内容"""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]


def parse_markdown_memory(path: str, content: str) -> MarkdownMemory:
    """解析 .md 记忆文件"""
    if not content:
        raise ValueError(f"empty content: {path}")
    # 提取 tags（只匹配 inline #tag · 排除 Markdown 一级标题行首 #）
    # 用 ASCII \w (re.ASCII) 避免 # 被误识别为 word 字符
    tags = re.findall(r"#(\w+)", content, re.ASCII)
    return MarkdownMemory(
        path=path,
        sha256=sha256_dedup(content),
        created_at=datetime.now(timezone.utc).isoformat(),
        content=content,
        tags=tags,
    )


# ==============================================================================
# 2. Progressive retrieval（3 层借鉴：search → expand → transcript）
# ==============================================================================

@dataclass
class RetrievalLayer:
    """单层检索结果"""
    layer: str           # search / expand / transcript
    score: float         # 0.0 ~ 1.0
    memory_path: str
    snippet: str = ""


@dataclass
class RetrievalResult:
    query: str
    layers: List[RetrievalLayer] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "query": self.query,
            "layers": [asdict(l) for l in self.layers],
        }


def progressive_retrieve(query: str, memories: List[MarkdownMemory]) -> RetrievalResult:
    """3 层检索（mock 借鉴设计 · 不实跑 Milvus 向量搜索）"""
    if not memories:
        return RetrievalResult(query=query)

    # Layer 1: 关键词命中（search）
    layer1 = []
    for m in memories:
        score = sum(1 for term in query.lower().split() if term in m.content.lower()) / max(len(query.split()), 1)
        if score > 0:
            layer1.append(RetrievalLayer(layer="search", score=score, memory_path=m.path, snippet=m.content[:100]))

    # Layer 2: tag 命中（expand）
    layer2 = []
    for m in memories:
        score = sum(1 for tag in m.tags if tag in query.lower()) / max(len(m.tags), 1)
        if score > 0:
            layer2.append(RetrievalLayer(layer="expand", score=score * 0.7, memory_path=m.path, snippet=f"#{','.join(m.tags[:3])}"))

    # Layer 3: transcript snippet（mock）
    layer3 = [
        RetrievalLayer(layer="transcript", score=0.3, memory_path=".memsearch/transcripts/latest.md",
                       snippet="mock transcript match")
    ]

    return RetrievalResult(
        query=query,
        layers=sorted(layer1 + layer2 + layer3, key=lambda l: -l.score),
    )


# ==============================================================================
# 3. Hybrid search（dense vector + BM25 sparse + RRF reranking）
# ==============================================================================

def rrf_rerank(
    dense_results: List[Tuple[str, float]],
    sparse_results: List[Tuple[str, float]],
    k: int = 60,
) -> List[Tuple[str, float]]:
    """Reciprocal Rank Fusion 借鉴实现"""
    fused: Dict[str, float] = {}
    for rank, (doc_id, score) in enumerate(dense_results):
        fused[doc_id] = fused.get(doc_id, 0) + 1 / (k + rank + 1)
    for rank, (doc_id, score) in enumerate(sparse_results):
        fused[doc_id] = fused.get(doc_id, 0) + 1 / (k + rank + 1)
    return sorted(fused.items(), key=lambda x: -x[1])


# ==============================================================================
# 4. Skills from memory（procedural memory 借鉴）
# ==============================================================================

@dataclass
class SkillCandidate:
    """上游 README §Skills from memory 借鉴设计"""
    name: str
    description: str
    workflow_steps: List[str] = field(default_factory=list)
    install_count: int = 0
    confidence: float = 0.0


def extract_skill_candidate(memory: MarkdownMemory, min_steps: int = 3) -> Optional[SkillCandidate]:
    """从 memory 提取 skill candidate（mock 借鉴算法）"""
    # 启发式：含 3+ 步骤描述（"1. xxx 2. yyy 3. zzz"）→ 候选
    steps = re.findall(r"^\s*\d+[\.、]\s*(.+?)$", memory.content, re.MULTILINE)
    if len(steps) >= min_steps:
        return SkillCandidate(
            name=f"auto-skill-{memory.sha256[:8]}",
            description=f"From memory {memory.path}: {memory.content[:80]}",
            workflow_steps=steps,
            confidence=0.7,
        )
    return None


# ==============================================================================
# CLI
# ==============================================================================

def cmd_hash(args: argparse.Namespace) -> int:
    """SHA-256 dedup demo"""
    h = sha256_dedup(args.input)
    print(json.dumps({"input_len": len(args.input), "sha256_short": h}, indent=2))
    return EXIT_OK


def cmd_retrieve(args: argparse.Namespace) -> int:
    """Progressive 3-layer retrieval demo"""
    # mock 记忆库
    mems = [
        MarkdownMemory(
            path=".memsearch/memory/2026-08-26.md",
            sha256="abc123",
            created_at="2026-08-26T10:00:00Z",
            content="今天讨论了 Redis caching 策略，选了 60s TTL。",
            tags=["redis", "caching"],
        ),
        MarkdownMemory(
            path=".memsearch/memory/2026-08-25.md",
            sha256="def456",
            created_at="2026-08-25T10:00:00Z",
            content="部署架构用 K8s + ArgoCD GitOps 流程",
            tags=["k8s", "deploy"],
        ),
    ]
    result = progressive_retrieve(args.query, mems)
    print(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))
    return EXIT_OK


def cmd_rrf(args: argparse.Namespace) -> int:
    """RRF rerank demo"""
    dense = [("doc1", 0.9), ("doc2", 0.7), ("doc3", 0.5)]
    sparse = [("doc2", 0.95), ("doc1", 0.6), ("doc4", 0.4)]
    fused = rrf_rerank(dense, sparse)
    print(json.dumps([{"doc_id": d, "rrf_score": float(s)} for d, s in fused], indent=2))
    return EXIT_OK


def cmd_extract_skill(args: argparse.Namespace) -> int:
    """从 memory 提取 skill candidate"""
    mem = MarkdownMemory(
        path="mock.md",
        sha256="xyz",
        created_at=datetime.now(timezone.utc).isoformat(),
        content=args.input,
        tags=[],
    )
    cand = extract_skill_candidate(mem)
    if cand:
        print(json.dumps(asdict(cand), indent=2, ensure_ascii=False))
    else:
        print("[skip] need 3+ numbered steps in content", file=sys.stderr)
        return EXIT_QUERY
    return EXIT_OK


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="memsearch_bridge",
        description="Stage 49.2 memsearch-bridge V1.0 · zilliztech/memsearch MIT 借鉴档",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("hash", help="SHA-256 dedup demo")
    sp.add_argument("--input", required=True)
    sp.set_defaults(func=cmd_hash)

    sp = sub.add_parser("retrieve", help="Progressive 3-layer retrieval demo")
    sp.add_argument("--query", required=True)
    sp.set_defaults(func=cmd_retrieve)

    sp = sub.add_parser("rrf", help="RRF rerank demo")
    sp.set_defaults(func=cmd_rrf)

    sp = sub.add_parser("extract-skill", help="从 memory 提取 skill candidate")
    sp.add_argument("--input", required=True, help="memory 内容文本（需 3+ 编号步骤）")
    sp.set_defaults(func=cmd_extract_skill)

    return p


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except (ValueError, KeyError) as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        return EXIT_QUERY


if __name__ == "__main__":
    sys.exit(main())
