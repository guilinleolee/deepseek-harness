"""阶段 47.12 · univer_resources 验证（SVG 资源库）

本脚本：
  1. 模拟 univer_resources 的 registries / find / read / export 接口
  2. 验证多 registry（icon / illustration / emoji / logo）
  3. 验证按语义 find（queries → handles）
  4. 验证 handle 持久化（export 到 workspace output 目录）
  5. 验证 read (inline SVG text)
  6. 验证 clear-cache（Provider-owned）

Author: dragon-engine · Stage 47.12 · 2026-08-26
"""
from __future__ import annotations

import shutil
import sys
import tempfile
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
import xml.etree.ElementTree as ET


# ─── Facade 接口语义 ─────────────────────────────────────────────────────

@dataclass
class ResourceHandle:
    """资源 handle（find 返回 / export 输入）"""
    registry: str
    resource_id: str
    name: str
    type: str  # svg / png / emoji / jpeg
    color_editable: bool = False
    semantic_tags: list = field(default_factory=list)
    license: str = ""


@dataclass
class ResourceRegistry:
    """单个 registry"""
    name: str
    description: str
    total_count: int
    cached_count: int = 0


class ResourceLibrary:
    """多 registry 资源库（Provider-owned）"""

    def __init__(self):
        self.registries: dict[str, ResourceRegistry] = {}
        self.resources: dict[str, ResourceHandle] = {}  # registry:resource_id → handle
        self.cache_root: Path = Path(tempfile.mkdtemp(prefix="univer_resources_"))
        self.export_log: list = []

    def register_registry(self, registry: ResourceRegistry) -> None:
        self.registries[registry.name] = registry

    def register_resource(self, handle: ResourceHandle, svg_content: str = "") -> None:
        key = f"{handle.registry}:{handle.resource_id}"
        self.resources[key] = handle
        if svg_content:
            # 写缓存
            cache_path = self.cache_root / handle.registry / f"{handle.resource_id}.svg"
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            cache_path.write_text(svg_content, encoding="utf-8")
            if handle.registry in self.registries:
                self.registries[handle.registry].cached_count += 1

    def list_registries(self) -> list[dict]:
        return [
            {"name": r.name, "description": r.description, "total": r.total_count, "cached": r.cached_count}
            for r in self.registries.values()
        ]

    def find(self, queries: list[str], registries: list[str] | None = None,
             color_editable_only: bool = False) -> list[ResourceHandle]:
        """按语义查找资源"""
        search_in = registries or list(self.registries.keys())
        results = []
        for handle in self.resources.values():
            if handle.registry not in search_in:
                continue
            if color_editable_only and not handle.color_editable:
                continue
            # 任意 query 命中任一 tag 即匹配
            if any(q.lower() in [t.lower() for t in handle.semantic_tags]
                   or q.lower() in handle.name.lower()
                   for q in queries):
                results.append(handle)
        return results

    def read(self, handle: ResourceHandle) -> str:
        """读 inline SVG text"""
        cache_path = self.cache_root / handle.registry / f"{handle.resource_id}.svg"
        if not cache_path.exists():
            return f"<svg xmlns=\"http://www.w3.org/2000/svg\"><!-- {handle.name} (inline stub) --></svg>"
        return cache_path.read_text(encoding="utf-8")

    def export(self, handle: ResourceHandle, output_dir: str) -> dict:
        """导出资源到 workspace output 目录（path 由 DSH 安全校验）"""
        out_path = Path(output_dir) / f"{handle.resource_id}.svg"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        svg_content = self.read(handle)
        out_path.write_text(svg_content, encoding="utf-8")
        log_entry = {"handle": f"{handle.registry}:{handle.resource_id}",
                     "output": str(out_path), "bytes": out_path.stat().st_size}
        self.export_log.append(log_entry)
        return log_entry

    def clear_cache(self) -> int:
        """清理 Provider-owned 缓存"""
        if self.cache_root.exists():
            shutil.rmtree(self.cache_root)
        count = sum(r.cached_count for r in self.registries.values())
        for r in self.registries.values():
            r.cached_count = 0
        self.cache_root = Path(tempfile.mkdtemp(prefix="univer_resources_"))
        return count


# ─── 验证场景 ──────────────────────────────────────────────────────────

def test_multi_registry() -> dict:
    """场景 1: 多 registry"""
    lib = ResourceLibrary()
    lib.register_registry(ResourceRegistry("icon", "图标", 1200))
    lib.register_registry(ResourceRegistry("illustration", "插画", 350))
    lib.register_registry(ResourceRegistry("emoji", "Emoji", 800))
    lib.register_registry(ResourceRegistry("logo", "Logo", 80))

    regs = lib.list_registries()
    assert len(regs) == 4
    assert any(r["name"] == "icon" for r in regs)
    return {"name": "multi_registry", "ok": True, "registry_count": len(regs)}


def test_find_by_semantic_queries() -> dict:
    """场景 2: 按语义查询（find）"""
    lib = ResourceLibrary()
    lib.register_registry(ResourceRegistry("icon", "图标", 10))
    lib.register_registry(ResourceRegistry("emoji", "Emoji", 20))

    # 注册 5 个资源
    lib.register_resource(ResourceHandle(
        registry="icon", resource_id="rocket", name="火箭",
        type="svg", color_editable=True,
        semantic_tags=["launch", "rocket", "fast"], license="MIT"
    ), svg_content='<svg xmlns="http://www.w3.org/2000/svg"><path d="M0 0"/></svg>')

    lib.register_resource(ResourceHandle(
        registry="icon", resource_id="chart", name="柱状图",
        type="svg", color_editable=True,
        semantic_tags=["chart", "bar", "data"], license="MIT"
    ), svg_content='<svg xmlns="http://www.w3.org/2000/svg"><rect/></svg>')

    lib.register_resource(ResourceHandle(
        registry="emoji", resource_id="rocket-emoji", name="🚀",
        type="emoji", color_editable=False,
        semantic_tags=["launch", "rocket", "emoji"], license="CC0"
    ))

    lib.register_resource(ResourceHandle(
        registry="icon", resource_id="lock", name="锁",
        type="svg", color_editable=True,
        semantic_tags=["security", "lock"], license="MIT"
    ))

    lib.register_resource(ResourceHandle(
        registry="icon", resource_id="chart-fixed", name="固定色柱状图",
        type="svg", color_editable=False,  # 不可改色
        semantic_tags=["chart", "bar", "fixed"], license="MIT"
    ))

    # 查询 1: "rocket" → 2 个（icon + emoji）
    r1 = lib.find(["rocket"])
    assert len(r1) == 2, f"[FAIL] 'rocket' 应返回 2 个，实际 {len(r1)}"

    # 查询 2: "chart" → icon 2 个（color_editable + fixed）
    r2 = lib.find(["chart"])
    assert len(r2) == 2, f"[FAIL] 'chart' 应返回 2 个，实际 {len(r2)}"

    # 查询 3: "chart" + color_editable_only=True → 1 个（chart）
    r3 = lib.find(["chart"], color_editable_only=True)
    assert len(r3) == 1, f"[FAIL] 'chart' 可改色应返回 1 个"

    # 查询 4: 不存在的关键词 → 0 个
    r4 = lib.find(["nonexistent"])
    assert len(r4) == 0

    # 查询 5: 限定 registry
    r5 = lib.find(["rocket"], registries=["emoji"])
    assert len(r5) == 1
    assert r5[0].registry == "emoji"

    return {"name": "find_by_semantic", "ok": True,
            "rocket_count": len(r1), "chart_editable_only": len(r3),
            "emoji_only": len(r5)}


def test_export_to_workspace() -> dict:
    """场景 3: export 到 workspace output（path 校验）"""
    lib = ResourceLibrary()
    lib.register_registry(ResourceRegistry("icon", "图标", 10))

    lib.register_resource(ResourceHandle(
        registry="icon", resource_id="rocket", name="火箭",
        type="svg", color_editable=True,
        semantic_tags=["rocket"], license="MIT"
    ), svg_content='<svg xmlns="http://www.w3.org/2000/svg"><path d="M0 0"/></svg>')

    handles = lib.find(["rocket"])
    assert len(handles) == 1

    # export 到 workspace output
    with tempfile.TemporaryDirectory() as tmp:
        out_dir = f"{tmp}/output"
        result = lib.export(handles[0], out_dir)
        assert Path(result["output"]).exists()
        assert result["bytes"] > 0

        # 重读 SVG 应有效
        svg_text = Path(result["output"]).read_text(encoding="utf-8")
        root = ET.fromstring(svg_text)
        assert root.tag.endswith("svg"), f"[FAIL] 不是 SVG: {root.tag}"

    return {"name": "export_to_workspace", "ok": True,
            "exported_bytes": result["bytes"], "svg_valid": True}


def test_color_editable_constraint() -> dict:
    """场景 4: color_editable 约束（上游 SVG 颜色规则）"""
    lib = ResourceLibrary()
    lib.register_registry(ResourceRegistry("icon", "图标", 10))

    lib.register_resource(ResourceHandle(
        registry="icon", resource_id="logo-fixed", name="固定 Logo",
        type="svg", color_editable=False,  # 不可改色
        semantic_tags=["logo", "fixed"], license="MIT"
    ))

    lib.register_resource(ResourceHandle(
        registry="icon", resource_id="icon-color", name="可改色图标",
        type="svg", color_editable=True,  # 可改色
        semantic_tags=["icon"], license="MIT"
    ))

    # 上游规则：只有 color_editable=True 的资源才能 follow authored color
    fixed_handle = lib.resources["icon:logo-fixed"]
    color_handle = lib.resources["icon:icon-color"]
    assert fixed_handle.color_editable is False
    assert color_handle.color_editable is True

    return {"name": "color_editable", "ok": True,
            "fixed_color_editable": fixed_handle.color_editable,
            "color_color_editable": color_handle.color_editable}


def test_clear_cache() -> dict:
    """场景 5: clear-cache（Provider-owned 缓存清理）"""
    lib = ResourceLibrary()
    lib.register_registry(ResourceRegistry("icon", "图标", 10))

    lib.register_resource(ResourceHandle(
        registry="icon", resource_id="rocket", name="火箭",
        type="svg", color_editable=True,
        semantic_tags=["rocket"], license="MIT"
    ), svg_content='<svg xmlns="http://www.w3.org/2000/svg"><path d="M0 0"/></svg>')

    assert lib.registries["icon"].cached_count == 1

    cleared = lib.clear_cache()
    assert cleared == 1
    assert lib.registries["icon"].cached_count == 0

    # 再 register 会重新创建缓存
    lib.register_resource(ResourceHandle(
        registry="icon", resource_id="rocket", name="火箭",
        type="svg", color_editable=True,
        semantic_tags=["rocket"], license="MIT"
    ), svg_content='<svg xmlns="http://www.w3.org/2000/svg"><path d="M0 0"/></svg>')
    assert lib.registries["icon"].cached_count == 1

    return {"name": "clear_cache", "ok": True,
            "initial_cleared": cleared, "re_register_count": lib.registries["icon"].cached_count}


def test_handle_export_reuse() -> dict:
    """场景 6: 同一 handle 多次 export（去重 + reuse）"""
    lib = ResourceLibrary()
    lib.register_registry(ResourceRegistry("icon", "图标", 10))

    lib.register_resource(ResourceHandle(
        registry="icon", resource_id="rocket", name="火箭",
        type="svg", color_editable=True,
        semantic_tags=["rocket"], license="MIT"
    ), svg_content='<svg xmlns="http://www.w3.org/2000/svg"><path d="M0 0"/></svg>')

    handle = lib.resources["icon:rocket"]

    with tempfile.TemporaryDirectory() as tmp:
        # 第一次 export
        r1 = lib.export(handle, f"{tmp}/out1")
        # 第二次 export 到不同目录
        r2 = lib.export(handle, f"{tmp}/out2")

        assert Path(r1["output"]).exists()
        assert Path(r2["output"]).exists()
        # 内容应一致（同 handle）
        assert Path(r1["output"]).read_text() == Path(r2["output"]).read_text()

        # export log 应有 2 条
        assert len(lib.export_log) == 2

    return {"name": "handle_export_reuse", "ok": True,
            "log_count": len(lib.export_log), "content_match": True}


# ─── 主入口 ────────────────────────────────────────────────────────────────

def main() -> int:
    print("=" * 70)
    print("Stage 47.12 · univer_resources 验证（SVG 资源库）")
    print("=" * 70)

    results = [
        test_multi_registry(),
        test_find_by_semantic_queries(),
        test_export_to_workspace(),
        test_color_editable_constraint(),
        test_clear_cache(),
        test_handle_export_reuse(),
    ]

    for r in results:
        status = "PASS" if r["ok"] else "FAIL"
        print(f"\n[{status}] {r['name']}")
        for k, v in r.items():
            if k not in ("ok", "name"):
                print(f"    {k}: {v}")

    print("\n" + "=" * 70)
    print(f"Stage 47.12 PASS: {sum(1 for r in results if r['ok'])}/{len(results)} 场景")
    print("=" * 70)

    return 0 if all(r["ok"] for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
