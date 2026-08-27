# n8n-skill - 智能化工作流编排引擎

这是一个高度结构化的 n8n 知识库，专为 LLM 设计，旨在实现从自然语言到生产级 n8n 工作流 JSON 的精准转换。

## 🧠 架构设计 (Architecture)

本 Skill 采用**“索引寻址 + 知识分层”**架构，有效解决了 LLM 上下文窗口限制与海量节点文档之间的矛盾：
- **核心层 (Core Nodes)**: 常用节点（如 Code, HttpRequest）采用独立 Markdown 文件存储，提供最高检索权重。
- **扩展层 (Merged Resources)**: 500+ 个次要节点按功能分类合并至 `merged` 文件中，通过 `INDEX.md` 实现 `offset/limit` 精准定位。
- **外部脑 (External Research)**: 接入 `RESEARCH_SOURCES.md`，支持实时检索 n8n 官方库及 GitHub 社区资产。

## 🚀 核心功能

1. **精准寻址**: 通过 `INDEX.md` 快速定位 545+ 个内置节点的参数规范。
2. **实战协议**: 具备“外部研究协议 (External Research Protocol)”，在本地知识不足时自动触发全球社区检索。
3. **模板驱动**: 内置 30+ 种 AI、社交媒体、数据处理等场景的成熟工作流模板。

## 🛠️ 使用指南

- **查阅节点**: 优先访问 `INDEX.md` 获取目标节点的路径与行号。
- **构建流**: 结合 `SKILL.md` 中的“外部研究协议”进行跨平台逻辑编排。
- **外部资源**: 参考 `RESEARCH_SOURCES.md` 获取最新社区动态。

---
*Last Updated: 2026-01-27*
