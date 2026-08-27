---
license: UNKNOWN
triggers: ["scar memory", "Scar-Memory（疤痕记忆系统）"]
---
# Scar-Memory（疤痕记忆系统）

## L0: 一句话描述
系统化失败模式记录，比lessons.md更结构化的YAML格式记忆系统。

## L1: 使用场景

### 触发条件
- 任务失败时自动记录
- 重复错误发生时记录
- 用户纠正时记录
- 三次失败后强制记录

### 适用场景
- Bug修复失败记录
- 架构决策失误记录
- 测试失败模式记录
- 性能问题记录
- 安全事件记录

## L2: 详细文档

### 核心哲学

> **Scars make you stronger, not lessons.**
>
> 疤痕让你更强，而非仅仅记录教训。

### Scar vs Lessons对比

| 维度 | lessons.md | Scar系统 |
|------|-----------|----------|
| **触发条件** | 用户纠正/重复错误 | 所有失败自动记录 |
| **结构化** | 自由格式 | YAML标准格式 |
| **可追溯性** | 弱 | 强（关联任务/Agent/时间） |
| **查询效率** | 低 | 高（按标签分类） |
| **反模式检测** | 无 | 自动识别重复模式 |
| **自动归档** | 无 | 30天无复发自动归档 |

### 三层记忆架构

```
Layer 1: memory/scars/       ← Scars永久存储
Layer 2: memory/scars/archive/  ← 过期归档（30天无复发）
Layer 3: memory/scars/candidates/ ← 待确认候选
```

### 核心函数

```javascript
// 记录Scar
recordScar({
  trigger: string,           // 触发条件
  pattern: string,            // 失败模式
  severity: critical|high|medium|low,
  resolution: string,        // 解决方案
  related_skills: string[],   // 相关Skills
  related_agents: string[],   // 相关Agents
  context: object            // 上下文
})

// 查询Scar
queryScar({
  tags?: string[],
  severity?: string,
  agent?: string,
  skill?: string,
  since?: Date
})

// 复发检测
checkRecurrence(scarId) → recurrence_count++
```

### Scar YAML格式

```yaml
scar:
  id: SCAR-001
  title: "多文件修改时忽略边界条件"

  # 元数据
  created: 2026-04-07T10:30:00Z
  created_by: 03-builder
  severity: high

  # 触发条件
  trigger:
    type: "git-diff"
    threshold: 5  # diff > 5个文件
    symptoms:
      - "边界测试失败"
      - "跨模块变量未同步"

  # 失败模式
  pattern:
    category: "boundary-condition"
    root_cause: "修改多文件时未强制运行边界测试"
    frequency: "每次多文件修改"

  # 解决方案
  resolution:
    action: "每次修改后强制运行边界测试"
    verification: "边界测试PASS"
    related_fixes:
      - "git hook: post-checkout"

  # 关联
  related_skills:
    - "tdd-workflow"
    - "systematic-debugging"
    - "verification-loop"

  related_agents:
    - "03-builder"
    - "04-validator"

  # 追踪
  recurrence_count: 3
  last_occurrence: 2026-04-07
  first_occurrence: 2026-03-15

  # 状态
  status: active|archived|monitoring
  archive_reason: null  # 如果archived，说明原因

  # 证据
  evidence:
    - "Test failed: boundary test in module X"
    - "Variable Y not synchronized across files"
```

### 反模式检测

自动识别以下模式：

```yaml
anti-patterns:
  # 重复Scar
  duplicate_trigger:
    detect: "相同trigger的Scar数量 > 2"
    action: "合并为新的通用Scar"

  # 相似Scar
  similar_pattern:
    detect: "相似度 > 0.8"
    action: "标记为候选合并"

  # 深层根因
  shallow_root:
    detect: "resolution过于具体"
    action: "向上追溯根因"

  # 孤立的Scar
  orphaned_scar:
    detect: "无related_skills"
    action: "关联到相关Skill"
```

### 归档策略

```yaml
archive_rules:
  # 30天无复发自动归档
  no_recurrence_30d:
    condition: "recurrence_count == 0 AND last_occurrence < now - 30d"
    action: "archive"
    reason: "长期无复发，模式已解决"

  # 已解决的Scar
  resolved:
    condition: "resolution_verified == true"
    action: "archive"
    reason: "解决方案已验证"

  # 过时的Scar
  outdated:
    condition: "created < now - 90d AND status == active"
    action: "review_required"
    reason: "需要审查是否仍然相关"
```

### 使用示例

```bash
# 记录Scar
/scar记录 "修复登录Bug失败" --severity high --agent 03-builder

# 查询Scar
/scar查询 --tag boundary-condition --severity high
/scar查询 --agent 03-builder --since 2026-04-01

# 复发检测
/scar复发 SCAR-001

# 合并Scar
/scar合并 SCAR-001, SCAR-002, SCAR-003

# 归档Scar
/scar归档 SCAR-001 --reason "长期无复发"
```

### 自动化触发

```yaml
auto_triggers:
  # 任务失败
  task_failure:
    trigger: "任务执行失败"
    action: "自动创建candidate Scar"
    notification: "通知相关Agent"

  # 重复错误
  repeated_error:
    trigger: "相同错误发生3次"
    action: "自动升级为Scar"
    notification: "通知所有相关Agent"

  # 用户纠正
  user_correction:
    trigger: "用户纠正Agent错误"
    action: "创建candidate Scar"
    notification: "等待Agent确认"
```

### 与Meta-Prism协同

```
Meta-Prism检测失败 → Scar记录 → lessons.md更新 → Skill优化
                    ↓
              Scars反模式检测
                    ↓
              能力缺口识别 → Meta-Scout发现新Skill
```

### 与现有天龙组件协同

| 天龙组件 | 协同方式 |
|---------|---------|
| lessons.md | Scar自动摘要 → lessons.md同步 |
| meta-prism | 质量失败 → Scar记录 |
| skill-evolution-manager | Scar反模式 → 能力缺口 |
| 09-03元审查师 | Scar审查 → 元审查触发 |

### 文件位置

```
skills/scar-memory/
├── SKILL.md                    # 本文件
├── templates/
│   └── scar-template.yaml      # Scar YAML模板
├── scripts/
│   ├── scar_record.py          # 记录脚本
│   ├── scar_query.py           # 查询脚本
│   └── scar_archive.py        # 归档脚本
├── memory/scars/               # Scars存储
│   ├── SCAR-001.yaml
│   └── SCAR-002.yaml
├── memory/scars/archive/       # 归档存储
└── memory/scars/candidates/    # 候选存储
```

### 质量门槛

与Meta-Prism的lessons.md质量门槛一致：

1. **需要发现** — 非文档查询
2. **可复用** — 有助于未来任务
3. **明确触发条件** — 具体错误/症状
4. **已验证** — 实际有效
