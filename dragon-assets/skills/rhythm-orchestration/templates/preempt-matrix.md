# 插队矩阵模板 (Preempt Protocol Matrix)

> **版本**: V1.0
> **用途**: 定义何时可以提升任务优先级的决策矩阵

---

## 插队协议概述

插队协议定义了Agent调度中"谁可以抢跑"的规则。核心原则：
- **插队必须有正当理由** - 不能随意打断正在执行的任务
- **插队有代价** - 需要保存当前状态、恢复上下文
- **插队需通知** - 所有相关方必须知道插队事件

---

## 插队决策矩阵

```yaml
preempt_matrix:
  version: "1.0"
  created: "YYYY-MM-DD"
  matrix_id: "PREEMPT-MATRIX-XXX"

  # ===== 插队类型定义 =====
  preempt_types:
    security_preempt:
      name: "安全插队"
      description: "安全相关任务必须立即执行"
      priority: "critical"
      threshold:
        risk_level: "high / critical"
        contains_security_keywords: true
        touches_auth_or_permissions: true
      actions:
        - "立即暂停当前任务（保存状态）"
        - "执行安全审查"
        - "通知安全师"
        - "恢复被中断任务"

    data_integrity_preempt:
      name: "数据完整性插队"
      description: "防止数据损坏或丢失的操作优先"
      priority: "high"
      threshold:
        modifies_critical_data: true
        bulk_operation: true
        no_transaction: true
      actions:
        - "备份当前状态"
        - "执行数据保护操作"
        - "记录数据变更"
        - "验证完整性"

    performance_preempt:
      name: "性能插队"
      description: "性能瓶颈或资源争用需要立即处理"
      priority: "medium"
      threshold:
        cpu_usage: "> 80%"
        memory_usage: "> 85%"
        response_time: "> 10s"
        error_rate: "> 5%"
      actions:
        - "触发性能优化"
        - "分配额外资源"
        - "启用缓存"
        - "降级非关键任务"

    user_interaction_preempt:
      name: "用户交互插队"
      description: "用户直接交互任务优先处理"
      priority: "high"
      threshold:
        user_is_waiting: true
        session_timeout_imminent: true
        explicit_user_request: true
      actions:
        - "优先处理用户请求"
        - "通知用户等待时间"
        - "后台任务降级"

    deadline_preempt:
      name: "截止时间插队"
      description: "接近截止时间的任务提升优先级"
      priority: "medium"
      threshold:
        time_to_deadline: "< 10分钟"
        task_impact: "high"
        downstream_dependencies: "> 3"
      actions:
        - "评估是否可以并行"
        - "通知其他任务延迟"
        - "加速执行"

  # ===== 插队决策规则 =====
  decision_rules:
    # 规则1: 安全关键
    rule_1:
      name: "安全漏洞检测"
      condition: "security_keyword_detected OR auth_tampering"
      action: "immediate_preempt"
      confidence: 1.0
      interrupt_level: "full"
      override: true

    # 规则2: 数据保护
    rule_2:
      name: "数据损坏预防"
      condition: "data_loss_risk AND no_backup"
      action: "preempt_with_backup"
      confidence: 0.95
      interrupt_level: "partial"
      override: true

    # 规则3: 性能告警
    rule_3:
      name: "性能降级响应"
      condition: "response_time > threshold AND user_impact > 50%"
      action: "preempt_optimize"
      confidence: 0.85
      interrupt_level: "minimal"
      override: false

    # 规则4: 用户等待
    rule_4:
      name: "用户体验优先"
      condition: "user_waiting_time > 30s AND task_is_blocking"
      action: "preempt_user_facing"
      confidence: 0.90
      interrupt_level: "minimal"
      override: false

    # 规则5: 截止时间紧迫
    rule_5:
      name: "Deadline响应"
      condition: "time_to_deadline < 10m AND task_critical"
      action: "preempt_accelerate"
      confidence: 0.80
      interrupt_level: "none"
      override: false
```

---

## 插队评估检查表

```markdown
## 插队评估检查表

### 1. 安全评估
- [ ] 涉及安全相关关键词？
- [ ] 操作认证或权限系统？
- [ ] 检测到安全漏洞？

### 2. 数据评估
- [ ] 修改关键数据？
- [ ] 批量操作无事务？
- [ ] 可能导致数据丢失？

### 3. 性能评估
- [ ] CPU使用率 > 80%？
- [ ] 响应时间 > 10秒？
- [ ] 错误率 > 5%？

### 4. 用户体验评估
- [ ] 用户正在等待？
- [ ] 会话即将超时？
- [ ] 显式用户请求？

### 5. 截止时间评估
- [ ] 距离截止 < 10分钟？
- [ ] 任务影响度高？
- [ ] 下游依赖 > 3个？

---

### 插队决策

| 检查项 | 结果 | 优先级提升 |
|--------|------|-----------|
| 安全插队 | ✅ / ❌ | CRITICAL |
| 数据完整性插队 | ✅ / ❌ | HIGH |
| 性能插队 | ✅ / ❌ | MEDIUM |
| 用户交互插队 | ✅ / ❌ | HIGH |
| 截止时间插队 | ✅ / ❌ | MEDIUM |

### 最终决策
- **立即插队**: 安全/数据关键任务，立即中断
- **延迟插队**: 性能/DL任务，等待当前任务完成
- **并行插队**: 用户交互任务，并行执行
- **不插队**: 正常调度
```

---

## 插队执行流程

```yaml
preempt_execution_flow:
  name: "插队执行流程"
  steps:
    - step: 1
      name: "检测插队条件"
      action: "评估是否满足插队阈值"
      tools: ["preempt-detector"]
      output: "preempt_signal"

    - step: 2
      name: "保存当前状态"
      action: "保存执行上下文、检查点"
      tools: ["state-snapshot"]
      output: "snapshot_id"
      required: true

    - step: 3
      name: "通知相关方"
      action: "通知编排协调师、被中断Agent"
      tools: ["notification-service"]
      output: "notifications_sent"

    - step: 4
      name: "执行插队任务"
      action: "高优先级任务执行"
      tools: ["preempt-task-executor"]
      output: "preempt_result"

    - step: 5
      name: "验证结果"
      action: "验证插队任务完成"
      tools: ["result-validator"]
      output: "validation_result"

    - step: 6
      name: "恢复被中断任务"
      action: "从检查点恢复执行"
      tools: ["state-restorer"]
      output: "restored_task_id"

    - step: 7
      name: "记录插队事件"
      action: "写入元经验库"
      tools: ["event-recorder"]
      output: "preempt_record_id"
```

---

## 插队记录格式

```yaml
preempt_records:
  - preempt_id: "PREEMPT-001"
    timestamp: "YYYY-MM-DDTHH:mm:ss"
    preempt_type: "security_preempt"
    preempt_task:
      id: "security_scan_01"
      name: "支付模块安全扫描"
      agent_id: "05"
      priority: "critical"
    interrupted_task:
      id: "user_auth_03"
      name: "用户认证开发"
      agent_id: "03"
      progress: "65%"
      snapshot_id: "SNAP-003"
    reason: "支付模块涉及资金安全，必须先完成安全审查"
    duration:
      interruption_time: "2m"
      resumed_time: "T+25m"
      total_impact: "2m"
    resolution:
      security_scan_result: "passed"
      resumed_from: "checkpoint_3"
      data_loss: "none"

  - preempt_id: "PREEMPT-002"
    timestamp: "YYYY-MM-DDTHH:mm:ss"
    preempt_type: "performance_preempt"
    preempt_task:
      id: "cache_warm_01"
      name: "缓存预热"
      agent_id: "03"
      priority: "medium"
    interrupted_task:
      id: "report_gen_02"
      name: "报表生成"
      agent_id: "03"
      progress: "30%"
      snapshot_id: "SNAP-004"
    reason: "CPU使用率95%，需要先清理缓存"
    resolution:
      cache_cleared: true
      cpu_normalized: "45%"
      resumed_from: "checkpoint_1"
```

---

## 版本历史

```yaml
versions:
  - version: "1.0.0"
    date: "YYYY-MM-DD"
    author: "天龙引擎"
    changes:
      - "初始版本"
```
