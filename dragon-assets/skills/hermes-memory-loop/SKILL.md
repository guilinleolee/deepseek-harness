---
license: UNKNOWN
triggers: ["hermes memory loop", "hermes-memory-loop"]
---
# hermes-memory-loop

## 元信息

```yaml
name: hermes-memory-loop
description: Hermes自改进记忆闭环 - FTS5搜索+跨会话召回+用户画像建模
version: 1.0.0
category: autonomous-ai-agents
source: NousResearch/hermes-agent
stars: 21.7k
```

## 核心能力

```
┌─────────────────────────────────────────────────────────────┐
│ Hermes Memory Loop 自改进闭环                                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  📝 MEMORY.md  (Agent笔记)                                 │
│  └── 环境、项目、已学事实 (~2.2k chars)                     │
│                                                             │
│  👤 USER.md   (用户画像)                                   │
│  └── 偏好、沟通风格、上下文 (~1.4k chars)                   │
│                                                             │
│  🔍 FTS5 Session Search                                     │
│  └── SQLite全文搜索，跨会话召回                              │
│  └── LLM总结加速召回                                        │
│                                                             │
│  🧠 Honcho 用户建模                                        │
│  └── 辩证式画像构建                                        │
│  └── 跨会话用户理解                                         │
│                                                             │
│  ⏰ 记忆提醒 (Nudges)                                       │
│  └── 定期推送相关记忆                                       │
│  └── 任务相关自动激活                                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 两层记忆存储

### MEMORY.md
```markdown
# Agent Memory
- 工作目录: /path/to/project
- 当前项目: X项目
- 已解决问题: Y问题用Z方案
- 重要配置: ...
```

### USER.md
```markdown
# User Profile
- 沟通风格: 简洁/详细
- 偏好: 使用工具A而非B
- 上下文: 正在开发Web应用
- 反馈模式: ...
```

## FTS5会话搜索

```sql
-- 创建FTS5虚拟表
CREATE VIRTUAL TABLE sessions_fts USING fts5(
    content,
    session_id,
    timestamp
);

-- 搜索跨会话记忆
SELECT session_id, content, highlight(content, 0, '**', '**') as snippet
FROM sessions_fts
WHERE sessions_fts MATCH '关键词'
ORDER BY timestamp DESC
LIMIT 10;
```

## 冻结快照模式

```
关键原则: Frozen Snapshot Pattern

会话中修改 → 立即持久化到磁盘
系统提示词 → 下次会话启动时加载

效果:
- 实时保存 ✓
- 无需等待 ✓
- 跨会话持久 ✓
```

## 记忆操作

```bash
# 添加记忆
memory add "用户在X场景偏好Y"

# 替换记忆
memory replace "old content" "new content"

# 删除记忆
memory remove "要删除的内容"

# 搜索会话
memory search "关键词" --sessions 10

# 查看记忆
memory list
```

## 容量管理

```python
# 严格字符限制保持专注
MAX_MEMORY_CHARS = 5000
MAX_USER_CHARS = 3000

# 当满时自动整合
def consolidate_memory():
    # 合并相似条目
    # 删除过期条目
    # 保留核心洞察
```

## Honcho用户画像

```
┌─────────────────────────────────────────────────────────────┐
│ Honcho 辩证式用户建模                                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  收集阶段                                                   │
│  ├── 沟通风格观察                                          │
│  ├── 技术偏好记录                                          │
│  └── 反馈模式识别                                          │
│                      ↓                                      │
│  建模阶段                                                   │
│  ├── 核心特质提取                                          │
│  ├── 偏好优先级排序                                        │
│  └── 潜在需求推断                                          │
│                      ↓                                      │
│  验证阶段                                                   │
│  ├── 行为一致性检验                                        │
│  └── 画像准确性反馈                                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 天龙引擎集成

### 适用岗位
- **07记录师** - 记忆系统核心增强
- **01调研师** - 跨会话知识召回
- **09-04首席幕僚长** - 用户画像建模

### 调用方式

```bash
# 记忆操作
[@记录师] 添加记忆：用户偏好使用YYYY-MM-DD日期格式
[@记录师] 搜索与"API设计"相关的历史会话
[@记录师] 查看当前记忆状态

# 用户画像
[@首席幕僚长] 更新用户画像：用户喜欢简洁的代码风格
[@首席幕僚长] 查看当前用户的沟通偏好

# 记忆提醒
[@记录师] 设置当处理GitHub任务时自动提醒相关经验
```

## 与现有系统协同

| 天龙组件 | Hermes协同 | 效果 |
|---------|-----------|------|
| **V8.6 claude-mem** | FTS5搜索增强 | SQLite→FTS5升级 |
| **V8.74 Supermemory** | 事实提取+矛盾解决 | 跨平台统一 |
| **V8.75 OpenSpace** | 记忆自演化 | CAPTURED模式 |
| **V8.61 advanced-memory-sync** | L0-L3分层+Obsidian | 分层增强 |

## 融合方案

```python
# 天龙三层记忆架构 + Hermes闭环

Layer 1: claude-mem (会话自动捕获)
    ↓
Layer 2: hermes-memory-loop (FTS5搜索+Honcho画像) ⭐新增
    ↓
Layer 3: Supermemory (跨平台事实提取)
    ↓
Layer 4: advanced-memory-sync (L0-L3分层+Obsidian)
```

## 核心命令

```bash
# 记忆管理
memory add "<content>"
memory replace "<old>" "<new>"
memory remove "<content>"
memory list

# 会话搜索
memory search "<query>" --limit 10
memory search "<query>" --session-id <id>

# 用户画像
user-profile show
user-profile update --key communication_style --value concise

# 记忆统计
memory stats
memory capacity
```

## 预期收益

| 指标 | 集成前 | 集成后 | 提升 |
|------|--------|--------|------|
| 跨会话召回率 | 40% | 90% | +125% |
| 记忆检索速度 | 500ms | 50ms | -90% |
| 用户理解准确率 | 60% | 95% | +58% |
| 重复问题解决时间 | 5分钟 | 30秒 | -83% |
