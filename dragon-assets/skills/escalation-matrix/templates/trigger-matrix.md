# 升级触发矩阵模板
# Trigger Matrix Template
# 基于 组织镜像4标准 设计

---

## 触发矩阵概述

升级触发矩阵定义何时、从哪个条件触发升级，以及升级的目标层级和处理时限。

---

## 触发条件分类

### 1. 执行层(L1)触发条件

| 触发条件 | 描述 | 阈值 | 触发目标 | 处理时限 |
|---------|------|------|---------|---------|
| `retry_exceeded` | 重试次数超限 | 重试次数 > 3 | L2 | 5分钟 |
| `time_exceeded` | 执行时间超限 | 执行时间 > SLA | L2 | 即时 |
| `error_type_blacklist` | 特定错误类型 | 错误类型 in 黑名单 | L2 | 即时 |
| `unknown_error` | 无法识别的错误 | 错误类型 unknown | L2 | 即时 |
| `resource_exhausted` | 资源耗尽 | 资源使用率 > 100% | L2 | 5分钟 |
| `impact_level` | 影响范围超限 | 影响范围 > 阈值 | L2 | 即时 |

### 2. 编排层(L2)触发条件

| 触发条件 | 描述 | 阈值 | 触发目标 | 处理时限 |
|---------|------|------|---------|---------|
| `coordination_failed` | 协调无效 | 协调尝试 > 3次 | L3 | 10分钟 |
| `dependency_blocked` | 依赖方不可用 | 依赖状态 = unavailable | L3 | 10分钟 |
| `resource_exhausted` | 资源完全耗尽 | 资源使用率 > 100% | L3 | 10分钟 |
| `cross_system_impact` | 跨系统影响 | 影响系统数 > 1 | L3 | 即时 |
| `error_type_blacklist` | 特定错误类型 | 错误类型 in 黑名单 | L3 | 即时 |
| `escalation_from_l1` | L1升级上来的 | L1升级标记 | L3 | 5分钟 |

### 3. 治理层(L3)触发条件

| 触发条件 | 描述 | 阈值 | 触发目标 | 处理时限 |
|---------|------|------|---------|---------|
| `governance_ineffective` | 治理措施无效 | 治理尝试 > 3次 | L4 | 30分钟 |
| `business_decision_required` | 需要业务决策 | 决策类型 = business | L4 | 人工判断 |
| `core_function_impact` | 影响核心功能 | 影响核心功能 = true | L4 | 即时 |
| `cross_system_failure` | 多系统故障 | 故障系统数 > 2 | L4 | 即时 |
| `security_incident` | 安全事件 | 安全级别 >= 高 | L4 | 即时 |
| `resource_constraint` | 资源约束 | 需要资源调配 | L4 | 30分钟 |
| `escalation_from_l2` | L2升级上来的 | L2升级标记 | L4 | 15分钟 |

### 4. 决策层(L4)触发条件

| 触发条件 | 描述 | 最终处理 |
|---------|------|---------|
| `max_level_reached` | 达到最高层级 | 人工介入，启动危机响应 |
| `circular_escalation` | 循环升级 | 强制指定处理者 |
| `unrecoverable_state` | 不可恢复状态 | 启动灾难恢复 |

---

## 触发矩阵详细定义

### 触发矩阵YAML结构

```yaml
trigger_matrix:
  # ==========================================================================
  # L1执行层触发配置
  # ==========================================================================
  level_1_triggers:
    retry_exceeded:
      id: "retry_exceeded"
      level: 1
      source: "execution_layer"
      description: "重试次数超过预设阈值"
      condition:
        field: "retry_count"
        operator: ">"
        value: 3
      action:
        type: "escalate"
        target: "level_2"
        priority: "high"
      notification:
        - "level_2"
        - "level_1_parent"
      sla:
        max_response_time: "5分钟"
        warning_time: "3分钟"

    time_exceeded:
      id: "time_exceeded"
      level: 1
      source: "execution_layer"
      description: "执行时间超过SLA"
      condition:
        field: "execution_time"
        operator: ">"
        value: "${sla_threshold}"
      action:
        type: "escalate"
        target: "level_2"
        priority: "high"
      notification:
        - "level_2"
      sla:
        max_response_time: "即时"
        warning_time: "N/A"

    error_type_blacklist:
      id: "error_type_blacklist"
      level: 1
      source: "execution_layer"
      description: "遇到黑名单中的错误类型"
      condition:
        field: "error_type"
        operator: "in"
        value: "${error_blacklist}"
      action:
        type: "escalate"
        target: "level_2"
        priority: "critical"
      notification:
        - "level_2"
        - "level_1_parent"
      sla:
        max_response_time: "即时"
        warning_time: "N/A"

    unknown_error:
      id: "unknown_error"
      level: 1
      source: "execution_layer"
      description: "无法识别的错误类型"
      condition:
        field: "error_recognizable"
        operator: "=="
        value: false
      action:
        type: "escalate"
        target: "level_2"
        priority: "medium"
      notification:
        - "level_2"
      sla:
        max_response_time: "5分钟"
        warning_time: "2分钟"

  # ==========================================================================
  # L2编排层触发配置
  # ==========================================================================
  level_2_triggers:
    coordination_failed:
      id: "coordination_failed"
      level: 2
      source: "orchestration_layer"
      description: "多Agent协调无效"
      condition:
        field: "coordination_attempts"
        operator: ">"
        value: 3
      action:
        type: "escalate"
        target: "level_3"
        priority: "high"
      notification:
        - "level_3"
        - "level_2_parent"
      sla:
        max_response_time: "10分钟"
        warning_time: "5分钟"

    dependency_blocked:
      id: "dependency_blocked"
      level: 2
      source: "orchestration_layer"
      description: "依赖方不可用"
      condition:
        field: "dependency_status"
        operator: "in"
        value: ["unavailable", "failed", "timeout"]
      action:
        type: "escalate"
        target: "level_3"
        priority: "high"
      notification:
        - "level_3"
      sla:
        max_response_time: "10分钟"
        warning_time: "5分钟"

    cross_system_impact:
      id: "cross_system_impact"
      level: 2
      source: "orchestration_layer"
      description: "影响多个系统"
      condition:
        field: "affected_systems_count"
        operator: ">"
        value: 1
      action:
        type: "escalate"
        target: "level_3"
        priority: "critical"
      notification:
        - "level_3"
        - "level_2_parent"
        - "stakeholders"
      sla:
        max_response_time: "即时"
        warning_time: "N/A"

    resource_exhausted:
      id: "resource_exhausted"
      level: 2
      source: "orchestration_layer"
      description: "资源完全耗尽"
      condition:
        field: "resource_utilization"
        operator: ">"
        value: 100
      action:
        type: "escalate"
        target: "level_3"
        priority: "high"
      notification:
        - "level_3"
      sla:
        max_response_time: "10分钟"
        warning_time: "5分钟"

  # ==========================================================================
  # L3治理层触发配置
  # ==========================================================================
  level_3_triggers:
    governance_ineffective:
      id: "governance_ineffective"
      level: 3
      source: "governance_layer"
      description: "治理措施无效"
      condition:
        field: "governance_attempts"
        operator: ">"
        value: 3
      action:
        type: "escalate"
        target: "level_4"
        priority: "critical"
      notification:
        - "level_4"
        - "level_3_parent"
        - "stakeholders"
      sla:
        max_response_time: "30分钟"
        warning_time: "15分钟"

    business_decision_required:
      id: "business_decision_required"
      level: 3
      source: "governance_layer"
      description: "需要业务决策"
      condition:
        field: "decision_type"
        operator: "=="
        value: "business"
      action:
        type: "escalate"
        target: "level_4"
        priority: "high"
      notification:
        - "level_4"
        - "decision_makers"
      sla:
        max_response_time: "人工判断"
        warning_time: "N/A"

    core_function_impact:
      id: "core_function_impact"
      level: 3
      source: "governance_layer"
      description: "影响核心功能"
      condition:
        field: "core_function_affected"
        operator: "=="
        value: true
      action:
        type: "escalate"
        target: "level_4"
        priority: "critical"
      notification:
        - "level_4"
        - "stakeholders"
        - "emergency_team"
      sla:
        max_response_time: "即时"
        warning_time: "N/A"

    security_incident:
      id: "security_incident"
      level: 3
      source: "governance_layer"
      description: "安全事件"
      condition:
        field: "security_level"
        operator: ">="
        value: "high"
      action:
        type: "escalate"
        target: "level_4"
        priority: "critical"
        bypass_normal_path: true
      notification:
        - "level_4"
        - "security_team"
        - "emergency_team"
      sla:
        max_response_time: "即时"
        warning_time: "N/A"

  # ==========================================================================
  # L4决策层触发配置
  # ==========================================================================
  level_4_triggers:
    max_level_reached:
      id: "max_level_reached"
      level: 4
      source: "decision_layer"
      description: "达到最高层级仍无法解决"
      action:
        type: "manual_intervention"
        target: "human_operator"
        priority: "critical"
      notification:
        - "human_operator"
        - "emergency_team"
        - "management"
      sla:
        max_response_time: "人工响应"
        warning_time: "N/A"

    circular_escalation:
      id: "circular_escalation"
      level: 4
      source: "decision_layer"
      description: "检测到循环升级"
      action:
        type: "force_assignment"
        target: "designated_handler"
        priority: "critical"
      notification:
        - "designated_handler"
        - "management"
      sla:
        max_response_time: "10分钟"
        warning_time: "5分钟"

    unrecoverable_state:
      id: "unrecoverable_state"
      level: 4
      source: "decision_layer"
      description: "系统进入不可恢复状态"
      action:
        type: "disaster_recovery"
        target: "disaster_recovery_plan"
        priority: "critical"
      notification:
        - "all_stakeholders"
        - "emergency_team"
      sla:
        max_response_time: "即时"
        warning_time: "N/A"
```

---

## 触发条件权重

### 紧急升级路径（跳过中间层）

```yaml
urgent_escalation_paths:
  triggers:
    - security_incident          # 安全事件
    - data_loss_risk            # 数据丢失风险
    - core_function_failure     # 核心功能故障
    - cross_system_failure       # 多系统同时故障

  normal_path: "L1 → L2 → L3 → L4"
  urgent_path: "L1 → L4 (跳过L2和L3)"

  conditions:
    bypass_intermediate_levels: true
    parallel_notification: true
    immediate_escalation: true
```

### 触发优先级排序

| 优先级 | 触发条件 | 说明 |
|-------|---------|------|
| P0 | security_incident | 安全事件，最高优先级 |
| P0 | core_function_impact | 核心功能影响 |
| P0 | unrecoverable_state | 不可恢复状态 |
| P1 | cross_system_failure | 跨系统故障 |
| P1 | data_loss_risk | 数据丢失风险 |
| P2 | governance_ineffective | 治理无效 |
| P2 | coordination_failed | 协调失败 |
| P3 | retry_exceeded | 重试超限 |
| P3 | time_exceeded | 时间超限 |
| P4 | unknown_error | 未知错误 |

---

## 触发决策流程

### 触发决策流程图

```
┌─────────────────────────────────────────────────────────────┐
│                     触发决策流程                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Step 1: 检测触发条件                                       │
│  ├── 监控执行状态                                          │
│  ├── 收集指标数据                                          │
│  └── 评估触发条件                                          │
│                         ↓                                    │
│  Step 2: 判断触发类型                                      │
│  ├── 正常升级 → 按路径 L1→L2→L3→L4                     │
│  └── 紧急升级 → 跳过中间层直达L4                          │
│                         ↓                                    │
│  Step 3: 执行升级动作                                      │
│  ├── 保存执行上下文                                        │
│  ├── 通知目标层级                                          │
│  └── 传递升级信息                                          │
│                         ↓                                    │
│  Step 4: 记录升级事件                                      │
│  ├── 记录触发原因                                          │
│  ├── 记录升级路径                                          │
│  └── 更新元经验库                                          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 触发条件判断伪代码

```python
def evaluate_escalation_trigger(current_level, metrics):
    """评估是否满足触发条件"""

    # 获取当前层级的触发配置
    trigger_config = get_trigger_config(current_level)

    # 遍历所有触发条件
    for trigger in trigger_config.conditions:
        if evaluate_condition(trigger, metrics):
            # 检查是否为紧急触发
            if is_urgent_trigger(trigger):
                return escalate_urgent(trigger)
            else:
                return escalate_normal(trigger)

    return no_escalation()

def is_urgent_trigger(trigger):
    """判断是否为紧急触发"""
    urgent_types = [
        "security_incident",
        "core_function_impact",
        "unrecoverable_state",
        "data_loss_risk",
        "cross_system_failure"
    ]
    return trigger.id in urgent_types
```

---

## 触发阈值配置

### 动态阈值配置

```yaml
dynamic_thresholds:
  # 根据系统负载动态调整阈值
  load_based_adjustment:
    enabled: true
    adjustment_factors:
      high_load:
        retry_threshold: 2      # 高负载时降低阈值
        time_multiplier: 0.8    # 时间阈值乘数
      normal_load:
        retry_threshold: 3
        time_multiplier: 1.0
      low_load:
        retry_threshold: 5
        time_multiplier: 1.5

  # 根据任务优先级调整阈值
  priority_based_adjustment:
    critical:
      time_threshold_multiplier: 0.5  # 关键任务更快速升级
      retry_threshold: 1
    high:
      time_threshold_multiplier: 0.75
      retry_threshold: 2
    normal:
      time_threshold_multiplier: 1.0
      retry_threshold: 3
    low:
      time_threshold_multiplier: 1.5
      retry_threshold: 5
```

---

## 触发统计与分析

### 触发统计指标

```yaml
trigger_statistics:
  metrics:
    - name: "trigger_count"
      description: "触发次数统计"
      aggregation: "count"
      group_by: ["level", "trigger_type"]

    - name: "escalation_rate"
      description: "升级率"
      calculation: "trigger_count / total_tasks"
      unit: "percentage"

    - name: "escalation_latency"
      description: "升级延迟"
      aggregation: "avg, max, p95"
      unit: "seconds"

    - name: "false_positive_rate"
      description: "误触发率"
      calculation: "false_positive / trigger_count"
      unit: "percentage"

    - name: "repeat_escalation_count"
      description: "重复触发次数"
      aggregation: "count"
      filter: "same_trigger_within_5min"

  alerts:
    - name: "escalation_rate_high"
      condition: "escalation_rate > 20%"
      severity: "warning"

    - name: "circular_escalation_detected"
      condition: "same_task_escalated > 3"
      severity: "critical"

    - name: "false_positive_rate_high"
      condition: "false_positive_rate > 10%"
      severity: "warning"
```

---

## 版本历史

```yaml
versions:
  - version: "1.0.0"
    date: "2026-04-24"
    author: "天龙引擎"
    changes:
      - "初始版本"
```
