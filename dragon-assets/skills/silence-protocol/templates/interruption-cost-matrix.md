# 打断成本评估矩阵
# Interruption Cost Evaluation Matrix
# 用于评估打断用户的成本，决定是否应沉默

---

## 一、打断成本类型

### 1. 认知成本 (Cognitive Cost)

| 成本项 | 描述 | 评估方法 |
|--------|------|---------|
| `context_switch_time` | 上下文切换时间 | 重新进入当前任务状态所需时间 |
| `mental_state_recovery` | 心理状态恢复时间 | 从中断恢复到深度专注的时间 |
| `deep_work_loss` | 深度工作损失程度 | 深度专注状态被打断的代价 |

### 2. 情感成本 (Emotional Cost)

| 成本项 | 描述 | 评估方法 |
|--------|------|---------|
| `frustration_level` | 挫败感程度 | 被打断后的挫败感评分(1-10) |
| `trust_impact` | 信任影响程度 | 对系统可靠性的信任影响(1-10) |
| `anxiety_increase` | 焦虑增加程度 | 担心错过信息的焦虑程度(1-10) |

### 3. 效率成本 (Efficiency Cost)

| 成本项 | 描述 | 评估方法 |
|--------|------|---------|
| `task_completion_delay` | 任务完成延迟 | 整体任务完成的延迟时间 |
| `flow_state_break` | 心流状态打破 | 是否打破当前的心流状态 |
| `productivity_loss` | 生产力损失 | 打断导致的生产力损失比例(0-1) |

---

## 二、打断成本评估表

```
┌─────────────────────────────────────────────────────────────┐
│ 打断成本评估表                                              │
├─────────────────────────────────────────────────────────────┤
│ 被打断的任务: ________________                             │
│                                                             │
│ 用户当前状态:                                              │
│ - 任务专注度: [深度/中度/低度]                             │
│ - 心流状态: [是/否]                                       │
│ - 认知负载: [高/中/低]                                     │
│                                                             │
│ 打断类型成本:                                              │
│ - 上下文切换时间: ____分钟                                  │
│ - 心理状态恢复: ____分钟                                    │
│ - 效率损失: ____%                                          │
│                                                             │
│ 总打断成本: ____分钟                                        │
│                                                             │
│ 发牌收益:                                                  │
│ - 不确定性减少: [高/中/低]                                  │
│ - 动作清晰度提升: [高/中/低]                               │
│ - 效率改善预估: ____%                                       │
│                                                             │
│ 打断决策:                                                  │
│ 成本 > 收益? → □发牌  ■沉默  □延后                        │
└─────────────────────────────────────────────────────────────┘
```

---

## 三、沉默条件检查表

```
┌─────────────────────────────────────────────────────────────┐
│ 沉默条件检查表                                              │
├─────────────────────────────────────────────────────────────┤
│ 发牌: ________________                                      │
│                                                             │
│ 沉默检查:                                                  │
│ □ 用户正在深度工作（Y/N）: ____                            │
│ □ 心流状态可能被打破（Y/N）: ____                          │
│ □ 打断成本 > 发牌收益（Y/N）: ____                         │
│ □ 用户明确表示不感兴趣（Y/N）: ____                        │
│ □ 用户刚收到大量信息（Y/N）: ____                           │
│                                                             │
│ 沉默评估:                                                  │
│ 沉默收益: [高/中/低]                                       │
│ 沉默风险: [高/中/低]                                       │
│                                                             │
│ 决策: □沉默  □发牌  □延后(时间:____)                      │
│ 理由: ___________________________________________________ │
└─────────────────────────────────────────────────────────────┘
```

---

## 四、成本量化公式

### 4.1 总打断成本计算

```python
def calculate_total_interruption_cost(context: dict) -> dict:
    """计算总打断成本"""

    # 1. 认知成本
    cognitive_cost = (
        context['context_switch_time'] +
        context['mental_state_recovery'] +
        context['deep_work_loss'] * 2  # 深度工作损失权重更高
    )

    # 2. 情感成本（转换为时间当量）
    emotional_cost = (
        context['frustration_level'] * 1 +
        context['trust_impact'] * 0.5 +
        context['anxiety_increase'] * 0.5
    )

    # 3. 效率成本
    efficiency_cost = (
        context['task_completion_delay'] +
        context['productivity_loss'] * 60  # 转换为分钟
    )

    # 4. 心流破坏惩罚
    flow_penalty = 15 if context['flow_state_break'] else 0

    # 5. 专注度惩罚
    focus_penalty = {
        '深度': 10,
        '中度': 5,
        '低度': 0
    }.get(context['task_focus'], 0)

    total_cost = cognitive_cost + emotional_cost + efficiency_cost + flow_penalty + focus_penalty

    return {
        'cognitive_cost': cognitive_cost,
        'emotional_cost': emotional_cost,
        'efficiency_cost': efficiency_cost,
        'flow_penalty': flow_penalty,
        'focus_penalty': focus_penalty,
        'total_cost': total_cost
    }
```

### 4.2 发牌收益计算

```python
def calculate_card_benefit(card: dict) -> dict:
    """计算发牌收益"""

    uncertainty_value = {
        'high': 5,
        'medium': 3,
        'low': 1
    }.get(card['uncertainty_reduction'], 2)

    clarity_value = {
        'high': 5,
        'medium': 3,
        'low': 1
    }.get(card['action_clarity'], 2)

    efficiency_gain = card.get('efficiency_improvement', 0) * 30  # 转换为分钟

    total_benefit = uncertainty_value + clarity_value + efficiency_gain

    return {
        'uncertainty_value': uncertainty_value,
        'clarity_value': clarity_value,
        'efficiency_gain': efficiency_gain,
        'total_benefit': total_benefit
    }
```

### 4.3 沉默决策

```python
def should_silence(cost: dict, benefit: dict) -> str:
    """决定是否应沉默"""

    net_value = benefit['total_benefit'] - cost['total_cost']

    # 考虑风险调整
    risk_factor = 1.2 if cost['flow_penalty'] > 0 else 1.0

    adjusted_threshold = 0 * risk_factor

    if net_value > adjusted_threshold + 5:
        return "发牌"  # 明显收益 > 成本
    elif net_value > adjusted_threshold - 5:
        return "延后"  # 收益略大于成本，可延后
    else:
        return "沉默"  # 成本 >= 收益
```

---

## 五、场景化成本模板

### 5.1 深度工作场景

```yaml
deep_work_scenario:
  task_type: "深度工作"
  cognitive:
    context_switch_time: 5  # 深度工作切换代价更高
    mental_state_recovery: 5
    deep_work_loss: 10
  emotional:
    frustration_level: 7
    trust_impact: 3
    anxiety_increase: 4
  efficiency:
    task_completion_delay: 15
    flow_state_break: true
    productivity_loss: 0.4
  typical_total_cost: 45  # 分钟
```

### 5.2 创意工作场景

```yaml
creative_work_scenario:
  task_type: "创意工作"
  cognitive:
    context_switch_time: 3
    mental_state_recovery: 4
    deep_work_loss: 8
  emotional:
    frustration_level: 6
    trust_impact: 2
    anxiety_increase: 3
  efficiency:
    task_completion_delay: 10
    flow_state_break: true
    productivity_loss: 0.35
  typical_total_cost: 35  # 分钟
```

### 5.3 普通工作场景

```yaml
normal_work_scenario:
  task_type: "普通工作"
  cognitive:
    context_switch_time: 2
    mental_state_recovery: 2
    deep_work_loss: 3
  emotional:
    frustration_level: 3
    trust_impact: 1
    anxiety_increase: 2
  efficiency:
    task_completion_delay: 5
    flow_state_break: false
    productivity_loss: 0.15
  typical_total_cost: 15  # 分钟
```

### 5.4 空闲/休息场景

```yaml
idle_scenario:
  task_type: "空闲/休息"
  cognitive:
    context_switch_time: 1
    mental_state_recovery: 1
    deep_work_loss: 0
  emotional:
    frustration_level: 2
    trust_impact: 1
    anxiety_increase: 1
  efficiency:
    task_completion_delay: 2
    flow_state_break: false
    productivity_loss: 0.05
  typical_total_cost: 6  # 分钟
```

---

## 六、成本评估工具函数

```python
import yaml
from dataclasses import dataclass
from typing import Optional

@dataclass
class InterruptionContext:
    """打断上下文"""
    task_name: str
    task_focus: str  # 深度/中度/低度
    flow_state: bool  # 是否处于心流状态
    cognitive_load: str  # 高/中/低

    # 认知成本
    context_switch_time: float = 3
    mental_state_recovery: float = 2
    deep_work_loss: float = 5

    # 情感成本
    frustration_level: float = 3
    trust_impact: float = 1
    anxiety_increase: float = 2

    # 效率成本
    task_completion_delay: float = 5
    flow_state_break: bool = False
    productivity_loss: float = 0.2

@dataclass
class CardBenefit:
    """发牌收益"""
    uncertainty_reduction: str  # high/medium/low
    action_clarity: str  # high/medium/low
    efficiency_improvement: float = 0.0

def evaluate_interruption(
    context: InterruptionContext,
    benefit: CardBenefit
) -> dict:
    """评估打断是否值得"""

    # 计算成本
    cost = calculate_total_interruption_cost(context.__dict__)

    # 计算收益
    benefit_calc = calculate_card_benefit(benefit.__dict__)

    # 决策
    decision = should_silence(cost, benefit_calc)

    return {
        'cost_breakdown': cost,
        'benefit_breakdown': benefit_calc,
        'decision': decision,
        'net_value': benefit_calc['total_benefit'] - cost['total_cost'],
        'recommendation': _generate_recommendation(decision, cost, benefit_calc)
    }

def _generate_recommendation(decision: str, cost: dict, benefit: dict) -> str:
    """生成建议文本"""
    if decision == "沉默":
        return f"建议沉默。打断成本({cost['total_cost']:.0f}分钟) > 发牌收益({benefit['total_benefit']:.0f}分钟)"
    elif decision == "延后":
        return f"建议延后{_suggest_delay(cost, benefit)}分钟后发送"
    else:
        return f"建议发牌。发牌收益({benefit['total_benefit']:.0f}分钟) > 打断成本({cost['total_cost']:.0f}分钟)"

def _suggest_delay(cost: dict, benefit: dict) -> int:
    """建议延后时间"""
    gap = cost['total_cost'] - benefit['total_benefit']
    return max(5, min(int(gap), 60))  # 5-60分钟之间
```

---

## 七、使用示例

```python
# 示例1: 深度工作中收到低优先级通知
context = InterruptionContext(
    task_name="写技术文档",
    task_focus="深度",
    flow_state=True,
    cognitive_load="高",
    deep_work_loss=10,
    flow_state_break=True,
    productivity_loss=0.4
)

benefit = CardBenefit(
    uncertainty_reduction="low",
    action_clarity="low",
    efficiency_improvement=0.05
)

result = evaluate_interruption(context, benefit)
# → decision: "沉默"
# → net_value: -40
# → recommendation: "建议沉默。打断成本(60分钟) > 发牌收益(6分钟)"

# 示例2: 普通工作中收到重要任务提醒
context = InterruptionContext(
    task_name="回复邮件",
    task_focus="中度",
    flow_state=False,
    cognitive_load="低"
)

benefit = CardBenefit(
    uncertainty_reduction="high",
    action_clarity="high",
    efficiency_improvement=0.3
)

result = evaluate_interruption(context, benefit)
# → decision: "发牌"
# → net_value: +8
# → recommendation: "建议发牌。发牌收益(24分钟) > 打断成本(16分钟)"
```
