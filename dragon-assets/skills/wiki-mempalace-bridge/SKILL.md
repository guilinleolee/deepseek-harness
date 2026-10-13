---
license: UNKNOWN
triggers: ["wiki mempalace bridge", "Wiki-MemPalace 桥接器 (wiki-mempalace-bridge)"]
---
# Wiki-MemPalace 桥接器 (wiki-mempalace-bridge)

## L0: 一句话描述 (≤15字)
Wiki笔记与MemPalace宫殿记忆双向同步

## L1: 使用场景 (50-100字)
当Wiki笔记被归档时，自动映射到MemPalace房间。当MemPalace检测到矛盾时，同步到Wiki矛盾标记。实现知识在两层系统间无缝流动。

## L2: 详细文档

### 核心理念

```
┌─────────────────────────────────────────────────────────────┐
│                  Wiki ↔ MemPalace 双向桥接                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   Wiki笔记 ───映射──▶ MemPalace房间                        │
│   ↓                       ↓                               │
│   知识沉淀              矛盾检测                          │
│   ↓                       ↓                               │
│   复利增长              记忆共鸣                          │
│   ↓                       ↓                               │
│   Wiki更新 ◀──反馈── MemPalace                           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 映射规则

| Wiki概念 | MemPalace概念 | 映射说明 |
|---------|--------------|---------|
| 笔记标题 | Entity | 作为实体存入KG |
| 笔记标签 | Room | 映射到Wing/Rooms/Halls |
| 笔记链接 | Relations | 存入三元组(entity, relation, target) |
| 矛盾标记 | 矛盾检测 | 触发MemPalace矛盾解决 |
| 复利值 | 实体重要性 | 影响搜索权重 |

### 映射触发器

```yaml
同步触发:
  Wiki → MemPalace:
    - 笔记创建: 创建实体 + 存入房间
    - 笔记链接: 创建三元组关系
    - 矛盾标记: 触发矛盾检测流程
    - 复利更新: 更新实体重要性评分

  MemPalace → Wiki:
    - 矛盾发现: 更新Wiki矛盾标记
    - 房间关联: 添加Wiki相关链接
    - 遗忘触发: Wiki笔记添加"待复习"标记
```

### 使用方式

```bash
# 同步单条笔记到MemPalace
python3 ~/.claude/skills/wiki-mempalace-bridge/scripts/bridge.py \
  --sync wiki-to-mp \
  --note-id "microservice-ddd"

# 双向同步(全部)
python3 ~/.claude/skills/wiki-mempalace-bridge/scripts/bridge.py \
  --sync bidirectional \
  --all

# 同步矛盾标记
python3 ~/.claude/skills/wiki-mempalace-bridge/scripts/bridge.py \
  --sync contradiction \
  --note-id "microservice-ddd" \
  --status "resolved"

# 查看桥接状态
python3 ~/.claude/skills/wiki-mempalace-bridge/scripts/bridge.py \
  --status
```

### 数据格式

```yaml
# Wiki笔记Frontmatter新增映射字段
---
title: 微服务DDD边界划分
mempalace:
  entity_id: "entity_abc123"          # MemPalace实体ID
  room: "technical/architecture"        # 映射房间
  wing: "knowledge_hall"               # 映射Wing
  importance: 0.85                     # 重要性(0-1)
  synced_at: 2026-04-12T10:30:00
  last_contradiction: 2026-04-10
  contradiction_count: 2               # 解决的矛盾数
---

# MemPalace实体扩展字段
Entity:
  wiki_notes: ["microservice-ddd", "ddd-context-mapping"]
  wiki_compound_value: 1847
  bridge_status: "synced"
  last_sync: 2026-04-12T10:30:00
```

### 矛盾同步流程

```
1. MemPalace检测到矛盾
   entity_a.claim ≠ entity_b.claim

2. 查询矛盾涉及的Wiki笔记
   → note_a.md, note_b.md

3. 更新Wiki笔记矛盾标记
   compound:
     disputed: true
     disputed_with: [note_b_id]
     dispute_reason: "..."
     resolution_status: "pending"

4. 矛盾解决后
   → 更新MemPalace实体
   → 更新Wiki笔记
   → 复利值+10%(矛盾解决奖励)
```

### 与07记录师协同

```
[@07记录师] 归档这个发现
  ↓
[llm-wiki-compiler] 编译为Wiki笔记
  ↓
[wiki-mempalace-bridge] 映射到MemPalace房间
  ↓
[MemPalace] 存入KG + 矛盾检测
  ↓
[wiki-compound-interest] 计算复利值
  ↓
反馈: Wiki笔记 ⇄ MemPalace双向同步
```

### 桥接仪表盘

```bash
python3 ~/.claude/skills/wiki-mempalace-bridge/scripts/dashboard.py

# 输出示例:
# ╔══════════════════════════════════════════════════════════╗
# ║       Wiki ↔ MemPalace 桥接状态                      ║
# ╠══════════════════════════════════════════════════════════╣
# ║  Wiki笔记: 1,234    MemPalace实体: 1,180           ║
# ║  同步率: 95.6%     矛盾数: 23 (已解决18)          ║
# ║  最后同步: 2分钟前   记忆共鸣: 0.85               ║
# ╠══════════════════════════════════════════════════════════╣
# ║  未同步笔记: 54个                                   ║
# ║  待解决矛盾: 5个                                    ║
# ╚══════════════════════════════════════════════════════════╝
```

## 文件结构

```
wiki-mempalace-bridge/
├── SKILL.md                              # 本文件
├── scripts/
│   ├── bridge.py                       # 桥接核心脚本
│   ├── mapper.py                       # 映射器
│   ├── contradiction_sync.py            # 矛盾同步
│   └── dashboard.py                    # 桥接仪表盘
└── prompts/
    └── mapping_prompt.md             # 映射评估提示词
```

## 预期收益

| 指标 | 效果 |
|------|------|
| 知识一致性 | +95% |
| 矛盾发现率 | +300% |
| 记忆召回率 | +50% |
| 双系统协同效率 | +200% |
