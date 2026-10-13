# 暂停矩阵模板 (Pause Protocol Matrix)

> **版本**: V1.0
> **用途**: 定义何时应该暂停任务执行的决策矩阵

---

## 暂停协议概述

暂停协议定义了Agent调度中"何时该等一等"的规则。核心原则：
- **暂停是为了更好的执行** - 不是失败，是策略性等待
- **暂停有明确条件** - 不能因为无法决策就暂停
- **暂停有时间限制** - 超时必须升级或采取行动

---

## 暂停决策矩阵

```yaml
pause_matrix:
  version: "1.0"
  created: "YYYY-MM-DD"
  matrix_id: "PAUSE-MATRIX-XXX"

  # ===== 暂停类型定义 =====
  pause_types:
    resource_contention:
      name: "资源争用暂停"
      description: "等待稀缺资源（API配额、数据库连接、外部服务）"
      threshold:
        resource_available: false
        wait_time: "> 30秒"
        alternative_resource: false
      actions:
        - "检查资源状态"
        - "尝试替代方案"
        - "设置超时提醒"
        - "通知协调师"

    backpressure:
      name: "背压暂停"
      description: "下游能力不足导致队列积压"
      threshold:
        queue_depth: "> 20"
        processing_rate: "< 50%"
        memory_usage: "> 80%"
      actions:
        - "启用背压控制"
        - "降低生产速率"
        - "扩容下游处理"
        - "通知编排协调师"

    circuit_breaker:
      name: "熔断器暂停"
      description: "检测到故障，暂停以防止级联失败"
      threshold:
        error_rate: "> 50%"
        timeout_count: "> 10"
        health_check_failed: true
      actions:
        - "触发熔断器"
        - "返回降级结果"
        - "启动健康检查"
        - "记录故障"

    dependency_pause:
      name: "依赖暂停"
      description: "等待前置任务或外部依赖完成"
      threshold:
        dependency_status: "pending / failed"
        estimated_wait: "> 5分钟"
        can_proceed_alternatively: false
      actions:
        - "评估是否可以并行"
        - "通知等待"
        - "设置唤醒条件"
        - "超时升级"

    human_review:
      name: "人工审核暂停"
      description: "需要人工决策或批准才能继续"
      threshold:
        decision_required: true
        risk_level: "medium / high"
        no_clear_path: true
      actions:
        - "暂停并请求输入"
        - "提供决策选项"
        - "设置响应超时"
        - "超时默认继续"

  # ===== 暂停决策规则 =====
  decision_rules:
    # 规则1: 资源不可用
    rule_1:
      name: "资源等待"
      condition: "resource_available == false AND wait_time > 30s"
      action: "pause_wait"
      confidence: 0.90
      max_pause_duration: "5m"
      override: false

    # 规则2: 背压告警
    rule_2:
      name: "背压控制"
      condition: "queue_depth > 20 AND processing_rate < 50%"
      action: "pause_backpressure"
      confidence: 0.95
      max_pause_duration: "10m"
      override: false

    # 规则3: 熔断触发
    rule_3:
      name: "熔断保护"
      condition: "error_rate > 50% OR health_check_failed"
      action: "pause_circuit"
      confidence: 1.0
      max_pause_duration: "15m"
      override: true

    # 规则4: 依赖等待
    rule_4:
      name: "依赖阻塞"
      condition: "dependency_status != completed AND alternative == false"
      action: "pause_dependency"
      confidence: 0.85
      max_pause_duration: "30m"
      override: false

    # 规则5: 人工介入
    rule_5:
      name: "需要决策"
      condition: "decision_required AND risk_level >= medium"
      action: "pause_human"
      confidence: 1.0
      max_pause_duration: "60m"
      override: false
```

---

## 暂停评估检查表

```markdown
## 暂停评估检查表

### 1. 资源状态
- [ ] 所需资源可用？
- [ ] API配额充足？
- [ ] 数据库连接正常？

### 2. 队列状态
- [ ] 队列深度 < 20？
- [ ] 处理速率正常？
- [ ] 内存使用 < 80%？

### 3. 服务健康
- [ ] 错误率 < 50%？
- [ ] 健康检查通过？
- [ ] 超时次数 < 10？

### 4. 依赖状态
- [ ] 前置任务完成？
- [ ] 外部服务可用？
- [ ] 有替代路径？

### 5. 决策需求
- [ ] 需要人工决策？
- [ ] 风险等级中高？
- [ ] 无明确执行路径？

---

### 暂停决策

| 检查项 | 结果 | 暂停类型 |
|--------|------|---------|
| 资源争用 | ✅ / ❌ | resource_contention |
| 背压告警 | ✅ / ❌ | backpressure |
| 熔断触发 | ✅ / ❌ | circuit_breaker |
| 依赖阻塞 | ✅ / ❌ | dependency_pause |
| 人工审核 | ✅ / ❌ | human_review |

### 最终决策
- **立即暂停**: 熔断触发、背压严重
- **延迟暂停**: 资源等待、依赖阻塞
- **请求人工**: 决策需求、高风险
- **不暂停**: 所有条件正常
```

---

## 暂停执行流程

```yaml
pause_execution_flow:
  name: "暂停执行流程"
  steps:
    - step: 1
      name: "检测暂停条件"
      action: "评估是否满足暂停阈值"
      tools: ["pause-detector"]
      output: "pause_signal"

    - step: 2
      name: "保存执行状态"
      action: "保存变量、上下文、检查点"
      tools: ["execution-snapshot"]
      output: "execution_context_id"

    - step: 3
      name: "通知编排协调师"
      action: "报告暂停原因和预计时长"
      tools: ["notification-service"]
      output: "notification_id"

    - step: 4
      name: "执行暂停动作"
      action: "根据暂停类型执行对应动作"
      tools: ["pause-action-executor"]
      output: "pause_result"

    - step: 5
      name: "监控暂停状态"
      action: "监控资源/队列/依赖状态"
      tools: ["pause-monitor"]
      output: "monitor_status"

    - step: 6
      name: "评估恢复条件"
      action: "检查是否可以恢复执行"
      tools: ["recovery-evaluator"]
      output: "recovery_signal"

    - step: 7
      name: "恢复执行"
      action: "从保存的状态恢复任务"
      tools: ["execution-restorer"]
      output: "restored_task_id"

    - step: 8
      name: "记录暂停事件"
      action: "写入元经验库"
      tools: ["event-recorder"]
      output: "pause_record_id"
```

---

## 暂停记录格式

```yaml
pause_records:
  - pause_id: "PAUSE-001"
    timestamp: "YYYY-MM-DDTHH:mm:ss"
    pause_type: "resource_contention"
    task:
      id: "data_sync_01"
      name: "数据同步"
      agent_id: "03"
      progress: "45%"
      context_id: "CTX-001"
    pause_reason:
      resource_type: "external_api"
      resource_name: "第三方支付API"
      unavailable_since: "T+15m"
      wait_time: "3m"
    actions_taken:
      - "检查API状态"
      - "尝试备用API"
      - "设置5分钟超时"
    resolution:
      recovered_at: "T+18m"
      wait_duration: "3m"
      total_impact: "3m"
      data_loss: "none"
      resumed_from: "checkpoint_4"

  - pause_id: "PAUSE-002"
    timestamp: "YYYY-MM-DDTHH:mm:ss"
    pause_type: "backpressure"
    task:
      id: "report_generation_01"
      name: "批量报表生成"
      agent_id: "03"
      progress: "60%"
      context_id: "CTX-002"
    pause_reason:
      queue_depth: "35"
      processing_rate: "30%"
      memory_usage: "88%"
    actions_taken:
      - "触发背压控制"
      - "降低生成速率"
      - "清理缓存释放内存"
    resolution:
      queue_drained_at: "T+25m"
      memory_normalized: "65%"
      resumed_from: "checkpoint_6"

  - pause_id: "PAUSE-003"
    timestamp: "YYYY-MM-DDTHH:mm:ss"
    pause_type: "circuit_breaker"
    task:
      id: "payment_process_01"
      name: "支付处理"
      agent_id: "03"
      progress: "20%"
      context_id: "CTX-003"
    pause_reason:
      error_rate: "65%"
      timeout_count: "15"
      failed_endpoint: "/api/payment/charge"
    actions_taken:
      - "触发熔断器"
      - "返回降级响应"
      - "启动健康检查"
      - "通知运维团队"
    resolution:
      health_check_passed: true
      circuit_closed_at: "T+10m"
      resumed_from: "checkpoint_2"
      impact_analysis:
        failed_requests: 15
        degraded_responses: 8
        fallback_used: true
```

---

## 暂停统计指标

```yaml
pause_metrics:
  total_tasks: 100
  paused_tasks: 8
  pause_rate: "8%"

  by_type:
    resource_contention: 3
    backpressure: 2
    circuit_breaker: 1
    dependency_pause: 1
    human_review: 1

  time_impact:
    total_pause_time: "45m"
    average_pause_duration: "5.6m"
    max_pause_duration: "15m"
    pause_overhead: "5%"

  resolution_quality:
    automatic_recovery: 6
    human_intervention: 1
    escalated: 1

  recommendations:
    - "增加API重试机制，减少resource_contention"
    - "优化队列大小配置，减少backpressure"
    - "增加熔断器阈值精细度"
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
