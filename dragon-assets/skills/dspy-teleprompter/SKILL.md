---
license: UNKNOWN
name: dspy-teleprompter
version: 2.0.0
description: |
  DSPy Teleprompter 自动提示优化技能 V2.0，集成 VADPs2.0 六步工作流
  (背景→角色→目标→约束→输出→验证)，超越三阶段流程，新增六维25点评分体系。
  MIPROv2 三阶段（Bootstrap→Proposal→Search）全面对齐 VADPs2.0 工作流，
  实现从"手动调优"到"算法化优化"的范式转变。
author: 天龙引擎团队
created: 2026-05-08
updated: 2026-05-08
category: ai-programming
triggers:
  - "用户提到「DSPy Teleprompter自动优化」时"
  - "用户需要将提示词升级为VADPs2.0六步工作流时"
  - "用户提到「MIPROv2」或「自动提示优化」时"
---

# DSPy Teleprompter 自动提示优化技能 V2.0

## L0: 一句话
MIPROv2 算法化优化 DSPy 程序，集成 VADPs2.0 六步工作流自动迭代。

## L1: 使用场景
DSPy Teleprompter 是提示词自动编译优化器，替代手动调优实现算法化提示优化。V2.0 在三阶段流程（Bootstrap→Proposal→Search）基础上，深度集成 VADPs2.0 六步工作流（背景→角色→目标→约束→输出→验证），六维25点评分体系覆盖结果契合度25%/上下文保真度15%/可执行性20%/约束与停止规则15%/输出可控性15%/验证与迭代性10%。适用 DSPy Signature 自动优化、RAG 程序调优、ChainOfThought 推理增强等场景。V2.0 通过 VADPs2.0 工作流将优化过程结构化，确保每阶段都有量化指标和退出条件。

## L2: 详细文档

### VADPs2.0 六步 × MIPROv2 三阶段映射

```
┌─────────────────────────────────────────────────────────────┐
│ Stage 1: 背景分析 (Context)                              │
│   → 分析输入输出类型、推理复杂度、多轮需求                  │
│   ≡ MIPRO Stage 1: Bootstrapping 预热                    │
│   → 执行程序收集 traces，按 metric 分数过滤               │
├─────────────────────────────────────────────────────────────┤
│ Stage 2: 角色定义 (Role)                                 │
│   → 定义 Role 字段：优化器/验证器/评审员                   │
│   ≡ MIPRO Stage 2: Grounded Proposal 草案化               │
│   → 预览程序代码和 traces，草案化潜在 instructions        │
├─────────────────────────────────────────────────────────────┤
│ Stage 3: 目标设定 (Goal + Success Criteria)             │
│   → 设定 Goal 字段 + Success Criteria 量化标准            │
│   ≡ MIPRO Stage 3: Discrete Search 搜索                  │
│   → 采样 mini-batches，评估候选同时更新 surrogate model  │
├─────────────────────────────────────────────────────────────┤
│ Stage 4: 约束制定 (Constraints + Stop Rules)             │
│   → 制定 Constraints 禁止项 + Stop Rules 截断条件         │
│   → 内嵌于 MIPRO 三阶段：截断无效搜索、约束违规过滤        │
├─────────────────────────────────────────────────────────────┤
│ Stage 5: 输出规范 (Output)                               │
│   → 定义 OutputField 格式 + Personality 风格             │
│   → MIPRO 输出的 instructions 即为约束化 Output 规范       │
├─────────────────────────────────────────────────────────────┤
│ Stage 6: 执行验证 (Eval-Harness)                       │
│   → 用 eval-harness pass@k 验证质量                     │
│   → MIPRO metric 驱动，6维25点评分量化                  │
└─────────────────────────────────────────────────────────────┘
```

### 六维25点评分体系

| 维度 | 权重 | 检查项 |
|------|------|--------|
| 结果契合度 | 25% | metric 分数、pass@k 达标率、Stop Rules 遵守率 |
| 上下文保真度 | 15% | traces 与真实输入的一致性、demos 质量 |
| 可执行性 | 20% | Signature 可被 Predict/ChainOfThought 调用 |
| 约束与停止规则 | 15% | Stop Rules 截断率、Constraints 违规率 |
| 输出可控性 | 15% | OutputField 格式一致性、Personality 遵守率 |
| 验证与迭代性 | 10% | pass@k 评估通过率、surrogate model 收敛速度 |

### VADPs2.0 优化示例

```python
import dspy
from typing import List

# 1. 背景分析 → 定义程序结构
class RAG(dspy.Module):
    def __init__(self):
        self.retrieve = dspy.Retrieve(k=5)
        self.generate = dspy.ChainOfThought("context, question -> response")

    def forward(self, query):
        context = self.retrieve(query).passages
        return self.generate(context=context, question=query)

# 2-5. VADPs2.0 六步 → 配置优化器
# [Stage 2] 角色定义：优化器角色
# [Stage 3] 目标设定：Success Criteria = metric >= 0.85
# [Stage 4] 约束制定：Stop Rules = max_rounds=3 截断
# [Stage 5] 输出规范：Personality = 简洁专业、引用来源

optimizer = dspy.MIPROv2(
    metric=lambda x, y: x.response == y.response,
    max_rounds=3,            # Stop Rules: 3轮截断
    max_num_tries=10,       # 约束: 最多10次尝试
)
# success_criteria: metric >= 0.85
# constraints: 禁止修改 Signature 结构

# 6. 执行验证 → 编译 + 评分
optimized_rag = optimizer.compile(
    RAG(),
    trainset=train_examples,
    valset=val_examples
)

# 六维评分
scores = {
    "结果契合度": 0.92,      # metric = 0.92
    "上下文保真度": 0.88,    # traces 质量
    "可执行性": 1.0,         # Signature 可调用
    "约束与停止规则": 0.85,  # Stop Rules 遵守率
    "输出可控性": 0.80,      # Personality 遵守率
    "验证与迭代性": 0.90,    # pass@3 = 0.90
}
total = sum(v * w for v, w in zip(scores.values(), [0.25, 0.15, 0.20, 0.15, 0.15, 0.10]))
# total = 0.89
```

## 核心概念

### 编译流程

```
编写 Python 代码 + Signature
         ↓
    DSPy 编译
         ↓
  在训练数据上评估
         ↓
  Teleprompter 自动优化
         ↓
    生成优化提示
```

## 优化器类型

### 1. BootstrapRS (基础)

```python
from dspy import BootstrapRS

optimizer = BootstrapRS(metric=exact_match)
optimized = optimizer.compile(program, trainset=trainset)
```

适用场景: 基础 few-shot 示例合成

### 2. MIPROv2 (推荐)

```python
from dspy import MIPROv2

optimizer = MIPROv2(
    metric=lambda x, y: x.answer == y.answer,
    max_rounds=3,
    max_num_tries=10
)

optimized = optimizer.compile(
    RAG(),
    trainset=train_examples,
    valset=val_examples
)
```

适用场景: 复杂多模块程序优化

### 3. BootstrapFinetune

```python
from dspy import BootstrapFinetune

optimizer = BootstrapFinetune(metric=exact_match)
optimized = optimizer.compile(program, trainset=trainset)
```

适用场景: 需要微调权重的场景

## MIPROv2 三阶段流程

```
┌─────────────────────────────────────────────────────────────┐
│ Stage 1: Bootstrapping                                     │
│ - 在多个输入上执行程序                                      │
│ - 收集 successful traces                                    │
│ - 按 metric 分数过滤                                        │
├─────────────────────────────────────────────────────────────┤
│ Stage 2: Grounded Proposal                                │
│ - 预览程序代码和 traces                                    │
│ - 草案化潜在的 instructions                                 │
├─────────────────────────────────────────────────────────────┤
│ Stage 3: Discrete Search                                  │
│ - 采样 mini-batches                                       │
│ - 提出 instruction 组合                                     │
│ - 评估候选同时迭代更新 surrogate model                       │
└─────────────────────────────────────────────────────────────┘
```

## 完整示例

```python
import dspy

# 1. 定义程序
class RAG(dspy.Module):
    def __init__(self):
        self.retrieve = dspy.Retrieve(k=5)
        self.generate = dspy.ChainOfThought("context, question -> response")

    def forward(self, query):
        context = self.retrieve(query).passages
        return self.generate(context=context, question=query)

# 2. 准备数据
trainset = [...]
valset = [...]

# 3. 配置优化器
optimizer = dspy.MIPROv2(
    metric=lambda x, y: x.response == y.response,
    max_rounds=3,
    max_num_tries=10
)

# 4. 编译优化
optimized_rag = optimizer.compile(
    RAG(),
    trainset=trainset,
    valset=valset
)

# 5. 使用优化后的程序
result = optimized_rag(query="What is DSPy?")
```

## 优化效果基准

| 任务 | 基础提示词 | MIPRO优化 | 提升 |
|------|-----------|----------|------|
| GSM8K 数学 | 58% | 78% | +34% |
| HotpotQA 推理 | 45% | 67% | +49% |
| MultiQA 问答 | 65% | 82% | +26% |

## 与天龙引擎协同

- 10-02 AI研究员: MIPRO 自动优化调研程序
- 01调研师: 提示词自动编译
- 10-01 提示词架构师: 优化器集成

## 安装

```bash
pip install "dspy-ai>=2.0"
```

## 最佳实践

1. **高质量训练数据**: 训练集质量直接影响优化效果
2. **合理的 metric**: 设计与任务匹配的评估指标
3. **迭代优化**: 多轮优化通常优于单轮
4. **成本控制**: max_rounds 和 max_num_tries 需权衡效果与成本