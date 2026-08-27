---
license: UNKNOWN
name: anysearch-academic
description: AnySearch学术研究专用封装 - 论文搜索、学术观点、技术趋势深度调研
version: 1.0.0
author: 天龙引擎 AnySearch团队
integrations: - anysearch (search/batch_search/extract/list_domains)
- grill-me (追问框架)
triggers: ["anysearch academic", "学术论文搜索"]
---

## L0: 一句话描述

学术领域深度调研SKILL，支持论文检索、学术观点挖掘、技术趋势分析。

## L1: 使用场景 (50-100字)

适用场景：学术论文调研、技术趋势分析、学术观点综述、研究方向验证。
触发条件：用户提到「学术搜索」「论文检索」「研究趋势」「学术观点」时激活。
与deep-research形成双轨：AnySearch快速摸底 → Deep Research深度研究。

## L2: 详细文档

### 核心能力

| 能力 | 命令 | 说明 |
|------|------|------|
| 论文搜索 | `academic_search` | 学术论文、arXiv、学术观点 |
| 技术趋势 | `tech_trend_search` | 技术发展、研究前沿、学术热点 |
| 竞品学术 | `competitor_research` | 竞品技术论文、学术专利 |
| 批量学术调研 | `batch_academic` | 多主题并发学术调研 |
| 网页内容提取 | `academic_extract` | 学术页面深度内容 |

### 学术领域参数模板

```bash
# 学术论文搜索
TOPIC="大模型推理优化"
node <anysearch>/scripts/anysearch_cli.js search \
  "${TOPIC} research paper arXiv" \
  --domain academic \
  --content_types academic,web \
  --max_results 10 \
  --freshness year

# 技术趋势分析
node <anysearch>/scripts/anysearch_cli.js search \
  "${TOPIC} 技术趋势 研究前沿" \
  --domain academic \
  --freshness month

# 批量学术调研（5个并发）
node <anysearch>/scripts/anysearch_cli.js batch_search \
  --queries '[{"query":"大模型效率优化 论文","domain":"academic","max_results":5},{"query":"大模型推理加速 研究","domain":"academic","max_results":5}]'
```

### 学术领域查询词模板（关联数组）

| 子领域 | 查询模板 |
|--------|---------|
| `paper` | "${TOPIC} 论文 研究 arXiv 技术" |
| `trend` | "${TOPIC} 技术趋势 研究前沿 发展方向" |
| `review` | "${TOPIC} 综述 学术观点 专家分析" |
| `patent` | "${TOPIC} 专利 技术布局 研究" |
| `competitor` | "竞品 ${TOPIC} 技术 研究 论文" |

### 学术调研三步工作流

```
Step 1: 快速摸底
  → academic_search "主题" --max_results 10
  → 确认学术资源分布

Step 2: 深度采集
  → batch_academic ["主题1论文","主题2趋势","主题3竞品"]
  → 批量采集多维度学术资源

Step 3: 内容提取
  → academic_extract "高价值URL"
  → 深度提取全文内容用于报告
```

### 与62-02行业研究员协同

```
62-02行业研究员
  ├─► anysearch-academic → 学术论文调研
  ├─► anysearch-business → 商业市场调研
  └─► anysearch-finance  → 融资投资调研
```

### 天龙岗位升级

| 岗位 | 版本 | 新增能力 |
|------|------|---------|
| 62-02 行业研究员 | V10.2 → V10.3 | 学术论文批量调研 + 技术趋势分析 |
| 62-03 公司研究员 | V9.0 → V9.1 | 竞品学术研究 + 专利布局分析 |
| 01调研师 | V8.89 → V8.90 | 学术领域快速摸底 |
| 10-02 AI研究员 | V9.0 → V9.1 | AI学术前沿追踪 |

### 质量检查点

| 检查点 | 通过条件 |
|--------|---------|
| 论文覆盖 | 返回 ≥5 条学术来源 |
| 时效性 | 优先 1年内文献 |
| 来源权威 | 包含 arXiv/Nature/Science/ACL 等 |
| 边界覆盖 | 论文+趋势+竞品 三维覆盖 |
