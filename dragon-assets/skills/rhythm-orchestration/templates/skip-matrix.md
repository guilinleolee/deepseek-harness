# 跳过矩阵模板 (Skip Protocol Matrix)

> **版本**: V1.0
> **用途**: 定义何时可以跳过某个任务的决策矩阵

---

## 跳过协议概述

跳过协议定义了Agent调度中"谁可以跳过"的条件和流程。核心原则：
- **跳过不是失败** - 跳过是智能决策，避免不必要的执行
- **跳过有据可查** - 每一次跳过都必须有明确的理由
- **跳过可追溯** - 跳过记录需要进入元经验库

---

## 跳过决策矩阵

```yaml
skip_matrix:
  version: "1.0"
  created: "YYYY-MM-DD"
  matrix_id: "SKIP-MATRIX-XXX"

  # ===== 跳过类型定义 =====
  skip_types:
    trivial_skip:
      name: "微任务跳过"
      description: "任务工作量低于阈值，直接返回最小可行结果"
      threshold:
        estimated_time: "< 30秒"
        complexity: "simple"
        dependencies: "无外部依赖"
      actions:
        - "记录跳过原因"
        - "返回最小可行结果"
        - "更新执行统计"

    redundancy_skip:
      name: "冗余跳过"
      description: "任务已被其他Agent完成或结果已存在"
      conditions:
        - "相同任务已在近期执行（< 2小时）"
        - "上游结果已包含下游所需信息"
        - "并行分支已完成等效任务"
      actions:
        - "复用已有结果"
        - "记录来源"
        - "跳过执行"

    context_skip:
      name: "上下文跳过"
      description: "当前上下文已不满足任务执行条件"
      conditions:
        - "用户已取消或修改需求"
        - "前置任务失败导致依赖不可用"
        - "时间窗口已过期"
      actions:
        - "评估是否可以降级处理"
        - "通知编排协调师"
        - "记录跳过原因"

    risk_skip:
      name: "风险跳过"
      description: "任务执行风险超过阈值，选择跳过"
      conditions:
        - "执行可能破坏已有功能"
        - "安全风险未评估"
        - "资源不足可能超时"
      actions:
        - "触发安全审查"
        - "通知安全师"
        - "记录风险点"

    expertise_skip:
      name: "能力跳过"
      description: "当前Agent不具备执行任务的必要能力"
      conditions:
        - "任务类型超出Agent能力范围"
        - "需要升级到更专业的Agent"
        - "需要外部工具或API"
      actions:
        - "委托给合适的Agent"
        - "更新能力矩阵"
        - "记录能力缺口"

  # ===== 跳过决策规则 =====
  decision_rules:
    # 规则1: 微任务阈值
    rule_1:
      name: "微任务自动跳过"
      condition: "estimated_time < 30s AND complexity == simple"
      action: "skip"
      confidence: 0.95
      override: false

    # 规则2: 结果复用
    rule_2:
      name: "近期结果复用"
      condition: "cache_hit AND freshness < 2h"
      action: "reuse"
      confidence: 0.90
      override: false

    # 规则3: 上下文变更
    rule_3:
      name: "上下文失效"
      condition: "context_version < current_version"
      action: "reassess"
      confidence: 1.0
      override: false

    # 规则4: 依赖失败
    rule_4:
      name: "依赖不可用"
      condition: "depends_on.status == failed"
      action: "escalate"
      confidence: 1.0
      override: false

    # 规则5: 风险阈值
    rule_5:
      name: "高风险任务"
      condition: "risk_score > 0.7"
      action: "review_required"
      confidence: 0.85
      override: true
```

---

## 跳过评估检查表

```markdown
## 跳过评估检查表

### 1. 微任务判断
- [ ] 预估时间 < 30秒？
- [ ] 复杂度为simple？
- [ ] 无外部依赖？

### 2. 冗余判断
- [ ] 相同任务在2小时内执行过？
- [ ] 上游结果包含所需信息？
- [ ] 有可复用的缓存结果？

### 3. 上下文判断
- [ ] 用户需求未变更？
- [ ] 前置任务全部成功？
- [ ] 在有效时间窗口内？

### 4. 风险判断
- [ ] 风险评分 < 0.7？
- [ ] 安全评估已通过？
- [ ] 资源充足？

### 5. 能力判断
- [ ] 当前Agent有能力执行？
- [ ] 无需外部工具？
- [ ] 权限充足？

---

### 跳过决策

| 检查项 | 结果 |
|--------|------|
| 微任务跳过 | ✅ / ❌ |
| 冗余跳过 | ✅ / ❌ |
| 上下文跳过 | ✅ / ❌ |
| 风险跳过 | ✅ / ❌ |
| 能力跳过 | ✅ / ❌ |

### 最终决策
- **跳过**: 记录原因，执行跳过动作
- **继续**: 正常执行任务
- **上报**: 通知编排协调师决策
```

---

## 跳过记录格式

```yaml
skip_records:
  - skip_id: "SKIP-001"
    timestamp: "YYYY-MM-DDTHH:mm:ss"
    task_id: "task_xxx"
    task_name: "任务名称"
    agent_id: "03"
    skip_type: "trivial_skip"
    reason: "预估时间15秒，复杂度simple"
    action_taken: "返回最小可行结果"
    reused_result: null
    metadata:
      estimated_time: "15s"
      actual_time_saved: "15s"
      confidence: 0.95

  - skip_id: "SKIP-002"
    timestamp: "YYYY-MM-DDTHH:mm:ss"
    task_id: "task_yyy"
    task_name: "竞品分析"
    agent_id: "01"
    skip_type: "redundancy_skip"
    reason: "task_xxx结果已包含竞品信息"
    action_taken: "复用task_xxx结果"
    reused_result:
      source_task: "task_xxx"
      reuse_rate: "100%"
    metadata:
      original_freshness: "1.5h"
      cache_hit: true
```

---

## 跳过统计指标

```yaml
skip_metrics:
  total_tasks: 100
  skipped_tasks: 12
  skip_rate: "12%"

  by_type:
    trivial_skip: 5
    redundancy_skip: 4
    context_skip: 2
    risk_skip: 1
    expertise_skip: 0

  time_saved:
    total_seconds: 1800
    average_per_skip: "150s"

  quality_impact:
    negative: 0
    neutral: 10
    positive: 2
    improvement_rate: "20%"

  recommendations:
    - "trivial_skip阈值可适当提高"
    - "考虑增加redundancy_skip缓存命中率"
    - "context_skip应触发需求确认"
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
