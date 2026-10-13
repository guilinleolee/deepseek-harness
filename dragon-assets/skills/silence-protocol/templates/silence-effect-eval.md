# 沉默效果评估模板
# Silence Effect Evaluation Template
# 用于评估沉默协议的执行效果和健康度

---

## 一、沉默效果评估维度

### 1. 正面指标 (Positive Indicators)

| 指标名称 | 描述 | 测量方法 | 目标值 |
|----------|------|---------|--------|
| `task_completion_rate` | 任务完成率上升 | 对比沉默期前后 | >+10% |
| `user_satisfaction` | 用户满意度上升 | 用户反馈调查 | >+15% |
| `deep_work_duration` | 深度工作时间增加 | 专注度追踪 | >+20% |
| `flow_state_duration` | 心流状态持续时间增加 | 状态检测 | >+25% |

### 2. 负面指标 (Negative Indicators)

| 指标名称 | 描述 | 测量方法 | 警戒值 |
|----------|------|---------|--------|
| `missed_information` | 用户错过重要信息 | 用户反馈 | >5% |
| `help_requests` | 用户反馈"没有得到帮助" | 投诉统计 | >3% |
| `problem_resolution_time` | 问题未及时解决 | 工单响应时间 | >+30% |
| `anxiety_increase` | 用户焦虑感上升 | 用户反馈 | >+10% |

### 3. 平衡指标 (Balance Metrics)

| 指标名称 | 描述 | 测量方法 | 目标值 |
|----------|------|---------|--------|
| `silence_rate` | 沉默率 vs 发牌率 | 统计比率 | 20-40% |
| `silence_coverage` | 沉默场景覆盖率 | 场景覆盖评估 | >90% |
| `silence_timeout_rate` | 沉默超时触发率 | 超时统计 | <10% |
| `silence_bypass_rate` | 沉默被绕过率 | 绕过统计 | <5% |

---

## 二、沉默健康度检查表

```
┌─────────────────────────────────────────────────────────────┐
│ 沉默健康度检查表                                            │
├─────────────────────────────────────────────────────────────┤
│ 时间范围: [开始日期] - [结束日期]                          │
│                                                             │
│ 沉默统计:                                                  │
│ - 沉默事件数: ____                                         │
│ - 平均沉默时长: ____分钟                                    │
│ - 沉默后发牌数: ____（沉默超时后）                        │
│ - 总发牌尝试数: ____                                       │
│                                                             │
│ 沉默质量:                                                  │
│ - 沉默正确率: ____%（沉默正确/总沉默）                     │
│ - 沉默超时率: ____%（超时触发/总沉默）                     │
│ - 沉默被绕过率: ____%（高优先级绕过/总沉默）              │
│ - 用户满意度变化: ____%                                     │
│                                                             │
│ 用户反馈:                                                  │
│ - 负面反馈: ____条                                          │
│ - 正面反馈: ____条                                          │
│ - 中性反馈: ____条                                          │
│                                                             │
│ 健康度评估: [优秀/良好/警告/危险]                          │
│ 主要问题: ________________________________________________ │
│ 优化建议: ________________________________________________ │
└─────────────────────────────────────────────────────────────┘
```

---

## 三、沉默效果评估报告模板

```yaml
silence_effect_report:
  # ==========================================================================
  # 基本信息
  # ==========================================================================
  report_id: "报告ID"
  report_name: "沉默效果评估报告"
  evaluation_period:
    start_date: "YYYY-MM-DD"
    end_date: "YYYY-MM-DD"
    duration_days: 30  # 评估周期（天）

  # ==========================================================================
  # 沉默统计摘要
  # ==========================================================================
  silence_statistics:
    total_silence_events: 150  # 总沉默事件数
    total_card_attempts: 500  # 总发牌尝试数
    silence_rate: 0.30  # 沉默率 = 沉默事件/发牌尝试
    average_silence_duration: 12  # 平均沉默时长（分钟）
    silence_after_timeout: 45  # 超时后发牌数

  # ==========================================================================
  # 沉默质量指标
  # ==========================================================================
  silence_quality:
    correctness_rate:
      value: 0.87
      description: "沉默正确的比例"
      formula: "沉默正确数 / 总沉默数"
      status: "良好"  # 优秀>90%, 良好>85%, 警告>80%, 危险<80%

    timeout_rate:
      value: 0.08
      description: "沉默超时触发的比例"
      formula: "超时触发数 / 总沉默数"
      status: "优秀"  # 优秀<5%, 良好<10%, 警告<15%, 危险>15%

    bypass_rate:
      value: 0.03
      description: "高优先级绕过沉默的比例"
      formula: "绕过数 / 总沉默数"
      status: "优秀"  # 优秀<3%, 良好<5%, 警告<8%, 危险>8%

  # ==========================================================================
  # 用户影响指标
  # ==========================================================================
  user_impact:
    satisfaction_change: +0.12  # 满意度变化（+为提升）
    missed_information_rate: 0.02  # 错过信息率
    anxiety_change: -0.05  # 焦虑感变化（-为降低）

    task_completion_change: +0.08  # 任务完成率变化
    deep_work_duration_change: +0.15  # 深度工作时间变化

  # ==========================================================================
  # 问题识别
  # ==========================================================================
  issues_identified:
    - issue_id: "issue_001"
      severity: "medium"
      description: "某些场景沉默时长过长"
      affected_scenarios: ["创意工作", "决策过程"]
      recommendation: "缩短创意工作场景的沉默时长阈值"

    - issue_id: "issue_002"
      severity: "low"
      description: "深夜时段沉默率偏高"
      affected_time: "22:00-24:00"
      recommendation: "考虑在深夜时段降低沉默阈值"

  # ==========================================================================
  # 优化建议
  # ==========================================================================
  optimization_suggestions:
    - priority: "high"
      suggestion: "调整深度工作保护场景的沉默时长"
      expected_impact: "沉默正确率提升至90%+"

    - priority: "medium"
      suggestion: "优化唤醒机制，减少超时触发"
      expected_impact: "超时率降至5%以下"

    - priority: "low"
      suggestion: "增加用户反馈收集渠道"
      expected_impact: "更准确地评估沉默效果"

  # ==========================================================================
  # 综合评估
  # ==========================================================================
  overall_assessment:
    health_score: 85  # 健康度评分（0-100）
    health_level: "良好"
    trend: "改善中"

    summary: |
      本评估周期内沉默协议执行效果良好。
      沉默正确率达到87%，超过85%的目标值。
      用户满意度提升12%，深度工作时间增加15%。
      存在2个中低优先级问题，建议下周期优化。

    next_review_date: "YYYY-MM-DD"
```

---

## 四、沉默效果评估流程

### 4.1 日评估流程

```
每日评估流程:
1. 收集昨日沉默统计数据
   - 沉默事件数、发牌尝试数、沉默率
   - 超时触发数、绕过数

2. 收集用户反馈
   - 沉默相关投诉
   - 帮助请求

3. 更新沉默统计面板
   - 更新日趋势图
   - 标记异常事件

4. 生成日评估摘要
   - 发送至相关方（如有必要）
```

### 4.2 周评估流程

```
周评估流程:
1. 汇总本周沉默数据
   - 累计沉默统计
   - 周趋势分析

2. 分析用户反馈
   - 分类统计反馈类型
   - 识别反复出现的问题

3. 评估沉默质量指标
   - 正确率、超时率、绕过率
   - 与目标值对比

4. 生成周评估报告
   - 发送给治理委员会
   - 提出优化建议
```

### 4.3 月评估流程

```
月评估流程:
1. 汇总本月沉默数据
   - 累计沉默统计
   - 月趋势分析

2. 分析沉默场景覆盖度
   - 评估各场景沉默效果
   - 识别覆盖盲区

3. 评估用户长期影响
   - 满意度趋势
   - 任务完成率趋势

4. 审查沉默协议配置
   - 评估阈值合理性
   - 调整沉默场景定义

5. 生成月评估报告
   - 包含综合评估和优化建议
   - 提交给决策层审批
```

---

## 五、沉默效果评估工具函数

```python
import json
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Optional

@dataclass
class SilenceEvent:
    """沉默事件"""
    event_id: str
    timestamp: datetime
    card_content: str  # 被沉默的卡片内容
    silence_duration: int  # 沉默时长（分钟）
    silence_reason: str  # 沉默原因
    outcome: str  # 结果：timeout/forced/wake_bypass
    was_correct: bool  # 沉默是否正确

@dataclass
class SilenceMetrics:
    """沉默指标"""
    total_silence_events: int
    total_card_attempts: int
    correct_silences: int
    timeout_triggers: int
    bypass_triggers: int

class SilenceEffectEvaluator:
    """沉默效果评估器"""

    def __init__(self, events: List[SilenceEvent]):
        self.events = events

    def calculate_metrics(self) -> SilenceMetrics:
        """计算沉默指标"""
        return SilenceMetrics(
            total_silence_events=len(self.events),
            total_card_attempts=sum(1 for e in self.events) / 0.3,  # 估算
            correct_silences=sum(1 for e in self.events if e.was_correct),
            timeout_triggers=sum(1 for e in self.events if e.outcome == 'timeout'),
            bypass_triggers=sum(1 for e in self.events if e.outcome == 'forced')
        )

    def calculate_rates(self, metrics: SilenceMetrics) -> dict:
        """计算沉默比率"""
        total = metrics.total_silence_events
        return {
            'silence_rate': total / metrics.total_card_attempts,
            'correct_rate': metrics.correct_silences / total if total > 0 else 0,
            'timeout_rate': metrics.timeout_triggers / total if total > 0 else 0,
            'bypass_rate': metrics.bypass_triggers / total if total > 0 else 0
        }

    def evaluate_health_score(self, rates: dict) -> dict:
        """评估健康度评分"""
        # 加权计算健康度
        correct_weight = 0.4
        timeout_weight = 0.3
        bypass_weight = 0.3

        score = (
            rates['correct_rate'] * correct_weight * 100 +
            (1 - rates['timeout_rate']) * timeout_weight * 100 +
            (1 - rates['bypass_rate']) * bypass_weight * 100
        )

        level = (
            "优秀" if score >= 90 else
            "良好" if score >= 80 else
            "警告" if score >= 70 else
            "危险"
        )

        return {
            'health_score': round(score, 1),
            'health_level': level,
            'trend': self._calculate_trend()
        }

    def generate_report(self) -> dict:
        """生成评估报告"""
        metrics = self.calculate_metrics()
        rates = self.calculate_rates(metrics)
        health = self.evaluate_health_score(rates)

        return {
            'report_id': f"ser_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'evaluation_period': {
                'start_date': min(e.timestamp for e in self.events).date().isoformat(),
                'end_date': max(e.timestamp for e in self.events).date().isoformat(),
            },
            'silence_statistics': {
                'total_silence_events': metrics.total_silence_events,
                'total_card_attempts': metrics.total_card_attempts,
                'silence_rate': round(rates['silence_rate'], 3)
            },
            'silence_quality': {
                'correct_rate': round(rates['correct_rate'], 3),
                'timeout_rate': round(rates['timeout_rate'], 3),
                'bypass_rate': round(rates['bypass_rate'], 3)
            },
            'overall_assessment': health
        }

    def _calculate_trend(self) -> str:
        """计算趋势"""
        # 比较近期与早期数据
        recent = self.events[-10:] if len(self.events) >= 10 else self.events
        early = self.events[:10] if len(self.events) >= 10 else self.events

        recent_correct = sum(1 for e in recent if e.was_correct) / len(recent)
        early_correct = sum(1 for e in early if e.was_correct) / len(early)

        if recent_correct > early_correct + 0.05:
            return "改善中"
        elif recent_correct < early_correct - 0.05:
            return "退化中"
        else:
            return "稳定"
```

---

## 六、沉默效果评估示例

```python
# 示例数据
events = [
    SilenceEvent(
        event_id="se_001",
        timestamp=datetime(2026, 4, 23, 10, 30),
        card_content="新消息通知",
        silence_duration=15,
        silence_reason="深度工作保护",
        outcome="wake_bypass",
        was_correct=True
    ),
    # ... 更多事件
]

# 生成评估报告
evaluator = SilenceEffectEvaluator(events)
report = evaluator.generate_report()

print(f"健康度评分: {report['overall_assessment']['health_score']}")
print(f"健康等级: {report['overall_assessment']['health_level']}")
print(f"沉默正确率: {report['silence_quality']['correct_rate']:.1%}")
# → 健康度评分: 87.5
# → 健康等级: 良好
# → 沉默正确率: 87.5%
```
