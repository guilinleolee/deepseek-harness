---
license: UNKNOWN
triggers: ["crawler quality grader", "crawler-quality-grader — 爬虫数据质量分级引擎"]
---
# crawler-quality-grader — 爬虫数据质量分级引擎

> 来源: blogger-distiller/scripts/utils/quality.py + verify.py 通用化提取
> 版本: V1.0 | 状态: P1 提案

---

## 一句话描述

通用爬虫数据质量分级 + 自愈合并 + V1-V6 质量门控系统。

---

## 核心能力

### 1. 质量分级（`check_note_quality`）

对单条爬虫记录做数据质量分级，支持字段级缺失追踪：

| 字段类别 | 检查内容 | 重要性 |
|---------|---------|--------|
| `content` | title/desc 非空 | **核心**，无则 failed |
| `author` | user.nickname / userId | 重要 |
| `interact` | likedCount/collectedCount/commentCount 非"0" | 重要 |
| `time` | time/createTime/publish_time 非0 | 中等 |
| `comments` | comments.list 非空 | 中等 |

**返回值**:

```python
{
    "level": "complete" | "partial" | "failed",
    "missing": ["author", "interact"],  # 缺失字段列表
    "has_content": bool,
    "has_author": bool,
    "has_interact": bool,
    "has_time": bool,
    "has_comments": bool
}
```

### 2. 自愈合并（`merge_note_supplement`）

轮次2补调结果合并到轮次1记录，只填空字段，不覆盖已有：

```python
# 轮次1 拿到了正文
existing = {note: {title: "X", desc: "正文", interactInfo: {}}}
# 轮次2 拿到了互动数据
supplement = {note: {interactInfo: {likedCount: "1000", collectedCount: "200"}}}
# 合并后：正文保留，互动数据补全
result = merge_note_supplement(existing, supplement)
# → {note: {title: "X", desc: "正文", interactInfo: {likedCount: "1000", collectedCount: "200"}}}
```

**特殊处理**：
- `interactInfo` 逐字段合并
- `user` 逐字段合并
- `comments` 仅在原为空时覆盖
- 合并后标记 `_meta.repaired = True`

### 3. 空值判断（`_is_empty_value`）

**重要边界条件**：`"0"` 交互数视为空

```python
def _is_empty_value(v):
    if v is None: return True
    if isinstance(v, str):
        return v.strip() in ("", "0")  # ← "0" 算空
    if isinstance(v, (list, dict)):
        return len(v) == 0
    if isinstance(v, (int, float)):
        return v == 0
    return False
```

---

## 二、V1-V6 质量门控（verify.py）

### 门控类型

| 门控 | 类型 | 阈值 | 阻断 |
|------|------|------|------|
| V1 正文完整性 | blocking | 50% | **是**（sys.exit） |
| V2 采集数量 | warning | 70% | 否 |
| V3 时间字段 | warning | 80% | 否 |
| V4 去重检查 | warning | 0重复 | 否 |
| V5 数据水印 | info | — | 否 |
| V6 产出文件 | blocking | 100% | **是**（sys.exit） |

### API

```python
from crawler_quality_grader import (
    check_note_quality,
    merge_note_supplement,
    check_content_completeness,   # V1
    check_note_count,              # V2
    check_time_field,              # V3
    check_duplicates,              # V4
    get_sample_watermark,         # V5
    check_output_files,           # V6
    QualityGateRunner
)

# 快速评估
runner = QualityGateRunner(threshold_v1=0.5, threshold_v3=0.8)
result = runner.run_all(notes=[...], profile={...})
# result: {passed: bool, gates: {...}, summary: str}

# 自愈合并（轮次2用）
merged = merge_note_supplement(existing_note, round2_note)
```

---

## 三、通用化改造要点

从 blogger-distiller 源码提取时做了以下通用化：

| 原字段 | 通用化 |
|--------|--------|
| `note.desc` | `_get_content(obj)` — 兼容 `{note:{}}` 和直接 obj |
| `note.time` | `_get_time(obj)` — 兼容 time/createTime/publish_time |
| `interactInfo` | `_get_interact(obj)` — 兼容 interactInfo/interact_info |
| `_feed_id` | `_get_id(obj)` — 兼容 _feed_id/id/note_id |

---

## 四、天龙岗位集成

| 岗位 | 集成方式 |
|------|---------|
| **04 验证师** | V1-V6 质量门控命令 `quality-gate` |
| **17-01 数据分析师** | 采集后自动触发质量分级 |
| **35-06 博主蒸馏分析师** | Engine 3 质量验证 |

---

## 五、CLI 命令

```bash
# 质量评估
crawler-quality grade ./notes.json --threshold 0.5

# 自愈合并
crawler-quality merge ./round1.json ./round2.json --output merged.json

# 批量质量报告
crawler-quality report ./data/ --format json --output quality_report.json

# 质量门控（V1+V6 阻断）
crawler-quality gate ./data/ --blocking
```

---

## 六、预期收益

| 指标 | 提升 |
|------|------|
| 数据质量验证 | 依赖人工 → V1-V6 自动门控 |
| partial 数据利用率 | 0% → 80%+（自愈合并） |
| 质量评估效率 | +300% |

---

*基于 blogger-distiller V1.5 quality.py + verify.py 提取通用化*
