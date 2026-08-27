# 节奏设计提示词模板 - 任务流节奏引导框架

> **版本**: V1.0
> **来源**: 天龙引擎V9.02 × 老金元组织方法论
> **用途**: 引导用户完成多Agent协作的节奏设计

---

## 节奏设计引导流程

```
┌─────────────────────────────────────────────────────────────┐
│                  节奏设计5步法                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Step 1: 任务复杂度评估                                    │
│     → 识别任务的计算/沟通/等待比例                        │
│                                                             │
│  Step 2: Agent能力映射                                    │
│     → 将任务分配给具有相应能力的Agent                      │
│                                                             │
│  Step 3: 依赖关系分析                                      │
│     → 确定任务间的串行/并行关系                            │
│                                                             │
│  Step 4: 节奏强度选择                                      │
│     → 根据复杂度选择轻量/标准/重载节奏                    │
│                                                             │
│  Step 5: 时序参数调优                                      │
│     → 设定启动间隔、轮询周期、超时阈值                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Step 1: 任务复杂度评估

### 引导问题

```
┌─────────────────────────────────────────────────────────────┐
│ 任务复杂度评估 - 灵魂三问                                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ 1. 任务的计算密集度如何？                                 │
│    → 代码生成/数据分析/模型推理等CPU密集型？             │
│    → 还是以通信/协调/等待为主？                           │
│                                                             │
│ 2. 任务的沟通频率需求？                                  │
│    → 需要频繁的信息交换？                                 │
│    → 还是以独立执行为主？                                 │
│                                                             │
│ 3. 任务的等待敏感度？                                    │
│    → 对延迟的容忍度如何？                                 │
│    → 有硬性截止时间吗？                                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 复杂度计算公式

```python
complexity = (
    compute_ratio * compute_weight +      # 计算密集度
    communication_ratio * comm_weight +    # 沟通频率
    waiting_tolerance * wait_weight        # 等待容忍度
)

# 复杂度分级
if complexity < 0.3:    → 简单任务 (轻量节奏)
elif complexity < 0.6:   → 中等任务 (标准节奏)
elif complexity < 0.8:   → 复杂任务 (重载节奏)
else:                     → 超复杂任务 (定制节奏)
```

---

## Step 2: Agent能力映射

### Agent能力矩阵

| Agent | 计算能力 | 沟通能力 | 并行容量 | 最佳节奏 |
|-------|---------|---------|---------|---------|
| 01调研师 | 高 | 中 | 低 | 深度探索 |
| 02架构师 | 中 | 高 | 中 | 评审协调 |
| 03构建师 | 极高 | 低 | 高 | 批量执行 |
| 04验证师 | 高 | 中 | 中 | 循环验证 |
| 05安全师 | 高 | 中 | 低 | 专项审查 |
| 06审查师 | 中 | 高 | 中 | 综合评估 |

### 能力匹配决策树

```
┌─────────────────────────────────────────────────────────────┐
│ 能力匹配决策树                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ 任务类型 = 计算密集？                                      │
│   ├─ 是 → 优先分配给03构建师                             │
│   │         ↓                                             │
│   │      并行容量足够？                                    │
│   │         ├─ 是 → 批量分配                             │
│   │         └─ 否 → 串行队列                            │
│   │                                                         │
│   └─ 否 → 任务类型 = 沟通密集？                          │
│             ├─ 是 → 优先分配给02架构师/06审查师          │
│             │         ↓                                   │
│             │      需要多轮协调？                         │
│             │         ├─ 是 → 启用评审节奏                 │
│             │         └─ 否 → 单轮协调                   │
│             │                                                 │
│             └─ 否 → 任务类型 = 验证密集？                │
│                       ├─ 是 → 分配给04验证师             │
│                       │         ↓                         │
│                       │      验证频率？                    │
│                       │         ├─ 高 → 实时验证节奏       │
│                       │         └─ 低 → 批量验证节奏       │
│                       │                                         │
│                       └─ 否 → 分配给05安全师              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Step 3: 依赖关系分析

### 依赖类型矩阵

| 依赖类型 | 符号 | 含义 | 对节奏的影响 |
|---------|------|------|------------|
| 完成依赖 | FS | 必须等待前置任务完成 | 强制串行 |
| 开始依赖 | SS | 必须等待前置任务开始 | 可并行启动 |
| 完成-开始 | FS | A完成后B开始 | 标准串行 |
| 开始-开始 | SS | A开始后B开始 | 并行启动 |
| 包含依赖 | CN | A包含B | 嵌套节奏 |

### 依赖图生成

```yaml
dependency_graph:
  nodes:
    - id: "task_1"
      name: "需求分析"
      type: "start"
      duration: "5m"

    - id: "task_2"
      name: "架构设计"
      type: "normal"
      depends_on: ["task_1"]

    - id: "task_3a"
      name: "前端开发"
      type: "normal"
      depends_on: ["task_2"]

    - id: "task_3b"
      name: "后端开发"
      type: "normal"
      depends_on: ["task_2"]

    - id: "task_4"
      name: "集成测试"
      type: "end"
      depends_on: ["task_3a", "task_3b"]
```

---

## Step 4: 节奏强度选择

### 节奏强度分级

```yaml
rhythm_intensity:
  lightweight:
    name: "轻量节奏"
    trigger_interval: "1s"
    poll_interval: "5s"
    timeout_threshold: "30s"
    parallel_limit: 3
    use_case: "简单任务、快速指令"

  standard:
    name: "标准节奏"
    trigger_interval: "5s"
    poll_interval: "30s"
    timeout_threshold: "5m"
    parallel_limit: 5
    use_case: "中等复杂度任务"

  heavy:
    name: "重载节奏"
    trigger_interval: "30s"
    poll_interval: "2m"
    timeout_threshold: "30m"
    parallel_limit: 10
    use_case: "复杂项目、多阶段任务"

  custom:
    name: "定制节奏"
    trigger_interval: "user_defined"
    poll_interval: "user_defined"
    timeout_threshold: "user_defined"
    parallel_limit: "user_defined"
    use_case: "超复杂任务、特殊需求"
```

### 强度选择决策矩阵

| 任务复杂度 | Agent数量 | 推荐强度 |
|-----------|----------|---------|
| 简单 | 1 | 轻量 |
| 简单 | 2-3 | 轻量 |
| 中等 | 1-2 | 轻量 |
| 中等 | 3-5 | 标准 |
| 复杂 | 2-4 | 标准 |
| 复杂 | 5+ | 重载 |
| 超复杂 | 任意 | 定制 |

---

## Step 5: 时序参数调优

### 时序参数定义

```yaml
timing_parameters:
  trigger_interval:
    description: "新任务触发检查间隔"
    unit: "秒"
    range: "1-60"
    recommendation:
      realtime: "1-5"
      batch: "30-60"

  poll_interval:
    description: "任务状态轮询间隔"
    unit: "秒"
    range: "5-300"
    recommendation:
      fast_response: "5-15"
      normal: "30-60"
      slow_check: "120-300"

  timeout_threshold:
    description: "任务超时阈值"
    unit: "分钟"
    range: "1-60"
    recommendation:
      quick_task: "1-5"
      normal_task: "5-15"
      long_task: "15-60"

  heartbeat_interval:
    description: "Agent心跳间隔"
    unit: "秒"
    range: "10-120"
    recommendation:
      active_task: "10-30"
      idle_wait: "60-120"
```

### 参数调优检查表

```
┌─────────────────────────────────────────────────────────────┐
│ 时序参数调优检查表                                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ 响应延迟                                                    │
│ □ 实时响应需求？ → trigger_interval ≤ 5s                   │
│ □ 可接受延迟？ → trigger_interval ≤ 30s                    │
│ □ 批量处理？ → trigger_interval ≤ 60s                      │
│                                                             │
│ 资源利用                                                    │
│ □ 高并发需求？ → parallel_limit 提高                       │
│ □ 资源受限？ → parallel_limit 降低                         │
│ □ 混合负载？ → 设置动态调整规则                           │
│                                                             │
│ 可靠性                                                    │
│ □ 长任务？ → timeout_threshold 提高                        │
│ □ 短任务？ → timeout_threshold 降低                       │
│ □ 关键任务？ → 设置告警阈值                               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 节奏设计输出模板

```yaml
rhythm_design_output:
  metadata:
    design_id: "RHY-YYYYMMDD-XXX"
    designer: "设计者"
    design_date: "YYYY-MM-DD"

  task_analysis:
    complexity_score: ___/1.0
    complexity_level: "简单/中等/复杂/超复杂"
    compute_ratio: ___%
    communication_ratio: ___%
    waiting_tolerance: "高/中/低"

  agent_mapping:
    primary_agents:
      - agent_id: "01"
        role: "职责"
        allocation: ___%

      - agent_id: "02"
        role: "职责"
        allocation: ___%

    parallel_capacity: ___个Agent并发

  dependency_structure:
    is_parallel: true/false
    critical_path: ["task_1", "task_2", ...]
    critical_path_duration: "___m"

  rhythm_configuration:
    intensity_level: "轻量/标准/重载/定制"
    trigger_interval: "___s"
    poll_interval: "___s"
    timeout_threshold: "___m"
    parallel_limit: ___

  expected_metrics:
    throughput: "___任务/分钟"
    avg_latency: "___秒"
    resource_utilization: "___%"
```

---

## 版本历史

```yaml
versions:
  - version: "1.0.0"
    date: "YYYY-MM-DD"
    author: "作者"
    changes:
      - "初始版本"
```
