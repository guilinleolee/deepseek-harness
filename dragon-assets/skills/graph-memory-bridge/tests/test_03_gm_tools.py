"""test_03_gm_tools · 4 个 gm_* 工具"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from extractor import (
    GraphStore, gm_status, gm_search, gm_record, gm_stats,
    extract_triples, auto_link,
)


def test_03_gm_tools():
    store = GraphStore()

    # 准备数据
    messages = [
        {"role": "user", "content": "我需要做 KOL 选题", "timestamp": 1000.0},
        {"role": "assistant", "content": "推荐方法：先用 agent-reach 调研", "timestamp": 1001.0},
    ]
    nodes = extract_triples(messages, session_id="gm-test")
    for n in nodes:
        store.add_node(n)
    for e in auto_link(nodes):
        store.add_edge(e)

    # 1. gm_status
    s = gm_status(store)
    assert s["ok"] and s["tool"] == "gm_status"
    assert s["graph_counts"]["nodes"] == len(nodes)
    print(f"[PASS] gm_status: nodes={s['graph_counts']['nodes']}, edges={s['graph_counts']['edges']}, types={s['graph_counts']['by_type']}")

    # 2. gm_search
    sr = gm_search(store, "KOL 选题", top_k=3)
    assert sr["ok"] and sr["tool"] == "gm_search"
    assert sr["query"] == "KOL 选题"
    assert len(sr["results"]) >= 1
    print(f"[PASS] gm_search('KOL 选题'): {len(sr['results'])} results")

    # 3. gm_record（新建）
    r1 = gm_record(store, "TASK", "新建一个测试任务", session_id="record-test")
    assert r1["ok"]
    assert not r1["deduplicated"]
    assert r1["type"] == "TASK"
    print(f"[PASS] gm_record 新建: {r1['node_id']}, deduplicated={r1['deduplicated']}")

    # 4. gm_record 重复（应 deduplicated）
    r2 = gm_record(store, "TASK", "新建一个测试任务")
    assert r2["ok"]
    assert r2["deduplicated"] is True
    print(f"[PASS] gm_record 重复: deduplicated=True (idempotent)")

    # 5. gm_record 错误 type
    r3 = gm_record(store, "INVALID_TYPE", "test")
    assert not r3["ok"]
    assert r3["error"] == "INVALID_TYPE"
    print(f"[PASS] gm_record 错误类型: rejected")

    # 6. gm_stats
    st = gm_stats(store)
    assert st["ok"] and st["tool"] == "gm_stats"
    assert st["total_nodes"] == len(store.nodes)
    print(f"[PASS] gm_stats: {st['total_nodes']} nodes, {st['total_edges']} edges, communities={st['communities']}")


if __name__ == "__main__":
    test_03_gm_tools()
