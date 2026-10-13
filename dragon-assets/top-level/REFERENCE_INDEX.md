# 引用关系索引 (REFERENCE_INDEX.md)

> **版本**: 1.2
> **更新日期**: 2026-08-22
> **用途**: 天龙引擎 Agent 与 Skill 引用关系追踪

---

## 📊 统计概览

| 引用类型 | 数量 |
|----------|------|
| **Agent → Skill 引用** | 131 个唯一 Skill |
| **Agent → Agent 引用** | ~30 组 |
| **冷门 Skill (未被引用)** | ~650 个 |

---

## 🔗 Agent → Skill 引用 (Top 50)

| 排名 | Skill | 引用次数 | 领域 |
|------|-------|----------|------|
| 1 | lightrag-knowledge-base | 36 | 知识库 |
| 2 | rag-anything | 20 | RAG |
| 3 | unified-search | 17 | 搜索 |
| 4 | dageno-api | 15 | API |
| 5 | advanced-memory-sync | 14 | 记忆 |
| 6 | shared | 12 | 共享 |
| 7 | llamaindex-rag | 11 | RAG |
| 8 | valuecell-trading-agent | 10 | 交易 |
| 9 | remotion-best-practices | 10 | 视频 |
| 10 | quadrants | 10 | 可视化 |
| 11 | math-visualizer | 10 | 可视化 |
| 12 | geo-optimizer | 10 | GEO |
| 13 | bilibili-operations | 9 | B站 |
| 14 | quiz-generator | 8 | 测验 |
| 15 | free-llm-provider-aggregator | 8 | LLM |
| 16 | deeptutor-bridge | 8 | 教学 |
| 17 | ai-csuite | 8 | 决策 |
| 18 | supermemory-memory | 7 | 记忆 |
| 19 | wechat-article-exporter | 6 | 微信 |
| 20 | web-access | 6 | 网络 |
| 21 | scrapy-spider-developer | 6 | 爬虫 |
| 22 | scrapy-data-pipeline | 6 | 爬虫 |
| 23 | scrapy-anti-ban | 6 | 爬虫 |
| 24 | qiushi-methodology | 6 | 方法论 |
| 25 | multi-search-engine | 6 | 搜索 |
| 26 | hyperframes-pipeline | 6 | 视频 |
| 27 | youtube-ultimate | 5 | 视频 |
| 28 | spec-kit-workflow | 5 | 工作流 |
| 29 | valuecell-deep-research | 4 | 研究 |
| 30 | tg-cli | 4 | 工具 |
| 31 | swarm-intelligence | 4 | AI |
| 32 | context-budget | 3 | 上下文 |
| 33 | seo-technical | 3 | SEO |
| 34 | seo-content | 3 | SEO |
| 35 | baoyu-image-gen | 3 | 图像 |
| 36 | gpt-image-2-prompt-library | 3 | 图像 |
| 37 | gpt-image-2-style-library | 3 | 图像 |
| 38 | blogger-distiller | 3 | 博主 |
| 39 | blogger-distill-orchestration | 3 | 博主 |
| 40 | blogger-distill-verify-gate | 3 | 博主 |
| 41 | firecrawl-api | 3 | 爬虫 |
| 42 | crawler-quality-grader | 3 | 爬虫 |
| 43 | aitoearn-publish | 3 | 发布 |
| 44 | aitoearn-engage | 3 | 互动 |
| 45 | aitoearn-monetize | 3 | 变现 |
| 46 | im-local-kb | 3 | 知识库 |
| 47 | learning-mentor | 3 | 学习 |
| 48 | tianlong-report | 2 | 报告 |
| 49 | mindmap-generator | 2 | 可视化 |
| 50 | a-stock-data | 2 | 金融 |

---

## 🔗 Agent → Agent 引用

| 被引用 Agent | 引用次数 | 主要引用来源 |
|-------------|----------|-------------|
| 35-04-content-operator.md | 4 | 28系列 |
| 28-01-copywriter-extended.md | 4 | 28系列内部 |
| 28-04-content-planner.md | 3 | 28系列 |
| 32-01-market-research.md | 2 | 32系列 |
| 47-03-im-operator.md | 2 | 47系列 |

---

## 🆕 新增 SEO/GEO 技能 (2026-08-22)

### 📥 来源仓库

| 仓库 | 来源 | Skills | Agents | 特点 |
|------|------|--------|--------|------|
| geo-seo-claude | zubair-trabzada | 15 | 5 | GEO优先 · AI搜索优化 |
| seo-skill | aevans-eng | 1 | - | 轻量级静态站点SEO |
| claude-blog | AgriciDaniel | 32 | 5 | 博客全生命周期 |
| claude-seo | AgriciDaniel | 25 | 18 | 全功能SEO分析 |
| localseoskills | garrettjsmith | 39 | - | 本地SEO专家 |

**新增总计**: 112 Skills + 28 Agents

### 🎯 统一编排系统 (SEO/GEO融合)

| 组件 | 路径 | 说明 |
|------|------|------|
| **编排Agent** | `agents/40-seo-orchestrator.md` | 统一调度所有SEO/GEO技能 |
| **统一Skill** | `skills/seo-orchestrator.md` | 命令路由和技能库 |
| **统一命令** | `commands/seo.md` | `/seo` 主入口 |
| **GEO命令** | `commands/geo.md` | `/geo` 快捷命令 |

### 🎯 GEO Skills (geo-seo-claude)

| Skill | 功能 |
|-------|------|
| geo-audit | GEO+SEO完整审计 |
| geo-brand-mentions | 品牌提及分析 |
| geo-citability | AI引用可评分 |
| geo-compare | 竞品GEO对比 |
| geo-content | GEO内容优化 |
| geo-crawlers | AI爬虫访问检查 |
| geo-llmstxt | llms.txt合规检查 |
| geo-platform-optimizer | 平台专项优化 |
| geo-proposal | GEO提案生成 |
| geo-prospect | 潜客GEO分析 |
| geo-report | 报告生成 |
| geo-report-pdf | PDF报告 |
| geo-schema | Schema优化 |
| geo-technical | 技术SEO |
| geo-update | GEO更新追踪 |

### 🔍 SEO Skills (claude-seo)

| Category | Skills |
|----------|--------|
| **Audit** | seo, seo-audit, seo-page |
| **Content** | seo-content, seo-content-brief, seo-cluster |
| **Technical** | seo-technical, seo-sitemap |
| **Schema** | seo-schema |
| **GEO/AI** | seo-geo |
| **Local** | seo-local, seo-maps |
| **Commerce** | seo-ecommerce |
| **Tools** | seo-dataforseo, seo-backlinks, seo-google, seo-image-gen, seo-images, seo-sxo, seo-drift, seo-flow, seo-competitor-pages, seo-hreflang, seo-plan, seo-programmatic |

### 📝 Blog Skills (claude-blog)

| Command | 功能 |
|---------|------|
| /blog write | 博客写作 |
| /blog seo-check | SEO检查 |
| /blog geo | GEO优化 |
| /blog analyze | 内容分析 |
| /blog rewrite | 重写 |
| /blog translate | 翻译 |
| /blog localize | 本地化 |
| /blog cluster | 主题聚类 |
| /blog strategy | 策略规划 |

### 🗺️ Local SEO Skills (localseoskills)

| Category | Skills |
|----------|--------|
| **Strategy** | local-seo-audit, gbp-optimization, local-citations, local-keyword-research, local-content-strategy |
| **Tools** | localseodata-tool, dataforseo-tool, brightlocal-tool, semrush-tool, ahrefs-tool |
| **GBP** | gbp-posts, gbp-suspension-recovery, apple-business-connect |
| **Maps** | geogrid-analysis, local-maps |
| **Reviews** | review-management |
| **Reporting** | local-reporting, client-deliverables |
| **Multi-location** | multi-location-seo, service-area-seo |

---

## 🏠 冷门 Skills (未被引用)

**总计**: ~650 个 Skill 未被任何 Agent 引用

**高价值但未被引用**:
- seo-local
- seo-performance
- seo-schema
- seo-sitemap
- seo-visual

**建议**: 评估这些 Skill 是否需要推广或归档

---

## 📈 引用分析

### 高度集中的引用
| Skill | 36次引用 | 占比 |
|-------|----------|------|
| lightrag-knowledge-base | 36 | 27% |
| rag-anything | 20 | 15% |
| unified-search | 17 | 13% |

**分析**: 知识库/RAG 是核心依赖

### 未被引用的 Skill 体系
| 体系 | 数量 | 建议 |
|------|------|------|
| OPC 14件套 | 14 | 新体系，待推广 |
| DBS 30+ | 30 | 活跃使用 |
| Baoyu 22 | 22 | 批量引用 |

---

## 🔄 更新机制

### 定期更新命令
```bash
# 更新引用统计
grep -rh "skills/" agents/*.md | \
  grep -oE "skills/[a-zA-Z0-9_-]+" | \
  sort | uniq -c | sort -rn > /tmp/skill-refs.txt

# 查找新增引用
diff /tmp/skill-refs-prev.txt /tmp/skill-refs.txt
```

### 触发条件
- 新增 Agent/Skill 时
- 每周定期更新
- 优化完成后更新

---

**最后更新**: 2026-08-22
**维护者**: 天龙引擎
