"""test_em_check.py · a-stock-data-bridge V1.0 质检脚本 5 个单测

覆盖 em_check.py 的 9 个 check 函数 + 退出码契约（0/1/2/3）。
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import pytest

# 让 pytest 能 import 上级目录的 em_check.py
import sys as _sys
_sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import em_check  # noqa: E402


# ===== fixture：4 类测试底稿 =====

PASS_MD = """# 600519.SH 个股深度底稿

> **生成时间**: 2026-08-03T07:42:33+08:00
> **底稿类型**: stock
> **调用端点数**: 25
> **备胎使用**: 0

## 端点列表

| 端点名 | 层 | 溯源 | 备胎 | 数据 |
|--------|----|------|------|------|
| kline_with_ma | L1 | kline_with_ma | 否 | OK |
| five_level_quote | L1 | five_level_quote | 否 | OK |
| pe_pb_market_cap | L1 | pe_pb_market_cap | 否 | OK |
| cninfo_announcement | L7 | cninfo_announcement | 否 | OK |

---

*Powered by simonlin1212/a-stock-data V3.4.0 (Apache-2.0) · 天龙引擎 a-stock-data-bridge V1.0 包装 · 修改日期 2026-07-21*
"""

W3_FAIL_MD = """# test_w3_fail

> **生成时间**: 2026-08-03T00:00:00+08:00
> **底稿类型**: stock
> **调用端点数**: 3
> **备胎使用**: 0

## 端点列表

| 端点名 | 层 | 溯源 | 备胎 | 数据 |
|--------|----|------|------|------|
| kline_with_ma | L1 | kline_with_ma | 否 | OK |
| five_level_quote | L1 | five_level_quote | 否 | OK |
| pe_pb_market_cap | L1 | pe_pb_market_cap | 否 | OK |

---

*Powered by simonlin1212/a-stock-data V3.4.0 (Apache-2.0) · 天龙引擎 a-stock-data-bridge V1.0 包装 · 修改日期 2026-07-21*
"""

W4_NOMARKET_MD = """# test_w4_no_market

> **生成时间**: 2026-08-03T00:00:00+08:00
> **调用端点数**: 3
> **备胎使用**: 0

## 端点列表

| 端点名 | 层 | 溯源 | 备胎 | 数据 |
|--------|----|------|------|------|
| kline_with_ma | L1 | kline_with_ma | 否 | OK |
| five_level_quote | L1 | five_level_quote | 否 | OK |
| pe_pb_market_cap | L1 | pe_pb_market_cap | 否 | OK |

---

*Powered by simonlin1212/a-stock-data V3.4.0 (Apache-2.0) · 天龙引擎 a-stock-data-bridge V1.0 包装 · 修改日期 2026-07-21*
"""

W5_FAIL_MD = """# test_w5_fail

> **生成时间**: 2026-08-03T00:00:00+08:00
> **底稿类型**: stock
> **调用端点数**: 3
> **备胎使用**: 0

## 端点列表

| 端点名 | 层 | 溯源 | 备胎 | 数据 |
|--------|----|------|------|------|
| kline_with_ma | L1 | kline_with_ma | 否 | OK |
| five_level_quote | L1 | five_level_quote | 否 | OK |
| pe_pb_market_cap | L1 | pe_pb_market_cap | 否 | OK |
| margin_balance | L4 | margin_balance | 否 | OK |

---

*此底稿故意缺上游致谢 + Modified 段*
"""


# ===== 测试 1：完整底稿 → 5 必检全 PASS =====

def test_5_required_checks_on_pass_md():
    """完整底稿 PASS_MD 应满足 W1-W5 全部 5 项必检"""
    md = PASS_MD

    ok_w1, _ = em_check.check_required_fields_markdown(md)
    ok_w2, note_w2 = em_check.check_endpoints_called(md)
    ok_w3, note_w3 = em_check.check_layer_coverage(md)
    ok_w4, note_w4 = em_check.check_market_tag_present(md)
    ok_w5, note_w5 = em_check.check_apache_attribution(md)

    assert ok_w1, "W1 溯源字段应齐全"
    assert ok_w2, f"W2 端点数应 >= 3 (got: {note_w2})"
    assert ok_w3, f"W3 层级覆盖应 >= 2 (got: {note_w3})"
    assert ok_w4, f"W4 市场标签应齐全 (got: {note_w4})"
    assert ok_w5, f"W5 Apache 归属应齐全 (got: {note_w5})"


# ===== 测试 2：完整底稿 → R1+R3 PASS · R2 WARN =====

def test_3_recommended_checks_on_pass_md():
    """完整底稿 PASS_MD 应满足 R1+R3 推荐项 PASS · R2 WARN（备胎未触发=0）"""
    md = PASS_MD

    ok_r1, note_r1 = em_check.check_traceability_completeness(md)
    ok_r2, note_r2 = em_check.check_fallback_recorded(md)
    ok_r3, note_r3 = em_check.check_endpoint_count_reasonable(md)

    assert ok_r1, f"R1 时间戳应齐全 (got: {note_r1})"
    assert not ok_r2, f"R2 备胎字段应 WARN（无 fallback 触发，字段 missing）(got: {note_r2})"
    assert ok_r3, f"R3 端点数应 <= 30 (got: {note_r3})"


# ===== 测试 3：W3 严到 ≥ 2 层（1 层 FAIL）=====

def test_w3_layer_coverage_threshold():
    """W3 应严格到 >= 2 层；只有 1 层 L1 时 FAIL"""
    md = W3_FAIL_MD

    ok, note = em_check.check_layer_coverage(md)
    assert not ok, f"W3 单层底稿应 FAIL (got: {note})"
    # 但 W3 不影响 W1/W2/W5
    ok_w1, _ = em_check.check_required_fields_markdown(md)
    ok_w2, _ = em_check.check_endpoints_called(md)
    ok_w5, _ = em_check.check_apache_attribution(md)
    assert ok_w1 and ok_w2 and ok_w5


# ===== 测试 4：W4 市场标签识别 =====

def test_w4_market_tag_pattern():
    """W4 应识别 SH/SZ/BJ 6 位股票代码 + 底稿类型 stock/industry/event/announcement"""
    # PASS_MD：含 600519.SH + type=stock → PASS
    ok_pass, note_pass = em_check.check_market_tag_present(PASS_MD)
    assert ok_pass, f"PASS_MD 应识别 600519.SH + type=stock (got: {note_pass})"

    # W4_NOMARKET_MD：缺股票代码 + 缺底稿类型 → 应 FAIL（除非有 industry 关键词）
    ok_no, note_no = em_check.check_market_tag_present(W4_NOMARKET_MD)
    assert not ok_no, f"W4_NOMARKET_MD 应 FAIL (got: {note_no})"


# ===== 测试 5：W5 Apache 归属严格性 =====

def test_w5_apache_attribution():
    """W5 应同时要求 upstream + apache + modified 三个字段全有"""
    # PASS_MD：全有 → PASS
    ok_pass, note_pass = em_check.check_apache_attribution(PASS_MD)
    assert ok_pass, f"PASS_MD 应 PASS (got: {note_pass})"

    # W5_FAIL_MD：故意缺 simonlin1212 和 天龙引擎/Modified → FAIL
    ok_fail, note_fail = em_check.check_apache_attribution(W5_FAIL_MD)
    assert not ok_fail, f"W5_FAIL_MD 应 FAIL（缺 upstream + modified）(got: {note_fail})"

    # 单独缺 upstream
    md_no_upstream = re.sub(r"simonlin1212", "REDACTED", PASS_MD)
    ok_no_up, note_no_up = em_check.check_apache_attribution(md_no_upstream)
    assert not ok_no_up, f"缺 upstream 应 FAIL (got: {note_no_up})"

    # 单独缺 modified（同时去掉"天龙引擎"和"Modified"/"修改日期"才能触发）
    md_no_modified = re.sub(r"天龙引擎", "REDACTED", PASS_MD)
    md_no_modified = re.sub(r"修改日期 2026-07-21", "REDACTED", md_no_modified)
    ok_no_mod, note_no_mod = em_check.check_apache_attribution(md_no_modified)
    assert not ok_no_mod, f"缺 modified 应 FAIL (got: {note_no_mod})"