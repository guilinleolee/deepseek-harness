---
license: UNKNOWN
triggers: ["gate control", "Gate Control - 阶段门控机制"]
---
# Gate Control - 阶段门控机制

> Meta_Kim Gate门控系统，确保每个阶段必须满足通过条件才能进入下一阶段

## L0: 一句话描述
阶段通过条件判定系统，防止跳过关键验证步骤。

## L1: 使用场景
- 需要强制执行质量门禁
- 防止过早进入下一阶段
- 需要明确的通过/失败判定

## L2: 详细文档

### Gate状态定义

```typescript
enum GateStatus {
  PENDING = 'pending',   // 未开始检查
  PASS = 'pass',          // 通过，继续下一阶段
  FAIL = 'fail',          // 不通过，返回重做
  HOLD = 'hold',          // 暂停，等待条件
  ESCALATE = 'escalate'   // 升级，超出处理能力
}
```

### 4种Gate状态的处理

```
┌─────────────────────────────────────────────────────────────────┐
│                         GATE 处理流程                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Gate检查触发                                                   │
│       ↓                                                        │
│  交付物完整且质量达标？                                         │
│    ↓YES              ↓NO                                        │
│  PASS ─────────→ FAIL                                          │
│    │                │                                          │
│    │                ↓                                          │
│    │           返回该阶段重做                                   │
│    │                │                                          │
│    │                ↓                                          │
│    │           重做后再次检查Gate                               │
│    │                │                                          │
│    │           3次失败？                                        │
│    │           ↓YES                                             │
│    │           ESCALATE                                        │
│    │                │                                          │
│    │                ↓                                          │
│    │           升级给用户/更高层Agent                          │
│    │                                                                │
│    ↓                                                             │
│  外部条件满足？                                                  │
│    ↓NO                                                           │
│  HOLD (暂停等待)                                                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 各阶段Gate检查清单

#### Stage 1: CRITICAL Gate
```yaml
check_items:
  - intentPacket.id exists
  - intentPacket.understoodIntent non-empty
  - intentPacket.constraints not-empty
  - intentPacket.successCriteria not-empty
  - intentPacket.confidence >= 0.7
pass: "意图清晰，可进入下一阶段"
fail: "意图不明确，返回澄清"
```

#### Stage 2: FETCH Gate
```yaml
check_items:
  - capabilityMap.intent matches Stage1 intent
  - capabilityMap.gaps empty OR gaps have resolution plan
  - all required skills have owners
pass: "能力完整，可进入下一阶段"
fail: "能力缺口未解决，暂停分发"
hold: "等待能力补充"
```

#### Stage 3: THINKING Gate
```yaml
check_items:
  - dispatchBoard.stages not-empty
  - each stage has assigned agent
  - each task has clear instructions
  - dependency graph is acyclic (no circular deps)
  - estimated duration reasonable
pass: "计划可行，可进入执行"
fail: "计划不可行，重新规划"
escalate: "规划超出能力，寻求外部帮助"
```

#### Stage 4: EXECUTION Gate
```yaml
check_items:
  - all critical tasks completed
  - non-critical tasks have status
  - no blocking issues without resolution plan
  - execution time within acceptable range
pass: "执行完成，可进入审查"
fail: "执行未完成，继续或重试"
hold: "等待外部资源"
```

#### Stage 5: REVIEW Gate
```yaml
check_items:
  - all task results reviewed
  - issues categorized (critical/major/minor)
  - critical issues have fixes
  - quality score >= threshold
pass: "审查通过，可进入元审查"
fail: "质量问题需修复"
escalate: "质量问题超出修复能力"
```

#### Stage 6: META-REVIEW Gate
```yaml
check_items:
  - review itself audited
  - no bias detected in review process
  - review completeness >= 0.9
  - gate criteria properly applied
pass: "元审查通过，继续验证"
fail: "审查过程有问题，重新审查"
```

#### Stage 7: VERIFICATION Gate
```yaml
check_items:
  - original intent matched
  - success criteria satisfied
  - gaps identified and categorized
  - risks assessed
pass: "验证通过，进入经验总结"
fail: "验证未通过，需返工"
escalate: "验证标准本身有问题"
```

#### Stage 8: EVOLUTION Gate
```yaml
check_items:
  - lessons extracted and structured
  - new capabilities registered
  - refinements documented
  - lessons available for future runs
pass: "经验已固化，工作流完成"
fail: "经验未保存，需要重试"
```

### 命令

```bash
/gate-status              # 查看当前所有Gate状态
/gate-check [stage]       # 检查指定阶段Gate
/gate-pass [stage]        # 强制标记为Pass（需谨慎）
/ate-hold [stage]         # 暂停指定阶段
/gate-escalate [stage]   # 升级指定阶段
```

### 与天龙引擎协同

| 天龙组件 | 协同方式 |
|---------|---------|
| 09-02编排协调师 | 执行Gate分发决策 |
| 09-03元审查师 | Stage 6 元审查Gate |
| 06审查师 | Stage 5 审查Gate |
| 04验证师 | Stage 4 执行监控 + Stage 7 验证 |

### 配置示例

```json
{
  "gate_config": {
    "stage_thresholds": {
      "critical": 0.7,
      "fetch": 1.0,
      "thinking": 1.0,
      "execution": 0.8,
      "review": 0.85,
      "meta_review": 0.9,
      "verification": 0.9,
      "evolution": 1.0
    },
    "max_retries": 3,
    "escalate_on_repeat_fail": true,
    "hold_timeout_minutes": 30
  }
}
```

## 来源

- Meta_Kim: https://github.com/KimYx0207/Meta_Kim
- 115 Stars, MIT License