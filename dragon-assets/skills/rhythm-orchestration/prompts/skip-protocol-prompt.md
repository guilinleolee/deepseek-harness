# 跳过协议提示词 (Skip Protocol Prompt)

> **版本**: V1.0
> **用途**: 指导何时智能跳过任务执行的决策提示词

---

## 跳过协议核心原则

跳过不是失败，跳过是智能决策。当任务满足以下条件时，应考虑跳过：
- **跳过是为了更好的执行** - 避免不必要的重复工作
- **跳过有据可查** - 每一次跳过都必须有明确的理由
- **跳过可追溯** - 跳过记录需要进入元经验库

---

## 跳过决策引导

### 第一步：评估跳过类型

```markdown
## 跳过类型评估

请根据以下问题，判断当前任务属于哪种跳过类型：

### 问题1：任务规模
- 预估时间 < 30秒？
- 复杂度为 simple？
- 无外部依赖？
→ 如果全部是：触发 **trivial_skip**

### 问题2：冗余检查
- 相同任务在2小时内执行过？
- 上游结果已包含所需信息？
- 有可复用的缓存结果？
→ 如果全部是：触发 **redundancy_skip**

### 问题3：上下文有效性
- 用户需求未变更？
- 前置任务全部成功？
- 在有效时间窗口内？
→ 如果全部是：跳过
→ 如果任一否：触发 **context_skip**

### 问题4：风险评估
- 风险评分 < 0.7？
- 安全评估已通过？
- 资源充足？
→ 如果全部是：正常执行
→ 如果任一否：触发 **risk_skip**

### 问题5：能力匹配
- 当前Agent有能力执行？
- 无需外部工具？
- 权限充足？
→ 如果全部是：正常执行
→ 如果任一否：触发 **expertise_skip**
```

### 第二步：评估跳过条件

```markdown
## 跳过条件评估

### 微任务跳过条件 (trivial_skip)
- [ ] estimated_time < 30秒
- [ ] complexity == "simple"
- [ ] 无外部依赖
- [ ] confidence >= 0.95

**跳过置信度**: {confidence}
**预估节省时间**: {estimated_time}s
**决策**: {"跳过" if all_conditions_met else "继续执行"}

### 冗余跳过条件 (redundancy_skip)
- [ ] cache_hit == true
- [ ] freshness < 2小时
- [ ] source_task 存在
- [ ] 结果完整可复用

**缓存命中率**: {cache_hit_rate}
**结果新鲜度**: {freshness}h
**复用来源**: {source_task}
**决策**: {"复用结果" if cache_hit else "继续执行"}

### 上下文跳过条件 (context_skip)
- [ ] context_version == current_version
- [ ] depends_on.status == "completed"
- [ ] within_time_window == true
- [ ] user_intent_unchanged == true

**上下文版本**: v{context_version}
**依赖状态**: {depends_on.status}
**时间窗口**: {"有效" if within else "已过期"}
**决策**: {"跳过" if context_invalid else "继续执行"}

### 风险跳过条件 (risk_skip)
- [ ] risk_score < 0.7
- [ ] security_approved == true
- [ ] resource_available == true
- [ ] no_regression_risk == true

**风险评分**: {risk_score}/1.0
**安全状态**: {"已批准" if security_approved else "待审查"}
**决策**: {"上报审批" if high_risk else "正常执行"}

### 能力跳过条件 (expertise_skip)
- [ ] agent_has_capability == true
- [ ] no_external_tools_needed == true
- [ ] has_required_permissions == true

**当前Agent能力**: {agent_capability}
**所需能力**: {required_capability}
**能力差距**: {capability_gap}
**决策**: {"委托专业Agent" if no_capability else "当前Agent执行"}
```

### 第三步：执行跳过动作

```markdown
## 跳过执行决策

### 最终跳过决策表

| 跳过类型 | 触发条件 | 执行动作 | 置信度 |
|---------|---------|---------|--------|
| trivial_skip | time<30s AND simple | 返回最小可行结果 | 0.95 |
| redundancy_skip | cache_hit AND fresh<2h | 复用已有结果 | 0.90 |
| context_skip | version_mismatch OR deps_failed | 重新评估上下文 | 1.00 |
| risk_skip | risk>0.7 OR !security_approved | 触发安全审查 | 0.85 |
| expertise_skip | !has_capability | 委托合适Agent | 1.00 |

### 跳过执行流程

```
评估跳过条件
    ↓
识别跳过类型
    ↓
计算跳过置信度
    ↓
检查覆盖标志 override
    ↓
执行跳过动作
    ↓
记录跳过原因
    ↓
更新元经验库
```

### 跳过后处理

```markdown
## 跳过后处理

### 对于 trivial_skip
1. 记录跳过原因："预估时间{time}s，复杂度{complexity}"
2. 返回最小可行结果
3. 更新执行统计

### 对于 redundancy_skip
1. 记录来源：{source_task_id}
2. 复用已有结果
3. 标记结果来源
4. 更新缓存统计

### 对于 context_skip
1. 通知编排协调师
2. 重新评估任务必要性
3. 可能需要用户确认

### 对于 risk_skip
1. 触发安全审查
2. 通知安全师
3. 等待安全评估结果

### 对于 expertise_skip
1. 委托给合适的Agent
2. 更新能力矩阵
3. 记录能力缺口
```

### 第四步：记录跳过事件

```markdown
## 跳过事件记录格式

请按以下格式记录跳过事件：

```yaml
skip_record:
  skip_id: "SKIP-{timestamp}"
  timestamp: "{YYYY-MM-DDTHH:mm:ss}"
  task_id: "{task_id}"
  task_name: "{task_name}"
  agent_id: "{agent_id}"
  skip_type: "{type}"
  reason: "{detailed_reason}"
  action_taken: "{action}"
  reused_result:
    source_task: "{source_task_id}"  # 仅 redundancy_skip
    reuse_rate: "100%"
  metadata:
    estimated_time: "{time}s"
    actual_time_saved: "{time_saved}s"
    confidence: {confidence}
    override: {true/false}
  quality_impact: "{positive/neutral/negative}"
  review_status: "{auto/manual}"

### 质量影响评估

- **positive**: 跳过提升了整体效率或质量
- **neutral**: 跳过对结果无影响
- **negative**: 跳过可能影响了质量，需后续验证

### 审查状态

- **auto**: 自动跳过，置信度 >= 0.90
- **manual**: 需要人工确认，置信度 < 0.90
```

### 第五步：更新元经验库

```markdown
## 元经验库更新

跳过事件完成后，更新元经验库：

```yaml
meta_experience:
  event_type: "skip"
  event_id: "{skip_id}"
  pattern_detected: "{pattern_name}"
  conditions:
    - "{condition_1}"
    - "{condition_2}"
  action_taken: "{action}"
  outcome:
    quality_impact: "{impact}"
    time_saved: "{time_saved}s"
    confidence: {confidence}
  lessons_learned:
    - "{lesson_1}"
    - "{lesson_2}"
  recommendations:
    - "{recommendation_1}"
    - "{recommendation_2}"
```

### 模式识别

从跳过事件中识别可复用的模式：

```markdown
## 常见跳过模式

### 模式1: 缓存命中模式
条件: cache_hit AND freshness < threshold
动作: 直接复用结果
效果: 节省 {saved_time}s

### 模式2: 微任务累积模式
条件: 多个微小任务排队
动作: 批量处理或跳过
效果: 减少上下文切换

### 模式3: 上下文失效模式
条件: context_version < current_version
动作: 重新评估任务必要性
效果: 避免执行无效任务

### 模式4: 能力不匹配模式
条件: agent_capability < required_capability
动作: 委托专业Agent
效果: 提高执行质量
```

---

## 跳过决策检查清单

```markdown
## 跳过决策检查清单

### 跳过前检查
- [ ] 已识别跳过类型
- [ ] 已计算跳过置信度
- [ ] 已检查覆盖标志
- [ ] 已评估质量影响

### 跳过执行检查
- [ ] 已执行跳过动作
- [ ] 已返回结果或委托
- [ ] 已记录跳过事件

### 跳过后检查
- [ ] 已更新执行统计
- [ ] 已更新元经验库
- [ ] 已通知相关方（如需要）
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
