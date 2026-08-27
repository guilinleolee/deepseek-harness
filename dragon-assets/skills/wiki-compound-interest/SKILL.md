---
license: UNKNOWN
triggers: ["wiki compound interest", "Wiki知识复利引擎 (wiki-compound-interest)"]
---
# Wiki知识复利引擎 (wiki-compound-interest)

## L0: 一句话描述 (≤15字)
知识像复利一样增长，每次引用都增值

## L1: 使用场景 (50-100字)
当笔记被创建、更新、被引用时，计算并更新知识复利值。复利值越高，说明该知识被验证、被复用越多，价值越大。

## L2: 详细文档

### 核心理念

```
价值(第N次) = 价值(第1次) × (1 + 链接数 × 0.1)^N × memory_resonance
```

知识不是线性累积，而是指数级复利增长。每次引用都是"利息"，复利效应使高频引用的知识价值远超初始价值。

### 复利公式详解

```python
# 基础复利公式
def calculate_compound_value(initial_value, link_count, compilation_count):
    """
    initial_value: 初始价值 (1-10分，基于内容质量)
    link_count: 被引用/链接次数
    compilation_count: 被编译次数(每次复习/更新)
    """
    base_multiplier = (1 + link_count * 0.1) ** compilation_count
    return initial_value * base_multiplier

# 增强版公式(集成MemPalace)
def calculate_enhanced_value(initial_value, link_count, compilation_count, memory_resonance):
    """
    memory_resonance: 宫殿记忆共鸣度
        = room_association × contradiction_solved × 0.5
    """
    base_value = initial_value * (1 + link_count * 0.1) ** compilation_count
    return base_value * (1 + memory_resonance)
```

### 复利等级

| 等级 | 复利值范围 | 说明 | 行动 |
|------|-----------|------|------|
| 🔴 种子 | 1-10 | 初始笔记，需持续浇灌 | 定期复习 |
| 🟡 幼苗 | 10-50 | 知识发芽，开始被引用 | 鼓励链接 |
| 🟢 成长 | 50-200 | 知识成长，形成网络 | 深化连接 |
| 🔵 成熟 | 200-1000 | 知识成熟，稳定输出 | 保持更新 |
| 🟣 智慧 | >1000 | 核心智慧，复利飞轮 | 传承分享 |

### 复利触发器

```yaml
复利触发:
  引用触发:
    - 笔记被其他笔记链接: link_count += 1
    - 引用来源权威性高: multiplier × 1.5
    - 跨领域引用: multiplier × 1.2

  复习触发:
    - 间隔重复复习: compilation_count += 1
    - 发现新证据: value × 1.1
    - 修正错误: value × 0.95 (惩罚)

  矛盾解决:
    - 解决知识矛盾: contradiction_solved += 1
    - 记忆共鸣度: memory_resonance += 0.2
```

### 使用方式

```bash
# 计算单条笔记复利值
python3 ~/.claude/skills/wiki-compound-interest/scripts/compound_calculator.py \
  --note-id "microservice-ddd-boundary" \
  --format json

# 批量计算并排序(查看知识Top)
python3 ~/.claude/skills/wiki-compound-interest/scripts/compound_calculator.py \
  --top 20 \
  --format table

# 更新复利值(在笔记被引用后自动调用)
python3 ~/.claude/skills/wiki-compound-interest/scripts/compound_calculator.py \
  --update "note-id" \
  --trigger "link" \
  --source "source-note-id"

# 查看复利趋势
python3 ~/.claude/skills/wiki-compound-interest/scripts/compound_calculator.py \
  --trend "microservice-ddd-boundary" \
  --days 30
```

### 与07记录师协同

```
[@07记录师] 归档这个发现
  ↓
[wiki-compound-interest] 计算初始复利值
  ↓
[wiki-mempalace-bridge] 映射到MemPalace房间
  ↓
[spaced-repetition] 设置复习提醒
  ↓
[N次引用后] 复利值指数增长
```

### 复利仪表盘

```bash
# 查看知识复利总览
python3 ~/.claude/skills/wiki-compound-interest/scripts/dashboard.py

# 输出示例:
# ╔══════════════════════════════════════════════════════════╗
# ║          Wiki 知识复利仪表盘                              ║
# ╠══════════════════════════════════════════════════════════╣
# ║  知识总数: 1,234    平均复利值: 23.5                    ║
# ║  总复利值: 29,012   复利飞轮: 🔵 45个                   ║
# ║  本月增长: +15.2%   最高复利: 微服务架构 (1,847)       ║
# ╠══════════════════════════════════════════════════════════╣
# ║  Top 5 知识复利:                                        ║
# ║  1. 微服务架构 (1,847) ⭐智慧级                        ║
# ║  2. DDD战术设计 (892)  成熟级                           ║
# ║  3. 事件溯源 (456)     成长级                           ║
# ║  4. CQRS模式 (234)     成长级                           ║
# ║  5. 限界上下文 (123)    幼苗级                           ║
# ╚══════════════════════════════════════════════════════════╝
```

### 存储格式

笔记Frontmatter新增复利字段:

```yaml
---
title: 微服务DDD边界划分
compound:
  initial_value: 5      # 初始价值(1-10)
  current_value: 1847    # 当前复利值
  link_count: 23        # 链接次数
  compilation_count: 15   # 复习次数
  memory_resonance: 0.8  # 记忆共鸣度
  level: wisdom         # 等级: seed/seedling/growth/mature/wisdom
  last_updated: 2026-04-12
  compound_history:
    - date: 2026-03-01
      value: 5
      event: initial
    - date: 2026-03-15
      value: 45
      event: link_added
    - date: 2026-04-01
      value: 234
      event: milestone_reached
---
```

## 文件结构

```
wiki-compound-interest/
├── SKILL.md                              # 本文件
├── scripts/
│   ├── compound_calculator.py          # 复利计算器
│   ├── dashboard.py                      # 复利仪表盘
│   └── batch_update.py                  # 批量更新
└── prompts/
    └── compound_value_prompt.md         # 初始价值评估提示词
```

## 预期收益

| 指标 | 效果 |
|------|------|
| 知识复用率 | +300% |
| 归档积极性 | +200% |
| 知识网络密度 | +150% |
