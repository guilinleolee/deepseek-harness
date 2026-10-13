---
license: UNKNOWN
triggers: ["wiki contradiction resolver", "Wiki 矛盾检测器"]
---
# Wiki 矛盾检测器

检测 Wiki 笔记中的内容矛盾，支持实体关系矛盾、时序矛盾、因果矛盾、语义矛盾四种类型，维护知识库一致性。

## 功能

- **四维矛盾检测**：实体关系、时序、因果、语义矛盾识别
- **矛盾图谱构建**：节点=笔记，边=矛盾关系
- **置信度评估**：0-1置信度评分，可信度<0.4自动过滤
- **解决方案生成**：自动生成矛盾解决建议
- **与自愈系统联动**：矛盾自动修复或标记争议

## 目录结构

```
wiki-contradiction-resolver/
├── SKILL.md                    # 本文件
├── prompts/
│   └── contradiction_prompt.md  # 矛盾检测提示词
└── scripts/
    ├── resolver.py             # 矛盾检测核心
    └── graph_builder.py         # 矛盾图谱构建
```

## 使用方法

### 扫描所有笔记

```bash
python3 ~/.claude/skills/wiki-contradiction-resolver/scripts/resolver.py --scan
```

### 检测单条笔记

```bash
python3 ~/.claude/skills/wiki-contradiction-resolver/scripts/resolver.py --note "笔记ID"
```

### 构建矛盾图谱

```bash
python3 ~/.claude/skills/wiki-contradiction-resolver/scripts/graph_builder.py --build
```

### 查看矛盾报告

```bash
python3 ~/.claude/skills/wiki-contradiction-resolver/scripts/resolver.py --report --json
```

## 矛盾类型

### 1. 实体关系矛盾

笔记A声明"X=Y"，笔记B声明"X≠Y"：

```yaml
type: entity_relation
node_a: note_id_A
node_b: note_id_B
entity: "X"
statement_a: "X是Y的类型"
statement_b: "X不是Y的类型"
confidence: 0.85
```

### 2. 时序矛盾

时间线不一致：

```yaml
type: temporal
node_a: note_id_A
node_b: note_id_B
event: "事件X"
time_a: "2024年"
time_b: "2023年"
confidence: 0.92
```

### 3. 因果矛盾

因果关系相反：

```yaml
type: causal
node_a: note_id_A
node_b: note_id_B
cause: "A导致B"
counter: "B导致A"
confidence: 0.78
```

### 4. 语义矛盾

语义上相互否定：

```yaml
type: semantic
node_a: note_id_A
node_b: note_id_B
statement_a: "X是好的"
statement_b: "X是不好的"
confidence: 0.65
```

## 置信度评估

| 置信度 | 等级 | 处理方式 |
|--------|------|---------|
| 0.8-1.0 | 高 | 自动标记为争议，等待人工确认 |
| 0.5-0.8 | 中 | 生成解决建议，优先展示 |
| 0.4-0.5 | 低 | 记录但不强制展示 |
| <0.4 | 极低 | 自动过滤，不计入报告 |

## 矛盾解决策略

| 矛盾类型 | 解决策略 | 优先级 |
|----------|---------|--------|
| 事实矛盾 | 引用权威来源验证 | P0 |
| 时序矛盾 | 追溯原始时间戳 | P0 |
| 观点矛盾 | 保留双方，标注立场 | P1 |
| 数据矛盾 | 重新统计验证 | P1 |
| 来源矛盾 | 引用溯源，标记时效 | P2 |

## 图谱节点类型

```
┌─────────────────────────────────────────────────────────────┐
│                    矛盾图谱节点类型                          │
├─────────────────────────────────────────────────────────────┤
│  正常节点 (green)     - 无矛盾                              │
│  争议节点 (yellow)    - 置信度 0.5-0.8                     │
│  矛盾节点 (red)      - 置信度 >0.8                         │
│  已解决节点 (blue)    - 矛盾已修复                          │
└─────────────────────────────────────────────────────────────┘
```

## 与自愈系统联动

```python
# 矛盾检测完成后触发自愈
from wiki_contradiction_resolver import ContradictionResolver

resolver = ContradictionResolver()
conflicts = resolver.scan_all()

for conflict in conflicts:
    if conflict.confidence > 0.8:
        # 触发自愈流程
        self_healer.heal(conflict)
```

## 健康度影响

Wiki 健康度计算中，矛盾贡献：

```
health_score -= min(10, disputed_count * 2)
```

| 矛盾数量 | 健康度扣分 |
|----------|-----------|
| 0 | 0 |
| 1-5 | -2 |
| 6-10 | -5 |
| >10 | -10 |

## 适用场景

- Wiki 知识库质量维护
- 多人协作知识库审核
- 知识库合并后的矛盾检测
- 自愈系统的前置检测
- 知识复利系统健康监控
