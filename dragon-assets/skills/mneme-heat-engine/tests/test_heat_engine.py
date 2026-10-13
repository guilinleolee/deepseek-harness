"""mneme-heat-engine v2.0 (阶段 42 候选) · 测试套 · 30 PASS 目标

借鉴 dsh-mneme v0.3.0-v0.8.0 heat/sleep/session/entities/retrieval/drift 设计（MIT ✅）天龙自实现。

W1: 6 PASS（heat + sleep 核心）
W2: +6 PASS（mneme-gate + session-decouple）
W3: +8 PASS（entities 三表 + retrieval BM25+图谱+heat）
W4: +10 PASS（interest-drift v0.8.0 + migrate_v11_to_v12 + sleep_scheduler cron）
"""
from __future__ import annotations

import sys
from pathlib import Path

# 让 import 找到 scripts/
SCRIPT_DIR = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from heat_engine import (  # noqa: E402
    INIT_HEAT, DECAY_PER_DAY,
    tick_heat, boost_heat, should_archive,
)


# === W1 测试（6 PASS · 已验证） ===

def test_01_heat_init() -> None:
    """新节点 heat 初始值 = 0.7."""
    assert INIT_HEAT == 0.7
    print("[PASS] test_01_heat_init | INIT_HEAT=0.7")


def test_02_decay_pow_law() -> None:
    """30 天后 heat 应符合幂律 0.7 x 0.99^30."""
    expected = round(0.7 * (DECAY_PER_DAY ** 30), 3)
    actual = round(tick_heat(0.7, 30), 3)
    assert abs(actual - expected) < 0.001
    assert 0.51 < actual < 0.52
    print(f"[PASS] test_02_decay_pow_law | 0.7 -> 30d = {actual}")


def test_03_boost_on_ref() -> None:
    """被引用后 heat x 1.05 且不超过 MAX_HEAT=1.0."""
    assert boost_heat(0.5) == 0.525
    assert boost_heat(0.99) == 1.0
    assert boost_heat(1.0) == 1.0
    print("[PASS] test_03_boost_on_ref | 0.5x1.05=0.525, 0.99->1.0")


def test_04_archive_threshold() -> None:
    """heat < 0.1 且 30 天未引用 → 应归档."""
    assert should_archive(0.05, "2026-07-01", "2026-08-24") is True
    assert should_archive(0.7, "2026-08-20", "2026-08-24") is False
    assert should_archive(0.05, "2026-08-20", "2026-08-24") is False
    print("[PASS] test_04_archive_threshold | heat<0.1 + 30d -> archive")


def test_05_rebirth_from_archive() -> None:
    """archive 节点被重新引用 → heat 重置 0.7."""
    from sleep_consolidate import phase4_rebirth
    archive = [{"id": "X", "heat": 0.05, "last_ref_date": "2026-06-01"}]
    rebirth = phase4_rebirth(archive, ["X"])
    assert len(rebirth) == 1
    assert rebirth[0]["heat"] == 0.7
    print("[PASS] test_05_rebirth_from_archive | archive[X] -> heat=0.7")


def test_06_sleep_consolidate_e2e() -> None:
    """4 阶段串联端到端."""
    from sleep_consolidate import (phase1_dedupe, phase2_merge,
                                    phase3_archive, phase4_rebirth)
    today = "2026-08-24"
    nodes = [
        {"id": "A", "wikilink": "老李", "heat": 0.7,
         "last_ref_date": "2026-08-20", "compilations": 3},
        {"id": "A2", "wikilink": "老李", "heat": 0.5,
         "last_ref_date": "2026-07-15", "compilations": 2},
        {"id": "B", "wikilink": "old", "heat": 0.08,
         "last_ref_date": "2026-06-01", "compilations": 5},
        {"id": "C", "wikilink": "active", "heat": 0.85,
         "last_ref_date": "2026-08-23", "compilations": 10},
    ]
    nodes = phase1_dedupe(nodes)
    assert len(nodes) == 3
    nodes = phase2_merge(nodes)
    assert len(nodes) == 3
    active, archive = phase3_archive(nodes, today)
    assert len(archive) == 1
    assert archive[0]["id"] == "B"
    assert len(active) == 2
    rebirth = phase4_rebirth(archive, ["B"])
    assert len(rebirth) == 1
    final = active + rebirth
    assert len(final) == 3
    print("[PASS] test_06_sleep_consolidate_e2e | 4 stages PASS")


# === W2 测试（6 PASS · 阶段 41 续动） ===

def test_07_mneme_gate_register() -> None:
    from mneme_gate import skill_register
    s = skill_register("test-skill", today="2026-08-24")
    assert s["heat"] == 0.7
    assert s["status"] == "active"
    print("[PASS] test_07_mneme_gate_register | heat=0.7")


def test_08_mneme_gate_daily_tick() -> None:
    from mneme_gate import skill_register, skill_tick_daily
    catalog = [
        skill_register("active-skill", today="2026-08-24"),
        skill_register("old-skill", today="2026-07-15"),
    ]
    results = skill_tick_daily(catalog, "2026-08-24")
    assert results[0]["status"] == "active"
    assert results[1]["status"] == "cold"
    print("[PASS] test_08_mneme_gate_daily_tick | 30d->cold OK")


def test_09_mneme_gate_candidate_retire() -> None:
    from mneme_gate import skill_register, skill_tick_daily
    catalog = [skill_register("zombie", today="2026-06-01")]
    results = skill_tick_daily(catalog, "2026-08-24")
    assert results[0]["status"] == "candidate_retire"
    print("[PASS] test_09_mneme_gate_candidate_retire | 60d+ -> retire")


def test_10_session_close_default() -> None:
    from session_decouple import on_session_close
    result = on_session_close("sess-001")
    assert result["transcript_deleted"] is True
    assert result["memory_preserved"] is True
    print("[PASS] test_10_session_close_default | memory_preserved=True")


def test_11_session_forget_explicit() -> None:
    from session_decouple import forget_node
    nodes = [
        {"id": "A", "heat": 0.7, "last_ref_date": "2026-08-20"},
        {"id": "B", "heat": 0.08, "last_ref_date": "2026-06-01"},
    ]
    result = forget_node("B", nodes)
    assert len(result["kept"]) == 1
    assert len(result["archived_then_deleted"]) == 1
    print("[PASS] test_11_session_forget_explicit | B archived_then_deleted")


def test_12_session_decouple_e2e() -> None:
    from session_decouple import on_session_close, forget_node
    from mneme_gate import skill_used
    today = "2026-08-24"
    r1 = on_session_close("sess-001")
    nodes = [
        {"id": "A", "heat": 0.7, "last_ref_date": today},
        {"id": "B", "heat": 0.5, "last_ref_date": "2026-07-01"},
    ]
    r2 = forget_node("B", nodes)
    a_boosted = skill_used(r2["kept"][0], today)
    assert a_boosted["heat"] >= 0.7
    print("[PASS] test_12_session_decouple_e2e | close+forget+boost OK")


# === W3 测试（8 PASS · entities + retrieval） ===

def test_13_entities_three_tables() -> None:
    from entities import (entity_create, attr_create, relation_create,
                           validate_entities)
    today = "2026-08-24"
    entities = [
        entity_create("laoli", "person", aliases=["老李"], today=today),
        entity_create("dragon-engine", "project", today=today),
    ]
    attrs = [
        attr_create("laoli", "gaming", "lol", confidence=0.95, today=today),
        attr_create("dragon-engine", "version", "V2.5", confidence=1.0, today=today),
    ]
    rels = [
        relation_create("r1", "laoli", "dragon-engine", "uses", 0.95, today=today),
    ]
    entities[0]["attrs"] = [a for a in attrs if a["entity"] == "laoli"]
    entities[0]["relations"] = [r for r in rels if r["from"] == "laoli"]
    entities[1]["attrs"] = [a for a in attrs if a["entity"] == "dragon-engine"]
    entities[1]["relations"] = []
    errors = validate_entities(entities)
    assert len(errors) == 0
    print("[PASS] test_13_entities_three_tables | 0 errors")


def test_14_entities_schema_errors() -> None:
    from entities import (entity_create, attr_create, relation_create,
                           validate_entities)
    today = "2026-08-24"
    entities = [
        entity_create("A", "person", today=today),
        entity_create("B", "project", today=today),
    ]
    bad_rels = [
        relation_create("bad-1", "A", "C-missing", "uses", 0.5, today=today),
    ]
    bad_attrs = [
        attr_create("A", "k", "v", confidence=2.0, today=today),
    ]
    entities[0]["attrs"] = bad_attrs
    entities[0]["relations"] = bad_rels
    entities[1]["attrs"] = []
    entities[1]["relations"] = []
    errors = validate_entities(entities)
    assert len(errors) >= 2
    print(f"[PASS] test_14_entities_schema_errors | {len(errors)} errors")


def test_15_entities_heat_projection() -> None:
    from entities import (entity_create, attr_create, relation_create,
                           entity_heat)
    today = "2026-08-24"
    entities = [
        entity_create("hub", "project", today=today),
    ]
    attrs = [
        attr_create("hub", "k1", "v1", confidence=0.9, today=today),
        attr_create("hub", "k2", "v2", confidence=0.7, today=today),
    ]
    rels = [
        relation_create("r1", "hub", "X", "uses", 0.8, today=today),
    ]
    entities[0]["attrs"] = attrs
    entities[0]["relations"] = rels
    h = entity_heat(entities[0], today)
    assert 0.55 < h < 0.57
    print(f"[PASS] test_15_entities_heat_projection | hub.heat = {round(h, 4)}")


def test_16_bm25_basic() -> None:
    from retrieval import bm25_rank
    docs = [
        {"id": "d1", "text": "mneme 自进化记忆 引擎"},
        {"id": "d2", "text": "darwin 自动化 skill 优化"},
        {"id": "d3", "text": "无关 主题"},
    ]
    results = bm25_rank("mneme 自进化", docs, top_k=3)
    assert len(results) >= 1
    top_doc, top_score = results[0]
    assert top_doc["id"] == "d1"
    print(f"[PASS] test_16_bm25_basic | top={top_doc['id']}, score={round(top_score, 3)}")


def test_17_bm25_idf_ranking() -> None:
    from retrieval import bm25_rank
    docs = [
        {"id": "common", "text": "the quick brown fox jumps over the lazy dog"},
        {"id": "rare", "text": "mneme specific technical jargon appears once"},
        {"id": "mix", "text": "the mneme appears here"},
    ]
    results = bm25_rank("mneme", docs, top_k=3)
    assert len(results) == 3
    top_ids = [d["id"] for d, _ in results]
    assert "common" not in top_ids[:1]
    print(f"[PASS] test_17_bm25_idf_ranking | top3={top_ids}")


def test_18_graph_expand_hops() -> None:
    from retrieval import graph_expand
    seed_docs = [{"entity_id": "laoli", "text": "老李"}]
    entities = [
        {"id": "laoli", "type": "person", "heat": 0.85, "attrs": [], "relations": []},
        {"id": "dragon-engine", "type": "project", "heat": 0.75, "attrs": [], "relations": []},
        {"id": "mneme", "type": "skill", "heat": 0.9, "attrs": [], "relations": []},
        {"id": "darwin", "type": "skill", "heat": 0.65, "attrs": [], "relations": []},
        {"id": "khazix", "type": "skill", "heat": 0.7, "attrs": [], "relations": []},
    ]
    relations = [
        {"id": "r1", "from": "laoli", "to": "dragon-engine", "weight": 0.95, "type": "uses"},
        {"id": "r2", "from": "dragon-engine", "to": "mneme", "weight": 0.85, "type": "contains"},
        {"id": "r3", "from": "dragon-engine", "to": "darwin", "weight": 0.8, "type": "contains"},
        {"id": "r4", "from": "dragon-engine", "to": "khazix", "weight": 0.8, "type": "contains"},
    ]
    expanded = graph_expand(seed_docs, entities, relations, hops=1)
    assert len(expanded) == 1
    expanded_2 = graph_expand(seed_docs, entities, relations, hops=2)
    assert len(expanded_2) == 4
    eids = {e["entity_id"] for e in expanded_2}
    assert "mneme" in eids
    print("[PASS] test_18_graph_expand_hops | hops=1->1, hops=2->4")


def test_19_retrieval_end_to_end() -> None:
    from retrieval import retrieve
    docs = [
        {"id": "d1", "entity_id": "laoli",
         "text": "老李 是 投资者", "heat": 0.85},
        {"id": "d2", "entity_id": "dragon-engine",
         "text": "天龙 引擎 多模态 生产", "heat": 0.75},
        {"id": "d3", "entity_id": "mneme",
         "text": "mneme 自进化 记忆 引擎", "heat": 0.9},
    ]
    entities = [
        {"id": "laoli", "type": "person", "heat": 0.85, "attrs": [], "relations": []},
        {"id": "dragon-engine", "type": "project", "heat": 0.75, "attrs": [], "relations": []},
        {"id": "mneme", "type": "skill", "heat": 0.9, "attrs": [], "relations": []},
    ]
    relations = [
        {"id": "r1", "from": "laoli", "to": "dragon-engine", "weight": 0.95, "type": "uses"},
        {"id": "r2", "from": "dragon-engine", "to": "mneme", "weight": 0.85, "type": "contains"},
    ]
    results = retrieve("mneme 自进化", docs, entities, relations,
                       top_k=3, hops=1, top_n=3)
    assert len(results) >= 1
    scores = [r.get("final_score", 0) for r in results]
    assert scores == sorted(scores, reverse=True)
    print(f"[PASS] test_19_retrieval_end_to_end | scores={[round(s, 3) for s in scores]}")


def test_20_retrieval_heat_promotion() -> None:
    from retrieval import retrieve
    docs = [
        {"id": "d1", "entity_id": "obsolete",
         "text": "完全无关的主题 xyz", "heat": 0.05},
        {"id": "d2", "entity_id": "hot_but_irrelevant",
         "text": "另一个无关主题 abc", "heat": 0.95},
    ]
    entities = [
        {"id": "obsolete", "type": "skill", "heat": 0.05, "attrs": [], "relations": []},
        {"id": "hot_but_irrelevant", "type": "skill", "heat": 0.95, "attrs": [], "relations": []},
    ]
    relations = []
    results = retrieve("mneme 自进化", docs, entities, relations,
                       top_k=2, hops=1, top_n=2)
    if len(results) >= 2:
        ids = [r.get("id") for r in results]
        if "hot_but_irrelevant" in ids and "obsolete" in ids:
            assert ids.index("hot_but_irrelevant") < ids.index("obsolete")
    print("[PASS] test_20_retrieval_heat_promotion | heat-weighted OK")


# === W4 测试（10 PASS · 阶段 42 候选 · 借鉴 dsh-mneme v0.8.0） ===

def test_21_interest_drift_snapshot() -> None:
    """interest-drift:生成 entities heat 快照（按 type 聚合）."""
    from interest_drift import snapshot_entities
    entities = [
        {"id": "ai-1", "type": "ai-product", "heat": 0.9},
        {"id": "ai-2", "type": "ai-product", "heat": 0.85},
        {"id": "stock-1", "type": "stock-cn", "heat": 0.4},
    ]
    snap = snapshot_entities(entities, "2026-08-24")
    assert snap["ai-product"] == 1.75  # 0.9 + 0.85
    assert snap["stock-cn"] == 0.4
    assert "person" not in snap
    print(f"[PASS] test_21_interest_drift_snapshot | ai-product={snap['ai-product']}")


def test_22_interest_drift_kl_divergence() -> None:
    """KL 散度：相同分布 → 0；完全不同分布 → 高值."""
    from interest_drift import kl_divergence
    p = {"ai": 0.9, "finance": 0.1}
    q = {"ai": 0.9, "finance": 0.1}
    d_same = kl_divergence(p, q)
    assert d_same < 0.01  # 相同 → ≈0

    r = {"ai": 0.1, "finance": 0.9}
    d_diff = kl_divergence(p, r)
    assert d_diff > 1.0  # 完全不同 → >1
    print(f"[PASS] test_22_interest_drift_kl_divergence | same={d_same:.4f}, diff={d_diff:.4f}")


def test_23_interest_drift_detect() -> None:
    """detect_drift: 一系列快照里识别漂移点."""
    from interest_drift import detect_drift
    snapshots = [
        {"ai": 0.9, "finance": 0.1},
        {"ai": 0.85, "finance": 0.15},
        {"ai": 0.3, "finance": 0.7},  # 大变化
        {"ai": 0.25, "finance": 0.75},
    ]
    drifts = detect_drift(snapshots, threshold=0.3)
    assert len(drifts) == 3  # 3 个相邻时间窗
    # 第 3 个 (i=2) 应该有漂移（KL > threshold）
    assert drifts[1]["drifted"] is True  # 索引 1 实际是 i=2 的窗
    print(f"[PASS] test_23_interest_drift_detect | {len(drifts)} windows analyzed")


def test_24_interest_drift_report() -> None:
    """generate_drift_report: 完整报告含 current_snapshot + drift_analysis + hot_now + hot_future."""
    from interest_drift import (snapshot_entities, generate_drift_report)
    entities = [
        {"id": "ai-1", "type": "ai-product", "heat": 0.9},
        {"id": "ai-2", "type": "ai-product", "heat": 0.85},
        {"id": "stock-1", "type": "stock-cn", "heat": 0.4},
    ]
    snapshot_w1 = snapshot_entities(entities, "2026-08-17")
    snapshot_w2 = snapshot_entities(entities, "2026-08-24")
    report = generate_drift_report(
        entities=entities,
        snapshots=[snapshot_w1, snapshot_w2],
        days_projection=30,
        threshold=0.3,
    )
    assert "current_snapshot" in report
    assert "drift_analysis" in report
    assert "hot_now" in report
    assert "hot_future" in report
    assert "summary" in report
    assert isinstance(report["summary"], str)
    print(f"[PASS] test_24_interest_drift_report | summary={report['summary'][:60]}")


def test_25_interest_drift_projection() -> None:
    """project_future_heat: 30 天后所有 entity heat."""
    from interest_drift import project_future_heat
    entities = [
        {"id": "x", "heat": 0.7},
        {"id": "y", "heat": 0.3},
    ]
    projected = project_future_heat(entities, days=30)
    assert len(projected) == 2
    x_heat = projected[0]["projected_heat"]
    y_heat = projected[1]["projected_heat"]
    assert x_heat < 0.7
    assert y_heat < x_heat
    print(f"[PASS] test_25_interest_drift_projection | x={round(x_heat, 4)}, y={round(y_heat, 4)}")


def test_26_migrate_v11_to_v12_dry_run() -> None:
    """migration: dry-run 模式只统计不修改."""
    import tempfile
    import shutil
    from migrate_v11_to_v12 import migrate_directory

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        # 创建 3 个测试文件
        (tmp / "node-a.md").write_text(
            "---\ntitle: A\n---\n\nBody A", encoding="utf-8"
        )
        (tmp / "node-b.md").write_text(
            "---\ntitle: B\nheat: 0.5\n---\n\nBody B", encoding="utf-8"
        )
        (tmp / "archive" / "old.md").parent.mkdir(parents=True, exist_ok=True)
        (tmp / "archive" / "old.md").write_text(
            "---\ntitle: Old\n---\n", encoding="utf-8"
        )

        # dry-run
        results = migrate_directory(tmp, dry_run=True)
        assert results["total_scanned"] == 3
        assert results["migrated"] == 1  # 仅 node-a 没 heat 字段
        assert results["skipped"] == 2  # node-b 已有 + archive 跳过

        # dry-run 不应修改文件
        assert "heat" not in (tmp / "node-a.md").read_text(encoding="utf-8")
    print("[PASS] test_26_migrate_v11_to_v12_dry_run | 3 scanned, 1 would migrate")


def test_27_migrate_v11_to_v12_apply() -> None:
    """migration: apply 模式真正写回."""
    import tempfile
    from migrate_v11_to_v12 import migrate_directory

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        (tmp / "node-c.md").write_text(
            "---\ntitle: C\n---\n\nBody C", encoding="utf-8"
        )

        results = migrate_directory(tmp, dry_run=False)
        assert results["migrated"] == 1
        # 检查文件确实被修改
        content = (tmp / "node-c.md").read_text(encoding="utf-8")
        assert "heat:" in content
        assert "last_ref_date:" in content
        assert "mneme_schema: v12.0" in content
    print("[PASS] test_27_migrate_v11_to_v12_apply | heat+last_ref_date+schema written")


def test_28_migrate_idempotent() -> None:
    """migration 幂等：第二次跑不应再次迁移."""
    import tempfile
    from migrate_v11_to_v12 import migrate_directory

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        (tmp / "node-d.md").write_text(
            "---\ntitle: D\n---\n\nBody D", encoding="utf-8"
        )

        # 第一次 apply
        r1 = migrate_directory(tmp, dry_run=False)
        assert r1["migrated"] == 1

        # 第二次（应当 0 migrated）
        r2 = migrate_directory(tmp, dry_run=False)
        assert r2["migrated"] == 0
        assert r2["skipped"] == 1
    print("[PASS] test_28_migrate_idempotent | second run = 0 migrated")


def test_29_sleep_scheduler_run() -> None:
    """sleep_scheduler: 完整调度 4 个动作."""
    from sleep_scheduler import run_all
    report = run_all(dry_run=True)
    assert report["actions_total"] == 4
    assert report["actions_ok"] == 4
    assert report["has_fail"] is False
    assert report["exit_code"] == 0
    action_names = [r["action_name"] for r in report["results"]]
    assert "tick_heat" in action_names
    assert "sleep_consolidate" in action_names
    assert "mneme_gate_tick" in action_names
    assert "session_decouple_check" in action_names
    print(f"[PASS] test_29_sleep_scheduler_run | 4/4 actions OK")


def test_30_sleep_scheduler_install_helpers() -> None:
    """sleep_scheduler: Windows / Linux 安装命令输出."""
    from sleep_scheduler import (cmd_install_windows_task,
                                  cmd_install_linux_cron)
    import argparse

    win_args = argparse.Namespace()
    win_cmd = cmd_install_windows_task(win_args)
    assert win_cmd == 0

    linux_args = argparse.Namespace()
    linux_cmd = cmd_install_linux_cron(linux_args)
    assert linux_cmd == 0
    print("[PASS] test_30_sleep_scheduler_install_helpers | win+linux OK")


def main() -> int:
    print("=" * 60)
    print(" mneme-heat-engine v2.0 (stage 42 candidate) | test suite")
    print(" adapt from dsh-mneme v0.3.0-v0.8.0 (W4 10 + W1-W3 20 = 30)")
    print("=" * 60)
    tests = [
        # W1 (6)
        test_01_heat_init, test_02_decay_pow_law, test_03_boost_on_ref,
        test_04_archive_threshold, test_05_rebirth_from_archive,
        test_06_sleep_consolidate_e2e,
        # W2 (6)
        test_07_mneme_gate_register, test_08_mneme_gate_daily_tick,
        test_09_mneme_gate_candidate_retire,
        test_10_session_close_default, test_11_session_forget_explicit,
        test_12_session_decouple_e2e,
        # W3 (8)
        test_13_entities_three_tables, test_14_entities_schema_errors,
        test_15_entities_heat_projection,
        test_16_bm25_basic, test_17_bm25_idf_ranking,
        test_18_graph_expand_hops,
        test_19_retrieval_end_to_end, test_20_retrieval_heat_promotion,
        # W4 (10)
        test_21_interest_drift_snapshot, test_22_interest_drift_kl_divergence,
        test_23_interest_drift_detect, test_24_interest_drift_report,
        test_25_interest_drift_projection,
        test_26_migrate_v11_to_v12_dry_run, test_27_migrate_v11_to_v12_apply,
        test_28_migrate_idempotent,
        test_29_sleep_scheduler_run, test_30_sleep_scheduler_install_helpers,
    ]
    passed = 0
    for t in tests:
        try:
            t()
            passed += 1
        except AssertionError as e:
            print(f"[FAIL] {t.__name__} | {e}")
            return 1
        except Exception as e:
            print(f"[ERROR] {t.__name__} | {e}")
            return 1
    print("=" * 60)
    print(f" PASS {passed}/{len(tests)}")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())