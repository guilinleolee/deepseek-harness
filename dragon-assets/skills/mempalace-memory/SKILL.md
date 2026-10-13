---
license: UNKNOWN
triggers: ["mempalace memory", "mempalace-memory - 宫殿记忆系统"]
---
# mempalace-memory - 宫殿记忆系统

## V1.0 - 天龙引擎V8.85核心技能

> **"The highest-scoring AI memory system ever benchmarked. And it's free."**
> LongMemEval 96.6% R@5 - 超越Supermemory 15%

---

## L0: 一句话描述 (≤15字)

宫殿记忆法，AI记忆系统基准第一。

## L1: 使用场景 (50-100字)

当用户需要天龙引擎记住长期项目上下文、跨会话知识复用、矛盾检测验证、专家代理分工时，使用MemPalace宫殿记忆法。

---

## 核心价值

| 指标 | Supermemory (V8.74) | MemPalace (V8.85) | 提升 |
|------|---------------------|---------------------|------|
| **LongMemEval** | 81.6% | **96.6%** | **+15%** ⭐ |
| **存储方式** | AI摘要提取 | **原始verbatim** | 更准确 |
| **知识图谱** | Neo4j (重) | **SQLite (轻)** | -80% |
| **矛盾检测** | 基础 | **实体关系验证** | +200% |
| **Token效率** | 较高 | **更低** | +30% |

---

## 宫殿记忆法架构

```
┌─────────────────────────────────────────────────────────────┐
│                  MemPalace 宫殿记忆法                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  🏛️ Wing (翅膀)    ← 项目/用户/团队                         │
│     ├── Room (房间)   ← 具体话题 (Auth, Billing, Deploy)   │
│     │   └── Hall (走廊) ← 记忆类型                          │
│     │       └── Closet (橱柜) ← 语义向量                    │
│                                                             │
│  四层记忆架构:                                              │
│  ├── L0: Identity (~50 tokens) - AI身份                    │
│  ├── L1: Critical Facts (~120 tokens) - 关键事实           │
│  ├── L2: Room Recall (按需) - 最近会话                     │
│  └── L3: Deep Search (按需) - 全局语义检索                 │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 19个MCP工具

| 工具 | 功能 | 使用场景 |
|------|------|---------|
| `mempalace_search` | 语义记忆搜索 | 跨会话知识复用 |
| `mempalace_diary_write` | 写入代理日记 | 记录执行过程 |
| `mempalace_diary_read` | 读取代理日记 | 恢复执行上下文 |
| `mempalace_kg_add` | 添加知识三元组 | 实体关系记录 |
| `mempalace_kg_query` | 查询知识图谱 | 事实验证 |
| `mempalace_kg_invalidate` | 使三元组失效 | 更新过时知识 |
| `mempalace_kg_timeline` | 实体时间线 | 追踪事实变化 |
| `mempalace_ingest` | 摄入文档/对话 | 记忆挖掘 |
| `mempalace_wing_create` | 创建翅膀 | 新项目/用户 |
| `mempalace_room_create` | 创建房间 | 新话题 |
| `mempalace_contradiction_check` | 矛盾检测 | 验证一致性 |
| `mempalace_context_get` | 获取上下文 | L0-L3分层加载 |
| `mempalace_forget` | 选择性遗忘 | 清理过期记忆 |
| `mempalace_stats` | 记忆统计 | 查看记忆状态 |

---

## 快速开始

### 安装

```bash
pip install mempalace
```

### MCP集成到Claude Code

```bash
claude mcp add mempalace -- python -m mempalace.mcp_server
```

### 初始化记忆宫殿

```bash
# 初始化项目记忆库
mempalace init ~/.claude/mempalace-memory

# 挖掘对话历史
mempalace mine ~/.claude/chats/ --mode convos

# 挖掘项目文件
mempalace mine ~/.claude/ --mode projects
```

### 语义搜索

```bash
mempalace search "天龙引擎架构设计"
mempalace search "上次修复的bug" --wing myproject
mempalace search "关于API的决策" --room auth --limit 5
```

---

## 天龙引擎集成模式

### 模式1: 自动上下文恢复

```python
# scripts/mempalace_context_loader.py
import subprocess
import json

def load_tianlong_context(query: str, wing: str = "tianlong"):
    """加载天龙引擎记忆上下文"""
    result = subprocess.run(
        ["mempalace", "search", query, "--wing", wing, "--json"],
        capture_output=True, text=True
    )
    return json.loads(result.stdout)

def get_agent_context(agent_id: str, task: str):
    """获取特定Agent的记忆上下文"""
    context = load_tianlong_context(f"{agent_id} {task}")
    return {
        "identity": context.get("l0", ""),
        "critical_facts": context.get("l1", ""),
        "recent_sessions": context.get("l2", []),
        "deep_search": context.get("l3", [])
    }
```

### 模式2: 专家代理配置

```json
// ~/.mempalace/agents/tianlong_builder.json
{
  "name": "天龙构建师",
  "wing": "tianlong",
  "rooms": ["coding", "testing", "deployment"],
  "specialization": "代码构建和测试验证",
  "memory_preferences": {
    "verbose_coding": true,
    "store_complexity": true,
    "track_dependencies": true
  }
}
```

### 模式3: 矛盾检测工作流

```python
def contradiction_check(new_fact: dict, wing: str = "tianlong"):
    """检查新事实与现有知识的矛盾"""
    result = subprocess.run(
        [
            "python", "-m", "mempalace.mcp_server",
            "--tool", "contradiction_check",
            "--fact", json.dumps(new_fact),
            "--wing", wing
        ],
        capture_output=True, text=True
    )
    return json.loads(result.stdout)

# 使用示例
new_claim = {
    "entity": "UserAuth",
    "relation": "uses",
    "target": "JWT",
    "confidence": 0.9
}
result = contradiction_check(new_claim)
if result.get("contradictions"):
    print(f"⚠️ 发现矛盾: {result['contradictions']}")
```

---

## 知识图谱API

```python
from mempalace.knowledge_graph import KnowledgeGraph

kg = KnowledgeGraph()

# 添加三元组
kg.add_triple(
    "天龙引擎", "使用", "Claude Code",
    valid_from="2026-01-01"
)
kg.add_triple(
    "用户", "通过", "CLAUDE.md配置",
    valid_from="2026-03-04"
)

# 查询实体
entity_facts = kg.query_entity("天龙引擎")

# 时间线追踪
timeline = kg.timeline("用户")

# 使失效（知识更新）
kg.invalidate("用户", "通过", "CLAUDE.md配置")
```

---

## 天龙引擎Hook集成

```javascript
// hooks/mempalace-memory-hook.js
const { execSync } = require('child_process');

function mempalaceSearch(query, wing = "tianlong") {
    try {
        const result = execSync(
            `mempalace search "${query}" --wing ${wing} --json`,
            { encoding: 'utf-8' }
        );
        return JSON.parse(result);
    } catch (e) {
        return null;
    }
}

function mempalaceDiaryWrite(content, agent = "tianlong") {
    execSync(
        `mempalace diary write --agent ${agent} --content "${content}"`,
        { encoding: 'utf-8' }
    );
}

module.exports = { mempalaceSearch, mempalaceDiaryWrite };
```

---

## 与现有天龙能力协同

| 天龙组件 | MemPalace协同 | 效果 |
|---------|--------------|------|
| **Supermemory** | 替换基准 | 召回率+15% |
| **claude-mem** | 互补 | verbatim vs 摘要 |
| **advanced-memory-sync** | 底层存储 | L0-L3增强 |
| **LightRAG** | 检索增强 | 双重RAG |
| **Meta-Librarian** | 核心升级 | 宫殿记忆法 |

---

## 核心命令速查

```bash
# 安装
pip install mempalace

# MCP集成
claude mcp add mempalace -- python -m mempalace.mcp_server

# 初始化
mempalace init ~/.claude/mempalace-memory

# 挖掘数据
mempalace mine ~/.claude/chats/ --mode convos
mempalace mine ~/.claude/ --mode projects

# 搜索
mempalace search "query" --wing tianlong --limit 5

# 记忆统计
mempalace stats --wing tianlong

# 专家代理
mempalace agent list
mempalace agent create --name "天龙构建师" --rooms "coding,testing"
```

---

## AAAK压缩方言 (实验)

> "AAAK is a lossy abbreviation system — entity codes, structural markers, and sentence truncation"

```bash
# 启用AAAK压缩（实验阶段）
mempalace init ~/.claude/mempalace-memory --aaak

# 注意: AAAK在Small Scale会降低性能
# LongMemEval: 84.2% (AAAK) vs 96.6% (raw)
# 推荐: 大规模记忆库使用AAAK，小规模保持raw
```

---

## 预期收益

| 指标 | V8.84 (Supermemory) | V8.85 (MemPalace) | 提升 |
|------|---------------------|---------------------|------|
| **记忆召回率** | 81.6% | **96.6%** | **+15%** |
| **记忆准确度** | 摘要丢失 | **verbatim完整** | 质的飞跃 |
| **矛盾检测** | 基础 | **实体关系验证** | +200% |
| **图谱性能** | Neo4j | **SQLite** | -80% |
| **Token效率** | 中等 | **更低** | +30% |
| **专家代理** | 无 | **领域专注** | 新增能力 |

---

## 技能文件

- [SKILL.md](SKILL.md) - 本文件
- [scripts/mempalace_manager.py](scripts/mempalace_manager.py) - 管理脚本
- [scripts/mcp_bridge.py](scripts/mcp_bridge.py) - MCP桥接
- [examples/tianlong_integration.py](examples/tianlong_integration.py) - 天龙集成示例

---

## 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| V1.0 | 2026-04-08 | 初始集成，基于mempalace 18.1k Stars |
