"""mneme-heat-engine · retrieval V1.3 (W3 · BM25 + 图谱召回)

借鉴自 dsh-mneme v0.5.0 BM25 + 图谱召回融合设计（MIT ✅）。
天龙自实现 Python 版（零依赖 · 仅标准库）。

召回路径：
  Step 1: 用户提问 → 文本 tokenize
  Step 2: BM25 召回 top-K chunks
  Step 3: 图谱扩展 hops=N（实体三表）
  Step 4: heat 加权排序 → top-N 输出
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from typing import Any

from heat_engine import INIT_HEAT, boost_heat


# === BM25 核心 ===

def tokenize(text: str) -> list[str]:
    """简单分词（按非字母数字字符切 + 小转）."""
    return [w for w in re.split(r"[^a-zA-Z0-9\u4e00-\u9fff]+", text.lower()) if w]


def bm25_score(
    query_terms: list[str],
    doc_terms: list[str],
    doc_lens: list[int],
    avg_dl: float,
    N: int,
    df: dict[str, int],
    k1: float = 1.5,
    b: float = 0.75,
) -> float:
    """单文档 BM25 评分（Robertson-Sparck Jones）."""
    score = 0.0
    doc_term_counts = Counter(doc_terms)
    dl = len(doc_terms)
    for q in query_terms:
        if q not in doc_term_counts:
            continue
        f = doc_term_counts[q]
        n_q = df.get(q, 0)
        idf = math.log((N - n_q + 0.5) / (n_q + 0.5) + 1)
        numerator = f * (k1 + 1)
        denominator = f + k1 * (1 - b + b * dl / avg_dl)
        score += idf * (numerator / denominator)
    return score


def bm25_rank(
    query: str,
    documents: list[dict],
    text_field: str = "text",
    top_k: int = 5,
) -> list[tuple[dict, float]]:
    """BM25 召回 top-K 文档."""
    query_terms = tokenize(query)
    if not query_terms or not documents:
        return []

    # 预计算语料统计
    doc_term_lists = [tokenize(d[text_field]) for d in documents]
    doc_lens = [len(t) for t in doc_term_lists]
    avg_dl = sum(doc_lens) / len(doc_lens) if doc_lens else 0
    N = len(documents)

    # 文档频率 df
    df: dict[str, int] = defaultdict(int)
    for terms in doc_term_lists:
        for q in set(query_terms) & set(terms):
            df[q] += 1

    # 评分
    scores = []
    for i, doc in enumerate(documents):
        s = bm25_score(query_terms, doc_term_lists[i], doc_lens,
                       avg_dl, N, df)
        scores.append((doc, s))

    scores.sort(key=lambda x: x[1], reverse=True)
    return scores[:top_k]


# === 图谱扩展（hops） ===

def graph_expand(
    seed_docs: list[dict],
    entities: list[dict],
    relations: list[dict],
    hops: int = 1,
) -> list[dict]:
    """从 seed 文档沿关系 hops 跳扩展，返回关联实体对应的文档."""
    # 构建实体索引
    entity_by_doc = {e.get("id"): e for e in entities}
    rels_by_from = defaultdict(list)
    rels_by_to = defaultdict(list)
    for r in relations:
        rels_by_from[r["from"]].append(r)
        rels_by_to[r["to"]].append(r)

    # 从 seed docs 提取实体 id
    seed_entity_ids = set()
    for doc in seed_docs:
        if doc.get("entity_id") in entity_by_doc:
            seed_entity_ids.add(doc["entity_id"])

    # BFS 扩展
    visited = set(seed_entity_ids)
    frontier = set(seed_entity_ids)
    for _ in range(hops):
        next_frontier = set()
        for eid in frontier:
            for r in rels_by_from.get(eid, []):
                if r["to"] not in visited:
                    visited.add(r["to"])
                    next_frontier.add(r["to"])
            for r in rels_by_to.get(eid, []):
                if r["from"] not in visited:
                    visited.add(r["from"])
                    next_frontier.add(r["from"])
        frontier = next_frontier
        if not frontier:
            break

    # 返回 seed 之外的新扩展文档
    expanded = []
    for eid in visited - seed_entity_ids:
        ent = entity_by_doc.get(eid)
        if ent:
            expanded.append({
                "entity_id": eid,
                "text": f"entity:{eid} type:{ent['type']}",
                "heat": ent.get("heat", INIT_HEAT),
                "source": "graph_expand",
            })
    return expanded


# === heat 加权排序 ===

def heat_weighted_rerank(
    bm25_results: list[tuple[dict, float]],
    graph_results: list[dict],
    bm25_weight: float = 0.7,
    heat_weight: float = 0.3,
    top_n: int = 5,
) -> list[dict]:
    """BM25 score + heat 综合排序."""
    # 归一化 BM25 分数
    max_bm25 = max((s for _, s in bm25_results), default=1.0) or 1.0

    # BM25 候选加权
    bm25_dict: dict[str, dict] = {}
    for doc, score in bm25_results:
        doc_id = doc.get("id", doc.get("entity_id", id(doc)))
        normalized = score / max_bm25
        doc["bm25_score"] = normalized
        doc["final_score"] = bm25_weight * normalized + heat_weight * doc.get("heat", INIT_HEAT)
        bm25_dict[doc_id] = doc

    # 图谱扩展候选加权（BM25=0，纯 heat 评分）
    for doc in graph_results:
        doc_id = doc.get("id", doc.get("entity_id", id(doc)))
        doc["bm25_score"] = 0.0
        doc["final_score"] = bm25_weight * 0.0 + heat_weight * doc.get("heat", INIT_HEAT)
        if doc_id not in bm25_dict:
            bm25_dict[doc_id] = doc

    # 排序
    results = sorted(bm25_dict.values(), key=lambda d: d["final_score"], reverse=True)
    return results[:top_n]


# === 端到端 pipeline ===

def retrieve(
    query: str,
    documents: list[dict],
    entities: list[dict],
    relations: list[dict],
    top_k: int = 20,
    hops: int = 1,
    top_n: int = 5,
) -> list[dict]:
    """BM25 top-K → 图谱 hops 扩展 → heat 加权 → top-N."""
    bm25_results = bm25_rank(query, documents, top_k=top_k)
    seed_docs = [d for d, _ in bm25_results]
    graph_results = graph_expand(seed_docs, entities, relations, hops=hops)
    final = heat_weighted_rerank(bm25_results, graph_results, top_n=top_n)
    return final


def cmd_demo(args: argparse.Namespace) -> int:
    """BM25 + 图谱 + heat 端到端演示."""
    today = "2026-08-24"

    # 语料库（天龙 MEMORY 模拟）
    documents = [
        {"id": "doc-1", "entity_id": "laoli",
         "text": "老李是投资者，关注 AI 和财经赛道，运营秉凌自媒体", "heat": 0.85},
        {"id": "doc-2", "entity_id": "dragon-engine",
         "text": "天龙引擎是博主全息克隆 + 多模态工业化生成 + 9 平台分发的内容生产引擎", "heat": 0.75},
        {"id": "doc-3", "entity_id": "28-01-khazix-writer",
         "text": "khazix-writer 是 28-01 岗位核心 skill，借鉴 KKKKhazix/khazix-skills 16k stars", "heat": 0.7},
        {"id": "doc-4", "entity_id": "mneme-heat-engine",
         "text": "mneme-heat-engine 自进化记忆引擎，借鉴 dsh-mneme MIT 协议", "heat": 0.9},
        {"id": "doc-5", "entity_id": "darwin-skill",
         "text": "darwin-skill 自动化 skill 优化器，9 维 rubric + hill climbing", "heat": 0.65},
    ]

    entities = [
        {"id": "laoli", "type": "person", "heat": 0.85, "attrs": [], "relations": []},
        {"id": "dragon-engine", "type": "project", "heat": 0.75, "attrs": [], "relations": []},
        {"id": "28-01-khazix-writer", "type": "agent", "heat": 0.7, "attrs": [], "relations": []},
        {"id": "mneme-heat-engine", "type": "skill", "heat": 0.9, "attrs": [], "relations": []},
        {"id": "darwin-skill", "type": "skill", "heat": 0.65, "attrs": [], "relations": []},
    ]

    relations = [
        {"id": "r1", "from": "laoli", "to": "dragon-engine", "weight": 0.95, "type": "uses"},
        {"id": "r2", "from": "dragon-engine", "to": "28-01-khazix-writer", "weight": 0.8, "type": "contains"},
        {"id": "r3", "from": "dragon-engine", "to": "mneme-heat-engine", "weight": 0.85, "type": "contains"},
        {"id": "r4", "from": "dragon-engine", "to": "darwin-skill", "weight": 0.8, "type": "contains"},
        {"id": "r5", "from": "mneme-heat-engine", "to": "darwin-skill", "weight": 0.5, "type": "complements"},
    ]

    # 查询 1：mememe 自进化记忆
    print("=== Query 1: 'mneme 自进化记忆' ===")
    results = retrieve("mneme 自进化记忆", documents, entities, relations,
                       top_k=3, hops=1, top_n=3)
    for r in results:
        print(f"  [{r.get('final_score', 0):.3f}] {r.get('id', r.get('entity_id'))}: "
              f"heat={r.get('heat', 0):.2f} bm25={r.get('bm25_score', 0):.2f} "
              f"source={r.get('source', 'bm25')}")

    # 查询 2：darwin 自动化
    print("\n=== Query 2: 'darwin 自动化 skill 优化' ===")
    results = retrieve("darwin 自动化 skill 优化", documents, entities, relations,
                       top_k=3, hops=1, top_n=3)
    for r in results:
        print(f"  [{r.get('final_score', 0):.3f}] {r.get('id', r.get('entity_id'))}: "
              f"heat={r.get('heat', 0):.2f} bm25={r.get('bm25_score', 0):.2f} "
              f"source={r.get('source', 'bm25')}")

    # 输出 JSON 摘要
    print(json.dumps({
        "queries_tested": 2,
        "documents_count": len(documents),
        "entities_count": len(entities),
        "relations_count": len(relations),
        "method": "bm25(0.7) + graph_hops_1 + heat(0.3) re-rank",
    }, ensure_ascii=False, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="mneme-heat-engine · retrieval V1.3 (BM25 + graph + heat)",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)
    p_demo = sub.add_parser("demo", help="演示 BM25+图谱+heat 端到端")
    p_demo.set_defaults(func=cmd_demo)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())