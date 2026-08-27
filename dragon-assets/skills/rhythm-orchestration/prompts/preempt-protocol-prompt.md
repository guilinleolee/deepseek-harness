# 插队协议提示词 (Preempt Protocol Prompt)

> **版本**: V1.0
> **用途**: 指导何时提升任务优先级的决策提示词

---

## 插队协议核心原则

插队是抢占执行权的行为，必须谨慎使用。核心原则：
- **插队必须有正当理由** - 不能随意打断正在执行的任务
- **插队有代价** - 需要保存当前状态、恢复上下文
- **插队需通知** - 所有相关方必须知道插队事件

---

## 插队决策引导

### 第一步：评估插队类型

```markdown
## 插队类型评估

请根据以下问题，判断当前情况属于哪种插队类型：

### 安全关键插队 (security_preempt)
- [ ] 涉及安全相关关键词？
- [ ] 操作认证或权限系统？
- [ ] 检测到安全漏洞？
- [ ] risk_level >= "high"？
→ 如果任一是：触发 **security_preempt** (CRITICAL)

### 数据完整性插队 (data_integrity_preempt)
- [ ] 修改关键数据？
- [ ] 批量操作无事务？
- [ ] 可能导致数据丢失？
- [ ] 没有备份？
→ 如果全部是：触发 **data_integrity_preempt** (HIGH)

### 性能插队 (performance_preempt)
- [ ] CPU使用率 > 80%？
- [ ] 响应时间 > 10秒？
- [ ] 错误率 > 5%？
- [ ] 用户影响 > 50%？
→ 如果全部是：触发 **performance_preempt** (MEDIUM)

### 用户交互插队 (user_interaction_preempt)
- [ ] 用户正在等待？
- [ ] 会话即将超时？
- [ ] 显式用户请求？
- [ ] 任务阻塞用户？
→ 如果任一是：触发 **user_interaction_preempt** (HIGH)

### 截止时间插队 (deadline_preempt)
- [ ] 距离截止 < 10分钟？
- [ ] 任务影响度高？
- [ ] 下游依赖 > 3个？
- [ ] 关键路径任务？
→ 如果全部是：触发 **deadline_preempt** (MEDIUM)
```

### 第二步：评估插队条件

```markdown
## 插队条件评估

### 安全关键条件 (security_preempt)
| 条件 | 阈值 | 当前值 | 状态 |
|------|------|--------|------|
| security_keyword_detected | true | {value} | {status} |
| auth_tampering | true | {value} | {status} |
| risk_level | >= high | {value} | {status} |
| confidence | >= 1.0 | {value} | {status} |

**插队置信度**: {confidence}
**中断级别**: {interrupt_level} (full/partial/minimal/none)
**覆盖标志**: {override}
**决策**: {"立即插队" if can_preempt else "等待完成"}

### 数据完整性条件 (data_integrity_preempt)
| 条件 | 阈值 | 当前值 | 状态 |
|------|------|--------|------|
| modifies_critical_data | true | {value} | {status} |
| bulk_operation | true | {value} | {status} |
| no_transaction | true | {value} | {status} |
| no_backup | true | {value} | {status} |

**数据风险等级**: {risk_level}
**影响范围**: {impact_scope}
**插队置信度**: {confidence}
**决策**: {"带备份插队" if has_backup else "先备份再插队"}

### 性能条件 (performance_preempt)
| 条件 | 阈值 | 当前值 | 状态 |
|------|------|--------|------|
| cpu_usage | > 80% | {value}% | {status} |
| memory_usage | > 85% | {value}% | {status} |
| response_time | > 10s | {value}s | {status} |
| error_rate | > 5% | {value}% | {status} |

**性能评分**: {score}/100
**用户影响**: {user_impact}%
**中断级别**: {interrupt_level}
**决策**: {"插队优化" if performance_critical else "等待完成"}

### 用户交互条件 (user_interaction_preempt)
| 条件 | 阈值 | 当前值 | 状态 |
|------|------|--------|------|
| user_waiting | true | {value} | {status} |
| session_timeout_imminent | < 5min | {value}min | {status} |
| explicit_user_request | true | {value} | {status} |
| task_is_blocking | true | {value} | {status} |

**用户等待时间**: {wait_time}s
**会话超时风险**: {timeout_risk}
**中断级别**: {interrupt_level}
**决策**: {"立即处理" if user_blocked else "后台处理"}

### 截止时间条件 (deadline_preempt)
| 条件 | 阈值 | 当前值 | 状态 |
|------|------|--------|------|
| time_to_deadline | < 10min | {value}min | {status} |
| task_impact | >= high | {value} | {status} |
| downstream_dependencies | > 3 | {value} | {status} |
| task_critical | true | {value} | {status} |

**距截止时间**: {time_to_deadline}min
**影响任务数**: {downstream_count}
**中断级别**: {interrupt_level}
**决策**: {"加速处理" if deadline_imminent else "正常调度"}
```

### 第三步：评估中断影响

```markdown
## 中断影响评估

### 中断级别定义

| 级别 | 说明 | 影响 | 适用场景 |
|------|------|------|---------|
| **full** | 完全中断当前任务 | 高优先级任务完整执行 | 安全/数据关键 |
| **partial** | 部分中断，保留状态 | 高优先级任务执行后恢复 | 性能/用户交互 |
| **minimal** | 最小中断 | 只暂停阻塞部分 | 截止时间紧迫 |
| **none** | 不中断 | 并行执行 | 截止时间紧迫（可并行时） |

### 中断成本计算

```yaml
interruption_cost:
  state_saving_overhead: "{time}s"
  context_recovery_overhead: "{time}s"
  total_overhead: "{time}s"
  priority_task_time: "{time}s"
  opportunity_cost: "{time}s"

### 影响评估

- **当前任务影响**:
  - 进度损失: {progress_loss}%
  - 恢复时间: {recovery_time}s
  - 数据完整性: {integrity_status}

- **优先级任务收益**:
  - 响应时间提升: {response_improvement}s
  - 用户满意度提升: {satisfaction_improvement}%
  - 风险避免: {risk_avoided}

- **净收益**:
  - 收益: {benefit}
  - 成本: {cost}
  - 决策: {"插队值得" if net_benefit > 0 else "插队不值"}
```

### 第四步：执行插队流程

```markdown
## 插队执行流程

### 插队前准备

```yaml
preempt_preparation:
  1. 保存当前状态:
     - 执行上下文: {context_id}
     - 检查点: {checkpoint_id}
     - 变量快照: {snapshot_id}

  2. 通知相关方:
     - 编排协调师: {notified}
     - 被中断Agent: {notified}
     - 用户（如需要）: {notified}

  3. 准备优先级任务:
     - 任务ID: {preempt_task_id}
     - 所需Agent: {agent_id}
     - 预期执行时间: {duration}
```

### 插队执行

```yaml
preempt_execution:
  step_1:
    name: "检测插队条件"
    action: "评估是否满足插队阈值"
    output: "preempt_signal"

  step_2:
    name: "保存当前状态"
    action: "保存执行上下文、检查点"
    required: true
    output: "snapshot_id"

  step_3:
    name: "通知相关方"
    action: "通知编排协调师、被中断Agent"
    output: "notifications_sent"

  step_4:
    name: "执行插队任务"
    action: "高优先级任务执行"
    interrupt_level: "{level}"
    output: "preempt_result"

  step_5:
    name: "验证结果"
    action: "验证插队任务完成"
    output: "validation_result"

  step_6:
    name: "恢复被中断任务"
    action: "从检查点恢复执行"
    output: "restored_task_id"

  step_7:
    name: "记录插队事件"
    action: "写入元经验库"
    output: "preempt_record_id"
```

### 第五步：记录插队事件

```markdown
## 插队事件记录格式

```yaml
preempt_record:
  preempt_id: "PREEMPT-{timestamp}"
  timestamp: "{YYYY-MM-DDTHH:mm:ss}"
  preempt_type: "{type}"
  preempt_task:
    id: "{task_id}"
    name: "{task_name}"
    agent_id: "{agent_id}"
    priority: "{priority}"
  interrupted_task:
    id: "{task_id}"
    name: "{task_name}"
    agent_id: "{agent_id}"
    progress: "{progress}%"
    snapshot_id: "{snapshot_id}"
  reason: "{detailed_reason}"
  duration:
    interruption_time: "{time}m"
    resumed_time: "T+{time}m"
    total_impact: "{time}m"
  resolution:
    preempt_result: "{result}"
    resumed_from: "checkpoint_{n}"
    data_loss: "{none/partial/total}"
  impact_analysis:
    user_impact: "{impact_level}"
    performance_impact: "{impact_level}"
    quality_impact: "{impact_level}"
```

### 第六步：恢复被中断任务

```markdown
## 恢复流程

### 恢复步骤

1. **加载快照**
   - 从 {snapshot_id} 加载执行上下文
   - 恢复变量状态
   - 验证数据完整性

2. **验证前置条件**
   - 检查依赖是否仍然满足
   - 验证资源可用性
   - 确认上下文版本

3. **继续执行**
   - 从 {checkpoint} 恢复执行
   - 记录恢复后的进度
   - 更新任务状态

4. **验证恢复成功**
   - 检查执行结果
   - 验证输出正确性
   - 更新元经验库
```

---

## 插队决策检查清单

```markdown
## 插队决策检查清单

### 插队前检查
- [ ] 已识别插队类型
- [ ] 已评估中断影响
- [ ] 已计算插队置信度
- [ ] 已检查覆盖标志
- [ ] 已准备状态保存

### 插队执行检查
- [ ] 已保存当前状态
- [ ] 已通知相关方
- [ ] 已执行优先级任务
- [ ] 已验证结果

### 插队后检查
- [ ] 已恢复被中断任务
- [ ] 已验证数据完整性
- [ ] 已记录插队事件
- [ ] 已更新元经验库
```

---

## 插队结果统计

```markdown
## 插队统计指标

| 指标 | 数值 |
|------|------|
| 总插队次数 | {count} |
| 成功率 | {success_rate}% |
| 平均中断时间 | {avg_interruption}m |
| 最大中断时间 | {max_interruption}m |
| 用户满意度变化 | {satisfaction_change}% |

### 按类型统计

| 类型 | 次数 | 成功率 | 平均影响 |
|------|------|--------|---------|
| security_preempt | {count} | {rate}% | {impact}m |
| data_integrity_preempt | {count} | {rate}% | {impact}m |
| performance_preempt | {count} | {rate}% | {impact}m |
| user_interaction_preempt | {count} | {rate}% | {impact}m |
| deadline_preempt | {count} | {rate}% | {impact}m |

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
