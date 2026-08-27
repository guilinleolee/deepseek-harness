---
license: UNKNOWN
triggers: ["blogger distill orchestration", "blogger-distill-orchestration — 博主蒸馏全流程编排引擎"]
---
# blogger-distill-orchestration — 博主蒸馏全流程编排引擎

> 来源: blogger-distiller 全流程整合 + 天龙引擎 09-02 编排协调师协同
> 版本: V1.0 | 状态: P2-1 实现完成

---

## 一句话描述

博主蒸馏全流程 6 步编排引擎，整合 universal-api-client、checkpoint-recovery、multi-schema-normalizer、crawler-quality-grader、xiaohongshu-content-analyzer 五大组件，实现采集→验证→补全→分析→蒸馏→归档的端到端自动化。

---

## 核心能力

### 1. 6 步编排架构

```
┌─────────────────────────────────────────────────────────────────────┐
│  PipelineOrchestrator  状态机                                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐ │
│  │ Step 1  │───▶│ Step 2  │───▶│ Step 3  │───▶│ Step 4  │ │
│  │  采 集  │    │  验 证  │    │  补 全  │    │  分 析  │ │
│  │ (P0-1) │    │ (P1-1) │    │ (P0-2)  │    │ (P0-2)  │ │
│  └────┬─────┘    └────┬─────┘    └────┬─────┘    └────┬─────┘ │
│       │                  │                  │                  │       │
│       │  checkpoint-recovery (P1-3)      │                  │       │
│       │  多 Blogger 并行隔离              │                  │       │
│       │                  │                  │                  │       │
│       ▼                  ▼                  ▼                  ▼       │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐ │
│  │ Step 5  │───▶│ Step 6  │    │ dead-   │    │ output/  │ │
│  │  蒸 馏  │    │  归 档  │    │ letter  │    │ partial  │ │
│  │ (P0-2) │    │ (LLM)   │    │ queue   │    │ files   │ │
│  └──────────┘    └──────────┘    └──────────┘    └──────────┘ │
│                                                             │
└─────────────────────────────────────────────────────────────────────┘
```

### 2. 步骤详解

#### Step 1：采集（采集管道）
**依赖**: `universal-api-client` (P0-1) + `endpoint-pool-router` (P1-2) + `multi-schema-normalizer` (P1-4)

**输入**: `{"blogger_id": "xxx", "notes_count": 100}`
**处理**:
1. `UniversalApiClient.search_notes()` → 获取笔记列表（web_v3/app/web_v2/app_v2 四端点探测）
2. `MultiSchemaNormalizer.normalize()` → 统一 D/B/A/C 四种响应结构
3. `EndpointPoolRouter.probe()` → 逐条获取详情（每 10 条 checkpoint-recovery 自动保存）
4. `CheckpointManager.auto_save()` → 每 10 条写入检查点文件

**输出**: `notes_raw.json` — 原始笔记列表（含补调前 partial 数据）

**关键参数**:
- `notes_count`: 目标采集数量（默认 100）
- `checkpoint_interval`: 每 N 条保存检查点（默认 10）
- `max_retries`: 端点探测最大重试（默认 3）

```python
# 采集步骤核心逻辑
from universal_api_client import UniversalApiClient
from multi_schema_normalizer import MultiSchemaNormalizer
from checkpoint_recovery import CheckpointManager

client = UniversalApiClient(token=api_token)
normalizer = MultiSchemaNormalizer()
checkpoint = CheckpointManager(
    output_dir=output_dir,
    task_name=blogger_name,
    batch_size=10
)

# 启动恢复（崩溃后自动续传）
state = checkpoint.load()
already_done = state["done_ids"]

# 采集笔记列表
notes = client.search_notes(blogger_id, count=notes_count)
for note in notes:
    if note["id"] in already_done:
        continue  # 跳过已采集
    detail = client.probe("fetch_note_detail", note_id=note["id"])
    normalized = normalizer.normalize(detail)
    results.append(normalized)
    checkpoint.auto_save(len(results), state)
```

#### Step 2：验证（质量门控）
**依赖**: `crawler-quality-grader` (P1-1)

**输入**: `notes_raw.json`
**处理**:
1. `QualityGateRunner.run_all()` → 批量质量评估（V1-V6 六门控）
2. V1/V6 阻断门控：正文完整度 <50% 或产出文件不存在 → `sys.exit(1)`
3. V2-V5 警告门控：记录但不阻断
4. `check_note_quality()` → 单条分级 complete/partial/failed

**输出**:
- `notes_verified.json` — 通过质量门控的笔记
- `quality_report.json` — V1-V6 质量报告
- `failed_notes.json` — failed 笔记（含 reason）

**门控参数**:
```python
from crawler_quality_grader import QualityGateRunner

runner = QualityGateRunner(
    threshold_v1=0.5,   # V1 正文完整度
    threshold_v3=0.8,    # V3 时间字段
    blocking=True         # V1/V6 阻断
)
result = runner.run_all(notes=notes_raw, profile=blogger_profile)

if not result["passed"]:
    print(f"V1/V6 阻断: {result['summary']}")
    sys.exit(1)  # 阻断后续流程
```

#### Step 3：补全（自愈合并）
**依赖**: `xiaohongshu-content-analyzer` (P0-2) + `crawler-quality-grader` self-healing

**输入**: `notes_verified.json`（含 partial 数据）
**处理**:
1. `repair_incomplete_notes()` → 轮次 2 补调缺失字段（author/interact）
2. `fetch_comments_batch()` → 轮次 3 评论采集
3. `merge_note_supplement()` → 自愈合并（只填空字段，不覆盖已有）
4. `"_is_empty_value"` 判断：交互数 "0" 视为空，触发补全

**输出**:
- `notes_repaired.json` — 补全后笔记（含评论）
- `repair_summary.json` — 每条笔记补全字段统计

**关键逻辑**:
```python
from crawler_quality_grader import merge_note_supplement

for note in notes_verified:
    quality = check_note_quality(note)
    if quality["level"] == "partial":
        supplement = repair_round2(note)      # 补 author/interact
        merged = merge_note_supplement(note, supplement)
        # 只填空字段，_meta.repaired = True
```

#### Step 4：分析（内容深度分析）
**依赖**: `xiaohongshu-content-analyzer` (P0-2)

**输入**: `notes_repaired.json`
**处理**:
1. `analyze_data_materials()` → 11 维内容分析（标题策略/内容框架/视觉风格/互动策略等）
2. `compare_bloggers()` → 横向对比（多博主时）
3. 统计指标：发布频率/互动均值/内容类型分布/情感趋势

**输出**:
- `analysis_report.json` — 11 维分析结果
- `blogger_stats.json` — 统计指标汇总
- `content_patterns.json` — 内容模式识别

```python
from xiaohongshu_content_analyzer import BloggerAnalyzer

analyzer = BloggerAnalyzer(blogger_name=blogger_name)
report = analyzer.analyze_data_materials(notes_repaired)

# 11 维分析
for dim in report["dimensions"]:
    print(f"  {dim['name']}: {dim['score']}/10, 置信度: {dim['confidence']}")
```

#### Step 5：蒸馏（风格提取）
**依赖**: `xiaohongshu-content-analyzer` (P0-2)

**输入**: `analysis_report.json` + `blogger_stats.json`
**处理**:

**Mode A — 学习他人**:
1. `distill(mode="learn")` → 生成 6 节 skill 文件
2. 创作指南三维度：像 TA 一样思考 / 像 TA 一样决策 / 像 TA 一样写

**Mode B — 自我分析**:
1. `distill(mode="self")` → 创作基因识别
2. 自我诊断三维度：你的思考模式 / 你的决策风格 / 你的写作方式

**输出**:
- `distill_guide.md` — 创作指南（Mode A）
- `self_analysis.md` — 自我分析报告（Mode B）
- `skill_files/6节/` — 结构化 skill 文件

```python
# Mode A: 学习他人风格
guide = analyzer.distill(
    mode="learn",
    report=analysis_report,
    stats=blogger_stats,
    output_dir=output_dir
)

# Mode B: 自我分析
self_report = analyzer.distill(
    mode="self",
    stats=blogger_stats,
    output_dir=output_dir
)
```

#### Step 6：归档（知识持久化）
**依赖**: 天龙引擎 `07 记录师` + `llm-wiki-compiler`

**输入**: 全部产出文件
**处理**:
1. `WikiArchiver.archive()` → 归档到 wiki 知识库
2. `PipelineSummary.generate()` → 生成 pipeline 执行摘要
3. `FollowupScheduler.schedule()` → 安排后续监控（可选）

**输出**:
- `wiki/{blogger_name}/` — wiki 归档目录
- `pipeline_summary.json` — 执行摘要（含各步骤耗时/成功率）
- `followup_reminder.json` — 后续提醒（定期复采建议）

---

### 3. 断点续传（每步骤独立）

每个步骤通过 `checkpoint-recovery` 实现独立检查点：

```python
class PipelineStep:
    def __init__(self, name, checkpoint_key, dependencies=None):
        self.name = name
        self.checkpoint_key = checkpoint_key
        self.state = self._load_checkpoint()

    def _load_checkpoint(self):
        """从检查点恢复步骤状态"""
        path = f"{output_dir}/checkpoint_{self.checkpoint_key}.json"
        if os.path.exists(path):
            return json.load(open(path))
        return {"completed": [], "failed": [], "last_idx": 0}

    def _save_checkpoint(self):
        """保存步骤检查点"""
        path = f"{output_dir}/checkpoint_{self.checkpoint_key}.json"
        with open(path, "w") as f:
            json.dump(self.state, f, ensure_ascii=False)

    def run(self, items, resume=True):
        """执行步骤，支持断点续传"""
        start_idx = 0 if not resume else self.state["last_idx"]
        for i, item in enumerate(items[start_idx:], start=start_idx):
            try:
                result = self.process(item)
                self.state["completed"].append(result)
            except Exception as e:
                self.state["failed"].append({"item": item, "error": str(e)})
            if (i + 1) % 10 == 0:
                self.state["last_idx"] = i + 1
                self._save_checkpoint()
        return self.state
```

**检查点文件命名**:
```
output_dir/
├── blogger_name_details_partial.json     # Step 1 采集检查点
├── checkpoint_step2_verified.json       # Step 2 验证检查点
├── checkpoint_step3_repaired.json       # Step 3 补全检查点
├── checkpoint_step4_analyzed.json       # Step 4 分析检查点
├── checkpoint_step5_distilled.json      # Step 5 蒸馏检查点
└── blogger_name_final.json             # 最终产出（成功后生成）
```

---

### 4. 错误处理与死信队列

```python
class DeadLetterQueue:
    """失败条目死信队列，支持人工介入"""

    def __init__(self, path):
        self.path = path
        self.queue = self._load()

    def add(self, step, item_id, reason, traceback):
        self.queue.append({
            "step": step,
            "item_id": item_id,
            "reason": reason,
            "traceback": traceback,
            "timestamp": datetime.now().isoformat(),
            "retries": 0,
            "status": "pending"  # pending / resolved / abandoned
        })
        self._save()

    def retry(self, idx, max_retries=3):
        """重试指定条目（最多3次）"""
        entry = self.queue[idx]
        if entry["retries"] < max_retries:
            entry["retries"] += 1
            entry["status"] = "pending"
            return True
        return False

    def report(self):
        """生成死信队列报告"""
        pending = [e for e in self.queue if e["status"] == "pending"]
        print(f"\n⚠️  Dead Letter Queue: {len(pending)} pending")
        for e in pending:
            print(f"  [{e['step']}] {e['item_id']}: {e['reason']}")
```

**重试策略**:
- 端点 400 错误：跳过当前端点，降级到下一优先级
- 端点 500 错误：等待 2s 重试，仍失败则降级
- 端点 429 限流：等待 5s 重试
- 单条处理异常：记录到 DLQ，继续处理下一条

---

### 5. 多 Blogger 并行隔离

```python
# 每个 Blogger 独立 PipelineOrchestrator 实例
def parallel_collect(blogger_ids: list, max_workers=3):
    """多 Blogger 并行采集，互不干扰"""
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(run_pipeline, blogger_id): blogger_id
            for blogger_id in blogger_ids
        }
        for future in as_completed(futures):
            blogger_id = futures[future]
            try:
                result = future.result()
                print(f"✅ {blogger_id} 完成")
            except Exception as e:
                print(f"❌ {blogger_id} 失败: {e}")
```

**并行隔离机制**:
- 每个 blogger 有独立检查点文件（通过 `blogger_name` 隔离）
- 无共享状态，每个线程独立读写自己的检查点
- 配合 `threading` 实现多 blogger 并行采集

---

## 二、API 参考

```python
from blogger_distill_orchestration import (
    PipelineOrchestrator,
    Step1Collector,
    Step2Verifier,
    Step3Repairer,
    Step4Analyzer,
    Step5Distiller,
    Step6Archiver,
    DeadLetterQueue
)

# 完整 pipeline
orchestrator = PipelineOrchestrator(
    blogger_id="xxx",
    blogger_name="博主名称",
    output_dir="./output",
    steps="all",           # "all" | [1,2,3] | "1-3"
    mode="learn",           # "learn" | "self"
    max_workers=3           # 多 blogger 并行数
)

# 执行 pipeline
result = orchestrator.run()

# 断点续传
orchestrator = PipelineOrchestrator(
    blogger_id="xxx",
    resume=True,
    resume_from_step=3     # 从 Step 3 恢复
)
result = orchestrator.run()
```

### PipelineOrchestrator 核心方法

```python
class PipelineOrchestrator:
    def __init__(self, blogger_id, blogger_name=None, output_dir="./output",
                 steps="all", mode="learn", max_workers=3,
                 resume=False, resume_from_step=None)

    def run(self) -> dict:
        """执行 pipeline，返回各步骤结果摘要"""

    def status(self) -> dict:
        """返回 pipeline 状态（各步骤完成度/失败数）"""

    def resume(self, from_step=None):
        """从指定步骤恢复执行"""

    def abort(self):
        """中止 pipeline，保存当前状态"""

    def get_dlq(self) -> DeadLetterQueue:
        """获取死信队列"""

    def export_summary(self, format="markdown") -> str:
        """导出 pipeline 执行摘要"""
```

### 步骤级 API

```python
# Step 1 采集
collector = Step1Collector(api_token, output_dir)
raw_notes = collector.run(blogger_id, notes_count=100)

# Step 2 验证
verifier = Step2Verifier(output_dir)
verified, report = verifier.run(raw_notes)

# Step 3 补全
repairer = Step3Repairer(api_token, output_dir)
repaired = repairer.run(verified)

# Step 4 分析
analyzer = Step4Analyzer(output_dir)
analysis, stats = analyzer.run(repaired)

# Step 5 蒸馏
distiller = Step5Distiller(mode="learn", output_dir)
guide = distiller.run(analysis, stats)

# Step 6 归档
archiver = Step6Archiver(output_dir)
archiver.archive(pipeline_result)
```

---

## 三、CLI 命令

```bash
# 完整 pipeline
blogger-distill orchestrate --blogger-id XXX --notes 100 --mode learn

# 断点续传（自动检测检查点）
blogger-distill orchestrate --blogger-id XXX --resume

# 从指定步骤恢复
blogger-distill orchestrate --blogger-id XXX --resume --from-step 3

# 指定步骤范围
blogger-distill orchestrate --blogger-id XXX --steps 1-3

# 多 blogger 并行
blogger-distill orchestrate --blogger-ids id1,id2,id3 --parallel 3

# 试运行（不执行，只输出 pipeline 计划）
blogger-distill orchestrate --blogger-id XXX --dry-run

# 导出摘要
blogger-distill orchestrate --blogger-id XXX --export-summary --format markdown

# 死信队列管理
blogger-distill dlq list --blogger-id XXX
blogger-distill dlq retry --blogger-id XXX --idx 3
blogger-distill dlq abandon --blogger-id XXX --idx 5

# 质量门控独立运行
blogger-distill verify ./notes_raw.json --threshold 0.5 --blocking
```

---

## 四、天龙岗位集成

| 岗位 | 集成方式 |
|------|---------|
| **09-02 编排协调师** | PipelineOrchestrator 编排引擎，Level 5 场景模板 |
| **50-01 产品策划** | 博主画像分析 → 产品定位建议 → 内容策略 |
| **17-01 数据分析师** | 采集管道核心依赖，Step 4 统计分析 |
| **35-06 博主蒸馏分析师** | 6 子引擎完整协同，Mode A/B 蒸馏 |
| **04 验证师** | Step 2 质量门控，V1-V6 阻断/警告分级 |
| **07 记录师** | Step 6 归档，wiki 知识库写回 |

---

## 五、预期收益

| 指标 | 集成前 | 集成后 | 提升 |
|------|--------|--------|------|
| 端到端时间 | 2天/博主 | 4小时/博主 | **-95%** |
| 自动化程度 | ~30% | ~95% | **+217%** |
| 数据采集成功率 | ~60-70% | ~99% | **+43%** |
| 崩溃恢复时间 | 小时级手动 | 秒级自动 | **-99%** |
| 多博主并行效率 | 串行 | 3x 并行 | **+200%** |

---

## 六、依赖关系

```
blogger-distill-orchestration/
├── orchestrator.py              # PipelineOrchestrator 状态机
├── steps/
│   ├── step1_collector.py     # Step 1 采集
│   ├── step2_verifier.py       # Step 2 验证
│   ├── step3_repairer.py       # Step 3 补全
│   ├── step4_analyzer.py       # Step 4 分析
│   ├── step5_distiller.py      # Step 5 蒸馏
│   └── step6_archiver.py      # Step 6 归档
├── dlq.py                      # DeadLetterQueue 死信队列
├── cli.py                      # CLI 入口
└── templates/
    └── pipeline_summary.md    # pipeline 执行摘要模板
```

---

*基于 blogger-distiller V1.5 全流程提取 + 天龙引擎 09-02 编排协调师协同*
