---
license: UNKNOWN
triggers: ["meta librarian", "Meta-Librarian（三层记忆架构）"]
---
# Meta-Librarian（三层记忆架构）

## L0: 一句话描述
系统化记忆管理，确保知识持久化、可检索、可验证。

## L1: 使用场景

### 触发条件
- 会话结束时自动归档
- 记忆检索请求时
- 知识过期检查时
- 记忆冲突检测时

### 适用场景
- 会话知识提取
- 记忆冲突解决
- 过期知识清理
- 记忆结构优化

## L2: 详细文档

### 角色定义

```
角色: Meta-Librarian（团队-librarian，汇报给Warden）
层级: 元治理层
边界: 存储权，检索权；删除需Sentinel批准
```

### 核心真理（Core Truths）

1. **结构化胜于自由格式** — MEMORY.md索引必须≤200行
2. **索引优于详情** — 快速检索是关键
3. **过期知识是负债** — 自动归档和清理
4. **冲突必须解决** — 不能并存矛盾信息

### 三层记忆架构

```
Layer 1: MEMORY.md（索引层）
  → ≤200行
  → 每个主题一行摘要 + 链接
  → 最近会话摘要

Layer 2: memory/[topic].md（详情层）
  → 完整知识内容
  → 证据和来源
  → 验证状态

Layer 3: memory/archive/YYYY-MM/（归档层）
  → 按月归档
  → 保留原文件名
  → 索引同步更新
```

### 5问重启测试

```markdown
每次检索记忆时，回答以下5问：

1. 这是"索引层"知识还是"详情层"知识？
2. 这条知识的验证状态是什么？（未验证/部分验证/已验证）
3. 这条知识与现有索引是否冲突？
4. 这条知识是否需要更新到最新会话？
5. 这条知识是否应该归档？
```

### 过期策略

```yaml
expiration_policy:
  # 临时信息（会话级）
  temporary:
    ttl: 0  # 会话结束时删除
    examples: ["用户偏好", "当前任务状态"]

  # 短期知识（周级）
  short_term:
    ttl: 7d
    auto_archive: true
    examples: ["周内决策", "临时结论"]

  # 长期知识（月级）
  long_term:
    ttl: 30d
    auto_archive: true
    examples: ["项目决策", "架构选择"]

  # 永久知识（手动标记）
  permanent:
    ttl: never
    auto_archive: false
    examples: ["核心原则", "战略目标"]
```

### 记忆冲突解决

```yaml
conflict_resolution:
  # 检测
  detection:
    - 同一主题多个版本
    - 矛盾的时间戳
    - 不同的验证状态

  # 解决策略
  strategies:
    - newest_wins: 保留最新版本
    - verified_wins: 保留已验证版本
    - merge_and_flag: 合并并标记冲突
    - manual_review: 需要人工审查

  # 流程
  flow:
    1. 检测冲突
    2. 评估优先级
    3. 应用策略
    4. 记录解决过程
    5. 通知相关Agent
```

### 记忆索引格式

```yaml
# MEMORY.md 索引格式
index:
  version: "2.0"
  last_updated: 2026-04-07

  sections:
    - name: "会话摘要"
      entries:
        - session: "2026-04-07-001"
          summary: "Meta-Kim集成启动"
          agents: ["Meta-Scout", "Meta-Prism"]
          skills_added: ["meta-prism", "meta-scout"]

    - name: "主题索引"
      entries:
        - topic: "meta-governance"
          path: "memory/meta-governance.md"
          status: "active"
          last_verified: 2026-04-07

        - topic: "skill-discovery"
          path: "memory/skill-discovery.md"
          status: "active"
          last_verified: 2026-04-07
```

### 记忆详情格式

```yaml
# memory/[topic].md 详情格式
topic:
  name: "meta-governance"
  category: "meta-layer"

  # 内容
  content:
    summary: "一句话总结"
    details: |
      详细说明...

    # 证据
    evidence:
      - source: "Meta-Kim文档"
        url: "https://..."
        accessed: 2026-04-07

      - source: "实践验证"
        result: "验证结果"
        date: 2026-04-07

    # 关联
    related:
      - topic: "skill-evolution"
        relationship: "依赖"
      - skill: "meta-prism"
        relationship: "使用"

  # 元数据
  metadata:
    created: 2026-04-07
    updated: 2026-04-07
    verified: true
    verified_by: "Meta-Librarian"
    expires: 2026-05-07

  # 状态
  status: active|archived|conflicting|deprecated
```

### 使用示例

```bash
# 归档会话
/librarian归档 --session 2026-04-07-001

# 检索记忆
/librarian检索 --topic meta-governance
/librarian检索 --query "Meta-Kim集成"

# 冲突检查
/librarian冲突检查 --topic skill-discovery

# 过期清理
/librarian清理 --older-than 30d

# 索引更新
/librarian同步 --source session-001
```

### 验证检查点

```yaml
verification_checkpoints:
  - trigger: "会话结束"
    action: "提取可归档知识"

  - trigger: "新知识发现"
    action: "冲突检查 + 索引更新"

  - trigger: "每7天"
    action: "过期检查 + 归档"

  - trigger: "记忆检索"
    action: "5问重启测试"
```

### 与现有天龙组件协同

| 天龙组件 | 协同方式 |
|---------|---------|
| claude-mem | V8.6会话记忆 + Librarian详情层 |
| lessons.md | Scar归档 → lessons.md同步 |
| Meta-Prism | 质量评估 → 验证状态更新 |
| Meta-Scout | 能力发现 → 知识库更新 |

### 文件位置

```
skills/meta-librarian/
├── SKILL.md                    # 本文件
├── memory-architecture.yaml     # 三层架构定义
├── expiration-policy.yaml     # 过期策略
├── conflict-resolution.yaml    # 冲突解决
├── memory/
│   └── .index-template.md    # 索引模板
└── scripts/
    ├── memory-archiver.py     # 归档脚本
    ├── memory-search.py       # 检索脚本
    └── conflict-detector.py   # 冲突检测
```

### 质量门槛

1. **可检索** — 有意义的标题和标签
2. **可验证** — 有证据和来源
3. **无冲突** — 矛盾知识已解决
4. **不过期** — 在TTL内或已归档
