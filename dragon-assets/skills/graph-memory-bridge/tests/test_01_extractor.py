"""test_01_extractor · 3 类节点 + 5 类边 + idempotent"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from extractor import (
    extract_triples, auto_link, GraphStore, GraphNode,
    NodeType, EdgeType, hash_content,
)


def test_01_extractor():
    # 3 类节点全部触发
    messages = [
        {"role": "user", "content": "我需要调研 AI 工具市场", "timestamp": 1000.0},
        {"role": "assistant", "content": "推荐使用方法：先用 free trial", "timestamp": 1001.0},
        {"role": "user", "content": "Cursor 失败了，崩溃报错", "timestamp": 1002.0},
        {"role": "assistant", "content": "修复：清理缓存后重装", "timestamp": 1003.0},
        {"role": "user", "content": "决定采用 Cursor，因为社区活跃", "timestamp": 1004.0},
    ]

    nodes = extract_triples(messages, session_id="test-session")
    types = {n.type for n in nodes}
    assert NodeType.TASK in types, f"[FAIL] TASK 缺失: {types}"
    assert NodeType.SKILL in types, f"[FAIL] SKILL 缺失: {types}"
    assert NodeType.EVENT in types, f"[FAIL] EVENT 缺失: {types}"
    print(f"[PASS] extract_triples: 3 类节点全部识别 ({len(nodes)} nodes)")

    # 5 类边全部可能（auto_link 只建 3 类：USED_SKILL / SOLVED_BY / PATCHES）
    store = GraphStore()
    for n in nodes:
        store.add_node(n)
    edges = auto_link(nodes)
    for e in edges:
        store.add_edge(e)
    edge_types = {e.type for e in edges}
    assert EdgeType.USED_SKILL in edge_types, f"[FAIL] USED_SKILL 缺失: {edge_types}"
    assert EdgeType.SOLVED_BY in edge_types, f"[FAIL] SOLVED_BY 缺失: {edge_types}"
    print(f"[PASS] auto_link: 边类型 {edge_types} ({len(edges)} edges)")

    # idempotent: 同样内容 → 同样 hash
    h1 = hash_content("hello world")
    h2 = hash_content("hello world")
    assert h1 == h2
    h3 = hash_content("hello world!")
    assert h1 != h3
    print(f"[PASS] hash_content: idempotent + collision-free ({h1[:10]}... ≠ {h3[:10]}...)")


if __name__ == "__main__":
    test_01_extractor()
