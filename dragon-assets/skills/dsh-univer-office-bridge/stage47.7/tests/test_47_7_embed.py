"""test_47_7_embed · univer_embed 4 个场景全部 PASS"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from embed_demo import (
    test_sibling_embeds,
    test_multi_level_forbidden,
    test_resource_ref_format,
    test_univer_workflow_with_embed,
)


def test_47_7_embed():
    """聚合验证 4 个场景"""
    # 场景 1: sibling embed 允许
    r1 = test_sibling_embeds()
    assert r1["ok"], f"[FAIL] sibling embeds: {r1}"
    assert r1["count"] == 3
    print(f"[PASS] sibling embeds: 3 sibling embeds allowed")

    # 场景 2: 多层 embed 禁止
    r2 = test_multi_level_forbidden()
    assert r2["ok"], f"[FAIL] multi-level forbidden: {r2}"
    assert r2["step1_embed_a"] and r2["step2_embed_b"]
    assert r2["step3_child_already_embedded"], \
        f"[FAIL] CHILD_ALREADY_EMBEDDED 拦截缺失（error={r2['step3_error']}）"
    assert r2["step4_multi_level_rejected"], \
        f"[FAIL] MULTI_LEVEL_EMBED_FORBIDDEN 拦截缺失（error={r2['step4_error']}）"
    print(f"[PASS] multi-level forbidden: 双拦截均生效")

    # 场景 3: ResourceRef
    r3 = test_resource_ref_format()
    assert r3["ok"] and r3["resource_ref"].startswith("#unit=")
    print(f"[PASS] resource ref: {r3['resource_ref']}")

    # 场景 4: 端到端
    r4 = test_univer_workflow_with_embed()
    assert r4["ok"] and r4["export_size"] > 0
    print(f"[PASS] workflow with embed: {r4['export_size']} B export")


# 4 个独立 test function（让 pytest 单测可分开 PASS/FAIL）
test_sibling_embeds.__test__ = True
test_multi_level_forbidden.__test__ = True
test_resource_ref_format.__test__ = True
test_univer_workflow_with_embed.__test__ = True


if __name__ == "__main__":
    test_47_7_embed()
