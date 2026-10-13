# seo-orchestrator.md · SEO/GEO统一入口

> **版本**: V1.0
> **日期**: 2026-08-22
> **用途**: SEO/GEO统一命令入口，智能路由到对应技能
> **触发词**: seo, geo, 搜索引擎优化, AI搜索, 博客SEO, 本地SEO

---

## 入口路由

### 主命令格式

```
/seo <动作> [目标] [选项]
```

### 路由表

| 命令 | 路由目标 | 说明 |
|------|----------|------|
| `/seo audit <url>` | seo-audit.md | 全站SEO审计 |
| `/seo geo <url>` | geo-audit.md | GEO优先审计 |
| `/seo quick <url>` | geo-citability.md | 60秒快速评分 |
| `/seo citability <url>` | geo-citability.md | AI引用评分 |
| `/seo local <business>` | local-seo-audit.md | 本地SEO审计 |
| `/seo blog <topic>` | blog-write.md | 博客SEO写作 |
| `/seo compare <url1> vs <url2>` | seo-competitor-pages.md | 竞品对比 |
| `/seo schema <url>` | seo-schema.md | Schema审计 |
| `/seo technical <url>` | seo-technical.md | 技术SEO |
| `/seo content <url>` | seo-content.md | 内容质量 |
| `/seo backlinks <url>` | seo-backlinks.md | 链接分析 |
| `/seo keywords <topic>` | seo-cluster.md | 关键词聚类 |
| `/seo maps <business>` | seo-maps.md | Google Maps |
| `/seo setup` | - | 初始化环境 |

---

## 快速路由逻辑

### 意图识别流程

```
用户输入 → 关键词提取 → 路由匹配

关键词映射:
├── "审计", "audit", "检查" → seo-audit
├── "GEO", "AI搜索", "引用" → geo-audit
├── "本地", "地图", "门店" → local-seo-audit
├── "博客", "文章", "写作" → blog-write
├── "竞品", "对比", "vs" → seo-competitor-pages
├── "Schema", "结构化" → seo-schema
├── "技术", "速度", "性能" → seo-technical
├── "内容", "质量", "E-E-A-T" → seo-content
├── "链接", "外链", "backlink" → seo-backlinks
└── "关键词", "keyword", "聚类" → seo-cluster
```

---

## 使用示例

### 完整审计
```
输入: /seo audit https://example.com
执行: 并行运行技术SEO + 内容 + Schema + GEO
输出: 综合报告 + 优先级清单
```

### GEO专项
```
输入: /seo geo https://example.com
执行: citability + crawlers + llms.txt + 内容
输出: GEO优化建议
```

### 本地SEO
```
输入: /seo local "北京烤鸭店"
执行: GBP + 引文 + 关键词 + 地理网格
输出: 本地SEO报告
```

### 博客写作
```
输入: /seo blog "2026年AI SEO趋势"
执行: 策略 + 简报 + 写作 + SEO检查
输出: 完整博客 + Schema
```

---

## 技能库

### 已集成的Skills

```
skills/
├── geo-seo-claude/     # 15个GEO技能
├── claude-seo/        # 25个SEO技能
├── localseoskills/     # 39个本地SEO技能
└── claude-blog/        # 32个博客技能
```

### 关键Skills

| 技能 | 路径 | 用途 |
|------|------|------|
| seo-audit | claude-seo/ | 全站审计 |
| geo-audit | geo-seo-claude/ | GEO审计 |
| local-seo-audit | localseoskills/ | 本地审计 |
| blog-write | claude-blog/ | 博客写作 |
| geo-citability | geo-seo-claude/ | AI引用 |
| seo-schema | claude-seo/ | Schema |
| seo-technical | claude-seo/ | 技术SEO |
| seo-content | claude-seo/ | 内容质量 |
| seo-backlinks | claude-seo/ | 链接 |
| seo-cluster | claude-seo/ | 关键词 |

---

## 编排Agent

使用 `agents/40-seo-orchestrator.md` 进行复杂任务的编排。

---

## License

MIT
