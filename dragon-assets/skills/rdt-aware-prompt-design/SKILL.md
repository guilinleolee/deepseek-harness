---
license: UNKNOWN
github_repo: kyegomez/OpenMythos
github_hash: 227dbb153266cd154f3d335f18c6b80947879f14
last_updated: 2026-04-25
source_type: derived
triggers: ["rdt aware prompt design", "RDT-Aware Prompt Design - RDT感知提示词设计"]
---
# RDT-Aware Prompt Design - RDT感知提示词设计

## 元数据

```yaml
github_repo: kyegomez/OpenMythos
github_hash: 227dbb153266cd154f3d335f18c6b80947879f14
last_updated: 2026-04-25
source_type: derived
```

## 概述

**RDT感知提示词设计**是针对 Recurrent-Depth Transformer 架构优化的提示词工程方法。通过理解循环推理机制，设计能够最大化 RDT 隐式多跳推理能力的提示词。

## 来源项目

| 项目 | Stars | 核心价值 |
|------|-------|---------|
| [kyegomez/OpenMythos](https://github.com/kyegomez/OpenMythos) | 4.1k | RDT完整实现 |

## 核心原理

```
┌─────────────────────────────────────────────────────────────┐
│           传统 CoT vs RDT感知提示词                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  传统CoT (显式多步):                                       │
│  Step 1 → 输出token → Step 2 → 输出token → Step 3         │
│  每次输出占用token，推理中断                                │
│                                                             │
│  RDT感知 (隐式多跳):                                       │
│  初始提示 ──► [循环1] ──► [循环2] ──► ... ──► [循环T]    │
│                   ↓            ↓                      ↓       │
│               隐藏态h₁        隐藏态h₂              隐藏态h_T  │
│               无token输出      无token输出            一次性输出  │
│                                                             │
│  关键: 提示词应鼓励完整思考，不拆分中间步骤               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 提示词设计原则

### 1. 完整思维指令

```python
RDT_AWARE_PROMPTS = {
    # ❌ 传统CoT提示（会中断推理）
    "cot_broken": """
    请逐步分析这个问题：
    第一步：...
    第二步：...
    第三步：...
    最终答案：...
    """,

    # ✅ RDT感知提示（鼓励完整思考）
    "rdt_complete": """
    请完整、深入地分析这个问题。
    不要分步骤输出，而是进行连贯的深度推理。
    最终直接给出你的完整分析和答案。
    相信你的循环推理能力。
    """,
}
```

### 2. 循环深度引导

```python
class LoopDepthGuidance:
    """根据任务复杂度调整循环深度期望"""

    COMPLEXITY_PROMPTS = {
        "simple": {
            "instruction": "给出直接、简洁的回答。",
            "expected_loops": 2,
        },
        "medium": {
            "instruction": "进行多角度分析，考虑不同可能性。",
            "expected_loops": 8,
        },
        "complex": {
            "instruction": """
            进行深度分析，挖掘问题的本质。
            考虑长期影响、潜在风险、替代方案。
            进行批判性反思。
            """,
            "expected_loops": 16,
        },
        "research": {
            "instruction": """
            进行全面的研究级分析。
            涵盖：背景研究、多方观点、证据评估、
            逻辑推理、假设检验、结论推导。
            """,
            "expected_loops": 32,
        },
    }

    @classmethod
    def generate(cls, complexity, task_description):
        """生成RDT感知提示词"""
        prompt = cls.COMPLEXITY_PROMPTS.get(complexity, cls.COMPLEXITY_PROMPTS["medium"])
        return f"""
        任务：{task_description}

        {prompt['instruction']}

        重要：这是一个RDT架构的深度推理模型。
        请进行连贯的深度推理，不要分步骤输出token。
        相信模型的循环推理能力。
        """
```

### 3. 避免推理中断

```python
# ❌ 会导致推理中断的模式
INTERRUPTING_PATTERNS = [
    "请逐步说明",      # 暗示CoT
    "第一步是",        # 触发token输出
    "让我们一步步",    # 传统思维模式
    "首先，然后，接着", # 显式序列
]

# ✅ 支持隐式推理的模式
RDTFRIENDLY_PATTERNS = [
    "完整分析",
    "深入思考",
    "综合考虑",
    "给出最终判断",
    "直接回答",
]
```

## 天龙引擎集成

### 与09-02编排协调师协同

```python
# RDT感知编排流程
RDT_ORCHESTRATION_PROMPT = """
# 天龙引擎 × RDT 协同编排

## 阶段1: 问题分析 (00分析师)
- 评估任务复杂度 (simple/medium/complex/research)
- 确定所需循环深度

## 阶段2: 深度推理 (RDT层)
- 使用RDT感知提示词
- 不拆分中间步骤
- 让循环机制完成多跳推理

## 阶段3: 结果整合
- 一次性输出完整分析
- 如需补充，使用后续追问

## RDT感知提示词模板
任务类型 → 循环深度 → 提示词模板
"""

# 复杂度与循环深度映射
COMPLEXITY_LOOP_MAP = {
    "简单问答": (2, "直接回答"),
    "问题诊断": (8, "多角度分析"),
    "风险评估": (16, "深度+批判"),
    "战略分析": (32, "研究级"),
    "学术研究": (64, "极限深度"),
}
```

### 与10-01提示词架构师协同

```python
# RDT-Signature模板
class RDTSignature(dspy.Signature):
    """RDT架构感知的DSPy Signature"""

    task: str = dspy.InputField(
        desc="待解决的复杂任务",
        complexity_hint="simple/medium/complex/research"
    )

    depth: int = dspy.InputField(
        desc="推理深度(1-64)",
        default=8
    )

    analysis: str = dspy.OutputField(
        desc="完整深度分析，无分步骤输出"
    )

    conclusion: str = dspy.OutputField(
        desc="最终结论和建议"
    )
```

## 提示词模板库

### 问题诊断模板

```python
PROBLEM_DIAGNOSIS_TEMPLATE = """
# 问题诊断：{problem}

## 背景
{background}

## 任务
请进行深入的问题诊断分析。

## 分析维度
1. 表面症状识别
2. 根本原因挖掘
3. 相关因素分析
4. 影响范围评估
5. 解决方案推导

## 输出要求
- 进行连贯的深度推理
- 不要分步骤输出
- 最终给出完整诊断报告

## RDT推理指令
这是RDT架构的深度推理模型。
请充分利用其隐式多跳推理能力。
相信循环机制会完成完整分析。
```

### 战略分析模板

```python
STRATEGIC_ANALYSIS_TEMPLATE = """
# 战略分析：{topic}

## 背景
{context}

## 任务
进行全面的战略级分析。

## 分析框架
1. **宏观环境**: PESTLE分析
2. **行业格局**: 五力分析
3. **竞争态势**: 竞争对手深度评估
4. **内部能力**: 资源、能力的SWOT
5. **战略选项**: 多方案对比分析
6. **风险评估**: 关键风险识别
7. **实施路径**: 阶段性行动计划

## 输出要求
- 进行研究级的深度分析
- 涵盖所有关键维度
- 最终给出战略建议

## 重要提示
这是RDT架构的深度推理模型。
请进行完整的隐式多跳推理。
不拆分中间步骤，一次性深度思考后给出完整分析。
"""
```

### 批判性审查模板

```python
CRITICAL_REVIEW_TEMPLATE = """
# 批判性审查：{subject}

## 待审查内容
{content}

## 审查要求
进行严格的批判性分析。

## 审查维度
1. **假设检验**: 这些假设是否成立？
2. **证据评估**: 证据是否充分和可靠？
3. **逻辑检查**: 推理过程是否严密？
4. **反例思考**: 有哪些反例被忽略了？
5. **盲点识别**: 有哪些盲点和偏见？
6. **改进建议**: 如何增强论证？

## 输出要求
- 进行诚实的批判性评估
- 不要只说好听的话
- 最终给出建设性的改进建议

## 推理模式
这是RDT架构，支持深度批判性思考。
请进行诚实的、多维度的批判。
相信模型的反思和自我修正能力。
"""
```

## 与CoT对比

| 维度 | Chain-of-Thought | RDT感知提示词 |
|------|------------------|---------------|
| **推理方式** | 显式多步输出 | 隐式循环推理 |
| **Token消耗** | 高（每步输出） | 低（仅最终输出） |
| **推理深度** | 3-5步 | 1-64步自适应 |
| **中间步骤** | 可见但中断推理 | 不可见但更深入 |
| **适用场景** | 简单推理/教学 | 复杂分析/研究 |

## 天龙岗位调用

```bash
# 00分析师 - 复杂问题RDT推理
[@00分析师] 使用RDT感知提示词分析这个架构决策

# 01调研师 - 深度调研
[@01调研师] 使用RDT感知提示词进行多跳推理调研

# 09-02编排协调师 - RDT增强编排
[@09-02] 配置RDT感知编排流程

# 10-01提示词架构师 - RDT-Signature设计
[@10-01] 设计RDT架构的DSPy Signature
```

## 预期收益

| 指标 | 传统CoT | RDT感知提示 | 提升 |
|------|----------|------------|------|
| **推理深度** | 3-5步 | 1-64步自适应 | **+1200%** |
| **Token效率** | 1x | ~3x | **+200%** |
| **分析完整性** | 表面 | 深度 | **质的飞跃** |
| **提示词有效性** | 中等 | 优化 | **+50%** |
