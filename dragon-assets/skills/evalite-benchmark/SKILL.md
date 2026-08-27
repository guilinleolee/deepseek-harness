---
license: UNKNOWN
triggers: ["evalite benchmark", "evalite-benchmark"]
---
# evalite-benchmark

## L0: 一句话描述
LLM Benchmark 数据集对比评估工具，支持多模型横向对比、统计显著性检验和排行榜生成。

## L1: 使用场景

**适用场景：**
- 比较多个模型在同一测试集上的性能差异
- 生成标准化 Benchmark 排行榜
- 评估模型对特定任务的能力边界
- 统计显著性检验（判断差异是否真实可靠）

**不适用：**
- 单一模型功能验证（用 evalite-native）
- 端到端集成测试（用 evalite-browser）

**触发关键词：** benchmark、对比评估、模型排行、排行榜、Statistical comparison

## L2: 详细文档

### 核心能力

```
┌─────────────────────────────────────────────────────────────┐
│ evalite-benchmark 核心能力                                   │
├─────────────────────────────────────────────────────────────┤
│ 1. 多模型横向对比                                          │
│    - 支持任意数量的模型同时对比                             │
│    - 统一测试集，统一评分标准                              │
│    - 表格化输出对比结果                                    │
│                                                             │
│ 2. 统计显著性检验                                          │
│    - t-test 比较均值差异                                    │
│    - Chi-square 比较通过率差异                              │
│    - 置信区间计算 (95% CI)                                 │
│    - p-value 报告                                          │
│                                                             │
│ 3. Benchmark 数据集管理                                     │
│    - 内置常用数据集 (MMLU, HellaSwag, TruthfulQA 等)      │
│    - 自定义数据集导入 (JSON/CSV)                           │
│    - 数据集版本追踪                                        │
│                                                             │
│ 4. 排行榜生成                                              │
│    - HTML 可视化排行榜                                     │
│    - Markdown 表格导出                                      │
│    - JSON 结果导出                                          │
│                                                             │
│ 5. 回归检测                                                │
│    - 与历史记录对比                                        │
│    - 自动检测性能回归                                      │
│    - 告警机制                                              │
└─────────────────────────────────────────────────────────────┘
```

### 安装

```bash
# 安装依赖
cd ~/.claude/skills/evalite-benchmark
pip install -r requirements.txt

# 初始化项目
bash scripts/init.sh
```

### 使用方法

#### 方法 1: Python API

```python
from evalite_benchmark import Benchmark, Model, Dataset

# 定义模型
models = [
    Model(name="GPT-4", provider="openai", model_id="gpt-4"),
    Model(name="Claude-3", provider="anthropic", model_id="claude-3-sonnet"),
    Model(name="Gemini-Pro", provider="google", model_id="gemini-pro"),
]

# 加载数据集
dataset = Dataset.from_json("datasets/mmlu_subset.json")

# 创建 Benchmark
benchmark = Benchmark(
    name="LLM Comparison",
    models=models,
    dataset=dataset,
    trials=5,
)

# 运行评估
results = benchmark.run()

# 生成报告
benchmark.generate_report(format="html")
```

#### 方法 2: Python CLI

```bash
# 初始化 benchmark 项目
python scripts/init.py

# 运行 benchmark
python scripts/benchmark_runner.py run \
    --config configs/benchmark_config.yaml \
    --models gpt-4 claude-3-sonnet gemini-pro \
    --dataset datasets/test.json \
    --trials 5

# 查看排行榜
python scripts/benchmark_runner.py leaderboard \
    --format html

# 回归检测
python scripts/benchmark_runner.py regression \
    --baseline results/baseline.json \
    --current results/current.json
```

#### 方法 3: TypeScript (evalite.config.ts)

```typescript
import { defineBenchmark } from "evalite";
import { openai } from "ai";
import { anthropic } from "@ai-sdk/anthropic";

export default defineBenchmark({
  name: "Model Comparison",
  models: [
    openai("gpt-4o"),
    anthropic("claude-3-5-sonnet-20241014"),
  ],
  dataset: "./datasets/qa_benchmark.json",
  metrics: ["accuracy", "latency", "cost"],
  trials: 10,
  statisticalTest: "t-test",
  reportFormat: ["html", "markdown", "json"],
});
```

### 配置文件格式 (YAML)

```yaml
# configs/benchmark_config.yaml
name: "LLM Capability Benchmark"
version: "1.0"

models:
  - name: "GPT-4"
    provider: "openai"
    model_id: "gpt-4"
    api_key_env: "OPENAI_API_KEY"

  - name: "Claude-3 Sonnet"
    provider: "anthropic"
    model_id: "claude-3-sonnet-20240229"
    api_key_env: "ANTHROPIC_API_KEY"

dataset:
  source: "./datasets/mmlu_subset.json"
  format: "multiple_choice"
  shuffle: true

evaluation:
  trials: 5
  timeout: 30
  parallel: true
  max_parallel_models: 3

statistical:
  test: "t-test"           # t-test | chi-square | wilcoxon
  alpha: 0.05              # significance level
  confidence_interval: 0.95

reporting:
  formats: ["html", "markdown", "json"]
  output_dir: "./results"
  include_charts: true

regression:
  enabled: true
  baseline_file: "./results/baseline.json"
  alert_threshold: 0.05     # 5% 性能下降告警
```

### 内置数据集

| 数据集 | 任务类型 | 题目数 | 来源 |
|--------|---------|--------|------|
| mmlu_subset | 多选题 | 100 | MMLU |
| hellaswag | 常识推理 | 100 | HellaSwag |
| truthfulqa | 事实问答 | 100 | TruthfulQA |
| math_simple | 数学推理 | 50 | GSM8K 子集 |
| code_debug | 代码调试 | 30 | 自定义 |

### 统计检验输出示例

```
┌─────────────────────────────────────────────────────────────┐
│ Statistical Analysis Results (α = 0.05)                      │
├─────────────────────────────────────────────────────────────┤
│ Model A: GPT-4         Accuracy: 86.2% ± 1.3%              │
│ Model B: Claude-3       Accuracy: 84.7% ± 1.5%              │
│                                                             │
│ t-test:                                                        │
│   t-statistic: 2.34                                          │
│   p-value: 0.021                                            │
│   Result: SIGNIFICANT (p < 0.05)                            │
│   Winner: GPT-4 (+1.5%)                                     │
│                                                             │
│ 95% Confidence Interval for difference: [0.2%, 2.8%]       │
└─────────────────────────────────────────────────────────────┘
```

### 排行榜输出示例

```markdown
# LLM Benchmark Leaderboard

## Overall Rankings

| Rank | Model        | Accuracy | Latency | Cost/1K | Score |
|------|--------------|---------|---------|----------|-------|
| 1   | GPT-4o       | 87.3%   | 1.2s    | $0.03    | 92.1 |
| 2   | Claude-3.5   | 85.8%   | 1.5s    | $0.015   | 89.4 |
| 3   | Gemini-Pro   | 82.1%   | 0.8s    | $0.001   | 84.7 |

*Score = 0.5×Accuracy + 0.3×(1/Latency) + 0.2×(1/Cost)*
```

### 文件结构

```
evalite-benchmark/
├── SKILL.md                          # 本文件
├── evalite.md                        # 核心文档
├── requirements.txt                  # Python 依赖
├── configs/
│   └── benchmark_config.yaml         # 配置文件模板
├── datasets/
│   └── .gitkeep
├── results/
│   └── .gitkeep
├── scripts/
│   ├── init.py                      # 项目初始化
│   ├── benchmark_runner.py          # CLI 运行器
│   └── statistical.py               # 统计检验模块
├── templates/
│   ├── benchmark_config.yaml        # 配置模板
│   └── dataset_template.json        # 数据集模板
└── prompts/
    └── benchmark-design.md          # Benchmark 设计指南
```

### 与 evalite-native 的区别

| 维度 | evalite-native | evalite-benchmark |
|------|--------------|-------------------|
| **目标** | 验证功能正确性 | 比较模型性能差异 |
| **输入** | 单一测试用例 | 标准化测试集 |
| **输出** | Pass/Fail | 排行榜 + 统计检验 |
| ** Trials** | 可选 | 推荐 ≥5 |
| **回归检测** | 无 | 有 |
| **统计检验** | 无 | 有 |
| **排行榜** | 无 | 有 |

## 相关技能

- **evalite-native**: 单一模型功能验证
- **evalite-browser**: 端到端浏览器测试
- **dspy-signature**: 声明式评测签名设计
