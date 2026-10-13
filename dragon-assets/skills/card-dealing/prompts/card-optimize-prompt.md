# 发牌协议优化提示词
# Card Protocol Optimization Prompt
# 用于优化发牌协议的配置和参数

---

## 角色定义

你是一个专业的AI Agent发牌协议优化师，负责根据评估结果优化发牌协议配置。

### 输入信息

| 信息项 | 说明 | 是否必需 |
|--------|------|---------|
| 评估报告 | 发牌效果评估报告 | 必需 |
| 问题列表 | 识别的发牌问题 | 必需 |
| 优化目标 | 优化优先级和约束 | 建议 |
| A/B测试需求 | 是否进行A/B测试 | 可选 |

---

## 优化维度

### 发牌阈值优化

```yaml
card_threshold_optimization:
  description: "优化发牌触发阈值"

  input_metrics:
    - confirmation_rate  # 确认率
    - ignore_rate       # 忽略率
    - false_positive_rate  # 误发率
    - user_satisfaction # 用户满意度

  optimization_rules:
    # 误发过多（确认率低，忽略率高）
    false_positive_excessive:
      condition: "confirmation_rate < 0.6 AND ignore_rate > 0.3"
      actions:
        - "提高不确定性降低阈值 0.3 → 0.4"
        - "提高行动清晰度阈值 0.6 → 0.7"
        - "增加质量门控检查项"

    # 漏发过多（用户主动查询多）
    false_negative_excessive:
      condition: "user_initiated_queries > baseline * 1.5"
      actions:
        - "降低不确定性降低阈值 0.3 → 0.25"
        - "放宽沉默协议限制"
        - "增加试探性发牌"

    # 满意度低
    low_satisfaction:
      condition: "satisfaction_score < 3.0"
      actions:
        - "分析打扰感来源"
        - "调整发牌时机策略"
        - "优化卡片内容质量"

  threshold_adjustment_formulas:
    uncertainty_threshold:
      description: "不确定性降低阈值调整"
      formula: |
        new_threshold = current_threshold * adjustment_factor

        adjustment based on gap:
        - gap > 15%: adjustment_factor = 1.2  # 放宽
        - gap > 5%: adjustment_factor = 1.1   # 轻微放宽
        - gap > 0%: adjustment_factor = 1.05   # 微调
        - gap < 0%: adjustment_factor = 0.95    # 微调收紧
        - gap < -5%: adjustment_factor = 0.9   # 轻微收紧
        - gap < -15%: adjustment_factor = 0.8   # 收紧

    clarity_threshold:
      description: "行动清晰度阈值调整"
      formula: |
        same as uncertainty_threshold formula

    frequency_adjustment:
      description: "发牌频率调整"
      formula: |
        if current_rate > 5:
          new_max = current_max - 1
        elif current_rate > 3:
          new_max = current_max
        else:
          new_max = current_max + 0.5  # 允许略有提升
```

### 发牌时机优化

```yaml
timing_optimization:
  description: "优化发牌时机策略"

  optimization_targets:
    interruption_rate:
      current: 0.0
      target: "< 0.05"
      weight: 0.4

    natural_break_accuracy:
      current: 0.0
      target: "> 0.85"
      weight: 0.3

    user_state_match:
      current: 0.0
      target: "> 0.90"
      weight: 0.3

  optimization_strategies:
    reduce_interruption:
      condition: "interruption_rate > 0.05"
      actions:
        - "加强心流状态检测"
        - "增加发牌前延迟检查"
        - "优化沉默协议协同逻辑"

    improve_natural_break:
      condition: "natural_break_accuracy < 0.85"
      actions:
        - "识别更多自然断点场景"
        - "分析用户自然行为模式"
        - "建立断点预测模型"

    match_user_state:
      condition: "user_state_match < 0.90"
      actions:
        - "细分用户状态分类"
        - "增加状态检测维度"
        - "建立状态到卡片类型映射"
```

### 卡片类型分布优化

```yaml
card_type_distribution_optimization:
  description: "优化各类型卡片的分布比例"

  target_distribution:
    information_card: "30-40%"
    confirmation_card: "20-30%"
    recommendation_card: "15-25%"
    action_card: "10-15%"
    warning_card: "5-10%"

  optimization_approach:
    over_distribution:
      condition: "card_type_ratio > target_max"
      actions:
        - "收紧该类型触发条件"
        - "检查是否存在误触发"
        - "调整质量门控对该类型的特殊规则"

    under_distribution:
      condition: "card_type_ratio < target_min"
      actions:
        - "放宽该类型触发条件"
        - "检查是否存在漏识别场景"
        - "优化该类型的优先级计算"

  priority_adjustment:
    description: "根据分布调整优先级权重"
    formula: |
      # 如果某类型过多，提高其他类型的优先级
      for card_type in all_types:
        if card_type_ratio > target_max:
          priority_weight[other_types] *= 1.1
        elif card_type_ratio < target_min:
          priority_weight[card_type] *= 1.15
```

---

## 优化算法

### 强化学习优化框架

```python
class CardProtocolOptimizer:
    """发牌协议强化学习优化器"""

    def __init__(self, config: CardProtocolConfig, rewards: RewardFunction):
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
            constraints=['confirmation_rate范围', 'frequency_limit']
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

        if report.confirmation_rate < 0.6:
            problems.append(Problem(
                type='false_positive',
                severity='high' if report.confirmation_rate < 0.4 else 'medium',
                metric_value=report.confirmation_rate,
                target_value=0.8
            ))

        if report.flow_interruption_rate > 0.05:
            problems.append(Problem(
                type='unwanted_interruption',
                severity='high' if report.flow_interruption_rate > 0.1 else 'medium',
                metric_value=report.flow_interruption_rate,
                target_value=0.05
            ))

        if report.action_completion_rate < 0.6:
            problems.append(Problem(
                type='low_action_completion',
                severity='high' if report.action_completion_rate < 0.4 else 'medium',
                metric_value=report.action_completion_rate,
                target_value=0.7
            ))

        if report.satisfaction_score < 3.0:
            problems.append(Problem(
                type='low_satisfaction',
                severity='high' if report.satisfaction_score < 2.5 else 'medium',
                metric_value=report.satisfaction_score,
                target_value=4.0
            ))

        return problems

    def generate_actions(self, problems: List[Problem]) -> List[OptimizationAction]:
        """生成优化动作"""
        action_library = {
            'false_positive': [
                OptimizationAction('提高不确定性阈值', 'uncertainty_threshold', +0.1),
                OptimizationAction('提高清晰度阈值', 'clarity_threshold', +0.1),
                OptimizationAction('增加质量门控', 'quality_gates', 'add_checks'),
            ],
            'unwanted_interruption': [
                OptimizationAction('加强心流检测', 'flow_detection', 'improve'),
                OptimizationAction('增加发牌前延迟', 'pre_deal_delay', +5),
                OptimizationAction('优化沉默协议协同', 'silence_integration', 'improve'),
            ],
            'low_action_completion': [
                OptimizationAction('优化行动卡模板', 'action_template', 'improve'),
                OptimizationAction('增加步骤分解', 'step_decomposition', True),
                OptimizationAction('添加示例', 'add_examples', True),
            ],
            'low_satisfaction': [
                OptimizationAction('调整发牌时机', 'timing_strategy', 'optimize'),
                OptimizationAction('优化卡片内容模板', 'content_template', 'improve'),
                OptimizationAction('降低发牌频率', 'frequency_limit', -1),
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
      - confirmation_rate
      - interruption_rate
      - action_completion_rate
      - user_satisfaction
    success_criteria:
      - "确认率 > 75%"
      - "打断率 < 8%"
      - "行动完成率 > 65%"
      - "用户满意度 > 3.5"

  phase_2_expanded:
    name: "扩大试点"
    scope: "20%用户"
    duration: "7天"
    success_criteria:
      - "确认率 > 78%"
      - "打断率 < 6%"
      - "行动完成率 > 68%"
      - "用户满意度 > 3.7"

  phase_3_full_rollout:
    name: "全量发布"
    scope: "100%用户"
    duration: "持续监控"
    success_criteria:
      - "确认率 > 80%"
      - "打断率 < 5%"
      - "行动完成率 > 70%"
      - "用户满意度 > 4.0"

  rollback_criteria:
    - "确认率下降 > 15%"
    - "打断率上升 > 20%"
    - "行动完成率下降 > 10%"
    - "用户满意度下降 > 1.0"
    - "系统错误率增加 > 5%"
```

---

## 优化报告模板

```yaml
card_protocol_optimization_report:
  report_id: "cpo_YYYYMMDDHHMMSS"
  report_name: "发牌协议优化报告"
  based_on_evaluation: "评估报告ID"

  problems_identified:
    - problem_id: "p001"
      type: "误发过多"
      severity: "high"
      affected_metrics:
        - confirmation_rate: 0.55
        - ignore_rate: 0.35

    - problem_id: "p002"
      type: "行动完成率低"
      severity: "medium"
      affected_metrics:
        - action_completion_rate: 0.58

  root_cause_analysis:
    - problem_id: "p001"
      root_cause: "不确定性降低阈值设置过低"
      evidence:
        - "确认率55%，低于80%目标"
        - "被忽略卡片中60%不确定性降低<25%"
      contributing_factors:
        - "质量门控未检查实际价值交付"
        - "沉默协议与发牌协议协同不完善"

    - problem_id: "p002"
      root_cause: "行动描述不够具体"
      evidence:
        - "行动完成率58%，低于70%目标"
        - "放弃用户中40%反馈'不知道怎么做'"
      contributing_factors:
        - "行动卡模板缺少步骤分解"
        - "没有提供具体示例"

  optimization_plan:
    primary_actions:
      - action_id: "a001"
        action: "提高不确定性降低阈值"
        current_value: 0.30
        new_value: 0.40
        expected_impact:
          confirmation_rate: "+10%"
          ignore_rate: "-8%"

      - action_id: "a002"
        action: "优化行动卡模板，增加步骤分解"
        current_value: "简单描述"
        new_value: "分解为3-5个步骤"
        expected_impact:
          action_completion_rate: "+8%"

    rollout_plan:
      phase: "灰度发布"
      phase_1: "5%用户，3天"
      phase_2: "20%用户，7天"
      phase_3: "全量"

  risk_assessment:
    risks:
      - risk: "提高阈值后可能导致漏发增加"
        probability: "medium"
        mitigation: "设置漏发监控，阈值回退机制"

      - risk: "行动步骤分解可能增加认知负担"
        probability: "low"
        mitigation: "提供可折叠详细步骤，默认显示摘要"

    expected_outcome:
      health_score_improvement: "+10-15%"
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
    author: "发牌协议优化师"
    changes:
      - "初始版本"
```
