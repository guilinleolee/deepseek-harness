---
license: UNKNOWN
triggers: ["blogger distill verify gate", "blogger-distill-verify-gate — 数据采集质量门控工作流"]
---
# blogger-distill-verify-gate — 数据采集质量门控工作流

> 来源: crawler-quality-grader V1-V6 质量门控 × blogger-distill-orchestration Step 2 验证集成
> 版本: V1.0 | 状态: P2-3 实现完成

---

## 一句话描述

V1-V6 六门控自动验收流水线，将 crawler-quality-grader 的质量门控嵌入博主蒸馏编排 Step 2，自动拦截不合格数据，确保进入 Step 3 补全的笔记均为可操作级质量。

---

## 核心能力

### 1. 六门控架构

```
┌─────────────────────────────────────────────────────────────────────┐
│  VerifyGatePipeline  质量门控流水线                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  V1: 正文完整度    [BLOCKING]  正文<50% → 阻断pipeline   │  │
│  │  V2: 采集数量      [WARNING]  笔记<50篇 → 警告        │  │
│  │  V3: 时间字段      [WARNING]  时间缺失>20% → 警告      │  │
│  │  V4: 去重检查      [WARNING]  重复率>10% → 警告      │  │
│  │  V5: 数据水印      [INFO]    无水印 → 记录日志       │  │
│  │  V6: 产出文件      [BLOCKING]  文件缺失 → 阻断pipeline │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              │                                │
│              ┌───────────────┼───────────────┐               │
│              ▼               ▼               ▼               │
│         ┌──────────┐  ┌──────────┐  ┌──────────┐          │
│         │ BLOCKING │  │ WARNING  │  │   PASS   │          │
│         │  阻断   │  │  警告   │  │  通过    │          │
│         └────┬─────┘  └────┬─────┘  └──────────┘          │
│              │               │                              │
│              ▼               ▼                                 │
│       sys.exit(1)    生成警告报告                            │
│       归档DLQ        → pipeline继续                          │
│                                                              │
└─────────────────────────────────────────────────────────────────────┘
```

### 2. 门控参数配置

```python
from crawler_quality_grader import QualityGateRunner

runner = QualityGateRunner(
    # V1 正文完整度（阻断门控）
    threshold_v1=0.50,       # 正文完整度 < 50% → 阻断

    # V2 采集数量（警告门控）
    threshold_v2=50,         # 笔记数量 < 50 → 警告

    # V3 时间字段（警告门控）
    threshold_v3=0.80,       # 时间字段覆盖率 < 80% → 警告

    # V4 去重检查（警告门控）
    threshold_v4=0.10,       # 重复率 > 10% → 警告

    # V5 数据水印（信息门控）
    threshold_v5=0.0,        # 仅记录，不阻断

    # V6 产出文件（阻断门控）
    threshold_v6=1.0,        # 文件缺失 → 阻断

    # 阻断模式
    blocking=True,            # True: V1/V6 阻断 pipeline
)

# 执行全部门控
result = runner.run_all(notes=notes_raw, profile=blogger_profile)

# result:
# {
#   "passed": True/False,
#   "gates": {
#     "v1_completeness": {"score": 0.85, "passed": True, "details": {...}},
#     "v2_quantity": {"count": 120, "passed": True, "details": {...}},
#     "v3_timestamps": {"coverage": 0.92, "passed": True, "details": {...}},
#     "v4_dedup": {"duplicate_rate": 0.03, "passed": True, "details": {...}},
#     "v5_watermark": {"has_watermark": False, "passed": True, "details": {...}},
#     "v6_files": {"all_exist": True, "passed": True, "details": {...}},
#   },
#   "summary": "5/6 通过, V1 完整度 85%, V5 无水印",
#   "blocking_gates": []  # 触发阻断的门控列表
# }
```

### 3. 集成到 Pipeline Step 2

```python
# Step 2: 验证 — 质量门控自动验收
from crawler_quality_grader import QualityGateRunner
from blogger_distill_orchestration import PipelineOrchestrator

orchestrator = PipelineOrchestrator(
    blogger_id="xxx",
    blogger_name="博主A",
    output_dir="./output"
)

def step2_verify(notes_raw, blogger_profile, config):
    """Step 2: 质量门控验收"""
    runner = QualityGateRunner(
        threshold_v1=config.get("v1_threshold", 0.50),
        threshold_v3=config.get("v3_threshold", 0.80),
        blocking=True  # V1/V6 阻断
    )

    result = runner.run_all(notes=notes_raw, profile=blogger_profile)

    # 生成质量报告
    report_path = f"{config['output_dir']}/quality_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    # 提取失败笔记
    failed_notes = [n for n in notes_raw
                    if runner.check_note_quality(n)["level"] == "failed"]

    # V1/V6 阻断：pipeline 中止
    if not result["passed"] or result["blocking_gates"]:
        print(f"\n🚫 V1/V6 阻断: {result['blocking_gates']}")
        print(f"   失败笔记: {len(failed_notes)} 条")

        # 归档到 DLQ
        dlq_path = f"{config['output_dir']}/failed_notes.json"
        with open(dlq_path, "w", encoding="utf-8") as f:
            json.dump(failed_notes, f, ensure_ascii=False, indent=2)

        sys.exit(1)  # 阻断后续流程

    # V2-V5 警告：pipeline 继续
    if result["gates"]["v2_quantity"]["passed"] is False:
        print(f"\n⚠️ V2 采集数量不足: {result['gates']['v2_quantity']['count']} 条")

    print(f"\n✅ Step 2 质量门控通过: {result['summary']}")
    return notes_raw, result
```

### 4. 单笔记质量分级

```python
from crawler_quality_grader import check_note_quality

# 对每条笔记进行质量分级
for note in notes_raw:
    quality = check_note_quality(note)

    if quality["level"] == "complete":
        # 完全合格，直接进入 Step 3
        pass

    elif quality["level"] == "partial":
        # 部分缺失 → 进入 Step 3 补全
        partial_notes.append(note)
        repair_needed[note["id"]] = quality["missing"]

    else:  # "failed"
        # 严重缺失 → 归档 DLQ，不进入 Step 3
        dlq.append(note)
```

**返回结构**：
```python
{
    "level": "complete" | "partial" | "failed",
    "missing": ["author", "interact"],   # 缺失字段
    "score": 0.78,                       # 综合质量分
    "blocking_reason": None | "v1_low" | "v6_missing"  # 阻断原因
}
```

### 5. 自愈补全触发

```python
# Step 3: 补全 — 基于质量分级触发自愈
from crawler_quality_grader import merge_note_supplement

def step3_repair(verified_notes, repair_needed, api_token):
    """只对 partial 笔记进行自愈补全"""
    repaired_count = 0

    for note in verified_notes:
        note_id = note["id"]
        if note_id not in repair_needed:
            continue  # complete 笔记跳过

        # 轮次 2: 补 author / interact
        supplement = fetch_supplement(note, api_token)
        merged = merge_note_supplement(note, supplement)

        # 合并后重新验证
        post_quality = check_note_quality(merged)
        if post_quality["level"] == "complete":
            repaired_count += 1
        else:
            # 仍 partial → 降级到 DLQ
            dlq.append(note)

    print(f"修复完成: {repaired_count}/{len(repair_needed)} 条 partial 笔记")
    return verified_notes  # 含 merged 结果
```

### 6. 阈值配置矩阵

| 门控 | 字段 | 阻断 | 建议阈值 | 低于阈值处理 |
|------|------|------|---------|-------------|
| V1 正文完整度 | `_note.completeness` | **阻断** | 50% | 直接终止 pipeline |
| V2 采集数量 | `_stats.count` | 警告 | 50篇 | pipeline 警告继续 |
| V3 时间字段 | `_meta.timestamps` | 警告 | 80% | pipeline 警告继续 |
| V4 去重检查 | `_note.dedup_hash` | 警告 | 10%重复率 | 警告+过滤重复 |
| V5 数据水印 | `_meta.watermark` | 无 | — | 仅记录日志 |
| V6 产出文件 | `_output.files` | **阻断** | 文件100%存在 | 直接终止 pipeline |

---

## 二、通用化改造要点

从 crawler-quality-grader 提取到 blogger-distill-verify-gate 时做了以下通用化：

| 原字段 | 通用化 |
|--------|--------|
| 小红书笔记 | 任意平台笔记（微博/抖音/B站） |
| `_note.completeness` | 任意 `content_field.body_length / expected_length` |
| `_note.dedup_hash` | 任意 `_record_hash`（MD5/SHA256） |
| `check_note_quality` | 任意 `quality_check(record, schema)` |
| `merge_note_supplement` | 任意 `merge_record(record, supplement)` |

---

## 三、API 参考

```python
from crawler_quality_grader import (
    QualityGateRunner,
    check_note_quality,
    merge_note_supplement,
    DEFAULT_THRESHOLDS
)

# 批量质量评估
runner = QualityGateRunner(
    threshold_v1=0.50,
    threshold_v2=50,
    threshold_v3=0.80,
    threshold_v4=0.10,
    blocking=True
)
result = runner.run_all(notes=notes_raw, profile=blogger_profile)

# 单笔记质量分级
quality = check_note_quality(note)
# → {"level": "complete"|"partial"|"failed", "missing": [...], "score": float}

# 自愈合并
merged = merge_note_supplement(note, supplement)
# → note（只填空字段，不覆盖已有值）

# 默认阈值
print(DEFAULT_THRESHOLDS)
# → {"v1": 0.50, "v2": 50, "v3": 0.80, "v4": 0.10, "v6": 1.0}
```

### VerifyGatePipeline 核心方法

```python
class VerifyGatePipeline:
    def __init__(self, thresholds=None, blocking=True, output_dir="./output"):

    def run(self, notes_raw: list, blogger_profile: dict) -> dict:
        """执行全部门控，返回验收结果"""

    def check_note_level(self, note: dict) -> str:
        """单笔记质量分级: complete / partial / failed"""

    def archive_dlq(self, failed_notes: list, reason: str) -> None:
        """归档失败笔记到 Dead Letter Queue"""

    def generate_report(self, result: dict) -> str:
        """生成质量验收报告"""

    def should_block(self, result: dict) -> bool:
        """判断是否触发阻断"""

    def get_partial_notes(self, notes: list) -> tuple:
        """分离 partial 笔记和 complete 笔记"""

    def retry_partial(self, partial_notes: list) -> list:
        """对 partial 笔记执行自愈补全"""

    def export_verified(self, verified_notes: list) -> None:
        """导出验收通过的笔记"""
```

---

## 四、CLI 命令

```bash
# 独立质量门控评估
crawlerquality grade ./notes_raw.json --output quality_report.json

# 指定阻断阈值
crawlerquality grade ./notes_raw.json \
  --v1-threshold 0.60 \
  --v2-threshold 100 \
  --blocking

# 自愈合并（轮次2补全）
crawlerquality merge ./partial_notes.json \
  --supplement ./supplements.json \
  --output repaired.json

# 质量报告生成
crawlerquality report ./quality_report.json --format markdown

# 集成 pipeline 门控
crawlerquality gate ./notes_raw.json \
  --profile ./blogger_profile.json \
  --output ./output/quality_verified.json
```

---

## 五、天龙岗位集成

| 岗位 | 集成方式 |
|------|---------|
| **04 验证师** | `_verify` 质量门控工作流，P2-3 新增 |
| **17-01 数据分析师** | Step 2 质量报告分析，数据验收依据 |
| **35-06 博主蒸馏分析师** | Step 2 验收前置，数据质量自动确认 |
| **01 调研师** | 质量分级驱动调研深度判断 |

---

## 六、预期收益

| 指标 | 集成前 | 集成后 | 提升 |
|------|--------|--------|------|
| 数据质量稳定性 | 依赖人工抽检 | 自动六门控验收 | **+300%** |
| V1/V6 阻断响应速度 | 小时级人工发现 | 秒级自动阻断 | **-99%** |
| Step 3 补全效率 | 全量补全 | 仅 partial 笔记补全 | **+60%** |
| 质量报告完整性 | 碎片化 | 自动生成结构化报告 | **+500%** |
| DLQ 归档率 | 无记录 | 自动归档失败笔记 | **新增能力** |

---

## 七、依赖关系

```
blogger-distill-verify-gate/
├── verify_gate_pipeline.py    # VerifyGatePipeline 核心类
├── gate_thresholds.py         # 六门控阈值配置
├── note_classifier.py        # 单笔记质量分级器
├── dlq_archiver.py         # Dead Letter Queue 归档
├── quality_report.py        # 质量报告生成
├── cli.py                  # CLI 入口
└── templates/
    └── quality_report.md   # 质量报告模板
```

**上游依赖**：
- `crawler-quality-grader` — V1-V6 门控引擎
- `blogger-distill-orchestration` — Step 2 验证步骤集成
- `multi-schema-normalizer` — 归一化数据质量基准

**下游依赖**：
- `blogger-distill-orchestration` Step 3 — partial 笔记自愈补全
- `crawler-quality-grader` — `_is_empty_value` 边界条件处理

---

*基于 crawler-quality-grader V1-V6 质量门控 × blogger-distill-orchestration P2-1 验证步骤集成*
