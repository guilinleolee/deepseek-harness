---
license: UNKNOWN
github_repo: supermemoryai/supermemory
github_hash: 210fceb74ba3243fd5931c8c3ceacfc33d8057f5
last_updated: 2026-04-25
source_type: derived
triggers: ["supermemory memory", "Supermemory - AI 记忆与上下文引擎"]
---
# Supermemory - AI 记忆与上下文引擎

> **Supermemory** 是 AI 时代的记忆和上下文引擎，在 LongMemEval、LoCoMo、ConvoMem 三大基准测试中排名第一。

## 核心价值

| 维度 | 数据 |
|------|------|
| **Benchmark** | LongMemEval 81.6% #1、LoCoMo #1、ConvoMem #1 |
| **响应速度** | ~50ms (用户画像查询) |
| **MCP 支持** | Claude Desktop/Code、Cursor、Windsurf、VS Code、OpenClaw |
| **多平台连接器** | Google Drive、Gmail、Notion、GitHub、Web Crawler |

## 安装方式

### MCP 快速安装（推荐）

```bash
# 安装到 Claude Code
npx -y install-mcp@latest https://mcp.supermemory.ai/mcp --client claude --oauth=yes

# 安装到其他客户端
npx -y install-mcp@latest https://mcp.supermemory.ai/mcp --client cursor
npx -y install-mcp@latest https://mcp.supermemory.ai/mcp --client windsurf
```

### npm 安装

```bash
npm install supermemory
```

### Python 安装

```bash
pip install supermemory
```

## MCP 手动配置

在 Claude Code 配置文件中添加：

```json
{
  "mcpServers": {
    "supermemory": {
      "url": "https://mcp.supermemory.ai/mcp"
    }
  }
}
```

或使用 API Key：

```json
{
  "mcpServers": {
    "supermemory": {
      "url": "https://mcp.supermemory.ai/mcp",
      "headers": {
        "Authorization": "Bearer sm_your_api_key_here"
      }
    }
  }
}
```

## 核心 API

### TypeScript 用法

```typescript
import Supermemory from "supermemory";

const client = new Supermemory();

// 存储对话
await client.add({
  content: "User loves TypeScript and prefers functional patterns",
  containerTag: "user_123",
});

// 获取用户画像 + 相关记忆
const { profile, searchResults } = await client.profile({
  containerTag: "user_123",
  q: "What programming style does the user prefer?",
});
```

### Python 用法

```python
from supermemory import Supermemory

client = Supermemory()
client.add(
  content="User loves TypeScript and prefers functional patterns",
  container_tag="user_123"
)

result = client.profile(container_tag="user_123", q="programming style")
```

## MCP 工具

Supermemory MCP 提供以下工具：

| 工具 | 用途 |
|------|------|
| `supermemory_search` | 混合搜索记忆和文档 |
| `supermemory_add` | 存储内容到记忆库 |
| `supermemory_profile` | 获取用户画像 |
| `supermemory_documents` | 上传和搜索文档 |

## 天龙引擎集成

### 解决的问题

| 痛点 | Supermemory 解决方案 |
|------|---------------------|
| **飞书/微信/WEB 记忆隔离** | 统一 Memory Store + 混合搜索 |
| **跨会话上下文丢失** | 持久化事实提取 + 用户画像 |
| **调研知识碎片化** | Container Tag 分组 + 语义搜索 |
| **过时信息污染** | 自动遗忘机制 + 矛盾解决 |

### 飞书/微信连接器

#### 飞书连接器

```bash
# 使用 Lark API 连接飞书
python3 scripts/connectors/feishu_connector.py --configure

# 同步飞书消息到 Supermemory
python3 scripts/connectors/feishu_connector.py sync --limit 100
```

#### 微信连接器

```bash
# 配置微信连接器
python3 scripts/connectors/wechat_connector.py --configure

# 同步微信消息到 Supermemory
python3 scripts/connectors/wechat_connector.py sync --limit 100
```

### 天龙岗位使用

#### 07记录师 - 跨平台记忆同步

```
场景：用户通过飞书询问项目进度，微信确认需求，Claude Code 调研
问题：三个渠道的记忆如何统一？
方案：Supermemory 统一存储，混合搜索
```

```bash
# 同步飞书消息
[@记录师] 将飞书消息同步到 Supermemory

# 同步微信消息
[@记录师] 将微信消息同步到 Supermemory

# 统一查询
[@记录师] 查询用户对项目"智能推荐"的需求
```

#### 01调研师 - 调研知识库化

```
场景：跨项目调研知识积累
问题：调研结论分散在不同会话，无法复用
方案：Container Tag 分组 + 自动事实提取
```

```bash
# 存储调研结论
[@调研师] 将"AI Agent 发展趋势"调研结论存入 Supermemory

# 查询历史调研
[@调研师] 查询之前关于"提示词工程"的调研结论
```

### Container Tag 策略

| Tag 格式 | 用途 |
|----------|------|
| `user_{userId}` | 用户画像 |
| `project_{projectId}` | 项目上下文 |
| `session_{sessionId}` | 会话记忆 |
| `research_{topic}` | 调研结论 |
| `feishu_{chatId}` | 飞书消息 |
| `wechat_{chatId}` | 微信消息 |

## 核心特性

### 1. Memory Engine

- **事实提取**：从对话中提取关键事实
- **追踪更新**：跟踪事实的变化
- **矛盾解决**：自动检测和解决矛盾信息
- **自动遗忘**：过期临时信息自动清理

### 2. User Profiles

- **静态事实**：用户偏好、技能、背景
- **动态上下文**：当前项目、任务、关注点
- **~50ms 响应**：快速检索用户上下文

### 3. Hybrid Search

- **RAG + Memory**：一次查询完成两种检索
- **语义理解**：理解查询意图
- **相关性排序**：返回最相关结果

### 4. 自动遗忘机制

```
┌─────────────────────────────────────────────────────────────┐
│ 临时事实（如"明天有考试"）→ 日期过后自动过期              │
│ 矛盾信息 → 自动解决并标注更新时间                          │
│ 低价值记忆 → 根据使用频率自动降级                          │
└─────────────────────────────────────────────────────────────┘
```

## 与 claude-mem 对比

| 维度 | claude-mem | Supermemory |
|------|------------|-------------|
| **Benchmark** | 无 | LongMemEval #1 |
| **响应速度** | 较快 | ~50ms |
| **事实提取** | 简单压缩 | 智能事实抽取 |
| **矛盾检测** | 无 | 自动解决 |
| **遗忘机制** | 手动 | 自动 |
| **多平台连接** | 有限 | 完整 |
| **飞书/微信** | 无 | Connectors |

## 使用场景

### 场景 1：跨平台用户理解

```
用户路径：
1. 飞书询问项目需求 → Supermemory 存储
2. 微信确认细节 → Supermemory 存储
3. Claude Code 调研 → 查询统一画像

结果：天龙引擎完整理解用户需求上下文
```

### 场景 2：调研知识积累

```
1. 调研"AI Agent 发展趋势" → 结论存入 Supermemory
2. 调研"提示词工程" → 结论存入 Supermemory
3. 调研"Multi-Agent" → 自动关联前两者结论
```

### 场景 3：记忆持久化

```
1. 今天讨论的项目决策 → 自动提取为事实
2. 明天继续 → 查询昨日决策上下文
3. 项目结束 → 归档到项目知识库
```

## 命令速查

```bash
# MCP 安装
npx -y install-mcp@latest https://mcp.supermemory.ai/mcp --client claude --oauth=yes

# 飞书连接器
python3 scripts/connectors/feishu_connector.py sync --limit 100

# 微信连接器
python3 scripts/connectors/wechat_connector.py sync --limit 100

# 查询记忆
python3 scripts/supermemory_query.py "用户需求" --container user_123

# 添加记忆
python3 scripts/supermemory_add.py --content "用户偏好..." --tag project_001
```

## 预期收益

| 指标 | 当前 | Supermemory | 提升 |
|------|------|-------------|------|
| **跨平台记忆** | 无 | 统一存储 | **质的飞跃** |
| **用户画像** | 手动 | ~50ms 自动 | **+500%** |
| **调研复用** | 碎片化 | 系统化 | **+300%** |
| **矛盾检测** | 无 | 自动 | **新增能力** |
| **遗忘机制** | 无 | 自动 | **新增能力** |

## 参考资源

- 官网：https://supermemory.ai
- 文档：https://supermemory.ai/docs
- GitHub：https://github.com/supermemoryai/supermemory
- Benchmark：https://supermemory.ai/docs/memorybench/overview
