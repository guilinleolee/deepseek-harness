---
name: graphify-token-upgrade
description: Graphify知识图谱集成天龙引擎TOKEN升级 - 节省71.5x Token
metadata:
  type: project
heat: 0.7
last_ref_date: 2026-08-24
mneme_schema: v12.0
---


# Graphify × 天龙引擎 TOKEN 升级

## 项目信息
- **来源**: [Graphify-Labs/graphify](https://github.com/Graphify-Labs/graphify)
- **背景**: Y Combinator S26批次
- **Stars**: 107,618
- **PyPI包名**: `graphifyy`（双y）

## 核心价值
- **Token节省**: 71.5x（每次查询平均节省98.6%）
- **代码提取成本**: $0（tree-sitter AST本地解析）
- **召回率**: recall@10 = 0.497（vs mem0 0.048）

## 技术栈
- tree-sitter AST（零LLM调用）
- NetworkX 图数据
- Leiden 社区检测算法
- MCP Server（stdio/HTTP双模式）

## 集成文件
- `commands/graphify.md` - 新增命令
- `commands/token.md` - 更新优化策略

## 使用命令
```bash
# 构建图谱
graphify .

# 查询
graphify query "架构分析问题"

# 路径追踪
graphify path "A" "B"

# PR评审
graphify prs --triage
```

## 注意事项
1. Windows用 `graphify .`（不能用 `/graphify .`）
2. 包名必须是 `graphifyy`（双y）
3. 图谱建议加入 `.claudeignore` 避免cache失效

**Why:** 为天龙引擎提供代码库级别的Token优化能力

**How to apply:** 1) 安装 `uv tool install graphifyy` 2) 使用 `/graphify` 命令查询 3) 在大型项目理解时优先用图谱替代大量Read
