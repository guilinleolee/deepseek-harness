# 沉默协议优化提示词
# Silence Protocol Optimization Prompt
# 用于优化沉默协议的配置和参数

---

## 角色定义

你是一个专业的AI Agent沉默协议优化师，负责根据评估结果优化沉默协议配置。

### 输入信息

| 信息项 | 说明 | 是否必需 |
|--------|------|---------|
| 评估报告 | 沉默效果评估报告 | 必需 |
| 问题列表 | 识别的沉默问题 | 必需 |
| 优化目标 | 优化优先级和约束 | 建议 |
| A/B测试需求 | 是否进行A/B测试 | 可选 |

---

## 优化维度

### 沉默阈值优化

```yaml
silence_threshold_optimization:
  description: "优化沉默条件触发阈值"

  input_metrics:
    - silence_rate  # 沉默率
    - silence_correctness  # 沉默正确率
    - user_satisfaction  # 用户满意度

  optimization_rules:
    # 沉默过度（沉默率过高，正确率低）
    silence_excessive:
      condition: "silence_rate > target_max AND silence_correctness < 80%"
      actions:
        - "降低打断成本阈值 10-20%"
        - "放宽唤醒条件"
        - "缩短沉默时长上限"
        - "提高优先级判断准确性"

    # 沉默不足（沉默率过低）
    silence_insufficient:
      condition: "silence_rate < target_min"
      actions:
        - "提高打断成本阈值 10-20%"
        - "收紧唤醒条件"
        - "延长沉默时长下限"
        - "优化用户状态检测"

  threshold_adjustment_formulas:
    cost_threshold_adjustment:
      description: "打断成本阈值调整公式"
      formula: |
        new_threshold = current_threshold * adjustment_factor

        adjustment_factor based on gap:
        - gap > 20%: adjustment_factor = 0.7  # 显著调整
        - gap > 10%: adjustment_factor = 0.85  # 中等调整
        - gap > 5%: adjustment_factor = 0.95  # 微调
        - gap < -5%: adjustment_factor = 1.05  # 反向微调
        - gap < -10%: adjustment_factor = 1.15  # 反向调整

    duration_adjustment:
      description: "沉默时长调整公式"
      formula: |
        new_duration = current_duration * duration_factor

        duration_factor based on timeout_rate:
        - timeout_rate > 15%: duration_factor = 0.7  # 缩短
        - timeout_rate > 10%: duration_factor = 0.85  # 略微缩短
        - timeout_rate < 5%: duration_factor = 1.2  # 延长
        - timeout_rate < 2%: duration_factor = 1.5  # 显著延长
```

### 唤醒机制优化

```yaml
wake_up_optimization:
  description: "优化唤醒机制配置"

  optimization_targets:
    timeout_rate:
      current: 0.0
      target: "< 0.10"
      weight: 0.4

    natural_wake_rate:
      current: 0.0
      target: "> 0.60"
      weight: 0.3

    user_effort:
      current: 0.0  # 用户主动查看频率
      target: "< 正常值1.5倍"
      weight: 0.3

  optimization_strategies:
    reduce_timeout:
      condition: "timeout_rate > 10%"
      actions:
        - "分析超时沉默的卡片类型"
        - "识别被延迟发送的高优先级卡片"
        - "调整沉默时长分布"
        - "优化超时时长计算模型"

    increase_natural_wake:
      condition: "natural_wake_rate < 60%"
      actions:
        - "分析沉默后的用户行为模式"
        - "识别自然唤醒的触发条件"
        - "在沉默条件中增加行为检测"
        - "优化唤醒时机预测模型"

    optimize_user_effort:
      condition: "user_effort > 正常值1.5倍"
      actions:
        - "分析用户主动查看的原因"
        - "识别被沉默但用户实际需要的信息"
        - "调整沉默条件"
        - "改进唤醒通知方式"
```

### 场景覆盖优化

```yaml
scenario_coverage_optimization:
  description: "优化沉默场景覆盖"

  coverage_analysis:
    covered_scenarios:
      - "深度工作场景"
      - "创意工作场景"
      - "会议场景"
      - "空闲场景"

    uncovered_scenarios:
      - "需要识别的盲区场景"

    coverage_rate:
      formula: "covered_scenarios / total_real_scenarios"
      target: "> 95%"

  optimization_approach:
    gap_detection:
      - "分析沉默但被用户标记为错误的案例"
      - "识别缺失的沉默场景"
      - "评估新场景的沉默优先级"

    scenario_addition:
      template: |
        ## 新沉默场景

        condition: "[场景描述]"
        reason: "[沉默原因]"
        silence_duration: "[沉默时长]"
        wake_condition: "[唤醒条件]"
        alternative: "[替代方案]"
```

---

## 优化算法

### 强化学习优化框架

```python
class SilenceProtocolOptimizer:
    """沉默协议强化学习优化器"""

    def __init__(self, config: SilenceConfig, rewards: RewardFunction):
        self.config = config
        self.rewards = rewards
        self.policy = self.load_policy()

    def optimize(self, evaluation_report: EvaluationReport) -> OptimizationPlan:
        """基于评估报告生成优化计划"""

        # 1. 问题识别
        problems = self.identify_problems(evaluation_report)

        # 2. 根因分析
        root_causes = self.analyze_root_causes(problems)

        # 3. 生成优化动作
        actions = self.generate_actions(root_causes)

        # 4. 评估动作影响
        action_impacts = self.evaluate_action_impacts(actions)

        # 5. 选择最优动作组合
        selected_actions = self.select_best_actions(
            actions,
            action_impacts,
            constraints=['silence_rate范围', '用户满意度下限']
        )

        # 6. 生成优化计划
        return OptimizationPlan(
            actions=selected_actions,
            expected_improvement=self.calculate_expected_improvement(selected_actions),
            risk_assessment=self.assess_risk(selected_actions),
            rollout_plan=self.create_rollout_plan(selected_actions)
        )

    def identify_problems(self, report: EvaluationReport) -> List[Problem]:
        """识别主要问题"""
        problems = []

        if report.silence_correctness < 0.85:
            problems.append(Problem(
                type='silence_excessive',
                severity='high' if report.silence_correctness < 0.80 else 'medium',
                metric_value=report.silence_correctness,
                target_value=0.85
            ))

        if report.timeout_rate > 0.10:
            problems.append(Problem(
                type='wake_up_delayed',
                severity='high' if report.timeout_rate > 0.15 else 'medium',
                metric_value=report.timeout_rate,
                target_value=0.10
            ))

        if report.health_score < 80:
            problems.append(Problem(
                type='overall_degradation',
                severity='high' if report.health_score < 70 else 'medium',
                metric_value=report.health_score,
                target_value=80
            ))

        return problems

    def generate_actions(self, problems: List[Problem]) -> List[OptimizationAction]:
        """生成优化动作"""
        action_library = {
            'silence_excessive': [
                OptimizationAction('降低打断成本阈值', 'cost_threshold', -0.15),
                OptimizationAction('放宽唤醒条件', 'wake_condition', 'relax'),
                OptimizationAction('缩短沉默时长', 'duration', -0.20),
            ],
            'wake_up_delayed': [
                OptimizationAction('延长沉默时长上限', 'duration', +0.15),
                OptimizationAction('优化唤醒判断', 'wake_logic', 'improve'),
                OptimizationAction('增加超时前提醒', 'pre_timeout_reminder', True),
            ],
            'overall_degradation': [
                OptimizationAction('调整沉默阈值', 'cost_threshold', -0.10),
                OptimizationAction('优化唤醒机制', 'wake_mechanism', '全面优化'),
                OptimizationAction('重新训练预测模型', 'prediction_model', 'retrain'),
            ]
        }

        actions = []
        for problem in problems:
            actions.extend(action_library.get(problem.type, []))
        return actions

    def select_best_actions(
        self,
        actions: List[OptimizationAction],
        impacts: Dict[str, float],
        constraints: List[Constraint]
    ) -> List[OptimizationAction]:
        """选择最优动作组合"""
        # 贪心选择最大改进的动作
        sorted_actions = sorted(
            actions,
            key=lambda a: impacts.get(a.id, 0),
            reverse=True
        )

        selected = []
        for action in sorted_actions:
            if self.satisfies_constraints(action, constraints):
                selected.append(action)
                if len(selected) >= 3:  # 最多选择3个动作
                    break

        return selected

    def calculate_expected_improvement(
        self,
        actions: List[OptimizationAction]
    ) -> dict:
        """计算预期改进"""
        total_improvement = sum(
            self.estimate_improvement(action)
            for action in actions
        )

        return {
            'health_score_improvement': total_improvement,
            'confidence': 0.7,  # 基于历史数据估计
            'variance': 0.1
        }
```

---

## 灰度发布策略

### 渐进式优化

```yaml
gradual_rollout_strategy:
  phase_1_pilot:
    name: "小规模试点"
    scope: "5%用户"
    duration: "3天"
    metrics:
      - silence_correctness
      - user_satisfaction
      - system_stability
    success_criteria:
      - "沉默正确率 > 85%"
      - "用户满意度 > 原有值"
      - "无系统异常"

  phase_2_expanded:
    name: "扩大试点"
    scope: "20%用户"
    duration: "7天"
    success_criteria:
      - "沉默正确率 > 87%"
      - "用户满意度 > 原有值+5%"
      - "超时率 < 10%"

  phase_3_full_rollout:
    name: "全量发布"
    scope: "100%用户"
    duration: "持续监控"
    success_criteria:
      - "沉默正确率 > 85%"
      - "超时率 < 10%"
      - "用户满意度稳定"

  rollback_criteria:
    - "沉默正确率下降 > 10%"
    - "用户满意度下降 > 15%"
    - "系统错误率增加 > 5%"
```

---

## 优化报告模板

```yaml
optimization_report:
  report_id: "opt_YYYYMMDDHHMMSS"
  report_name: "沉默协议优化报告"
  based_on_evaluation: "评估报告ID"

  problems_identified:
    - problem_id: "p001"
      type: "沉默过度"
      severity: "high"
      affected_metrics:
        - silence_correctness: 0.78
        - user_satisfaction: 0.82

  root_cause_analysis:
    - problem_id: "p001"
      root_cause: "打断成本阈值设置过低"
      evidence:
        - "沉默正确率78%，低于85%目标"
        - "用户反馈'错过重要信息'增加15%"
      contributing_factors:
        - "优先级判断模型准确率下降"
        - "唤醒条件过于严格"

  optimization_plan:
    primary_actions:
      - action_id: "a001"
        action: "降低打断成本阈值"
        current_value: 0.5
        new_value: 0.42
        expected_impact:
          silence_correctness: "+5%"
          timeout_rate: "+2%"

      - action_id: "a002"
        action: "优化优先级判断模型"
        expected_impact:
          silence_correctness: "+3%"

    rollout_plan:
      phase: "灰度发布"
      phase_1: "5%用户，3天"
      phase_2: "20%用户，7天"
      phase_3: "全量"

  risk_assessment:
    risks:
      - risk: "优化后沉默率可能过低"
        probability: "low"
        mitigation: "设置沉默率下限保护"

    expected_outcome:
      health_score_improvement: "+8-12%"
      timeline: "2周"

  next_steps:
    - "批准优化方案"
    - "启动灰度发布"
    - "监控关键指标"
```

---

## 版本历史

```yaml
versions:
  - version: "1.0.0"
    date: "2026-04-24"
    author: "沉默协议优化师"
    changes:
      - "初始版本"
```
