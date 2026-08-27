---
license: UNKNOWN
triggers: ["card dealing", "card-dealing - 发牌机制"]
---
# card-dealing - 发牌机制

> **版本**: V1.0
> **来源**: 老金元组织方法论 × 天龙引擎V8.96
> **核心**: 发牌三原则 + 发牌质量评估 + 噪音检测

---

## 核心概念

### 什么是"发牌"？

**发牌** = 系统在当前状态下，决定释放什么信息、什么动作机会、什么推进路径，来推动下一步更合理地发生。

### 发牌 ≠ 通知/提示/弹窗

| 错误理解 | 正确理解 |
|---------|---------|
| 发个提醒出来 | 推动下一步更合理地发生 |
| 看见触点就推 | 看当前最该推进什么 |
| 系统很勤奋 | 节奏治理的一部分 |
| 能发就发 | 知道什么不该发 |

### 发牌三原则

```
┌─────────────────────────────────────────────────────────────┐
│ 一张牌是否成立，至少看三件事                                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ 1. 它有没有减少用户的不确定性？                              │
│    → 如果不减少，没有价值                                   │
│                                                             │
│ 2. 它有没有提高下一步动作的清晰度？                          │
│    → 如果不提高，没有价值                                   │
│                                                             │
│ 3. 它有没有过度打断用户当前任务？                            │
│    → 如果过度打断，反而有害                                 │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 发牌质量评估矩阵

### 基础评估

```
┌─────────────────────────────────────────────────────────────┐
│ 发牌质量评估表                                              │
├─────────────────────────────────────────────────────────────┤
│ 牌ID: ________________                                      │
│ 牌类型: [提醒/提示/推荐/动作/信息]                          │
│                                                             │
│ 原则1: 减少不确定性                                        │
│ □ 用户知道发生了什么（Y/N）: ____                          │
│ □ 用户知道为什么发生（Y/N）: ____                           │
│ □ 不确定性减少量: [高/中/低]                                │
│                                                             │
│ 原则2: 提高动作清晰度                                       │
│ □ 下一步动作明确（Y/N）: ____                              │
│ □ 用户知道怎么做（Y/N）: ____                              │
│ □ 动作完成标准清晰（Y/N）: ____                            │
│                                                             │
│ 原则3: 不过度打断                                          │
│ □ 当前任务重要度: [高/中/低]                               │
│ □ 打断侵入度: [高/中/低]                                   │
│ □ 打断成本 > 收益?（Y/N）: ____                            │
│                                                             │
│ 质量评分: _____/15                                         │
│ 是否发牌: □是 □否 □需调整时机                               │
└─────────────────────────────────────────────────────────────┘
```

### 扩展评估维度

```yaml
quality_dimensions:
  necessity:
    # 这张牌是否必要？
    - question: "没有这张牌，系统能正常工作吗？"
      if_yes: "考虑不发牌"

    - question: "这张牌能改变什么结果吗？"
      if_no: "考虑不发牌"

    - question: "用户会因为没有这张牌而损失吗？"
      if_no: "考虑不发牌"

  timing:
    # 发牌时机是否合适？
    - question: "用户当前是否有余力接收？"
      factors:
        - 任务专注度
        - 认知负载
        - 情绪状态

    - question: "这个时机是否最优？"
      alternatives:
        - 任务完成后
        - 关键节点后
        - 用户主动询问时

  value:
    # 发的牌是否有价值？
    - question: "这张牌能带来什么改变？"
      metrics:
        - 不确定性减少量
        - 动作清晰度提升
        - 效率改善预估

    - question: "这个价值值得打断吗？"
      formula: "价值 > 打断成本 ? 发牌 : 不发"

  cost:
    # 发牌的成本是什么？
    direct_costs:
      - 用户注意力争夺
      - 任务中断恢复时间
      - 认知切换损耗

    indirect_costs:
      - 用户信任度降低
      - 系统被感知为"烦人"
      - 关键信息被淹没
```

---

## 发牌时机决策树

```
                    发牌请求
                        │
                        ▼
              ┌─────────────────┐
              │ 是否减少不确定性 │ ──否──▶ 不发牌
              └────────┬────────┘
                        │是
                        ▼
              ┌─────────────────┐
              │ 提高动作清晰度 │ ──否──▶ 不发牌
              └────────┬────────┘
                        │是
                        ▼
              ┌─────────────────┐
              │ 打断成本>收益?  │ ──是──▶ 不发/延后
              └────────┬────────┘
                        │否
                        ▼
              ┌─────────────────┐
              │  用户当前状态   │
              │  适合接收吗？   │ ──否──▶ 延后
              └────────┬────────┘
                        │是
                        ▼
                    ✓ 发牌
```

---

## 发牌类型分类

### 1. 信息牌（Information Card）

```yaml
type: information
purpose: 告知状态变化
trigger: 状态发生重要变化
examples:
  - "任务已完成"
  - "部署成功"
  - "检测到异常"

design:
  certainty_reduction: high
  action_clarity: low
  interruption: minimal
  recommendation: "低侵入，可随时发送"
```

### 2. 确认牌（Confirmation Card）

```yaml
type: confirmation
purpose: 请求用户确认
trigger: 需要用户决策
examples:
  - "是否继续？"
  - "确认执行此操作？"
  - "这个方向对吗？"

design:
  certainty_reduction: medium
  action_clarity: high
  interruption: medium
  recommendation: "必要时发牌，避免频繁确认"
```

### 3. 推荐牌（Recommendation Card）

```yaml
type: recommendation
purpose: 提供建议
trigger: 系统发现更好方案
examples:
  - "建议使用缓存"
  - "这个API有更快的替代方案"
  - "可以考虑并行执行"

design:
  certainty_reduction: medium
  action_clarity: medium
  interruption: medium
  recommendation: "可选性建议，非强制"
```

### 4. 动作牌（Action Card）

```yaml
type: action
purpose: 推动关键动作
trigger: 必须由用户完成的步骤
examples:
  - "需要您授权"
  - "请审查此方案"
  - "需要填写配置"

design:
  certainty_reduction: high
  action_clarity: high
  interruption: necessary
  recommendation: "关键动作必须推送，但需精简"
```

### 5. 警示牌（Warning Card）

```yaml
type: warning
purpose: 提醒潜在风险
trigger: 检测到风险信号
examples:
  - "检测到性能下降"
  - "配置可能有问题"
  - "即将超过配额"

design:
  certainty_reduction: high
  action_clarity: medium
  interruption: necessary
  recommendation: "高风险必须推送"
```

---

## 发牌噪音检测

### 噪音类型

```yaml
noise_types:
  - type: "over_notification"
    symptom: "发牌频率过高"
    threshold: "> 3张/分钟"
    impact: "用户开始忽略所有提醒"

  - type: "low_value_spam"
    symptom: "大量低价值牌"
    threshold: "价值评分 < 5/15"
    impact: "重要牌被淹没"

  - type: "wrong_timing"
    symptom: "时机不当"
    threshold: "用户负反馈 > 10%"
    impact: "用户体验严重下降"

  - type: "contradiction"
    symptom: "牌之间矛盾"
    threshold: "存在逻辑冲突"
    impact: "用户困惑"
```

### 噪音审计检查表

```
┌─────────────────────────────────────────────────────────────┐
│ 发牌噪音审计表                                              │
├─────────────────────────────────────────────────────────────┤
│ 时间范围: [开始时间] - [结束时间]                            │
│                                                             │
│ 数量统计:                                                  │
│ - 总发牌数: ____                                            │
│ - 平均每分钟: ____                                          │
│ - 峰值分钟: ____张                                          │
│                                                             │
│ 质量分布:                                                  │
│ - 高质量(12-15分): ____%                                    │
│ - 中质量(8-11分): ____%                                     │
│ - 低质量(0-7分): ____%                                     │
│                                                             │
│ 噪音检测:                                                  │
│ □ 发牌频率 > 3张/分钟（Y/N）: ____                         │
│ □ 低价值牌占比 > 30%（Y/N）: ____                           │
│ □ 用户忽略率 > 20%（Y/N）: ____                             │
│ □ 存在矛盾牌（Y/N）: ____                                  │
│                                                             │
│ 审计结论:                                                  │
│ 发牌健康度: [优秀/良好/警告/危险]                           │
│ 主要问题: ________________________________________________ │
│ 优化建议: ________________________________________________ │
└─────────────────────────────────────────────────────────────┘
```

---

## 发牌协议设计模板

```yaml
# card-protocol.yaml

card_id: "牌ID"
card_name: "牌名称"

# 基本属性
type: [information/confirmation/recommendation/action/warning]
channel: [inline/toast/modal/notification]
priority: [P0_CRITICAL/P1_HIGH/P2_MEDIUM/P3_LOW]

# 三原则评估
quality:
  necessity:
    required: true/false
    reason: "为什么必须发"

  timing:
    optimal: "最佳时机"
    alternatives: ["备选时机1", "备选时机2"]
    forbidden: "禁止时机"

  value:
    certainty_reduction: [high/medium/low]
    action_clarity: [high/medium/low]
    estimated_impact: "预估影响"

# 触发条件
trigger:
  conditions:
    - "条件1"
    - "条件2"

  cooldown: "冷却时间（避免重复发送）"
  max_frequency: "最大频率"

# 不发牌场景
skip_conditions:
  - "不发场景1"
  - "不发场景2"

# 用户控制
user_control:
  dismissible: true/false
  snoozeable: true/false
  permanent_hide: true/false
```

---

## 命令速查

```bash
# 发牌设计
/card-design <场景>               # 设计发牌协议
/card-protocol <牌ID>            # 生成发牌协议模板

# 发牌评估
/card-eval <牌>                   # 三原则质量评估
/card-matrix <系统>              # 评估所有发牌

# 发牌时机
/card-timing <牌>                # 分析发牌时机
/card-optimize-timing <牌>       # 优化发牌时机

# 噪音审计
/card-noise-audit <时间范围>     # 发牌噪音审计
/card-health                     # 发牌健康度检查

# 发牌管理
/card-list                      # 列出所有发牌
/card-disable <牌ID>             # 禁用低价值牌
/card-merge <牌A> <牌B>         # 合并矛盾牌
```

---

## 与其他技能协同

| 技能 | 协同方式 |
|------|---------|
| **rhythm-orchestration** | 节奏设计 → 发牌时机 |
| **silence-protocol** | 发牌决策 → 默认沉默 |
| **meta-design** | 元治理 → 发牌协议设计 |
| **escalation-matrix** | 警示牌触发 → 升级路径 |

---

## 适用场景

| 场景 | 发牌价值 |
|------|---------|
| 用户决策点 | 适时提供关键信息 |
| 风险预警 | 及时推送警示 |
| 效率优化 | 推荐更好方案 |
| 协作推进 | 推动关键动作 |
| 状态同步 | 减少不确定性 |

---

## 文件结构

```
card-dealing/
├── SKILL.md                         # 本文件
├── templates/
│   ├── card-protocol.yaml           # 发牌协议模板
│   ├── quality-matrix.md            # 质量评估矩阵
│   └── noise-audit.md               # 噪音审计模板
├── prompts/
│   ├── card-design-prompt.md        # 发牌设计提示词
│   ├── quality-eval-prompt.md        # 质量评估提示词
│   └── noise-detect-prompt.md       # 噪音检测提示词
└── scripts/
    ├── card-evaluator.py             # 发牌质量评估
    ├── noise-detector.py             # 噪音检测器
    ├── timing-optimizer.py           # 时机优化器
    └── card-manager.py               # 发牌管理器
```

---

## 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| V1.0 | 2026-04-24 | 初始版本，基于老金元组织方法论 |
