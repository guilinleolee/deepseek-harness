"""test_endpoints_schema.py · T1 必检

验证 17 端点 schema：
1. 端点总数 = 17
2. 每个端点有 layer / params / returns
3. 每个端点至少有 1 个参数
4. layer 覆盖 L1-L7 全 7 层
5. fallback.yaml 兜底链覆盖全部 17 端点
6. L3 技术指标层全部含 compute=True
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from pathlib import Path

import pytest
import yaml

BASE = Path(__file__).resolve().parent.parent

import em_global  # noqa: E402


def test_total_endpoints_is_17():
    """端点数严格 = 17，与上游 V1.0.1 一致"""
    assert len(em_global.ENDPOINTS) == 17, (
        f"端点数应为 17，实际 {len(em_global.ENDPOINTS)}"
    )


def test_every_endpoint_has_layer():
    """每个端点必须有 layer 字段"""
    for name, meta in em_global.ENDPOINTS.items():
        assert "layer" in meta, f"{name} 缺 layer"
        assert meta["layer"].startswith("L"), f"{name} layer 应为 Lx 格式"


def test_every_endpoint_has_params():
    """每个端点必须有 params 且至少 1 个"""
    for name, meta in em_global.ENDPOINTS.items():
        assert "params" in meta, f"{name} 缺 params"
        assert len(meta["params"]) >= 1, f"{name} params 应 >= 1"


def test_layer_coverage_full():
    """layer 覆盖 L1-L7 全 7 层"""
    layers = {m["layer"] for m in em_global.ENDPOINTS.values()}
    expected = {f"L{i}" for i in range(1, 8)}
    assert layers >= expected, f"覆盖 layers={sorted(layers)} 缺 {sorted(expected - layers)}"


def test_l3_technical_layer_all_compute():
    """L3 技术指标层 5 端点必须全部含 compute=True"""
    l3_endpoints = [name for name, meta in em_global.ENDPOINTS.items() if meta["layer"] == "L3"]
    assert len(l3_endpoints) == 5, f"L3 应有 5 端点，实际 {len(l3_endpoints)}"
    for name in l3_endpoints:
        assert em_global.ENDPOINTS[name].get("compute") is True, (
            f"{name} L3 端点必须 compute=True"
        )


def test_fallback_yaml_covers_all_17():
    """fallback.yaml 兜底链必须覆盖全部 17 端点"""
    with open(BASE / "fallback.yaml", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    covered = set(cfg["endpoints"].keys())
    defined = set(em_global.ENDPOINTS.keys())
    missing = defined - covered
    assert not missing, f"fallback.yaml 缺兜底链: {missing}"
    extra = covered - defined
    assert not extra, f"fallback.yaml 多余端点: {extra}"


def test_base_templates_use_defined_endpoints():
    """4 类底稿模板的端点必须在 ENDPOINTS 中"""
    for ttype, eps in em_global.BASE_TEMPLATES.items():
        for ep in eps:
            assert ep in em_global.ENDPOINTS, f"底稿 {ttype} 引用未知端点 {ep}"


def test_infer_market_logic():
    """_infer_market 函数：港股以 .HK 结尾，A 股 .SH/.SZ 结尾，其他美股"""
    assert em_global._infer_market("AAPL") == "US"
    assert em_global._infer_market("0700.HK") == "HK"
    assert em_global._infer_market("600519.SH") == "CN"
    assert em_global._infer_market("BABA") == "US"
    assert em_global._infer_market("9988.HK") == "HK"
