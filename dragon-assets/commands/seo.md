# seo.md · SEO/GEO统一命令

> **版本**: V1.0
> **日期**: 2026-08-22
> **用途**: SEO/GEO统一命令入口，调用40-seo-orchestrator Agent

---

## 命令列表

### `/seo <需求>`
统一SEO/GEO入口，自动路由到最合适的技能或Agent。

```
/seo audit https://example.com    # 全站审计
/seo geo https://example.com     # GEO优先审计
/seo local "北京烤鸭店"          # 本地SEO
/seo blog "2026 AI SEO"         # 博客写作
/seo compare a.com vs b.com     # 竞品对比
/seo quick https://example.com   # 快速评分
/seo citability https://example.com  # AI引用评分
/seo schema https://example.com  # Schema审计
/seo technical https://example.com  # 技术SEO
/seo content https://example.com   # 内容质量
/seo backlinks https://example.com # 链接分析
/seo keywords "AI写作工具"      # 关键词聚类
/seo maps "北京烤鸭店"          # Google Maps
/seo setup                       # 初始化环境
```

---

## 执行说明

此命令调用 `agents/40-seo-orchestrator.md` 进行统一编排。

**使用前**: 确认目标URL或业务信息已准备好。

**输出**: 统一格式的SEO/GEO报告，包含评分和行动建议。
