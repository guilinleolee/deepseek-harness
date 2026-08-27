---
name: graphify
description: graphify - 知识图谱查询命令（Token节省71.5x）
invokable: true
---
# /graphify - 知识图谱查询命令

基于 Graphify 的代码库知识图谱构建与查询，大幅降低Token消耗。

## 依赖安装

```bash
uv tool install graphifyy
```

## 命令列表

| 命令 | 功能 | Token节省 |
|------|------|----------|
| `graphify .` | 构建当前目录图谱 | 构建0成本 |
| `graphify query "问题"` | 自然语言查询 | 节省80%+ |
| `graphify path A B` | 追踪A→B依赖路径 | 节省60%+ |
| `graphify explain 节点` | 解释节点关系 | 节省50%+ |
| `graphify prs --triage` | PR评审队列排序 | 节省40%+ |
| `graphify reflect` | 反思聚合LESSONS | 渐进节省 |

## 使用示例

### 构建图谱
```bash
cd C:/Users/li/.claude/projects/dragon-engine
graphify .
```
生成三个输出文件：
- `graphify-out/graph.html` - 交互式可视化
- `graphify-out/GRAPH_REPORT.md` - 关键概念报告
- `graphify-out/graph.json` - 可重复查询的图谱

### 查询代码库
```bash
graphify query "dragon-engine的agent调用链是如何工作的？"
graphify query "token命令的实现逻辑在哪里？"
```

### 追踪依赖
```bash
graphify path "dragon-cli" "CommandRegistry"
graphify path "token" "cost-estimate"
```

### PR评审（集成到/07发布师）
```bash
graphify prs --triage
graphify prs 42 --impact
```

## 天龙岗位映射

| 岗位 | 用途 |
|------|------|
| **00分析师** | 图谱构建前的项目理解 |
| **01架构师** | `graphify query` 架构分析 |
| **02构建师** | `graphify path` 依赖追踪 |
| **05审查师** | `graphify prs --triage` 评审排序 |
| **07发布师** | PR影响分析与合并顺序 |

## MCP Server 模式（团队共享）

```bash
# 启动MCP服务
python -m graphify.serve graph.json

# HTTP模式（推荐团队）
python -m graphify.serve graph.json --transport http --port 8080
```

## 集成到现有命令

### 集成到 /code-review
在PR评审流程中加入：
```bash
graphify prs --triage  # 先排序，再评审
graphify prs <pr_number> --impact  # 分析单个PR影响
```

### 集成到 /llamaindex-rag
```bash
# 先用图谱精确定位
graphify query "关于token优化的问题"

# 再用向量检索补充
llamaindex-rag query --kb-name dragon-engine "token优化"
```

## 注意事项

1. **Windows PowerShell**：用 `graphify .`（不能用 `/graphify .`）
2. **图谱体积**：默认512MiB上限，超大项目用 `graphify . --no-viz`
3. **Prompt缓存**：建议把 `graph.json` 加入 `.claudeignore`
4. **包名**：必须是 `graphifyy`（双y）

## 来源

> [Graphify-Labs/graphify](https://github.com/Graphify-Labs/graphify) - YC S26
> Token节省数据：71.5x (每查询平均)
