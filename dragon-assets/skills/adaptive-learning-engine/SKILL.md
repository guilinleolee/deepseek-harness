---
license: UNKNOWN
triggers: ["adaptive learning engine", "自适应学习引擎 (Adaptive Learning Engine)"]
---
# 自适应学习引擎 (Adaptive Learning Engine)

## L0: 一句话描述
实时感知学习状态，动态调整学习策略，最大化学习效果

## L1: 使用场景
当用户进行长期学习时，持续监控学习状态，自动调整节奏、补充短板、强化记忆

## L2: 详细文档

### 核心能力

```
┌─────────────────────────────────────────────────────────────┐
│ 自适应学习引擎 - 基于多维度感知的智能学习调节                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  📊 状态感知                                               │
│  ├── 认知负荷：监控理解难度感知                            │
│  ├── 学习节奏：识别专注/疲劳状态                           │
│  ├── 遗忘曲线：追踪记忆衰减规律                           │
│  └── 动机水平：评估学习意愿变化                           │
│                                                             │
│  🔧 策略调节                                               │
│  ├── 难度调节：提升/降低/保持节奏                         │
│  ├── 内容切换：穿插不同类型内容                            │
│  ├── 时间管理：调整学习/休息比例                           │
│  └── 强化时机：最佳复习时间点                              │
│                                                             │
│  🎯 目标优化                                               │
│  ├── 效率最大化：最短时间达目标                           │
│  ├── 留存最大化：最长记忆保持                             │
│  └── 动机保持：避免倦怠和放弃                             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### DSPy Signature

```python
class LearningStateMonitor(dspy.Signature):
    """监控学习状态，识别需要干预的信号"""
    recent_activities: list[dict] = dspy.InputField(desc="近期学习活动记录")
    time_series: list[dict] = dspy.InputField(desc="时间序列数据: 速度/正确率/耗时")
    user_feedback: str = dspy.InputField(desc="用户反馈: 状态/感受/问题")
    cognitive_load: str = dspy.OutputField(desc="认知负荷评估: low/medium/high/overload")
    learning_state: str = dspy.OutputField(desc="学习状态: engaged/tired/frustrated/flow")
    alerts: list[dict] = dspy.OutputField(desc="需要干预的信号列表")
    recommendations: list[str] = dspy.OutputField(desc="调节建议")


class AdaptiveStrategySelector(dspy.Signature):
    """选择最优学习策略"""
    current_state: dict = dspy.InputField(desc="当前学习状态")
    learning_goal: str = dspy.InputField(desc="当前学习目标")
    history_patterns: list[dict] = dspy.InputField(desc="历史学习模式")
    optimal_strategy: dict = dspy.OutputField(desc="推荐策略: 类型/强度/时长")
    expected_outcome: str = dspy.OutputField(desc="预期效果")
    confidence_score: float = dspy.OutputField(desc="策略信心度")
```

### 学习状态模型

```python
class LearningStateModel:
    """多维度学习状态模型"""

    dimensions = {
        "cognitive": {
            "indicators": [
                "理解速度",      # 概念掌握快慢
                "错误类型",      # 粗心/理解/复杂
                "反应时间",      # 决策速度
                "混淆程度",      # 概念混淆频率
            ],
            "thresholds": {
                "low_load": {"error_rate": "<10%", "time": "fast"},
                "medium_load": {"error_rate": "10-30%", "time": "normal"},
                "high_load": {"error_rate": "30-50%", "time": "slow"},
                "overload": {"error_rate": ">50%", "time": "very_slow"},
            }
        },

        "motivational": {
            "indicators": [
                "主动性",        # 是否有学习意愿
                "坚持度",        # 遇到困难时的坚持
                "反馈质量",      # 回答问题的意愿
                "情绪状态",      # 积极/中性/消极
            ],
            "patterns": {
                "intrinsic_flow": "内在驱动，学习本身带来满足",
                "goal_directed": "目标驱动，完成目标有奖励",
                "compliance": "被动服从，需要监督",
                "burnout_risk": "倦怠风险，需要干预",
            }
        },

        "temporal": {
            "indicators": [
                "学习时段",      # 早/中/晚
                "专注持续",      # 专注时长
                "疲劳曲线",      # 疲劳积累
                "遗忘周期",      # 记忆衰减
            ],
            "patterns": {
                "morning_peak": "上午高峰期",
                "afternoon_dip": "下午低谷期",
                "evening_recovery": "晚间恢复期",
                "weekend_boost": "周末效率提升",
            }
        },

        "social": {
            "indicators": [
                "协作意愿",      # 是否愿意讨论
                "求助频率",      # 遇到困难的求助
                "教学倾向",      # 愿意教授他人
                "同伴反馈",      # 从他人学习
            ],
            "patterns": {
                "solo_prefer": "偏好独自学习",
                "collaborative": "喜欢协作学习",
                "teaching_style": "通过教来学",
            }
        }
    }
```

### 自适应策略库

```yaml
adaptive_strategies:
  difficulty_adjustment:
    - strategy: "reduce_complexity"
      trigger: "cognitive_overload"
      action:
        - "分解复杂概念为简单步骤"
        - "提供更多例子"
        - "减少新概念数量"
      recovery_time: "15-30分钟"

    - strategy: "increase_challenge"
      trigger: "low_engagement"
      action:
        - "引入更复杂的问题"
        - "减少提示和帮助"
        - "增加实战应用"
      expected_duration: "until_re_engaged"

    - strategy: "maintain_flow"
      trigger: "in_flow_state"
      action:
        - "保持当前节奏"
        - "适时微调难度"
        - "记录flow状态特征"
      note: "flow状态下学习效果最佳"

  content_modulation:
    - strategy: "interleave_practice"
      trigger: "same_content_fatigue"
      action:
        - "穿插不同类型练习"
        - "混合新旧概念"
        - "变化学习形式"
      example: "理论-实践-理论交替"

    - strategy: "context_switch"
      trigger: "stuck_on_problem"
      action:
        - "暂时放下当前问题"
        - "学习相关内容"
        - "30分钟后回来"
      science: " incubation effect"

    - strategy: "spiral_review"
      trigger: "accumulated_knowledge"
      action:
        - "定期回顾已学内容"
        - "与新内容建立联系"
        - "强化记忆痕迹"
      frequency: "每周review"

  temporal_optimization:
    - strategy: "pomodoro_adaptation"
      trigger: "session_length"
      intervals:
        deep_work: 50
        short_break: 10
        long_break: 30
      adaptation:
        - "监控专注度"
        - "疲劳时提前休息"
        - "精力恢复后延长"

    - strategy: "circadian_alignment"
      trigger: "time_of_day"
      recommendations:
        - "早7-9: 新概念学习"
        - "9-12: 复杂问题解决"
        - "14-16: 实践练习"
        - "16-18: 复习整理"
        - "20-22: 轻松回顾"

    - strategy: "sleep_integration"
      trigger: "end_of_day"
      action:
        - "睡前15分钟复习"
        - "利用睡眠巩固记忆"
        - "晨起快速测试"
      science: "memory_consolidation"

  motivation_boost:
    - strategy: "progress_celebration"
      trigger: "achievement_milestone"
      actions:
        - "记录里程碑达成"
        - "展示进步数据"
        - "适度奖励"
      frequency: "每周至少1次"

    - strategy: "challenge_calibration"
      trigger: "frustration"
      action:
        - "降低难度"
        - "回到熟悉内容"
        - "找回成就感"
      warning_signs:
        - "错误率突增"
        - "反应时间延长"
        - "回避行为"

    - strategy: "variety_injection"
      trigger: "monotony"
      options:
        - "改变学习环境"
        - "使用不同媒介"
        - "加入游戏元素"
        - "学习他人案例"
```

### 遗忘预测模型

```python
class ForgettingPredictor:
    """基于SM-2的遗忘预测模型"""

    def predict_forgetting(self, concept_id, user_id, last_review):
        """预测遗忘概率"""
        card = self.get_card(concept_id, user_id)
        days_since_review = (today - last_review).days

        # 基础遗忘曲线 (Ebbinghaus)
        retention = self.calculate_base_retention(days_since_review)

        # 个体化调整
        personal_factor = self.get_personal_factor(user_id)
        difficulty_factor = self.get_difficulty_factor(card)

        # 实际遗忘概率
        forgetting_prob = 1 - (retention * personal_factor / difficulty_factor)

        return {
            "concept": concept_id,
            "forgetting_probability": forgetting_prob,
            "optimal_review_time": self.calculate_optimal_review(forgetting_prob),
            "review_priority": self.calculate_priority(forgetting_prob),
        }

    def calculate_base_retention(self, days):
        """基础记忆保持率"""
        # 使用改进的遗忘曲线公式
        retention = 1 / (1 + (days / 7) ** 1.25)
        return retention

    def get_optimal_review_time(self, forgetting_prob):
        """计算最佳复习时间"""
        if forgetting_prob > 0.7:
            return "immediate"  # 今天内复习
        elif forgetting_prob > 0.5:
            return "tomorrow"  # 明天复习
        elif forgetting_prob > 0.3:
            return "this_week"  # 本周内复习
        else:
            return "next_week"  # 下周复习
```

### 实时调节循环

```python
class AdaptiveLearningLoop:
    """自适应学习主循环"""

    def __init__(self):
        self.state_monitor = LearningStateMonitor()
        self.strategy_selector = AdaptiveStrategySelector()
        self.forgetting_predictor = ForgettingPredictor()
        self.learning_recorder = LearningRecorder()

    def run_loop(self, user_id, current_activity):
        # 1. 记录当前活动
        self.learning_recorder.log_activity(user_id, current_activity)

        # 2. 获取历史数据
        recent = self.learning_recorder.get_recent(user_id, window=30)
        time_series = self.learning_recorder.get_time_series(user_id)

        # 3. 监控状态
        state = self.state_monitor(
            recent_activities=recent,
            time_series=time_series,
            user_feedback=current_activity.get("feedback", "")
        )

        # 4. 预测遗忘
        weak_concepts = self.forgetting_predictor.predict_weaknesses(user_id)

        # 5. 选择策略
        if state.alerts:
            strategy = self.strategy_selector(
                current_state=state,
                learning_goal=self.get_current_goal(user_id),
                history_patterns=self.get_patterns(user_id)
            )

            # 6. 执行干预
            self.execute_intervention(strategy, state.alerts)

        # 7. 触发间隔重复
        if weak_concepts:
            self.schedule_spaced_repetition(weak_concepts)

        # 8. 更新状态
        return {
            "current_state": state.learning_state,
            "cognitive_load": state.cognitive_load,
            "alerts": state.alerts,
            "recommendations": state.recommendations,
            "review_scheduled": len(weak_concepts),
        }
```

### 学习诊断系统

```yaml
learning_diagnostics:
  symptoms:
    - symptom: "学习时间长但效果差"
      causes:
        - "低效重复"
        - "被动学习"
        - "缺乏理解"
      solutions:
        - "主动回忆练习"
        - "费曼讲解法"
        - "间隔复习"

    - symptom: "遇到困难就放弃"
      causes:
        - "难度过高"
        - "缺乏动机"
        - "挫折感累积"
      solutions:
        - "降低难度"
        - "分解目标"
        - "小步成功"

    - symptom: "学了就忘"
      causes:
        - "复习不足"
        - "缺乏联结"
        - "睡眠不足"
      solutions:
        - "间隔重复"
        - "知识图谱"
        - "睡眠优化"

    - symptom: "注意力不集中"
      causes:
        - "任务无趣"
        - "环境干扰"
        - "认知疲劳"
      solutions:
        - "变换形式"
        - "番茄工作"
        - "短暂休息"

    - symptom: "缺乏动力"
      causes:
        - "目标模糊"
        - "看不到进步"
        - "任务无意义"
      solutions:
        - "明确目标"
        - "可视化进度"
        - "关联实际应用"
```

### 干预策略执行

```python
class InterventionExecutor:
    """干预策略执行器"""

    def execute(self, strategy, alerts):
        for alert in alerts:
            intervention = self.select_intervention(alert, strategy)

            if intervention.type == "pause":
                self.trigger_break(intervention)

            elif intervention.type == "content_switch":
                self.suggest_alternative(intervention)

            elif intervention.type == "difficulty_adjust":
                self.modify_difficulty(intervention)

            elif intervention.type == "review_insert":
                self.schedule_review(intervention)

            elif intervention.type == "encouragement":
                self.provide_feedback(intervention)

    def trigger_break(self, intervention):
        """触发休息"""
        return {
            "message": "休息一下吧！",
            "suggestions": [
                "站起来活动一下",
                "看看远方放松眼睛",
                "喝杯水"
            ],
            "duration": intervention.get("duration", 300),
            "activity": "stretch"
        }
```

### 学习报告生成

```python
def generate_learning_report(user_id, period="weekly"):
    """生成学习报告"""
    data = get_learning_data(user_id, period)

    report = {
        "period": period,
        "summary": {
            "total_hours": data["time_spent"],
            "concepts_learned": data["new_concepts"],
            "concepts_reviewed": data["reviews"],
            "mastery_improvement": data["mastery_delta"],
        },
        "patterns": {
            "peak_hours": identify_peak_hours(data),
            "optimal_duration": identify_optimal_session(data),
            "forgetting_weaknesses": data["weak_areas"],
        },
        "recommendations": {
            "schedule": optimize_schedule(data),
            "content": recommend_content(data),
            "habits": suggest_habits(data),
        },
        "insights": generate_insights(data),
    }

    return format_report(report)
```

### 使用示例

```markdown
## 📊 学习状态报告

### 当前状态
| 指标 | 数值 | 状态 |
|------|------|------|
| 认知负荷 | 65% | 🟡 中等 |
| 学习状态 | Flow | 🟢 专注 |
| 疲劳度 | 25% | 🟢 良好 |
| 动机水平 | 高 | 🟢 积极 |

### 📈 实时分析

**过去30分钟:**
- 理解速度: 加快 (+15%)
- 错误率: 稳定 (8%)
- 专注度: 高

**预测:**
- 遗忘风险: "React Hooks" 复习建议明天进行
- 疲劳预警: 约60分钟后可能出现疲劳

### 🎯 策略建议

**当前策略: 保持Flow**
- 继续当前节奏
- 15分钟后可考虑短暂休息
- 避免切换到更难内容

**如果出现以下情况:**
- 错误率 > 20%: 切换到实践练习
- 注意力下降: 尝试费曼讲解
- 30分钟后: 插入5分钟休息

### 📅 今日推荐

| 时间 | 活动 | 时长 |
|------|------|------|
| 现在-45min | 继续当前主题 | 🍅 |
| 45min后 | 快速休息 | 5min |
| 之后 | 间隔复习 | 15min |
| 之后 | 新内容学习 | 🍅 |

### 🏆 里程碑

[████████░░] 80% 完成本周目标

**本周进度:**
- 已学习: 8个新概念
- 已复习: 23次
- 掌握度: 72% → 81% (+9%)
```

### 与其他技能协同

```yaml
skill_integration:
  with_feynman_technique:
    trigger: "low_understanding_score"
    action: "启动费曼讲解练习"
    feedback: "讲解流畅度影响难度调整"

  with_spaced_repetition:
    trigger: "forgetting_risk > 0.6"
    action: "触发间隔复习"
    feedback: "复习效果影响复习频率"

  with_pomodoro_timer:
    trigger: "fatigue_level > 0.7"
    action: "建议提前休息"
    feedback: "休息后专注度恢复情况"

  with_curriculum_designer:
    trigger: "extended_underperformance"
    action: "建议课程路径调整"
    feedback: "路径调整后的效果"

  with_peer_learning:
    trigger: "stuck_on_concept"
    action: "建议同伴讨论"
    feedback: "讨论后的理解提升"
```

### 触发条件

| 触发词 | 场景 | 响应 |
|--------|------|------|
| "我感觉学不进去" | 学习障碍 | 分析原因+策略调整 |
| "太难了/太简单了" | 难度反馈 | 实时调整难度 |
| "帮我看看学习报告" | 状态诊断 | 生成分析报告 |
| "我好像忘了X" | 遗忘感知 | 安排即时复习 |
| "继续学习" | 继续任务 | 从上次中断处继续 |

### 预期效果

| 指标 | 效果 |
|------|------|
| 学习效率 | +75% |
| 知识留存 | +80% |
| 学习时长优化 | +40% |
| 放弃率降低 | -60% |

### 文件结构

```
adaptive-learning-engine/
├── SKILL.md                    # 本文件
├── prompts/
│   ├── state-analysis.md        # 状态分析模板
│   └── intervention-template.md # 干预策略模板
├── scripts/
│   ├── state_monitor.py         # 状态监控器
│   ├── strategy_selector.py     # 策略选择器
│   ├── forgetting_predictor.py  # 遗忘预测器
│   └── intervention_executor.py # 干预执行器
└── templates/
    └── learning-report.md        # 报告模板
```

---

## 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| V1.0 | 2026-04-24 | 初始版本，基于实时感知的自适应学习 |
