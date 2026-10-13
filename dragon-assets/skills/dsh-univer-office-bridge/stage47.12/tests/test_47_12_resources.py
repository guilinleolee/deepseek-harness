"""test_47_12_resources · 6 个 univer_resources 场景"""
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from resources import (
    ResourceLibrary,
    ResourceHandle,
    ResourceRegistry,
    test_multi_registry,
    test_find_by_semantic_queries,
    test_export_to_workspace,
    test_color_editable_constraint,
    test_clear_cache,
    test_handle_export_reuse,
)


def test_47_12_resources():
    # 场景 1: 多 registry
    r1 = test_multi_registry()
    assert r1["ok"]
    assert r1["registry_count"] == 4
    print(f"[PASS] multi_registry: 4 registries (icon/illustration/emoji/logo)")

    # 场景 2: find
    r2 = test_find_by_semantic_queries()
    assert r2["ok"]
    assert r2["rocket_count"] == 2  # icon + emoji
    assert r2["chart_editable_only"] == 1
    assert r2["emoji_only"] == 1
    print(f"[PASS] find: rocket={r2['rocket_count']}, chart_editable_only={r2['chart_editable_only']}")

    # 场景 3: export
    r3 = test_export_to_workspace()
    assert r3["ok"]
    assert r3["svg_valid"]
    print(f"[PASS] export: {r3['exported_bytes']} B valid SVG")

    # 场景 4: color_editable
    r4 = test_color_editable_constraint()
    assert r4["ok"]
    assert r4["fixed_color_editable"] is False
    assert r4["color_color_editable"] is True
    print(f"[PASS] color_editable: fixed={r4['fixed_color_editable']}, color={r4['color_color_editable']}")

    # 场景 5: clear_cache
    r5 = test_clear_cache()
    assert r5["ok"]
    assert r5["initial_cleared"] == 1
    assert r5["re_register_count"] == 1
    print(f"[PASS] clear_cache: cleared={r5['initial_cleared']}, re-register={r5['re_register_count']}")

    # 场景 6: handle 复用
    r6 = test_handle_export_reuse()
    assert r6["ok"]
    assert r6["log_count"] == 2
    assert r6["content_match"]
    print(f"[PASS] handle_export_reuse: {r6['log_count']} exports with identical content")


# 独立 test
test_multi_registry.__test__ = True
test_find_by_semantic_queries.__test__ = True
test_export_to_workspace.__test__ = True
test_color_editable_constraint.__test__ = True
test_clear_cache.__test__ = True
test_handle_export_reuse.__test__ = True
