---
license: UNKNOWN
github_repo: simstudioai/sim
github_hash: 3422f64c5f6e1a1c4c008fac1ac1709e9c97035a
last_updated: 2026-04-25
source_type: derived
triggers: ["simstudio api", "simstudio-api"]
---
# simstudio-api

> Sim工作流编排平台集成 - 构建、部署和编排AI Agent

## 来源项目

| 项目 | Stars | 核心能力 |
|------|-------|---------|
| [simstudioai/sim](https://github.com/simstudioai/sim) | 27.2k | AI Agent工作流编排 + 可视化画布 + 1,000+集成 |

## 核心价值

填补天龙引擎在**Sim工作流编排平台集成**的关键空白，实现：
- 可视化工作流设计（ReactFlow拖拽式画布）
- 1,000+ 第三方集成生态
- TypeScript/Python SDK工作流执行
- AI Copilot节点生成辅助

## 技术架构

```
┌─────────────────────────────────────────────────────────────┐
│ Sim Platform Architecture                                   │
├─────────────────────────────────────────────────────────────┤
│  Visual Canvas (ReactFlow) ← 可视化拖拽设计               │
│           ↓                                                │
│  Workflow Engine ← 工作流执行引擎                         │
│           ↓                                                │
│  Tool Layer ← 1,000+ 集成生态                            │
│           ↓                                                │
│  LLM Integration ← 多LLM支持                              │
└─────────────────────────────────────────────────────────────┘
```

## 核心能力

| 能力 | 功能 | 天龙对应 |
|------|------|---------|
| **工作流设计** | ReactFlow拖拽式可视化 | Level 7编排 |
| **SDK执行** | TypeScript/Python SDK | agent-execution |
| **集成生态** | 1,000+第三方工具 | ai-router |
| **AI辅助** | Copilot节点生成 | autoprompt |

## 天龙岗位升级

| 岗位 | 版本 | 新增能力 | 提升 |
|------|------|---------|------|
| **09-02 编排协调师** | V8.68 → V8.69 | Sim SDK集成 + 可视化编排 | ⭐⭐⭐⭐⭐ |
| **03 构建师** | V8.68 → V8.69 | Sim工作流开发 | ⭐⭐⭐⭐ |
| **04 验证师** | V8.68 → V8.69 | 工作流测试执行 | ⭐⭐⭐⭐ |

## 核心命令速查

```bash
# 安装Sim CLI
bunx simstudio

# 创建工作流
sim workflow create --name "my-workflow"

# 执行工作流
sim run <workflow-id> --input '{"key": "value"}'

# 使用SDK
npm install simstudio-ts-sdk
# 或
pip install simstudio-sdk

# 本地开发
docker-compose up
```

## SDK使用示例

### TypeScript SDK

```typescript
import { SimClient } from 'simstudio-ts-sdk';

const client = new SimClient({
  apiKey: process.env.SIM_API_KEY,
  baseUrl: 'https://api.sim.ai/v1'
});

// 执行工作流
const result = await client.workflows.run({
  workflowId: 'workflow_xxx',
  input: { query: 'Hello world' }
});

console.log(result.output);
```

### Python SDK

```python
from simstudio_sdk import SimClient

client = SimClient(api_key="your-api-key")

# 执行工作流
result = client.workflows.run(
    workflow_id="workflow_xxx",
    input={"query": "Hello world"}
)

print(result.output)
```

## 与现有天龙能力协同

| 天龙组件 | Sim集成 | 协同效果 |
|---------|---------|---------|
| **LangFlow** | Level 7可视化 | LangFlow → Sim迁移通道 |
| **ai-router** | 1,000+集成 | 扩展LLM/工具选择 |
| **paperclip-ticket** | 工作流持久化 | 工作流即任务票据 |
| **team-builder** | Agent编排 | Sim工作流作为Team任务 |

## 集成连接器示例

```typescript
// 工具集成模板
const tools = {
  // Web搜索
  search: async (query: string) => {
    const result = await client.tools.execute('web-search', { query });
    return result;
  },

  // 数据库查询
  dbQuery: async (sql: string) => {
    const result = await client.tools.execute('database', { sql });
    return result;
  },

  // 文件操作
  fileOp: async (operation: string, path: string) => {
    const result = await client.tools.execute('filesystem', { operation, path });
    return result;
  },

  // API调用
  httpRequest: async (method: string, url: string, data?: object) => {
    const result = await client.tools.execute('http', { method, url, data });
    return result;
  }
};
```

## 工作流模板

### 调研工作流

```yaml
name: research-workflow
description: AI驱动的深度调研工作流

nodes:
  - id: planner
    type: agent
    config:
      role: planner
      prompt: "分解研究主题为子问题"

  - id: searcher
    type: parallel
    config:
      agents: [web-search, github-search, docs-search]
      merge: union

  - id: synthesizer
    type: agent
    config:
      role: synthesizer
      prompt: "汇总搜索结果为完整报告"

edges:
  - from: planner
    to: searcher
  - from: searcher
    to: synthesizer
```

### 构建-测试工作流

```yaml
name: build-test-workflow
description: 自动化构建和测试工作流

nodes:
  - id: code-generator
    type: agent
    config:
      model: claude-sonnet

  - id: linter
    type: tool
    config:
      tool: biome-lint

  - id: tester
    type: agent
    config:
      model: claude-sonnet
      role: tester

  - id: deployer
    type: trigger
    config:
      when: all-tests-passed

edges:
  - from: code-generator
    to: linter
  - from: linter
    to: tester
  - from: tester
    to: deployer
```

## 安装与配置

```bash
# 安装Sim CLI
bun add -g simstudio

# 安装SDK
npm install simstudio-ts-sdk
# 或
pip install simstudio-sdk

# 环境变量
export SIM_API_KEY="your-api-key"
export SIM_WORKSPACE_ID="your-workspace-id"

# Docker本地开发
docker-compose -f docker-compose.local.yml up
```

## 预期收益

| 指标 | V8.68 | V8.69 | 提升 |
|------|-------|-------|------|
| **可视化编排体验** | LangFlow | Sim ReactFlow | ⭐⭐⭐⭐⭐ |
| **第三方集成数量** | ai-router 15+ | **1,000+** | +6500% |
| **工作流执行效率** | 手动 | SDK自动化 | +300% |
| **编排灵活性** | 模板化 | 拖拽+模板双模式 | ⭐⭐⭐⭐⭐ |

## 技能文件

- [skills/simstudio-api/SKILL.md](skills/simstudio-api/SKILL.md)
- [skills/simstudio-api/scripts/sim_client.py](skills/simstudio-api/scripts/sim_client.py)
- [skills/simstudio-api/templates/workflows/](skills/simstudio-api/templates/workflows/)
