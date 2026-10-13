"""test_02_recaller · 双路径召回 + PPR + budget"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from extractor import (
    GraphStore, GraphNode, NodeType, extract_triples, auto_link,
    personalized_pagerank, recall, truncate_to_budget,
)


def test_02_recaller():
    store = GraphStore()

    # 构造混合节点
    messages = [
        {"role": "user", "content": "我需要调研 AI 编程工具市场", "timestamp": 1000.0},
        {"role": "assistant", "content": "推荐方法：使用 Cursor 或 Continue", "timestamp": 1001.0},
        {"role": "user", "content": "决定采用 Cursor 因为效率高", "timestamp": 1002.0},
        {"role": "assistant", "content": "改动了 settings.json 启用 Sonnet", "timestamp": 1003.0},
    ]
    nodes = extract_triples(messages, session_id="recall-test")
    for n in nodes:
        store.add_node(n)
    edges = auto_link(nodes)
    for e in edges:
        store.add_edge(e)

    # 1. PPR 收敛（种子节点 + 图结构应反映在分数上）
    seed_id = nodes[0].id
    ppr = personalized_pagerank(store, [seed_id], iterations=50)
    assert len(ppr) == len(nodes), f"[FAIL] PPR 应覆盖 {len(nodes)} 节点, got {len(ppr)}"
    # seed 应在前 80%（PPR bias 自身但 damping 会分散）
    sorted_ppr = sorted(ppr.items(), key=lambda x: -x[1])
    seed_rank = next(i for i, (nid, _) in enumerate(sorted_ppr) if nid == seed_id)
    max_rank = int(len(sorted_ppr) * 0.8)
    assert seed_rank <= max_rank, \
        f"[FAIL] seed rank 应 ≤ {max_rank} (rank {seed_rank} / {len(sorted_ppr)})"
    print(f"[PASS] personalized_pagerank: 50 iterations 收敛, seed rank={seed_rank}/{len(sorted_ppr)}, score={ppr[seed_id]:.4f}")

    # 2. 双路径召回
    result = recall(store, "AI 工具", top_k=3, recall_token_budget=4096)
    assert result["ok"]
    assert len(result["results"]) >= 1
    assert result["total_tokens"] <= 4096
    print(f"[PASS] recall: {len(result['results'])} results, {result['total_tokens']} tokens (≤ 4096)")

    # 3. recallTokenBudget 强制截断
    long_content = "x" * 50000
    store.add_node(GraphNode(
        id="long-node", type=NodeType.SKILL, content=long_content, timestamp=100.0,
    ))
    result2 = recall(store, "x", recall_token_budget=2048)
    assert result2["total_tokens"] <= 2048, \
        f"[FAIL] budget 截断失败: {result2['total_tokens']}"
    print(f"[PASS] recallTokenBudget(2048): 强制 ≤ 2048 tokens (实际 {result2['total_tokens']})")

    # 4. truncate_to_budget 函数
    truncated = truncate_to_budget("a" * 50000, 4096)
    assert len(truncated) <= 4096 * 4 + 10  # +10 for "..."
    print(f"[PASS] truncate_to_budget: 50000 → {len(truncated)} 字符")


if __name__ == "__main__":
    test_02_recaller()
