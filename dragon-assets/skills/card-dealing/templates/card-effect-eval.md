# 发牌效果评估模板
# Card Dealing Effect Evaluation Template
# 用于周期性评估发牌效果并生成改进建议

---

## 一、评估周期定义

| 评估类型 | 周期 | 关键指标 | 输出 |
|---------|------|----------|------|
| **实时评估** | 每张卡片 | 确认率、响应时间 | 即时反馈 |
| **日评估** | 每天 | 发牌数量、类型分布、频率合规 | 日报 |
| **周评估** | 每周 | 行动完成率、用户满意度 | 周报 |
| **月评估** | 每月 | 综合健康度、趋势分析 | 月报+改进计划 |

---

## 二、核心评估指标

### 2.1 发牌效率指标

| 指标 | 定义 | 计算方式 | 目标值 | 告警阈值 |
|------|------|---------|--------|---------|
| **发牌总数** | 周期内发牌总量 | COUNT(cards) | - | - |
| **发牌频率** | 平均每小时发牌数 | cards / hours | <3 | >5 |
| **类型分布** | 各类型卡片的占比 | type_count / total | 符合预期分布 | 某类型>60% |
| **质量门控通过率** | 通过所有质量门控的比例 | passed_gates / total | >85% | <70% |

### 2.2 用户响应指标

| 指标 | 定义 | 计算方式 | 目标值 | 告警阈值 |
|------|------|------|---------|---------|
| **确认率** | 用户确认的卡片比例 | acknowledged / delivered | >80% | <60% |
| **响应时间** | 发牌到用户响应的平均时间 | AVG(response_time) | <5min | >15min |
| **行动完成率** | 用户完成行动的卡片比例 | completed / action_cards | >70% | <50% |
| **忽略率** | 用户忽略的卡片比例 | ignored / delivered | <20% | >40% |

### 2.3 沉默协议协同指标

| 指标 | 定义 | 计算方式 | 目标值 | 告警阈值 |
|------|------|------|---------|---------|
| **沉默保护率** | 正确保护心流的发牌比例 | properly_delayed / flow_needed | >95% | <85% |
| **打断次数** | 打断用户心流的次数 | flow_interruptions | 0 | >3 |
| **队列积压率** | 队列积压的卡片比例 | queued / total | <10% | >30% |
| **延迟准确率** | 延迟后正确发送的比例 | delayed_sent / delayed | >90% | <70% |

### 2.4 用户满意度指标

| 指标 | 定义 | 计算方式 | 目标值 | 告警阈值 |
|------|------|------|---------|---------|
| **满意度得分** | 用户反馈的平均分 | AVG(feedback_score) | >4.0/5 | <3.0/5 |
| **有用性评分** | 卡片有用性平均分 | AVG(perceived_helpfulness) | >4.0/5 | <3.0/5 |
| **打扰感评分** | 被打扰程度平均分 | AVG(disturbance_level) | <2.0/5 | >3.5/5 |
| **NPS评分** | 净推荐值 | promoters - detractors | >30 | <10 |

---

## 三、健康度评分模型

### 3.1 综合健康度计算

```
health_score = (
    efficiency_score × 0.25 +
    response_score × 0.25 +
    silence_compliance × 0.25 +
    satisfaction_score × 0.25
)

各分项得分 = Σ(指标值 × 权重) / Σ权重
```

### 3.2 健康度等级

| 等级 | 分数范围 | 颜色 | 说明 | 建议行动 |
|------|---------|------|------|----------|
| **优秀** | 90-100 | 绿色 | 全面超越目标 | 保持现状，探索优化空间 |
| **良好** | 75-89 | 蓝色 | 整体达标 | 关注短板指标 |
| **警告** | 60-74 | 黄色 | 部分指标不达标 | 需要改进 |
| **危险** | <60 | 红色 | 多项指标严重不达标 | 紧急干预 |

### 3.3 分项健康度

| 分项 | 权重 | 包含指标 |
|------|------|----------|
| **效率分** | 25% | 发牌频率、类型分布、质量门控通过率 |
| **响应分** | 25% | 确认率、响应时间、行动完成率、忽略率 |
| **沉默分** | 25% | 沉默保护率、打断次数、队列积压率、延迟准确率 |
| **满意分** | 25% | 满意度得分、有用性评分、打扰感评分、NPS |

---

## 四、问题识别与归因

### 4.1 问题识别规则

| 问题类型 | 识别条件 | 严重程度 | 归因方向 |
|---------|---------|---------|----------|
| **漏发问题** | 漏发率 > 15% | 高 | 发牌阈值过高、检测延迟 |
| **误发问题** | 误发率 > 20% | 高 | 发牌阈值过低、用户意图误判 |
| **打断问题** | 打断次数 > 3 | 高 | 心流检测不准确、沉默协议冲突 |
| **响应延迟** | 平均响应时间 > 15min | 中 | 发牌队列拥堵、优先级判断错误 |
| **行动失败** | 行动完成率 < 70% | 中 | 行动描述不清晰、可行性低 |
| **满意度低** | 满意度 < 3.0 | 高 | 多维度问题，需综合分析 |

### 4.2 根因分析框架

```
问题症状
    │
    ├─► 直接原因 → 立即可观测的因素
    │       │
    │       │   例如：打断心流 → 心流检测返回false
    │
    ├─► 中层原因 → 系统/流程因素
    │       │
    │       │   例如：心流检测失败 → 检测算法未更新
    │
    └─► 根本原因 → 设计/架构因素
            │
            例如：检测算法未更新 → 缺少持续优化机制
```

### 4.3 典型问题诊断

| 问题 | 症状 | 根因 | 解决方案 |
|------|------|------|----------|
| 高误发率 | 确认率低，忽略率高 | 质量门控不够严格 | 调整不确定降低阈值至0.4 |
| 高漏发率 | 用户主动查询多 | 发牌时机判断保守 | 放宽延迟阈值，增加试探性发牌 |
| 高打断率 | 满意度低，投诉多 | 心流检测不准确 | 改进心流检测算法，增加预检测 |
| 低行动完成 | 行动卡完成率<50% | 行动描述模糊 | 标准化行动卡格式，增加示例 |

---

## 五、评估报告模板

### 5.1 日报模板

```yaml
daily_report:
  date: "YYYY-MM-DD"
  period: "00:00-24:00"

  volume_summary:
    total_cards: N
    by_type:
      information: N
      confirmation: N
      recommendation: N
      action: N
      warning: N

  quality_summary:
    confirmation_rate: "XX%"
    avg_response_time: "X.X min"
    silence_compliance: "XX%"

  alerts:
    - type: "high_frequency"
      count: N
      recommendation: "暂时限制发牌频率"

  trend:
    vs_yesterday: "+/-X%"
    vs_week_average: "+/-X%"
```

### 5.2 周报模板

```yaml
weekly_report:
  week: "YYYY-WXX"
  period_start: "YYYY-MM-DD"
  period_end: "YYYY-MM-DD"

  health_summary:
    overall_score: XX
    efficiency_score: XX
    response_score: XX
    silence_score: XX
    satisfaction_score: XX
    grade: "优秀/良好/警告/危险"

  volume_trend:
    daily_chart: [data]
    by_type_distribution: [data]

  user_behavior:
    most_active_hours: ["HH:MM-HH:MM"]
    most_common_card_type: "type"
    avg_cards_per_session: X.X

  issues_identified:
    - issue_id: "i001"
      description: "..."
      severity: "high/medium/low"
      root_cause: "..."
      fix_recommendation: "..."

  improvement_plan:
    short_term:
      - action: "..."
        owner: "..."
        deadline: "YYYY-MM-DD"
    long_term:
      - action: "..."
        owner: "..."
        deadline: "YYYY-MM-DD"
```

### 5.3 月度评估报告

```yaml
monthly_report:
  month: "YYYY-MM"
  period_start: "YYYY-MM-01"
  period_end: "YYYY-MM-DD"

  executive_summary:
    overall_health: "grade"
    trend_direction: "improving/stable/declining"
    key_achievements:
      - "..."
    key_concerns:
      - "..."

  comprehensive_metrics:
    all_metrics_from_daily_and_weekly:
      [see above sections]

  comparative_analysis:
    vs_last_month:
      - metric: "..."
        change: "+/-X%"
        reason: "..."
    vs_last_quarter:
      - metric: "..."
        change: "+/-X%"
        reason: "..."
    vs_target:
      - metric: "..."
        gap: "X%"
        reason: "..."

  user_feedback_summary:
    total_responses: N
    positive_feedback_rate: "XX%"
    negative_feedback_rate: "XX%"
    common_praises:
      - "..."
    common_complaints:
      - "..."

  strategic_recommendations:
    - recommendation: "..."
      expected_impact: "..."
      implementation_effort: "low/medium/high"
      priority: "high/medium/low"

  next_month_focus:
    primary_goal: "..."
    key_metrics_to_improve:
      - metric: "..."
        target_improvement: "+X%"
```

---

## 六、CardEvaluator 评估类

```python
@dataclass
class CardEffectMetrics:
    """发牌效果指标"""
    period: str  # daily/weekly/monthly
    total_cards: int
    cards_by_type: dict[str, int]

    # 效率指标
    avg_frequency_per_hour: float
    quality_gate_pass_rate: float

    # 响应指标
    confirmation_rate: float
    avg_response_time_minutes: float
    action_completion_rate: float
    ignore_rate: float

    # 沉默协议协同
    silence_protection_rate: float
    flow_interruptions: int
    queue_backlog_rate: float
    delayed_accuracy_rate: float

    # 用户满意度
    satisfaction_score: float
    helpfulness_score: float
    disturbance_score: float
    nps_score: float


@dataclass
class HealthAssessment:
    """健康度评估"""
    health_score: float
    health_level: str  # 优秀/良好/警告/危险
    trend: str  # 改善中/稳定/退化中
    efficiency_score: float
    response_score: float
    silence_score: float
    satisfaction_score: float


@dataclass
class IdentifiedIssue:
    """识别的问题"""
    issue_id: str
    severity: str  # high/medium/low
    description: str
    affected_metrics: list
    root_cause: str
    recommendation: str


class CardEffectEvaluator:
    """发牌效果评估器"""

    def evaluate(self, period: str) -> tuple[HealthAssessment, list[IdentifiedIssue]]:
        """评估发牌效果"""
        pass

    def identify_issues(self, metrics: CardEffectMetrics) -> list[IdentifiedIssue]:
        """识别问题"""
        pass

    def calculate_health_score(self, metrics: CardEffectMetrics) -> HealthAssessment:
        """计算健康度"""
        pass

    def generate_report(self, period: str) -> dict:
        """生成评估报告"""
        pass
```
