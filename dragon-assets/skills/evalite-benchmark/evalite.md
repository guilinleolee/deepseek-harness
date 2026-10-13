# evalite Benchmark 核心文档

## 概述

evalite-benchmark 是基于 evalite 的 LLM Benchmark 对比评估工具，专注于多模型横向对比、统计显著性检验和排行榜生成。

## 快速开始

### 1. 安装

```bash
cd ~/.claude/skills/evalite-benchmark
pip install -r requirements.txt
```

### 2. 初始化项目

```bash
python scripts/init.py --name "my-benchmark"
```

### 3. 运行评估

```bash
python scripts/benchmark_runner.py run \
    --config configs/benchmark_config.yaml \
    --models gpt-4o claude-3-5-sonnet gemini-pro
```

## 核心概念

### Model (模型定义)

```python
@dataclass
class Model:
    name: str                    # 显示名称
    provider: str                 # 提供商: openai | anthropic | google
    model_id: str                # 模型 ID
    api_key_env: str = None      # API Key 环境变量名
    base_url: str = None         # 自定义端点
    extra_params: dict = None     # 额外参数 (temperature, top_p 等)
```

### Dataset (数据集)

```python
@dataclass
class Dataset:
    name: str
    source: str                  # 文件路径或 URL
    format: str                   # json | csv | mmlu | hellaswag
    tasks: List[Task]
    metadata: dict = None
```

### Task (评估任务)

```python
@dataclass
class Task:
    id: str
    question: str
    choices: List[str] = None    # 选择题选项
    answer: Union[str, int]      # 正确答案
    category: str = None          # 任务类别
    difficulty: str = None         # easy | medium | hard
    metadata: dict = None
```

### BenchmarkResult (评估结果)

```python
@dataclass
class BenchmarkResult:
    model: Model
    dataset: Dataset
    task_results: List[TaskResult]
    metrics: Dict[str, float]
    statistics: Dict[str, float]
    timestamp: datetime
```

## 统计检验

### 支持的检验方法

| 方法 | 适用场景 | 指标类型 |
|------|---------|---------|
| **t-test** | 比较均值差异 | 连续值 (accuracy, score) |
| **chi-square** | 比较通过率差异 | 分类值 (pass/fail) |
| **wilcoxon** | 配对样本比较 | 连续值 (非正态分布) |
| **bootstrap** | 置信区间估计 | 任意指标 |

### 使用示例

```python
from evalite_benchmark.statistical import t_test, chi_square, bootstrap_ci

# t-test: 比较两个模型的准确率
result = t_test(
    scores_a=[0.85, 0.87, 0.86, 0.88, 0.84],
    scores_b=[0.83, 0.82, 0.84, 0.81, 0.85],
    alpha=0.05
)
# result: {significant: True, p_value: 0.021, t_stat: 2.34}

# chi-square: 比较通过率
result = chi_square(
    passes_a=85, total_a=100,
    passes_b=82, total_b=100,
    alpha=0.05
)

# Bootstrap CI: 计算置信区间
ci = bootstrap_ci(
    scores=[0.85, 0.87, 0.86, 0.88, 0.84],
    confidence=0.95,
    n_iterations=10000
)
# ci: (0.831, 0.889)
```

## 排行榜生成

### 评分公式

```python
def compute_score(accuracy, latency, cost):
    """
    综合评分 = 0.5×准确率 + 0.3×速度得分 + 0.2×成本得分

    - 准确率: 原始值 0-1
    - 速度得分: min(latency_ref / latency, 1.0)
    - 成本得分: min(cost_ref / cost, 1.0)
    """
    speed_score = min(LATENCY_REF / latency, 1.0)
    cost_score = min(COST_REF / cost, 1.0)
    return 0.5 * accuracy + 0.3 * speed_score + 0.2 * cost_score
```

### 输出格式

```python
benchmark.generate_report(
    format="html",           # html | markdown | json
    include_charts=True,      # 是否包含可视化图表
    include_stats=True,       # 是否包含统计检验
    include_raw_data=True,    # 是否包含原始数据
)
```

## 回归检测

### 配置

```yaml
regression:
  enabled: true
  baseline_file: "./results/baseline.json"
  alert_threshold: 0.05      # 5% 性能下降触发告警
  comparison_metric: "accuracy" # 用于比较的指标
```

### 检测逻辑

```python
def check_regression(current, baseline, threshold=0.05):
    """检测性能回归"""
    diff = current - baseline
    pct_change = diff / baseline

    if pct_change < -threshold:
        return RegressionAlert(
            detected=True,
            metric="accuracy",
            baseline=baseline,
            current=current,
            change=pct_change,
            severity="HIGH" if pct_change < -0.1 else "MEDIUM"
        )
    return RegressionAlert(detected=False)
```

## API 参考

### Benchmark 类

```python
class Benchmark:
    def __init__(
        self,
        name: str,
        models: List[Model],
        dataset: Dataset,
        trials: int = 5,
        timeout: int = 30,
        parallel: bool = True,
        max_parallel_models: int = 3,
    ): ...

    def run(self) -> List[BenchmarkResult]: ...
    def compare_models(self) -> ComparisonResult: ...
    def generate_report(
        self,
        format: str = "html",
        include_charts: bool = True,
    ) -> str: ...
    def save_results(self, path: str): ...
    def load_results(self, path: str) -> List[BenchmarkResult]: ...
```

### Dataset 类

```python
class Dataset:
    @classmethod
    def from_json(cls, path: str) -> "Dataset": ...

    @classmethod
    def from_csv(cls, path: str, **kwargs) -> "Dataset": ...

    @classmethod
    def from_mmlu(cls, subset: str = "all") -> "Dataset": ...

    @classmethod
    def from_hellaswag(cls, split: str = "val") -> "Dataset": ...

    def filter(self, category: str = None, difficulty: str = None) -> "Dataset": ...

    def split(self, train_ratio: float = 0.8) -> Tuple["Dataset", "Dataset"]: ...
```

## 最佳实践

### 1. Trials 数量

| 场景 | 推荐 Trials | 原因 |
|------|-----------|------|
| 快速验证 | 3 | 快速迭代 |
| 标准评估 | 5 | 平衡速度和稳定性 |
| 正式发布 | 10 | 高可信度结果 |

### 2. 统计显著性

- 始终报告 p-value 和置信区间
- 样本量 > 30 时使用 z-test 或 t-test
- 样本量 < 30 时使用 bootstrap

### 3. 公平比较

- 所有模型使用相同的 prompt
- 所有模型使用相同的 temperature (推荐 0.1)
- 控制 random seed 确保可重复性
- 考虑 cost 和 latency 作为辅助指标

### 4. 数据集质量

- 验证答案正确性
- 去除有歧义或错误的题目
- 按难度分层，确保各模型都有挑战
