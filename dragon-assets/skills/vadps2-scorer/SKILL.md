---
license: UNKNOWN
name: vadps2-scorer
version: 1.0.0
description: |
  VADPs2.0 六维25点评分体系专用评分器，量化评估提示词/Agent/Pipeline质量。
  结果契合度25%/上下文保真度15%/可执行性20%/约束与停止规则15%/输出可控性15%/验证与迭代性10%。
author: 天龙引擎团队
created: 2026-05-08
updated: 2026-05-08
category: development
triggers:
  - "用户提到「VADPs2.0 六维评分」或「25点评分」时"
  - "用户需要量化评估提示词质量时"
  - "用户提到「结果契合度/上下文保真度/可执行性/约束与停止规则/输出可控性/验证与迭代性」时"
---

# VADPs2.0 六维25点评分体系 V1.0

## L0: 一句话
六维25点量化评分，评估提示词/Agent/Pipeline质量，综合分≥0.85为合格。

## L1: 使用场景
VADPs2.0 六维25点评分体系是量化质量门控工具，通过结果契合度25%/上下文保真度15%/可执行性20%/约束与停止规则15%/输出可控性15%/验证与迭代性10%六维25点评估，实现提示词/Agent/Pipeline的量化打分。综合评分≥0.85为合格。适用DSPy Signature评估、MIPROv2优化效果验证、eval-harness报告生成等场景。与vadps2-workflow六步工作流完整集成，每阶段输出量化评分。

## L2: 详细文档

### 六维评分维度

| 维度 | 权重 | 检查项 | 分值范围 |
|------|------|--------|----------|
| 结果契合度 | 25% | Success Criteria 达成率、pass@k 达标率 | 0-25 |
| 上下文保真度 | 15% | 输入输出一致性、demos 质量、traces 与真实分布的一致性 | 0-15 |
| 可执行性 | 20% | 端到端可运行、Signature 可被 Predict/ChainOfThought 调用 | 0-20 |
| 约束与停止规则 | 15% | Stop Rules 截断率、Constraints 违规率 | 0-15 |
| 输出可控性 | 15% | OutputField 格式一致性、Personality 遵守率 | 0-15 |
| 验证与迭代性 | 10% | pass@k 评估通过率、历史基线对比、surrogate model 收敛速度 | 0-10 |
| **总计** | **100%** | — | **0-25** |

### 评分计算公式

```python
# 综合评分 = Σ(各维度得分 × 权重)
# 各维度得分 = 实际分值 ÷ 权重满分

total_score = (
    result_fit_score * 0.25 +      # 结果契合度  (0-1)
    context_fidelity_score * 0.15 + # 上下文保真度 (0-1)
    executability_score * 0.20 +     # 可执行性     (0-1)
    constraints_score * 0.15 +       # 约束与停止规则 (0-1)
    output_controllability_score * 0.15 +  # 输出可控性 (0-1)
    validation_iteration_score * 0.10   # 验证与迭代性 (0-1)
)

# 合格标准: total_score >= 0.85
```

### 各维度详细评分标准

#### 1. 结果契合度 (25%)

| 分值 | 等级 | 标准 |
|------|------|------|
| 0.90-1.00 | A | pass@3 > 90%，远超 Success Criteria |
| 0.70-0.89 | B | pass@3 ≥ 90%，达到 Success Criteria |
| 0.50-0.69 | C | pass@1 ≥ 70%，部分达标 |
| 0.00-0.49 | D | 未达到基本标准 |

**检查方法**:
- 计算 pass@1 / pass@3 / pass@5 指标
- 对比 Success Criteria 阈值
- 记录达标/未达标具体原因

#### 2. 上下文保真度 (15%)

| 分值 | 等级 | 标准 |
|------|------|------|
| 0.90-1.00 | A | traces 与真实输入完全一致，demos 质量优秀 |
| 0.70-0.89 | B | traces 质量良好，无明显失真 |
| 0.50-0.69 | C | 存在轻微失真，需要优化 |
| 0.00-0.49 | D | 上下文严重失真，影响输出质量 |

**检查方法**:
- 抽样验证 traces 分布与真实数据的一致性
- 评估 demos 质量（相关性、多样性、代表性）
- 检查 InputField desc 描述准确性

#### 3. 可执行性 (20%)

| 分值 | 等级 | 标准 |
|------|------|------|
| 0.90-1.00 | A | Signature 可被 Predict/ChainOfThought 直接调用 |
| 0.70-0.89 | B | 需轻微调整后可运行 |
| 0.50-0.69 | C | 存在类型错误或接口不匹配 |
| 0.00-0.49 | D | 无法正常运行 |

**检查方法**:
- 执行 `dspy.Predict(Signature)` 测试调用
- 检查字段类型注解是否正确
- 验证输入输出字段是否完整

#### 4. 约束与停止规则 (15%)

| 分值 | 等级 | 标准 |
|------|------|------|
| 0.90-1.00 | A | Stop Rules 截断率 < 5%，无 Constraints 违规 |
| 0.70-0.89 | B | 截断率 < 10%，违规率 < 5% |
| 0.50-0.69 | C | 截断率 < 20%，违规率 < 10% |
| 0.00-0.49 | D | 严重违反 Constraints 或 Stop Rules |

**检查方法**:
- 统计 Stop Rules 触发次数和截断率
- 检查 Constraints 违规案例
- 验证停止规则逻辑正确性

#### 5. 输出可控性 (15%)

| 分值 | 等级 | 标准 |
|------|------|------|
| 0.90-1.00 | A | OutputField 格式一致率 > 95%，Personality 完全遵守 |
| 0.70-0.89 | B | 格式一致率 > 85%，Personality 基本遵守 |
| 0.50-0.69 | C | 格式一致率 > 70%，存在格式漂移 |
| 0.00-0.49 | D | 输出格式混乱，无法解析 |

**检查方法**:
- 统计 OutputField 格式一致率
- 评估 Personality 遵守率
- 检查输出稳定性（多次运行一致性）

#### 6. 验证与迭代性 (10%)

| 分值 | 等级 | 标准 |
|------|------|------|
| 0.90-1.00 | A | pass@k 稳定达标，迭代收敛速度快 |
| 0.70-0.89 | B | pass@k 达标，需3轮以内迭代 |
| 0.50-0.69 | C | 迭代5轮以内可达标 |
| 0.00-0.49 | D | 迭代5轮以上仍无法达标 |

**检查方法**:
- 追踪 pass@k 指标历史趋势
- 记录迭代轮数与收敛速度
- 对比历史基线

### 评分报告模板

```markdown
## VADPs2.0 六维评分报告

### 综合评分
| 维度 | 权重 | 得分 | 等级 |
|------|------|------|------|
| 结果契合度 | 25% | X.XX | A/B/C/D |
| 上下文保真度 | 15% | X.XX | A/B/C/D |
| 可执行性 | 20% | X.XX | A/B/C/D |
| 约束与停止规则 | 15% | X.XX | A/B/C/D |
| 输出可控性 | 15% | X.XX | A/B/C/D |
| 验证与迭代性 | 10% | X.XX | A/B/C/D |
| **综合评分** | 100% | **X.XX** | A/B/C/D |

### 详细分析

#### 1. 结果契合度 (X.XX/25)
- pass@1: XX%
- pass@3: XX%
- pass@5: XX%
- Success Criteria 达标率: XX%
- 主要问题: [描述]

#### 2. 上下文保真度 (X.XX/15)
- traces 质量评分: X.XX
- demos 质量评分: X.XX
- 主要问题: [描述]

#### 3. 可执行性 (X.XX/20)
- Signature 调用测试: 通过/失败
- 类型错误数: N
- 主要问题: [描述]

#### 4. 约束与停止规则 (X.XX/15)
- Stop Rules 截断率: XX%
- Constraints 违规率: XX%
- 主要问题: [描述]

#### 5. 输出可控性 (X.XX/15)
- OutputField 格式一致率: XX%
- Personality 遵守率: XX%
- 主要问题: [描述]

#### 6. 验证与迭代性 (X.XX/10)
- pass@k 稳定性: [稳定/波动/退化]
- 迭代轮数: N
- surrogate model 收敛速度: [快/正常/慢]
- 主要问题: [描述]

### 迭代建议
1. [优先级P0]: [建议]
2. [优先级P1]: [建议]
3. [优先级P2]: [建议]

### 结论
- 综合评分: X.XX
- 合格标准 (≥0.85): [通过/未通过]
- 状态: [READY FOR REVIEW / 需要迭代优化]
```

### Python 使用示例

```python
from vadps2_scorer import VADPs2Scorer

# 初始化评分器
scorer = VADPs2Scorer()

# 1. 结果契合度评估
result_fit = scorer.evaluate_result_fit(
    predictions=[...],  # 模型预测结果
    ground_truth=[...],  # 标准答案
    success_criteria={"pass@3": 0.90}  # Success Criteria
)

# 2. 上下文保真度评估
context_fidelity = scorer.evaluate_context_fidelity(
    traces=[...],  # 执行 traces
    real_data=[...],  # 真实数据分布
    demos_quality_score=0.85  # demos 质量评分
)

# 3. 可执行性评估
executability = scorer.evaluate_executability(
    signature=QA,  # DSPy Signature 类
    test_inputs=[...]  # 测试输入
)

# 4. 约束与停止规则评估
constraints = scorer.evaluate_constraints(
    execution_logs=[...],  # 执行日志
    constraints=["禁止编造事实", "禁止超出上下文"],
    stop_rules={"timeout": 30, "max_cost": 1.0}
)

# 5. 输出可控性评估
output_control = scorer.evaluate_output_controllability(
    outputs=[...],  # 模型输出
    output_fields={"answer": "string", "confidence": "float"},
    personality="简洁专业，引用来源"
)

# 6. 验证与迭代性评估
validation = scorer.evaluate_validation_iteration(
    pass_at_k_history=[...],  # pass@k 历史记录
    baseline={"pass@3": 0.85},  # 历史基线
    iterations=3  # 迭代轮数
)

# 生成综合评分报告
report = scorer.generate_report(
    result_fit=result_fit,
    context_fidelity=context_fidelity,
    executability=executability,
    constraints=constraints,
    output_control=output_control,
    validation=validation
)

print(f"综合评分: {report.total_score:.2f}")
print(f"合格标准 (≥0.85): {'通过' if report.total_score >= 0.85 else '未通过'}")
```

### 与 VADPs2.0 六步工作流集成

```
┌─────────────────────────────────────────────────────────────┐
│ Stage 1: 背景分析 → 评估上下文保真度基线                │
│ Stage 2: 角色定义 → 评估可执行性基线                    │
│ Stage 3: 目标设定 → 设定结果契合度目标 (≥0.85)        │
│ Stage 4: 约束制定 → 评估约束与停止规则                  │
│ Stage 5: 输出规范 → 评估输出可控性                      │
│ Stage 6: 执行验证 → 六维综合评分                        │
└─────────────────────────────────────────────────────────────┘
```

### 与天龙引擎协同

- 10-01 提示词架构师: Signature VADPs2.0 设计 + 六维评分验证
- 10-02 AI研究员: MIPROv2 优化效果六维评估
- 04 验证师: eval-harness 集成六维评分报告
- vadps2-workflow: 六步工作流每阶段输出量化评分
- eval-harness: pass@k 指标作为结果契合度核心依据

### 最佳实践

1. **量化门控**: 综合评分 < 0.85 必须迭代优化，禁止进入下一阶段
2. **维度平衡**: 任何单一维度得分 < 0.5 需优先修复
3. **历史基线**: 每次评估必须对比历史基线，记录退化原因
4. **迭代追踪**: 记录每次优化的维度提升，建立优化路径图
5. **阈值调整**: 根据场景调整阈值（高可靠性场景: ≥0.90）
