---
license: UNKNOWN
triggers: ["wiki spaced repetition", "Wiki 间隔重复复习系统"]
---
# Wiki 间隔重复复习系统

基于 SM-2 算法自动追踪 Wiki 笔记复习周期，确保知识在遗忘曲线关键节点被强化，维持长期记忆。

## 功能

- **SM-2 算法实现**：标准间隔重复算法，动态调整复习间隔
- **遗忘曲线追踪**：记录每次复习的难度评分，自动计算下次复习时间
- **与 Wiki 归档联动**：笔记归档后自动加入复习队列
- **知识复利引擎**：重复引用次数越多，复习间隔越长，知识越牢固

## 目录结构

```
wiki-spaced-repetition/
├── SKILL.md                    # 本文件
├── prompts/
│   └── sr_prompt.md           # LLM 复习调度提示词
└── scripts/
    ├── spaced_repetition.py     # 间隔重复引擎
    └── review_scheduler.py     # 复习调度器
```

## 核心算法

### SM-2 算法参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| 初次间隔 | 1 天 | 首次复习间隔 |
| EF (简易度因子) | 2.5 | 初始难度系数 |
| 最小 EF | 1.3 | EF 下限 |
| EF 调整量 | 按评分计算 | q=0→EF-0.8, q=3→EF不变, q=5→EF+0.1 |

### 间隔计算公式

```
I(1) = 1 天
I(2) = 6 天
I(n) = I(n-1) × EF    (n > 2)
```

### 质量评分 (q) 定义

| 评分 | 标签 | 描述 |
|------|------|------|
| 0 | 完全忘记 | 看完答案仍想不起来 |
| 1 | 错误但想起 | 稍后看到答案能回忆 |
| 2 | 错误易想起 | 答案很快在脑中出现 |
| 3 | 正确困难 | 回忆正确但很吃力 |
| 4 | 正确流畅 | 回忆正确，稍有停顿 |
| 5 | 瞬间回忆 | 完全正确，瞬间回忆 |

## 使用方法

### 调度今日复习

```bash
python3 ~/.claude/skills/wiki-spaced-repetition/scripts/review_scheduler.py --today
```

### 查看复习队列

```bash
python3 ~/.claude/skills/wiki-spaced-repetition/scripts/review_scheduler.py --queue
```

### 记录复习结果

```bash
python3 ~/.claude/skills/wiki-spaced-repetition/scripts/spaced_repetition.py --review "note_id" --quality 4
```

### 获取待复习笔记

```bash
python3 ~/.claude/skills/wiki-spaced-repetition/scripts/spaced_repetition.py --due
```

## 与 Wiki 归档联动

### 自动加入复习队列

笔记归档后自动调用：

```python
from spaced_repetition import SpacedRepetition

sr = SpacedRepetition()
sr.add_note("note_id", "笔记标题", tags=["#Python", "#异步"])
```

### 复习触发流程

```
笔记归档 → 自动加入复习队列
    ↓
复习时间到达 → LLM 生成复习问题
    ↓
用户回答 → SM-2 计算下次间隔
    ↓
更新复习记录 → 知识复利加分
```

## 知识复利公式

```
复利因子 = 1 + (归档次数 × 0.05) + (引用次数 × 0.1)
复习间隔 = 基础间隔 × 复利因子 × EF
```

| 归档次数 | 引用次数 | 复利因子 | 7天后基础间隔 |
|----------|----------|----------|--------------|
| 0 | 0 | 1.0 | 7 天 |
| 5 | 3 | 1.55 | 10.85 天 |
| 10 | 10 | 2.5 | 17.5 天 |
| 20 | 20 | 4.0 | 28 天 |

## 复习记录格式

```yaml
# ~/.claude/wiki_review_queue/{note_id}.yaml
note_id: "note_id"
title: "笔记标题"
added_at: 2026-04-11
reviews:
  - date: 2026-04-12
    quality: 4
    interval: 1
    ef: 2.5
    next_review: 2026-04-13
  - date: 2026-04-13
    quality: 5
    interval: 6
    ef: 2.6
    next_review: 2026-04-19
due_reviews: 1
total_reviews: 2
streak: 2
```

## 遗忘曲线分析

```
记忆保留率 (%)
│
100 │████████
 80 │████████████
 60 │████████████████
 40 │████████████████████████
 20 │████████████████████████████████████████
  0 └────┬────┬────┬────┬────┬──── 时间(天)
          1    3    7   14   30   60

红色区域 = 复习临界点 (遗忘前强化)
绿色区域 = 记忆巩固区
```

## 与其他系统协同

### 复习优先级排序

1. **遗忘临界笔记**：距离遗忘 < 1 天
2. **高引用笔记**：被引用次数 > 5
3. **新归档笔记**：添加时间 < 7 天
4. **陈旧笔记**：超过 30 天未复习

### 复习后触发

- 复习完成 → 更新 Wiki 健康度评分
- 高质量回忆 (q=5) → 增加笔记权重
- 遗忘 (q=0-1) → 降低笔记权重，缩短间隔

## 适用场景

- Wiki 知识库长期维护
- 学习笔记主动复习
- 遗忘曲线可视化追踪
- 知识复利自动积累
- 与 07 记录师 Wiki 归档联动
