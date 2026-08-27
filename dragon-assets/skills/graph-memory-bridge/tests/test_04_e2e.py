"""test_04_e2e · 端到端：session → extract → store → recall → PPR → budget"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from extractor import (
    GraphStore, extract_triples, auto_link, recall, personalized_pagerank,
    gm_status, gm_search, gm_record, gm_stats, rolling_checkpoint, truncate_to_budget,
)


def test_04_e2e():
    """完整链路：3 轮对话 → extract → store → recall → PPR + gm_* + rolling"""
    store = GraphStore()

    # 1. 模拟天龙真实场景
    messages = [
        {"role": "user", "content": "我需要调研 DSH 生态的 SKILL 集成模式", "timestamp": 1000.0},
        {"role": "assistant", "content": "推荐方法：先看 stage 41 mneme-heat-engine 的借鉴档实现", "timestamp": 1001.0},
        {"role": "user", "content": "采纳借鉴档模式，patch 了 check.py", "timestamp": 1002.0},
        {"role": "assistant", "content": "改动了 stage 53.1 dsh-chat-import 借鉴档", "timestamp": 1003.0},
    ]

    # 2. extract
    nodes = extract_triples(messages, session_id="e2e-test")
    assert len(nodes) >= 4, f"[FAIL] 应抽取 ≥4 个节点: {len(nodes)}"
    for n in nodes:
        store.add_node(n)
    print(f"[STEP 1] extract: {len(nodes)} nodes ({len({n.type for n in nodes})} 类)")

    # 3. auto_link
    edges = auto_link(nodes)
    for e in edges:
        store.add_edge(e)
    print(f"[STEP 2] auto_link: {len(edges)} edges ({len({e.type for e in edges})} 类)")

    # 4. PPR
    ppr = personalized_pagerank(store, [nodes[0].id])
    top_node = max(ppr.items(), key=lambda x: x[1])
    print(f"[STEP 3] PPR: top={top_node[0][:20]}... score={top_node[1]:.4f}")

    # 5. recall
    result = recall(store, "DSH 借鉴档", top_k=3, recall_token_budget=2048)
    assert result["total_tokens"] <= 2048
    print(f"[STEP 4] recall: {len(result['results'])} results, {result['total_tokens']} tokens")

    # 6. 4 gm_* 工具
    assert gm_status(store)["ok"]
    assert gm_search(store, "整合")["ok"]
    gm_record(store, "TASK", "e2e 测试任务", session_id="e2e-test")
    stats = gm_stats(store)
    print(f"[STEP 5] 4 gm_* tools: {stats['total_nodes']} nodes total")

    # 7. rolling checkpoint
    cp = rolling_checkpoint(messages, fresh_turn_count=2)
    assert cp["fresh_count"] == 2
    print(f"[STEP 6] rolling_checkpoint: fresh={cp['fresh_count']}, checkpoint={cp['checkpoint_count']}, ratio={cp['compression_ratio']}")

    # 8. budget truncate
    assert len(truncate_to_budget("x" * 100000, 4096)) <= 4096 * 4 + 10
    print(f"[STEP 7] truncate_to_budget: ≤ 16384 字符")

    # 端到端聚合
    print(f"\n{'=' * 60}")
    print(f"graph-memory-bridge 端到端 PASS:")
    print(f"  extract: {len(nodes)} nodes from {len(messages)} messages")
    print(f"  auto_link: {len(edges)} edges")
    print(f"  PPR top score: {top_node[1]:.4f}")
    print(f"  recall: {result['total_tokens']} tokens (budget 2048)")
    print(f"  gm_* tools: 4 OK")
    print(f"  rolling checkpoint: {cp['compression_ratio']} compression")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    test_04_e2e()
