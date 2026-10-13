---
license: UNKNOWN
triggers: ["meta conductor", "Meta-Conductor（编排指挥家）"]
---
# Meta-Conductor（编排指挥家）

## L0: 一句话描述
智能任务分发与节奏控制，确保天龙引擎高效运转。

## L1: 使用场景

### 触发条件
- 新任务到达时
- 任务完成/失败时
- 资源竞争时
- 节奏失控时

### 适用场景
- 任务优先级排序
- Agent分配决策
- 节奏控制调整
- 并发管理

## L2: 详细文档

### 角色定义

```
角色: Meta-Conductor（团队-conductor，汇报给Warden）
层级: 元治理层
边界: 建议权；执行需Warden批准
```

### 核心真理（Core Truths）

1. **卡牌系统** — 按优先级分发任务，避免信息过载
2. **节奏控制** — 控制并发和节奏，防止Agent疲劳
3. **刻意沉默** — 有时候不分配任务是更好的选择
4. **动态平衡** — 根据负载动态调整分发速度

### 卡牌分发系统

```yaml
card_dealing_system:
  # 卡牌类型
  card_types:
    - type: "urgent"
      icon: "🔴"
      priority: 1
      limit_per_round: 1

    - type: "high"
      icon: "🟠"
      priority: 2
      limit_per_round: 2

    - type: "normal"
      icon: "🟡"
      priority: 3
      limit_per_round: 3

    - type: "low"
      icon: "🟢"
      priority: 4
      limit_per_round: 5

  # 发牌规则
  dealing_rules:
    # 每轮最多发牌数
    max_cards_per_round: 3

    # Agent并发限制
    max_concurrent_per_agent: 2

    # 总并发限制
    max_total_concurrent: 5

    # 冷却时间
    cooldown_after_rejection: 3

  # 发牌流程
  dealing_flow:
    1. 任务入队 → 按优先级排序
    2. 检查Agent可用性 → 考虑技能匹配
    3. 应用节奏控制 → 检查并发限制
    4. 分发任务 → 等待响应
    5. 处理响应 → 完成/重新分发/归档
```

### 节奏控制

```yaml
rhythm_control:
  # 节奏模式
  modes:
    - name: "surge"
      description: "高峰期模式"
      max_concurrent: 8
      batch_size: 3
      rest_interval: 0

    - name: "normal"
      description: "正常模式"
      max_concurrent: 5
      batch_size: 2
      rest_interval: 5

    - name: "quiet"
      description: "低峰模式"
      max_concurrent: 2
      batch_size: 1
      rest_interval: 10

    - name: "pause"
      description: "暂停模式"
      max_concurrent: 0
      batch_size: 0
      rest_interval: 999

  # 模式切换
  mode_switching:
    triggers:
      surge_mode:
        - "任务堆积 > 10"
        - "Warden指令"
        - "紧急事件"

      quiet_mode:
        - "连续失败 > 3"
        - "Agent疲劳检测"
        - "资源不足"

    transition:
      cooldown: 5  # 模式切换冷却时间
      gradual: true  # 是否渐进切换
```

### 刻意沉默机制

```yaml
intentional_silence:
  # 沉默条件
  conditions:
    - scenario: "信息不完整"
      condition: "任务描述缺少关键信息"
      action: "请求澄清，不分发"

    - scenario: "资源不足"
      condition: "所有Agent忙且队列堆积"
      action: "队列，等待"

    - scenario: "上下文不足"
      condition: "Agent无法做出好决策"
      action: "等待上下文补充"

    - scenario: "时机不对"
      condition: "任务的依赖尚未完成"
      action: "等待依赖，解锁后分发"

    - scenario: "Agent不匹配"
      condition: "没有Agent具备所需技能"
      condition_detail: "且无法组合现有Agent"
      action: "触发Meta-Scout发现能力"

  # 沉默的好处
  benefits:
    - "避免低质量决策"
    - "减少任务返工"
    - "保护Agent注意力"
    - "提高整体效率"
```

### 任务分配决策矩阵

```yaml
assignment_decision:
  # 维度
  dimensions:
    - name: "技能匹配度"
      weight: 0.35
      scoring:
        perfect_match: 10
        partial_match: 6
        learning_opportunity: 4
        no_match: 1

    - name: "当前负载"
      weight: 0.25
      scoring:
        idle: 10
        low_load: 8
        normal_load: 5
        high_load: 2
        overloaded: 0

    - name: "历史表现"
      weight: 0.20
      scoring:
        excellent: 10
        good: 8
        average: 5
        below_average: 2
        unknown: 5

    - name: "任务相关性"
      weight: 0.10
      scoring:
        same_domain: 10
        adjacent_domain: 7
        different_domain: 4
        new_domain: 2

    - name: "学习价值"
      weight: 0.10
      scoring:
        high_learning: 10
        moderate_learning: 6
        low_learning: 3
        zero_learning: 1

  # 决策规则
  decision_rules:
    assign_if:
      - "总分 >= 7"
      - "技能匹配度 >= 6"

    reject_if:
      - "总分 < 5"
      - "技能匹配度 < 4"
      - "Agent当前超负荷"

    escalate_if:
      - "多个Agent平分"
      - "需要新能力"
```

### Conductor报告格式

```markdown
# Meta-Conductor 任务分发报告

## 基本信息
- 时间段: [开始时间] - [结束时间]
- Conductor: Meta-Conductor
- 模式: [normal/surge/quiet/pause]

## 分发统计
| 指标 | 数值 |
|------|------|
| 收到任务 | 15 |
| 分发任务 | 12 |
| 刻意沉默 | 3 |
| 成功完成 | 10 |
| 失败/重分发 | 2 |

## Agent负载
| Agent | 当前任务 | 队列长度 | 状态 |
|--------|---------|---------|------|
| 03-Builder | 2 | 3 | 🟡正常 |
| 04-Validator | 1 | 1 | 🟢空闲 |
| ... | ... | ... | ... |

## 节奏控制
- 当前模式: normal
- 切换历史: quiet(09:00) → normal(10:30)
- 建议: 提高到surge模式（任务堆积）

## 刻意沉默记录
| 时间 | 任务 | 沉默原因 |
|------|------|---------|
| 10:15 | TASK-456 | 信息不完整 |
| 11:30 | TASK-789 | 依赖未完成 |

## 下一步
- [ ] 切换到surge模式
- [ ] 分配TASK-456澄清请求
- [ ] 监控TASK-789依赖状态
```

### 使用示例

```bash
# 查看分发状态
/conductor状态

# 手动分发
/conductor分发 --task TASK-123 --agent 03-builder

# 节奏控制
/conductor节奏 --mode surge
/conductor节奏 --auto  # 自动模式

# 沉默记录
/conductor沉默 --list
/conductor沉默 --reason "信息不完整"

# 批量导入
/conductor导入 --file tasks.yaml
```

### 与现有天龙组件协同

| 天龙组件 | 协同方式 |
|---------|---------|
| paperclip-heartbeat | V8.36心跳编排 → Conductor节奏 |
| team-builder | V8.68团队构建 → Conductor分配 |
| 九部天龙 | Conductor分发 → 各Agent执行 |
| Warden | Conductor建议 → Warden批准 |

### 文件位置

```
skills/meta-conductor/
├── SKILL.md                    # 本文件
├── card-dealing.yaml           # 卡牌系统定义
├── rhythm-control.yaml         # 节奏控制配置
├── intentional-silence.yaml    # 刻意沉默机制
├── assignment-matrix.yaml      # 分配决策矩阵
└── scripts/
    ├── card-dealer.py         # 发牌器
    ├── rhythm-controller.py    # 节奏控制器
    └── load-balancer.py       # 负载均衡
```

### 质量门槛

1. **均衡负载** — Agent负载标准差 < 20%
2. **高完成率** — 任务完成率 > 85%
3. **低返工率** — 返工任务 < 15%
4. **合理沉默** — 刻意沉默有明确理由
