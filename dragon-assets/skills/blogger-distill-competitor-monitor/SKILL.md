---
license: UNKNOWN
triggers: ["blogger distill competitor monitor", "blogger-distill-competitor-monitor — 竞品博主监控流水线"]
---
# blogger-distill-competitor-monitor — 竞品博主监控流水线

> 来源: blogger-distill-orchestration 扩展 + 博主蒸馏全流程增量监控通用化提取
> 版本: V1.0 | 状态: P2-2 实现完成

---

## 一句话描述

扩展已蒸馏博主的增量监控流水线，自动探测风格变化并触发再蒸馏，实现竞品博主追踪的无人值守自动化。

---

## 核心能力

### 1. 增量监控架构

```
┌─────────────────────────────────────────────────────────────────────┐
│  CompetitorMonitor  竞品监控状态机                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    │
│  │  基准注册   │───▶│  增量采集   │───▶│  变化检测   │    │
│  │ register_  │    │ incremental_ │    │ detect_     │    │
│  │ baseline()  │    │ collect()   │    │ changes()   │    │
│  └──────────────┘    └──────────────┘    └──────┬───────┘    │
│                                                  │              │
│                            ┌─────────────────────┼──────────────┐  │
│                            ▼                     ▼              ▼  │
│                     ┌──────────┐    ┌──────────────┐  ┌──────────────┐ │
│                     │  变化    │    │  自动       │  │   变化     │ │
│                     │  <阈值   │    │  忽略       │  │  ≥阈值     │ │
│                     │  PASS    │    │  ΔStyle<5% │  │  触发再蒸馏 │ │
│                     └──────────┘    └──────────────┘  └──────┬───────┘ │
│                                                              │         │
│                                                    ┌─────────┴────────┐ │
│                                                    ▼                   ▼ │
│                                             ┌──────────────┐   ┌──────────────┐ │
│                                             │ 归档变化记录 │   │ re_distill() │ │
│                                             │ Δlog.md     │   │ 触发Step 1-6 │ │
│                                             └──────────────┘   └──────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

### 2. 基准注册（Baseline Registration）

新博主完成蒸馏后，将 distill_guide.md 指纹注册为监控基准：

```python
from blogger_distill_competitor_monitor import CompetitorMonitor

monitor = CompetitorMonitor(
    output_dir="./monitoring",
    check_interval_days=7,          # 每7天检查一次
    style_threshold=0.15,           # 风格变化≥15%触发再蒸馏
    content_threshold=0.20,           # 内容类型变化≥20%触发
    notify_webhooks=["飞书Hook"]     # 变化时通知
)

# 新博主蒸馏完成后，注册基准
monitor.register_baseline(
    blogger_name="咖啡博主A",
    distill_guide_path="./output/咖啡博主A/distill_guide.md",
    last_note_id="last_note_xxx",    # 最后一条监控笔记ID
    baseline_snapshot={
        "dominant_style": "生活美学+工具属性",
        "title_pattern": "痛点前置+情绪价值",
        "content_type_ratio": {"干货": 0.4, "种草": 0.35, "故事": 0.25},
        "posting_frequency": 3.2,    # 篇/周
        "avg_liked": 4500,
    }
)
# → 写入 monitoring/baselines/咖啡博主A_baseline.json
```

**基准快照字段**：

| 字段 | 说明 | 用途 |
|------|------|------|
| `dominant_style` | 主导风格描述 | 变化对比 |
| `title_pattern` | 标题规律 | 规律偏移检测 |
| `content_type_ratio` | 内容类型占比 | 类型漂移检测 |
| `posting_frequency` | 发布频率 | 活跃度监控 |
| `avg_liked` | 平均点赞 | 互动水平基线 |
| `last_note_id` | 最后监控笔记 | 增量采集起点 |

### 3. 增量采集（Incremental Collection）

基于 checkpoint-recovery，每轮只采集新增笔记：

```python
def incremental_collect(blogger_name, last_note_id, api_token):
    """
    只采集 last_note_id 之后的新笔记
    复用 Step1 采集逻辑，但不重复爬取已有笔记
    """
    # 1. 搜索博主最新笔记列表
    notes = universal_api_client.search_notes(blogger_id, count=50)

    # 2. 过滤出 last_note_id 之后的新笔记
    new_notes = []
    found_last = False
    for note in notes:
        if note["id"] == last_note_id:
            found_last = True
            break
        new_notes.append(note)

    if not found_last:
        # 历史重置：从头采集（last_note_id 已失效）
        print(f"⚠️ {blogger_name}: last_note_id 未找到，从头采集")
        new_notes = notes

    # 3. 增量采集详情
    results = []
    for note in reversed(new_notes):      # 旧到新顺序
        detail = universal_api_client.probe("fetch_note_detail", note_id=note["id"])
        normalized = multi_schema_normalizer.normalize(detail)
        results.append(normalized)

    return results, new_notes[0]["id"] if new_notes else last_note_id
```

**关键设计**：
- 不重复爬取已有笔记，节省 API 调用
- 使用 `last_note_id` 作为时间分界点
- 兼容 checkpoint-recovery 的断点续传

### 4. 变化检测（Change Detection）

三层对比引擎：

```python
from blogger_distill_competitor_monitor import ChangeDetector

detector = ChangeDetector()

# Step 1: 风格维度对比
style_score = detector.compare_style(
    baseline_snapshot=baseline,
    new_notes=new_notes_repaired,
    method="cosine_similarity"     # 余弦相似度
)
# style_score ∈ [0, 1], 1=完全一致

# Step 2: 内容类型漂移检测
type_drift = detector.compare_content_type_ratio(
    baseline_ratio=baseline["content_type_ratio"],
    new_notes=new_notes_repaired
)
# type_drift ∈ [0, 1], 0=完全一致

# Step 3: 发布频率变化检测
freq_change = detector.compare_posting_frequency(
    baseline_freq=baseline["posting_frequency"],
    new_notes=new_notes_repaired,
    period_days=check_interval_days * 7
)

# 综合决策
def evaluate_change(style_score, type_drift, freq_change):
    style_delta = 1 - style_score
    if style_delta >= threshold.style:
        return "RE_DISTILL", {
            "style_delta": style_delta,
            "type_drift": type_drift,
            "freq_change": freq_change,
            "reason": f"风格变化 {style_delta:.1%} ≥ 阈值 {threshold.style:.1%}"
        }
    if type_drift >= threshold.content:
        return "RE_DISTILL", {
            "type_drift": type_drift,
            "reason": f"内容类型漂移 {type_drift:.1%} ≥ 阈值 {threshold.content:.1%}"
        }
    return "PASS", {"style_delta": style_delta, "type_drift": type_drift}
```

**阈值配置**：

| 阈值 | 默认值 | 说明 |
|------|--------|------|
| `style_threshold` | 15% | 风格向量变化达到此值触发再蒸馏 |
| `content_threshold` | 20% | 内容类型分布KL散度达到此值触发 |
| `freq_threshold` | 2x | 发布频率超过2倍基线触发警告 |

### 5. 风格指纹提取（Style Fingerprint）

使用 xiaohongshu-content-analyzer 的分析能力，提取新笔记的风格向量：

```python
from xiaohongshu_content_analyzer import BloggerAnalyzer

analyzer = BloggerAnalyzer(blogger_name=blogger_name)

# 提取风格向量（11维降维）
fingerprint = analyzer.extract_style_vector(notes=new_notes_repaired)
# fingerprint: {
#     "aesthetic_score": 0.75,     # 美学维度
#     "utility_score": 0.82,       # 工具价值
#     "emotion_score": 0.60,       # 情绪价值
#     "story_score": 0.45,         # 叙事维度
#     "干货_ratio": 0.38,           # 干货占比
#     "种草_ratio": 0.35,
#     "故事_ratio": 0.15,
#     "other_ratio": 0.12,
#     "avg_title_length": 18.3,
#     "emoji_density": 0.22,
#     "hashtag_count": 4.7,
# }

# 余弦相似度
from numpy.linalg import norm
from numpy import dot

def cosine_similarity(a, b):
    vec_a = [a[k] for k in sorted(a.keys())]
    vec_b = [b[k] for k in sorted(b.keys())]
    return dot(vec_a, vec_b) / (norm(vec_a) * norm(vec_b))
```

### 6. 再蒸馏触发（Re-distillation Trigger）

变化检测通过后，自动触发完整蒸馏流程：

```python
def on_significant_change(blogger_name, change_report):
    """
    触发再蒸馏，更新博主风格基准
    """
    print(f"\n🔄 {blogger_name}: 检测到显著变化，开始再蒸馏...")

    # 触发完整 pipeline
    result = pipeline_orchestrator.run(
        blogger_id=change_report["blogger_id"],
        blogger_name=blogger_name,
        steps="all",
        mode="learn"
    )

    # 提取新 distill_guide
    new_distill_guide = load_json(f"./output/{blogger_name}/distill_guide.md")

    # 注册新基准（替换旧基准）
    monitor.update_baseline(
        blogger_name=blogger_name,
        new_distill_guide=new_distill_guide,
        new_last_note_id=change_report["latest_note_id"]
    )

    # 归档变化记录
    monitor.archive_change_log(blogger_name, change_report)

    # 发送通知
    if result["success"]:
        monitor.notify(
            blogger_name=blogger_name,
            event="re_distill_completed",
            data=change_report
        )
```

### 7. 定时调度（Scheduled Monitoring）

```python
from blogger_distill_competitor_monitor import CompetitorScheduler

scheduler = CompetitorScheduler(
    monitor=monitor,
    cron="0 9 * * 1"     # 每周一早上9点执行
)

# 注册所有已蒸馏博主
for blogger in get_distilled_bloggers("./output"):
    scheduler.add_blogger(
        blogger_name=blogger["name"],
        blogger_id=blogger["id"],
        baseline_path=blogger["distill_guide_path"],
        last_note_id=blogger["last_note_id"]
    )

# 启动调度（配合 paperclip-heartbeat 使用）
scheduler.start()
# 或一次性执行
scheduler.run_once()
```

---

## 二、变化日志管理

```python
class ChangeLogManager:
    """竞品博主变化日志，自动生成 Δlog.md"""

    def __init__(self, output_dir="./monitoring"):
        self.output_dir = output_dir

    def generate_delta_report(self, blogger_name, baseline, new_snapshot, change_eval):
        """生成变化报告"""
        report = {
            "blogger_name": blogger_name,
            "timestamp": datetime.now().isoformat(),
            "baseline": baseline,
            "new_snapshot": new_snapshot,
            "evaluation": change_eval,
            "deltas": self._compute_deltas(baseline, new_snapshot)
        }

        # 写入 Δlog.md
        path = f"{self.output_dir}/{blogger_name}/Δlog.md"
        with open(path, "w", encoding="utf-8") as f:
            f.write(self._render_delta_markdown(report))

        return report

    def _render_delta_markdown(self, report):
        lines = [
            f"# {report['blogger_name']} 风格变化日志",
            f"\n## {report['timestamp']}",
            f"\n## 变化评估: {report['evaluation']['decision']}",
            f"\n### 风格变化",
            f"- 风格相似度: **{(1-report['deltas']['style_delta']):.1%}**",
            f"- 风格变化量: **{report['deltas']['style_delta']:.1%}**",
            f"\n### 内容类型漂移",
            f"- 类型漂移量: **{report['deltas']['type_drift']:.1%}**",
        ]
        return "\n".join(lines)
```

---

## 三、通用化改造要点

从 blogger-distill-orchestration 扩展提取时做了以下通用化：

| 原字段 | 通用化 |
|--------|--------|
| 小红书博主 | 任意平台博主（微博/抖音/B站） |
| `distill_guide.md` 基准 | 任意风格指纹 JSON |
| `xiaohongshu-content-analyzer` | 平台对应分析器 |
| 风格向量 11 维 | 任意 N 维风格向量 |
| 余弦相似度 | 任意距离度量（欧氏/JSD/KL） |
| 飞书 Webhook | 任意 Webhook（钉钉/Telegram/Slack） |

---

## 四、API 参考

```python
from blogger_distill_competitor_monitor import (
    CompetitorMonitor,
    ChangeDetector,
    IncrementalCollector,
    ChangeLogManager,
    CompetitorScheduler
)

# 初始化监控器
monitor = CompetitorMonitor(
    output_dir="./monitoring",
    check_interval_days=7,
    style_threshold=0.15,
    content_threshold=0.20,
    blogger_profile=blogger_profile        # 复用 crawler-quality-grader
)

# 注册博主基准
monitor.register_baseline(
    blogger_name="咖啡博主A",
    distill_guide_path="./output/咖啡博主A/distill_guide.md",
    last_note_id="last_note_xxx",
    baseline_snapshot=fingerprint
)

# 执行监控检查（单次）
result = monitor.check(blogger_name="咖啡博主A")
# result: {decision: "PASS"|"RE_DISTILL", deltas: {...}}

# 批量监控所有注册博主
results = monitor.check_all()

# 触发再蒸馏
if results["咖啡博主A"]["decision"] == "RE_DISTILL":
    monitor.trigger_re_distill("咖啡博主A")

# 调度启动
scheduler = CompetitorScheduler(monitor=monitor, cron="0 9 * * 1")
scheduler.start()
```

### 核心类

```python
class CompetitorMonitor:
    def __init__(self, output_dir, check_interval_days=7,
                 style_threshold=0.15, content_threshold=0.20)

    def register_baseline(self, blogger_name, distill_guide_path,
                          last_note_id, baseline_snapshot) -> None

    def update_baseline(self, blogger_name, new_distill_guide,
                         new_last_note_id) -> None

    def check(self, blogger_name) -> dict:
        """检查单个博主，返回 {decision, deltas, report}"""

    def check_all(self) -> dict:
        """批量检查所有注册博主"""

    def trigger_re_distill(self, blogger_name) -> dict:
        """触发再蒸馏流程"""

    def notify(self, blogger_name, event, data) -> None:
        """发送 Webhook 通知"""

    def archive_change_log(self, blogger_name, report) -> None:
        """归档变化日志"""


class ChangeDetector:
    def compare_style(self, baseline_snapshot, new_notes) -> float:
        """返回风格余弦相似度 0-1"""

    def compare_content_type_ratio(self, baseline_ratio, new_notes) -> float:
        """返回内容类型漂移量 0-1"""

    def evaluate(self, style_score, type_drift, freq_change) -> str:
        """返回 PASS / RE_DISTILL"""
```

---

## 五、CLI 命令

```bash
# 注册新博主基准
competitor-monitor register --blogger "咖啡博主A" \
  --distill-guide ./output/咖啡博主A/distill_guide.md \
  --last-note-id "note_xxx"

# 执行单次检查
competitor-monitor check --blogger "咖啡博主A"

# 批量检查所有博主
competitor-monitor check-all

# 查看变化日志
competitor-monitor log --blogger "咖啡博主A"

# 触发手动再蒸馏
competitor-monitor re-distill --blogger "咖啡博主A"

# 启动定时调度
competitor-monitor schedule --cron "0 9 * * 1"

# 查看监控状态
competitor-monitor status

# 移除博主监控
competitor-monitor remove --blogger "咖啡博主A"

# 导入已蒸馏博主列表（批量注册）
competitor-monitor import-batch --from ./output/bloggers_manifest.json
```

---

## 六、天龙岗位集成

| 岗位 | 集成方式 |
|------|---------|
| **32-01 市场研究** | 竞品博主风格对比，自动化监控已蒸馏博主 |
| **32-02 竞品分析** | 变化检测引擎，Δlog 归档，风格漂移预警 |
| **35-02 社媒运营** | 新风格快速跟进，再蒸馏触发通知 |
| **09-02 编排协调师** | 调度编排，CompetitorScheduler 集成 |
| **35-06 博主蒸馏分析师** | re_distill() 触发完整 pipeline |
| **04 验证师** | 增量数据质量验证（复用 V1-V6） |

---

## 七、预期收益

| 指标 | 集成前 | 集成后 | 提升 |
|------|--------|--------|------|
| 竞品监控成本 | 全手动追踪 | 自动增量采集 | **-85%** |
| 风格变化发现速度 | 数周人工发现 | 7天自动检测 | **-85%** |
| 再蒸馏触发延迟 | 月级 | 周级 | **-80%** |
| API 调用节省 | 每次全量采集 | 仅增量采集 | **-90%** |
| 变化记录完整性 | 碎片化 | 自动化 Δlog | **+300%** |

---

## 八、依赖关系

```
blogger-distill-competitor-monitor/
├── monitor.py                   # CompetitorMonitor 核心类
├── change_detector.py          # ChangeDetector 变化检测引擎
├── incremental_collector.py    # IncrementalCollector 增量采集
├── change_log.py               # ChangeLogManager 变化日志
├── scheduler.py               # CompetitorScheduler 定时调度
├── cli.py                     # CLI 入口
├── config.py                  # 默认阈值配置
└── templates/
    └── delta_log.md          # Δlog 模板
```

**上游依赖**：
- `blogger-distill-orchestration` — 完整 pipeline 触发
- `checkpoint-recovery` — 增量采集断点续传
- `multi-schema-normalizer` — 增量数据归一化
- `crawler-quality-grader` — 增量数据质量验证（V1-V6）
- `xiaohongshu-content-analyzer` — 风格向量提取

---

*基于 blogger-distiller 竞品监控场景提取通用化 + blogger-distill-orchestration P2-2 扩展*
