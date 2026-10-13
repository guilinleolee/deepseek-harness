# 暂停协议提示词 (Pause Protocol Prompt)

> **版本**: V1.0
> **用途**: 指导何时暂停任务执行的决策提示词

---

## 暂停协议核心原则

暂停是策略性等待，不是失败。核心原则：
- **暂停是为了更好的执行** - 不是失败，是策略性等待
- **暂停有明确条件** - 不能因为无法决策就暂停
- **暂停有时间限制** - 超时必须升级或采取行动

---

## 暂停决策引导

### 第一步：评估暂停类型

```markdown
## 暂停类型评估

请根据以下问题，判断当前情况属于哪种暂停类型：

### 资源争用暂停 (resource_contention)
- [ ] 所需资源不可用？
- [ ] API配额耗尽？
- [ ] 数据库连接超时？
- [ ] 等待时间 > 30秒？
- [ ] 无替代资源？
→ 如果全部是：触发 **resource_contention**

### 背压暂停 (backpressure)
- [ ] 队列深度 > 20？
- [ ] 处理速率 < 50%？
- [ ] 内存使用 > 80%？
- [ ] 下游能力不足？
→ 如果全部是：触发 **backpressure**

### 熔断器暂停 (circuit_breaker)
- [ ] 错误率 > 50%？
- [ ] 超时次数 > 10？
- [ ] 健康检查失败？
- [ ] 检测到故障？
→ 如果任一是：触发 **circuit_breaker** (立即暂停)

### 依赖暂停 (dependency_pause)
- [ ] 前置任务未完成？
- [ ] 外部依赖不可用？
- [ ] 预估等待 > 5分钟？
- [ ] 无替代路径？
→ 如果全部是：触发 **dependency_pause**

### 人工审核暂停 (human_review)
- [ ] 需要人工决策？
- [ ] 风险等级中高？
- [ ] 无明确执行路径？
- [ ] 高影响决策？
→ 如果全部是：触发 **human_review** (请求人工)
```

### 第二步：评估暂停条件

```markdown
## 暂停条件评估

### 资源争用条件 (resource_contention)
| 条件 | 阈值 | 当前值 | 状态 |
|------|------|--------|------|
| resource_available | false | {value} | {status} |
| wait_time | > 30s | {value}s | {status} |
| alternative_resource | false | {value} | {status} |
| retry_exhausted | true | {value} | {status} |

**资源类型**: {resource_type}
**等待时间**: {wait_time}s
**最大暂停时长**: {max_pause_duration}
**决策**: {"暂停等待" if resource_unavailable else "继续执行"}

### 背压条件 (backpressure)
| 条件 | 阈值 | 当前值 | 状态 |
|------|------|--------|------|
| queue_depth | > 20 | {value} | {status} |
| processing_rate | < 50% | {value}% | {status} |
| memory_usage | > 80% | {value}% | {status} |
| downstream_capacity | insufficient | {value} | {status} |

**队列深度**: {queue_depth}
**处理速率**: {processing_rate}%
**内存使用**: {memory_usage}%
**背压等级**: {level} (normal/warning/critical)
**决策**: {"启用背压控制" if backpressure_detected else "正常处理"}

### 熔断器条件 (circuit_breaker)
| 条件 | 阈值 | 当前值 | 状态 |
|------|------|--------|------|
| error_rate | > 50% | {value}% | {status} |
| timeout_count | > 10 | {value} | {status} |
| health_check_failed | true | {value} | {status} |
| circuit_state | open | {value} | {status} |

**错误率**: {error_rate}%
**超时次数**: {timeout_count}
**健康检查状态**: {health_status}
**熔断器状态**: {circuit_state} (closed/open/half_open)
**决策**: {"触发熔断器" if should_circuit_break else "继续执行"}

### 依赖条件 (dependency_pause)
| 条件 | 阈值 | 当前值 | 状态 |
|------|------|--------|------|
| dependency_status | pending/failed | {value} | {status} |
| estimated_wait | > 5min | {value}min | {status} |
| alternative_path | false | {value} | {status} |
| can_parallel | false | {value} | {status} |

**依赖状态**: {dependency_status}
**预估等待**: {estimated_wait}min
**替代路径**: {alternative_path}
**并行可能性**: {can_parallel}
**决策**: {"暂停等待" if dependency_blocked else "尝试并行"}

### 人工审核条件 (human_review)
| 条件 | 阈值 | 当前值 | 状态 |
|------|------|--------|------|
| decision_required | true | {value} | {status} |
| risk_level | >= medium | {value} | {status} |
| no_clear_path | true | {value} | {status} |
| user_requested | true | {value} | {status} |

**决策需求**: {decision_required}
**风险等级**: {risk_level}
**影响范围**: {impact_scope}
**响应超时**: {response_timeout}h
**决策**: {"请求人工审核" if needs_human else "自主决策"}
```

### 第三步：执行暂停流程

```markdown
## 暂停执行流程

### 暂停前准备

```yaml
pause_preparation:
  1. 保存执行状态:
     - 执行上下文: {context_id}
     - 检查点: {checkpoint_id}
     - 变量快照: {snapshot_id}
     - 进度: {progress}%

  2. 通知编排协调师:
     - 暂停原因: {reason}
     - 预计时长: {estimated_duration}
     - 影响范围: {affected_tasks}

  3. 准备暂停动作:
     - 暂停类型: {pause_type}
     - 唤醒条件: {wake_condition}
     - 超时处理: {timeout_action}
```

### 暂停执行

```yaml
pause_execution:
  step_1:
    name: "检测暂停条件"
    action: "评估是否满足暂停阈值"
    tools: ["pause-detector"]
    output: "pause_signal"

  step_2:
    name: "保存执行状态"
    action: "保存变量、上下文、检查点"
    tools: ["execution-snapshot"]
    output: "execution_context_id"

  step_3:
    name: "通知编排协调师"
    action: "报告暂停原因和预计时长"
    tools: ["notification-service"]
    output: "notification_id"

  step_4:
    name: "执行暂停动作"
    action: "根据暂停类型执行对应动作"
    tools: ["pause-action-executor"]
    output: "pause_result"

  step_5:
    name: "监控暂停状态"
    action: "监控资源/队列/依赖状态"
    tools: ["pause-monitor"]
    output: "monitor_status"

  step_6:
    name: "评估恢复条件"
    action: "检查是否可以恢复执行"
    tools: ["recovery-evaluator"]
    output: "recovery_signal"

  step_7:
    name: "恢复执行"
    action: "从保存的状态恢复任务"
    tools: ["execution-restorer"]
    output: "restored_task_id"

  step_8:
    name: "记录暂停事件"
    action: "写入元经验库"
    tools: ["event-recorder"]
    output: "pause_record_id"
```

### 第四步：监控暂停状态

```markdown
## 暂停状态监控

### 监控指标

| 指标 | 当前值 | 阈值 | 状态 |
|------|--------|------|------|
| 暂停时长 | {elapsed}m | {max}m | {status} |
| 资源可用性 | {available}% | 100% | {status} |
| 队列深度 | {queue_depth} | 20 | {status} |
| 错误率 | {error_rate}% | 50% | {status} |
| 依赖状态 | {dep_status} | completed | {status} |

### 唤醒条件评估

```yaml
wake_conditions:
  resource_contention:
    - resource_available == true
    - wait_time < max_wait
    - alternative_available == true

  backpressure:
    - queue_depth < 15
    - processing_rate > 60%
    - memory_usage < 75%

  circuit_breaker:
    - health_check_passed == true
    - error_rate < 30%
    - circuit_state == "half_open"

  dependency_pause:
    - dependency_status == "completed"
    - alternative_path_available == true

  human_review:
    - decision_received == true
    - timeout_reached == true
```

### 第五步：处理超时

```markdown
## 暂停超时处理

### 超时决策树

```yaml
timeout_handling:
  if elapsed >= max_pause_duration:
    if can_proceed_without_resource:
      action: "降级执行"
      next: "尝试替代方案"

    elif escalation_required:
      action: "升级处理"
      next: "通知协调师/用户"

    else:
      action: "终止任务"
      next: "记录失败原因"
```

### 超时升级标准

| 暂停类型 | 超时阈值 | 升级条件 |
|---------|---------|---------|
| resource_contention | 5m | 无替代方案 |
| backpressure | 10m | 队列持续增长 |
| circuit_breaker | 15m | 健康检查持续失败 |
| dependency_pause | 30m | 依赖持续阻塞 |
| human_review | 60m | 无响应 |

### 降级执行策略

```yaml
degraded_execution:
  strategy_1:
    name: "使用缓存"
    conditions:
      - cache_available == true
      - cache_freshness < threshold
    outcome: "返回缓存结果"

  strategy_2:
    name: "返回部分结果"
    conditions:
      - partial_result_possible == true
      - user_acceptance == true
    outcome: "返回部分完成内容"

  strategy_3:
    name: "返回降级响应"
    conditions:
      - fallback_available == true
      - user_notified == true
    outcome: "返回预设降级结果"
```

### 第六步：记录暂停事件

```markdown
## 暂停事件记录格式

```yaml
pause_record:
  pause_id: "PAUSE-{timestamp}"
  timestamp: "{YYYY-MM-DDTHH:mm:ss}"
  pause_type: "{type}"
  task:
    id: "{task_id}"
    name: "{task_name}"
    agent_id: "{agent_id}"
    progress: "{progress}%"
    context_id: "{context_id}"
  pause_reason:
    primary: "{main_reason}"
    details:
      - "{detail_1}"
      - "{detail_2}"
    duration_waiting: "{time}m"
  actions_taken:
    - "{action_1}"
    - "{action_2}"
    - "{action_3}"
  resolution:
    recovered_at: "T+{time}m"
    wait_duration: "{time}m"
    total_impact: "{time}m"
    data_loss: "{none/partial}"
    resumed_from: "checkpoint_{n}"
    timeout_handled: "{true/false}"
    degraded_result: "{true/false}"

### 影响分析

```yaml
impact_analysis:
  time_impact:
    pause_duration: "{time}m"
    recovery_time: "{time}m"
    total_delay: "{time}m"

  quality_impact:
    result_completeness: "{percentage}%"
    data_integrity: "{status}"
    user_satisfaction: "{impact_level}"

  resource_impact:
    cpu_wasted: "{percentage}%"
    memory_wasted: "{percentage}%"
    api_calls_wasted: "{count}"
```

---

## 暂停决策检查清单

```markdown
## 暂停决策检查清单

### 暂停前检查
- [ ] 已识别暂停类型
- [ ] 已评估暂停条件
- [ ] 已计算最大暂停时长
- [ ] 已准备状态保存

### 暂停执行检查
- [ ] 已保存执行状态
- [ ] 已通知编排协调师
- [ ] 已执行暂停动作
- [ ] 已设置监控

### 暂停监控检查
- [ ] 已监控暂停状态
- [ ] 已评估唤醒条件
- [ ] 已在超时前处理

### 恢复执行检查
- [ ] 已验证恢复条件
- [ ] 已恢复执行状态
- [ ] 已验证数据完整性
- [ ] 已记录暂停事件
```

---

## 暂停统计指标

```markdown
## 暂停统计指标

### 总体统计

| 指标 | 数值 |
|------|------|
| 总任务数 | {total_tasks} |
| 暂停任务数 | {paused_tasks} |
| 暂停率 | {pause_rate}% |
| 自动恢复率 | {auto_recovery_rate}% |
| 人工干预率 | {human_intervention_rate}% |

### 按类型统计

| 类型 | 次数 | 平均时长 | 最大时长 | 自动恢复 |
|------|------|---------|---------|---------|
| resource_contention | {count} | {avg}m | {max}m | {rate}% |
| backpressure | {count} | {avg}m | {max}m | {rate}% |
| circuit_breaker | {count} | {avg}m | {max}m | {rate}% |
| dependency_pause | {count} | {avg}m | {max}m | {rate}% |
| human_review | {count} | {avg}m | {max}m | {rate}% |

### 优化建议

- "{recommendation_1}"
- "{recommendation_2}"
- "{recommendation_3}"
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
