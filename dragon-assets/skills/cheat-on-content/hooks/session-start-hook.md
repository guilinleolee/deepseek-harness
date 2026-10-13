# session-start Hook

> 新会话启动时初始化内容创作状态，管理系统Buffer和待复盘队列。

## 触发时机

`sessionStart` — Claude Code新会话开始时

## 初始化任务

### 1. Buffer状态检查

检查Buffer当前值，如果为0则警告:

```
🔔 Buffer耗尽警告

当前Buffer: 0/5
状态: 已耗尽

根据铁律，您需要先完成至少一次T+3d复盘才能继续发布。
请使用以下命令查看待复盘内容:
  python3 skills/cheat-on-content/hooks/session-start.py check-retro
```

### 2. 待复盘队列检查

列出所有发布满72小时但未复盘的内容:

```bash
python3 skills/cheat-on-content/hooks/session-start.py check-retro
```

输出示例:

```
📋 待复盘队列 (3项)

┌─────────────────────────────────────────────────────────────┐
│ #1 2026-05-22-01 [抖音] 职场沟通        T+3d ⏰立即复盘    │
├─────────────────────────────────────────────────────────────┤
│ #2 2026-05-22-02 [小红书] 效率工具    T+4d ⚠️超时复盘     │
├─────────────────────────────────────────────────────────────┤
│ #3 2026-05-21-01 [微博] AI趋势        T+5d ⚠️超时复盘     │
└─────────────────────────────────────────────────────────────┘

⚠️ 根据铁律，未完成复盘前不能发布新内容。
```

### 3. Rubric健康度检查

检查当前Rubric状态，提示需要更新观察的情况:

```bash
python3 skills/cheat-on-content/hooks/session-start.py check-rubric
```

输出示例:

```
📊 Rubric健康度: 72/100 (🟡 良好)

⚠️ 以下观察需要检查:
- [观察#7] "职场内容ER普遍较高" — 上周3条职场内容ER都偏低
- [观察#12] "视频前三秒很重要" — 最近2条视频HP实际分都高于预测

请使用复盘模板更新Rubric。
```

### 4. 近期事件摘要

显示最近7天的关键事件:

```
📅 最近7天摘要

预测提交: 5个
内容发布: 3个
首次复盘: 2个
最终复盘: 1个
Buffer变化: Ship -1, Shoot +2

平均预测准确度: 76%
最高分内容: 2026-05-24-01 (8.5分)
最大偏差: 2026-05-22-02 (ER偏差 -3分)
```

## 初始化数据加载

### 加载到上下文的L1关键事实

新会话时，将以下信息注入到上下文(L1 Critical Facts):

1. **当前Buffer**: `Buffer: 4/5`
2. **最近一次预测**: 发布ID、日期、话题、总分
3. **待复盘数量**: `待复盘: 3个`
4. **Rubric健康度**: `Rubric: 72/100`

## Buffer管理规则

| 事件 | Buffer变化 | 规则 |
|------|-----------|------|
| 会话启动 | 不变 | 读取上次状态 |
| 发布内容(Ship) | -1 | 消耗Buffer |
| 拍摄/制作完成(Shoot) | +1 | 完成制作，Buffer恢复 |
| T+3d复盘完成 | 0 | 不增加Buffer，但解锁发布 |
| T+7d最终复盘完成 | 0 | 不增加Buffer，但归档 |

## 使用方式

```bash
# 完整初始化检查
python3 skills/cheat-on-content/hooks/session-start.py init

# 仅检查Buffer
python3 skills/cheat-on-content/hooks/session-start.py check-buffer

# 仅检查待复盘
python3 skills/cheat-on-content/hooks/session-start.py check-retro

# 仅检查Rubric
python3 skills/cheat-on-content/hooks/session-start.py check-rubric
```

## 配置

```json
{
  "sessionStart": {
    "autoInit": true,
    "loadToContext": ["buffer", "pending_retro", "rubric_health"],
    "maxPendingRetro": 5,
    "bufferWarningThreshold": 2,
    "rubricWarningThreshold": 70
  }
}
```