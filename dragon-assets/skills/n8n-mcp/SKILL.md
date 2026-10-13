---
license: UNKNOWN
triggers: ["n8n mcp", "n8n-MCP Skill"]
---
# n8n-MCP Skill

## L0: 一句话描述 (≤15字)
AI 连接 n8n 工作流自动化平台

## L1: 使用场景 (50-100字)
通过 Claude Code 直接操作 n8n 平台：自动生成工作流、批量更新、验证部署、安全审计。适合需要工作流自动化的场景。

## L2: 详细文档

### 安装配置

```bash
# 安装 n8n-MCP
npm install -g n8n-mcp

# Claude Code MCP 配置
claude mcp add n8n -- npx n8n-mcp

# 环境变量配置
export N8N_API_URL="https://your-n8n.com/api/v1"
export N8N_API_KEY="your-api-key"
```

### 20个 MCP 工具

#### 核心工具

| 工具 | 功能 | 使用示例 |
|------|------|---------|
| `tools_documentation` | 获取 MCP 工具文档 | `tools_documentation()` |
| `search_nodes` | 全文本搜索节点 | `search_nodes({query: "HTTP Request"})` |
| `get_node` | 获取节点详细信息 | `get_node({node_name: "HTTP Request", mode: "minimal"})` |
| `validate_node` | 节点验证 | `validate_node({node_name: "HTTP Request", schema: {...}})` |
| `validate_workflow` | 完整工作流验证 | `validate_workflow({workflow: {...}})` |
| `search_templates` | 模板搜索 | `search_templates({query: "Slack", mode: "by_platform"})` |
| `get_template` | 获取模板详情 | `get_template({template_id: "123"})` |

#### n8n 管理工具

| 工具 | 功能 | 使用示例 |
|------|------|---------|
| `n8n_create_workflow` | 创建工作流 | `n8n_create_workflow({name: "My Workflow", nodes: [...]})` |
| `n8n_update_partial_workflow` | 批量更新工作流 | `n8n_update_partial_workflow({workflow_id: "123", nodes: [...]})` |
| `n8n_validate_workflow` | 验证已部署工作流 | `n8n_validate_workflow({workflow_id: "123"})` |
| `n8n_test_workflow` | 测试工作流执行 | `n8n_test_workflow({workflow_id: "123", input: {...}})` |
| `n8n_executions` | 执行管理 | `n8n_executions({workflow_id: "123", status: "success"})` |
| `n8n_manage_credentials` | 凭证管理 | `n8n_manage_credentials({operation: "list"})` |
| `n8n_audit_instance` | 安全审计 | `n8n_audit_instance({scan_depth: "full"})` |
| `n8n_health_check` | 健康检查 | `n8n_health_check()` |

### 天龙引擎调用方式

```bash
# 工作流生成
[@03] 使用 n8n-mcp 生成一个定时抓取网页数据的工作流

# 批量更新
[@08] 使用 n8n-update-partial-workflow 批量更新 10 个工作流

# 安全审计
[@05] 使用 n8n_audit_instance 审计 n8n 实例安全

# 模板搜索
[@01] 使用 search_templates 搜索 Slack 集成模板
```

### 与现有技能协同

```
┌─────────────────────────────────────────────────────────────┐
│ 天龙引擎 工作流编排全家桶                                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  LangFlow可视化设计 ──→ n8n工作流部署                     │
│  (拖拽式编排)              (自动化执行)                    │
│                                                             │
│  Trigger.dev事件驱动 ──→ n8n工作流编排                     │
│  (复杂AI任务)         (批量操作)                           │
│                                                             │
│  Paperclip心跳 ──→ n8n定时触发                            │
│  (心跳调度)           (1,650+节点生态)                     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 数据覆盖

| 类型 | 数量 |
|------|------|
| n8n 节点 | 1,650 个（820 核心 + 830 社区） |
| 节点属性覆盖率 | 99% |
| 节点操作覆盖率 | 63.6% |
| 官方文档覆盖率 | 87% |
| AI 工具 | 265 个变体 |
| 模板库 | 2,352 个 |

### 验证层级

```
minimal → full → workflow → post-deployment
```

### 注意事项

- **生产安全**：始终在测试环境验证后再部署到生产
- **凭证管理**：使用环境变量，不硬编码 API Key
- **版本兼容**：支持 n8n 2.18.4+

---

## 来源

| 项目 | Stars | 地址 |
|------|-------|------|
| n8n-MCP | 20,294 | https://github.com/czlonkowski/n8n-mcp |

## 版本

| 版本 | 日期 | 变更 |
|------|------|------|
| V1.0 | 2026-05-08 | 初始集成 |
