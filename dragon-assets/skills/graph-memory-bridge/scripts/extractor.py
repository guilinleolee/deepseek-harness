"""graph-memory-bridge 核心 · V1.0

借鉴 adoresever/graph-memory v1.6.0-beta.9 (576⭐ MIT) 的 9 大核心能力
"""
from __future__ import annotations

import re
import hashlib
import json
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any


# ─── 枚举 ──────────────────────────────────────────────────────────────────

class NodeType(str, Enum):
    TASK = "TASK"
    SKILL = "SKILL"
    EVENT = "EVENT"


class EdgeType(str, Enum):
    USED_SKILL = "USED_SKILL"
    SOLVED_BY = "SOLVED_BY"
    REQUIRES = "REQUIRES"
    PATCHES = "PATCHES"
    CONFLICTS_WITH = "CONFLICTS_WITH"


class EventCategory(str, Enum):
    ERROR = "error"
    FIX = "fix"
    DECISION = "decision"
    CHANGE = "change"
    FACT = "fact"


# ─── 1. 结构化抽取 ──────────────────────────────────────────────────────────

# TASK 触发词
TASK_TRIGGERS = ["需要", "目标是", "任务", "todo", "实现", "调研", "分析",
                 "need to", "task", "implement", "research", "analyze"]

# SKILL 触发词
SKILL_TRIGGERS = ["方法", "技巧", "流程", "经验", "可用", "推荐",
                  "method", "technique", "workflow", "best practice", "use"]

# EVENT 触发词 + 类别
ERROR_TRIGGERS = ["失败", "崩溃", "错误", "异常", "fail", "crash", "error", "exception"]
FIX_TRIGGERS = ["修复", "解决", "patch", "fix", "solve", "resolve"]
DECISION_TRIGGERS = ["决定", "选择", "采用", "decide", "choose", "adopt"]
CHANGE_TRIGGERS = ["改动", "更新", "重构", "change", "update", "refactor"]
FACT_TRIGGERS = ["是", "等于", "包含", "is", "equals", "contains"]


@dataclass
class GraphNode:
    id: str
    type: NodeType
    content: str
    session_id: str = ""
    timestamp: float = 0.0
    confidence: float = 1.0
    metadata: dict = field(default_factory=dict)
    embedding_hash: str = ""

    def to_dict(self) -> dict:
        d = asdict(self)
        d["type"] = self.type.value
        return {k: v for k, v in d.items() if v not in (None, "", {}, [])}


@dataclass
class GraphEdge:
    from_id: str
    to_id: str
    type: EdgeType
    weight: float = 1.0

    def to_dict(self) -> dict:
        d = asdict(self)
        d["type"] = self.type.value
        return {k: v for k, v in d.items() if k != "weight" or v != 1.0}


class GraphStore:
    """In-memory graph store（SQLite + FTS5 mock）"""
    def __init__(self):
        self.nodes: dict[str, GraphNode] = {}
        self.edges: list[GraphEdge] = []
        self.communities: dict[str, set] = {}  # community_id → {node_ids}
        self.fts_index: dict[str, list[str]] = {}  # word → [node_ids]

    def add_node(self, node: GraphNode) -> str:
        self.nodes[node.id] = node
        # 更新 FTS 索引
        for word in re.findall(r"\w+", node.content.lower()):
            self.fts_index.setdefault(word, []).append(node.id)
        return node.id

    def add_edge(self, edge: GraphEdge) -> None:
        self.edges.append(edge)

    def get_node(self, node_id: str) -> GraphNode | None:
        return self.nodes.get(node_id)

    def get_stats(self) -> dict:
        by_type = {}
        for n in self.nodes.values():
            by_type[n.type.value] = by_type.get(n.type.value, 0) + 1
        communities = len(set(frozenset(c) for c in self.communities.values()))
        return {
            "total_nodes": len(self.nodes),
            "total_edges": len(self.edges),
            "by_type": by_type,
            "communities": communities,
        }


# ─── 2. 抽取器 ──────────────────────────────────────────────────────────────

def hash_content(content: str) -> str:
    """稳定的内容 hash（idempotent event ID）"""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()[:12]


def extract_triples(messages: list[dict], session_id: str = "default") -> list[GraphNode]:
    """从对话消息提取 3 类节点

    上游规则：conversation → TASK / SKILL / EVENT
    借鉴档实现：基于 trigger 关键词 + 句式启发式
    """
    nodes = []
    for msg in messages:
        text = msg.get("content", "") or ""
        role = msg.get("role", "user")
        ts = msg.get("timestamp", 0.0)

        # TASK
        if any(t in text.lower() for t in TASK_TRIGGERS):
            nodes.append(GraphNode(
                id=f"task-{hash_content(text)}",
                type=NodeType.TASK,
                content=text,
                session_id=session_id,
                timestamp=ts,
                metadata={"role": role, "outcome": "pending"},
            ))

        # SKILL
        if any(t in text.lower() for t in SKILL_TRIGGERS):
            nodes.append(GraphNode(
                id=f"skill-{hash_content(text)}",
                type=NodeType.SKILL,
                content=text,
                session_id=session_id,
                timestamp=ts,
                confidence=0.85,
                metadata={"role": role, "reuse_count": 0},
            ))

        # EVENT（按触发词分类）
        if any(t in text.lower() for t in ERROR_TRIGGERS):
            cat, sev = EventCategory.ERROR, "error"
        elif any(t in text.lower() for t in FIX_TRIGGERS):
            cat, sev = EventCategory.FIX, "info"
        elif any(t in text.lower() for t in DECISION_TRIGGERS):
            cat, sev = EventCategory.DECISION, "info"
        elif any(t in text.lower() for t in CHANGE_TRIGGERS):
            cat, sev = EventCategory.CHANGE, "info"
        elif any(t in text.lower() for t in FACT_TRIGGERS):
            cat, sev = EventCategory.FACT, "info"
        else:
            cat, sev = None, None

        if cat:
            nodes.append(GraphNode(
                id=f"event-{hash_content(text)}",
                type=NodeType.EVENT,
                content=text,
                session_id=session_id,
                timestamp=ts,
                metadata={"role": role, "category": cat.value, "severity": sev},
            ))

    return nodes


def auto_link(nodes: list[GraphNode]) -> list[GraphEdge]:
    """根据节点类型自动建边

    上游规则：TASK → USED_SKILL → SKILL, TASK → SOLVED_BY → EVENT, etc.
    """
    edges = []
    tasks = [n for n in nodes if n.type == NodeType.TASK]
    skills = [n for n in nodes if n.type == NodeType.SKILL]
    events = [n for n in nodes if n.type == NodeType.EVENT]

    # TASK → SKILL (USED_SKILL)
    for t in tasks:
        for s in skills[:2]:  # 简化：每个 TASK 关联前 2 个 SKILL
            edges.append(GraphEdge(from_id=t.id, to_id=s.id, type=EdgeType.USED_SKILL))

    # TASK → EVENT (SOLVED_BY)
    for t in tasks:
        for e in events[:2]:
            edges.append(GraphEdge(from_id=t.id, to_id=e.id, type=EdgeType.SOLVED_BY))

    # EVENT → SKILL (PATCHES)
    for e in events:
        if e.metadata.get("category") == "fix":
            for s in skills[:1]:
                edges.append(GraphEdge(from_id=e.id, to_id=s.id, type=EdgeType.PATCHES))

    return edges


# ─── 3. PPR 算法 ─────────────────────────────────────────────────────────────

def personalized_pagerank(store: GraphStore, seed_ids: list[str],
                         damping: float = 0.85, iterations: int = 50) -> dict[str, float]:
    """Personalized PageRank（PPR）— graph-memory 推荐用

    标准算法：r(v) = (1-d)/N + d * Σ(r(u)/out(u) * edge_weight(u→v))
    """
    nodes = list(store.nodes.keys())
    n = len(nodes)
    if n == 0:
        return {}

    # 邻接表
    outgoing: dict[str, list[str]] = {nid: [] for nid in nodes}
    for edge in store.edges:
        if edge.from_id in outgoing:
            outgoing[edge.from_id].append(edge.to_id)

    # 初始 PPR（seed 节点 = 1.0，其他 = 0）
    ppr = {nid: 0.0 for nid in nodes}
    for sid in seed_ids:
        if sid in ppr:
            ppr[sid] = 1.0 / len(seed_ids)

    # 迭代
    for _ in range(iterations):
        new_ppr = {nid: (1 - damping) / n for nid in nodes}
        for uid in nodes:
            out = outgoing[uid]
            if out and ppr[uid] > 0:
                share = damping * ppr[uid] / len(out)
                for vid in out:
                    if vid in new_ppr:
                        new_ppr[vid] += share
        ppr = new_ppr

    return ppr


def community_detection(store: GraphStore, resolution: float = 1.0) -> dict[str, int]:
    """简单社区检测（label propagation 简化版）

    每个节点初始 = 自己的 label；
    迭代：选邻居最频繁的 label 作为新 label；
    收敛后，相同 label = 一个社区
    """
    labels = {nid: i for i, nid in enumerate(store.nodes)}

    # 邻接表（双向）
    adj: dict[str, set] = {nid: set() for nid in store.nodes}
    for edge in store.edges:
        if edge.from_id in adj:
            adj[edge.from_id].add(edge.to_id)
        if edge.to_id in adj:
            adj[edge.to_id].add(edge.from_id)

    # 迭代直到收敛
    for _ in range(10):
        changed = False
        for nid in list(store.nodes):
            if not adj[nid]:
                continue
            from collections import Counter
            neighbor_labels = Counter(labels[n] for n in adj[nid])
            most_common = neighbor_labels.most_common(1)[0][0]
            if labels[nid] != most_common:
                labels[nid] = most_common
                changed = True
        if not changed:
            break

    # nid → community_id
    return labels


# ─── 4. 双路径召回 ──────────────────────────────────────────────────────────

def recall(store: GraphStore, query: str, top_k: int = 5,
           recall_token_budget: int = 4096,
           auto_recall_min_score: float = 0.6) -> dict:
    """双路径召回（Exact + Generalized）

    上游算法：
      Exact path:    Vector/FTS5 → community expansion → PPR
      Generalized path: community summary match → members
    借鉴档实现：FTS5 + PPR + token budget
    """
    # Exact path: FTS5 检索
    query_words = set(re.findall(r"\w+", query.lower()))
    candidates = {}
    for word in query_words:
        for nid in store.fts_index.get(word, []):
            candidates[nid] = candidates.get(nid, 0) + 1

    # 取 top candidates 跑 PPR
    seed_ids = sorted(candidates.keys(), key=lambda n: -candidates[n])[:3]
    if not seed_ids:
        return {"ok": True, "results": [], "total_tokens": 0}

    ppr_scores = personalized_pagerank(store, seed_ids)

    # Token budget truncation
    results = []
    total_tokens = 0
    for nid, score in sorted(ppr_scores.items(), key=lambda x: -x[1]):
        node = store.get_node(nid)
        if not node:
            continue
        # Token 估算：~4 chars/token
        node_tokens = len(node.content) // 4
        if total_tokens + node_tokens > recall_token_budget:
            break
        if score >= auto_recall_min_score * 0.01:  # PPR 分数与 autoRecallMinScore 同尺度
            results.append({
                "node_id": nid,
                "type": node.type.value,
                "content": node.content,
                "score": round(score, 4),
                "tokens": node_tokens,
            })
            total_tokens += node_tokens

    return {
        "ok": True,
        "results": results[:top_k],
        "total_tokens": total_tokens,
        "candidates_count": len(candidates),
        "path": "Exact+FTS5+PPR",
    }


# ─── 5. 4 个 gm_* 工具 ──────────────────────────────────────────────────────

def gm_status(store: GraphStore) -> dict:
    """查询插件状态"""
    stats = store.get_stats()
    return {
        "ok": True,
        "tool": "gm_status",
        "store_path": "$DSH_HOME/graph-memory/graph-memory.db",
        "graph_counts": {
            "nodes": stats["total_nodes"],
            "edges": stats["total_edges"],
            "communities": stats["communities"],
            "by_type": stats["by_type"],
        },
        "vector_coverage": 0.0,  # mock
        "mode": "FTS5+vector-optional",
        "dimensions": 0,
    }


def gm_search(store: GraphStore, query: str, top_k: int = 5,
              recall_token_budget: int = 4096) -> dict:
    """显式长期 graph 搜索"""
    return {
        "ok": True,
        "tool": "gm_search",
        "query": query,
        **recall(store, query, top_k, recall_token_budget),
    }


def gm_record(store: GraphStore, type: str, content: str,
              session_id: str = "", confidence: float = 1.0) -> dict:
    """持久化节点（TASK / SKILL / EVENT）"""
    try:
        node_type = NodeType(type)
    except ValueError:
        return {"ok": False, "error": "INVALID_TYPE", "valid": [t.value for t in NodeType]}

    node_id = f"{node_type.value.lower()}-{hash_content(content)}"
    existing = store.get_node(node_id)
    if existing:
        return {
            "ok": True,
            "tool": "gm_record",
            "node_id": node_id,
            "type": type,
            "deduplicated": True,
            "message": "node already exists",
        }

    node = GraphNode(
        id=node_id,
        type=node_type,
        content=content,
        session_id=session_id,
        confidence=confidence,
        timestamp=__import__("time").time(),
    )
    store.add_node(node)
    return {
        "ok": True,
        "tool": "gm_record",
        "node_id": node_id,
        "type": type,
        "deduplicated": False,
        "new_node": node.to_dict(),
    }


def gm_stats(store: GraphStore) -> dict:
    """节点/边/类型/社区统计"""
    return {
        "ok": True,
        "tool": "gm_stats",
        **store.get_stats(),
    }


# ─── 6. rolling checkpoint + budget ────────────────────────────────────────

def rolling_checkpoint(messages: list[dict], fresh_turn_count: int = 5) -> dict:
    """保留最新 N 轮用户消息 + 检查点（旧消息摘要）

    上游规则：freshTurnCount=5（默认）；其余转 model-surface checkpoint
    """
    user_msgs = [m for m in messages if m.get("role") == "user"]

    fresh = user_msgs[-fresh_turn_count:] if len(user_msgs) > fresh_turn_count else user_msgs
    checkpoint_count = len(user_msgs) - len(fresh)

    return {
        "fresh_count": len(fresh),
        "checkpoint_count": checkpoint_count,
        "fresh_messages": [m.get("content", "")[:100] for m in fresh],
        "compression_ratio": round(len(fresh) / max(len(user_msgs), 1), 2),
    }


def truncate_to_budget(text: str, budget_tokens: int = 4096) -> str:
    """recallTokenBudget 截断（~4 chars/token）"""
    max_chars = budget_tokens * 4
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "..."


# ─── 主入口 ────────────────────────────────────────────────────────────────

def main() -> int:
    """演示：完整链路"""
    print("=" * 70)
    print("Stage 55.1 · graph-memory-bridge · V1.0 演示")
    print("=" * 70)

    store = GraphStore()

    # 1. 模拟 session 对话
    messages = [
        {"role": "user", "content": "我需要调研 AI 编程工具市场", "timestamp": 1000.0},
        {"role": "assistant", "content": "推荐使用 Cursor 或 Windsurf，方法是先用 free trial", "timestamp": 1001.0},
        {"role": "user", "content": "Cursor 失败了，崩溃报错", "timestamp": 1002.0},
        {"role": "assistant", "content": "修复：清理 ~/.cursor 缓存后重装", "timestamp": 1003.0},
        {"role": "user", "content": "决定采用 Cursor，因为社区活跃", "timestamp": 1004.0},
        {"role": "assistant", "content": "改动了 settings.json 启用 Sonnet 模型", "timestamp": 1005.0},
    ]

    # 2. 抽取
    nodes = extract_triples(messages, session_id="demo-001")
    for n in nodes:
        store.add_node(n)
    print(f"\n[1] extract_triples: {len(nodes)} nodes")
    print(f"  types: {[(n.type.value, n.content[:30]) for n in nodes[:3]]}")

    # 3. 自动建边
    edges = auto_link(nodes)
    for e in edges:
        store.add_edge(e)
    print(f"\n[2] auto_link: {len(edges)} edges")

    # 4. PPR
    ppr = personalized_pagerank(store, seed_ids=[nodes[0].id])
    top3 = sorted(ppr.items(), key=lambda x: -x[1])[:3]
    print(f"\n[3] personalized_pagerank: top 3 = {[(nid[:15], round(s, 3)) for nid, s in top3]}")

    # 5. 双路径召回
    recall_result = recall(store, "AI 编程工具", top_k=3, recall_token_budget=4096)
    print(f"\n[4] recall('AI 编程工具'): {len(recall_result['results'])} results, {recall_result['total_tokens']} tokens")

    # 6. 4 gm_* 工具
    print("\n[5] gm_status:", gm_status(store)["graph_counts"])
    r2 = gm_record(store, "TASK", "测试持久化任务")
    print(f"[6] gm_record: {r2['node_id']}, deduplicated={r2['deduplicated']}")
    print(f"[7] gm_stats: {gm_stats(store)}")

    # 7. rolling checkpoint
    cp = rolling_checkpoint(messages, fresh_turn_count=2)
    print(f"\n[8] rolling_checkpoint: fresh={cp['fresh_count']}, checkpoint={cp['checkpoint_count']}, ratio={cp['compression_ratio']}")

    # 8. budget truncate
    long_text = "x" * 50000
    truncated = truncate_to_budget(long_text, 4096)
    print(f"[9] truncate_to_budget: 50000 → {len(truncated)} 字符")

    print("\n" + "=" * 70)
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
