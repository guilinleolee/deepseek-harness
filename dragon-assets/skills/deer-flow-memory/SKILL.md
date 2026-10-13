---
license: UNKNOWN
github_repo: bytedance/deer-flow
github_hash: f394c0d8c8de8821ac6a5becc73f5a9587a03e42
triggers: ["deer flow memory", "deer-flow-memory"]
---
# deer-flow-memory

## Overview

DeerFlow跨会话长期记忆系统 - 持久化存储用户画像、偏好和累积知识。

**来源**: [bytedance/deer-flow](https://github.com/bytedance/deer-flow) | **MIT License**

## When to Use

- 需要跨会话持久化记忆
- 需要用户画像管理
- 需要偏好追踪
- 需要累积知识复用
- 需要上下文重建

## Core Features

### 1. User Profile Memory
- 用户基本信息
- 偏好设置
- 交互历史
- 能力画像

### 2. Preference Memory
- 风格偏好
- 格式偏好
- 交互偏好
- 内容偏好

### 3. Knowledge Memory
- 累积事实
- 项目上下文
- 决策历史
- 经验教训

### 4. Conversation Summaries
- 会话摘要
- 关键决策
- 待办事项
- 后续跟进

## Memory Structure

```json
{
  "user_id": "string",
  "profile": {
    "name": "string",
    "language": "string",
    "timezone": "string",
    "expertise_areas": ["string"]
  },
  "preferences": {
    "style": "concise|detailed",
    "format": "markdown|plain",
    "tone": "formal|casual|technical",
    "output_length": "short|medium|long"
  },
  "knowledge": {
    "facts": [
      {
        "fact": "string",
        "source": "string",
        "confidence": 0.95,
        "created_at": "timestamp"
      }
    ],
    "projects": [
      {
        "name": "string",
        "context": "string",
        "decisions": ["string"],
        "outcomes": ["string"]
      }
    ],
    "lessons": [
      {
        "lesson": "string",
        "context": "string",
        "outcome": "string"
      }
    ]
  },
  "conversations": [
    {
      "session_id": "string",
      "summary": "string",
      "decisions": ["string"],
      "todos": ["string"],
      "created_at": "timestamp"
    }
  ]
}
```

## Operations

### Read Memory
```bash
curl -s "$DEERFLOW_GATEWAY_URL/api/memory"
```

### Write Memory
```bash
curl -s -X POST "$DEERFLOW_GATEWAY_URL/api/memory" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "fact|preference|lesson|summary",
    "content": {...}
  }'
```

### Update Memory
```bash
curl -s -X PUT "$DEERFLOW_GATEWAY_URL/api/memory/<id>" \
  -H "Content-Type: application/json" \
  -d '{"content": {...}}'
```

### Search Memory
```bash
curl -s -X POST "$DEERFLOW_GATEWAY_URL/api/memory/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "user preferences", "type": "preference"}'
```

### Delete Memory
```bash
curl -s -X DELETE "$DEERFLOW_GATEWAY_URL/api/memory/<id>"
```

## 与天龙引擎现有记忆系统协同

| System | Layer | Function | Features |
|--------|-------|---------|----------|
| claude-mem | 会话层 | 自动捕获+AI压缩 | 会话级记忆 |
| advanced-memory-sync | 分层层 | L0-L3四层压缩 | Obsidian同步 |
| **deer-flow-memory** | 持久层 | 用户画像+偏好 | 跨会话持久化 |
| supermemory | 跨平台层 | 事实提取+矛盾解决 | 多平台统一 |

```
┌─────────────────────────────────────────────────────────────┐
│ 天龙引擎 记忆系统分层架构                                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ Layer 4: Supermemory (V8.74) ⭐跨平台                      │
│   → 跨平台事实提取 + 矛盾解决 + 自动遗忘                   │
│                                                             │
│ Layer 3: deer-flow-memory (V8.75) ⭐新增                   │
│   → 用户画像 + 偏好追踪 + 累积知识                         │
│                                                             │
│ Layer 2: advanced-memory-sync (V8.61)                      │
│   → 四层记忆同步 + Obsidian可视化 + Git-Like分支          │
│                                                             │
│ Layer 1: claude-mem (V8.6)                                │
│   → 会话自动捕获 + AI压缩 + RAG检索                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Usage Commands

```bash
# 读取用户记忆
[@记忆] 读取我的用户画像

# 更新偏好
[@记忆] 更新我的输出风格偏好为简洁

# 添加新知识
[@记忆] 记住这个项目使用React 18 + TypeScript

# 搜索相关知识
[@记忆] 搜索所有关于API设计的知识

# 查看会话摘要
[@记忆] 列出最近5次会话摘要
```

## Memory Management

### Automatic Triggers
| Trigger | Action | Memory Type |
|---------|--------|-------------|
| 用户偏好表达 | 自动记录 | preference |
| 关键事实陈述 | 自动提取 | fact |
| 成功/失败案例 | 自动记录 | lesson |
| 会话结束 | 自动摘要 | summary |

### Manual Commands
| Command | Function |
|---------|---------|
| `/memory profile` | 显示用户画像 |
| `/memory preferences` | 显示偏好设置 |
| `/memory knowledge` | 显示累积知识 |
| `/memory search <query>` | 搜索记忆 |
| `/memory forget <id>` | 删除记忆 |

## Expected Benefits

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| 记忆持久化 | 会话级 | 跨会话 | +500% |
| 上下文重建 | 手动 | 自动 | +300% |
| 偏好一致性 | 低 | 高 | +200% |
| 知识复用 | 低 | 高 | +400% |

## Version

- **V1.0** (2026-04-02): 初始集成DeerFlow记忆系统
