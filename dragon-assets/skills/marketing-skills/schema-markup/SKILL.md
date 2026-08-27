---
name: schema-markup
description: "结构化数据标记 - Schema.org、Rich Snippets、搜索结果增强。"
trigger: "结构化数据、Schema、Rich Snippet、富媒体搜索"
metadata:
  version: 1.0.0
  source: https://github.com/coreyhaines31/marketingskills
---

# Schema Markup

> **核心价值**：结构化数据让搜索结果更醒目，点击率提升20-30%。

## Before Starting

1. 确认已完善 `product-marketing-context`
2. 识别页面内容类型

---

## 常用Schema类型

| 类型 | 适用场景 | 增强效果 |
|------|----------|----------|
| **Article** | 博客文章 | 标题、日期、作者 |
| **Product** | 产品页 | 价格、库存、评分 |
| **FAQ** | FAQ页 | 问答展开 |
| **HowTo** | 教程页 | 步骤展示 |
| **Review** | 评论页 | 评分星级 |
| **LocalBusiness** | 本地商家 | 地址、营业时间 |
| **BreadcrumbList** | 导航 | 面包屑导航 |

---

## Schema实现示例

### Article Schema

```json
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "文章标题",
  "author": {
    "@type": "Person",
    "name": "作者名"
  },
  "datePublished": "2024-01-01",
  "dateModified": "2024-01-15",
  "image": "https://example.com/image.jpg"
}
```

### FAQ Schema

```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [{
    "@type": "Question",
    "name": "问题1",
    "acceptedAnswer": {
      "@type": "Answer",
      "text": "答案1"
    }
  }]
}
```

### Product Schema

```json
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "产品名称",
  "offers": {
    "@type": "Offer",
    "price": "99.00",
    "priceCurrency": "CNY",
    "availability": "https://schema.org/InStock"
  },
  "aggregateRating": {
    "@type": "AggregateRating",
    "ratingValue": "4.5",
    "reviewCount": "128"
  }
}
```

---

## 验证工具

| 工具 | 用途 |
|------|------|
| [Google Rich Results Test](https://search.google.com/test/rich-results) | 测试Schema效果 |
| [Schema Validator](https://validator.schema.org/) | 验证语法 |
| Google Search Console | 监控Rich Results |

---

## Output Format

```markdown
## Schema Markup方案

### 页面类型
- 页面：[URL]
- 类型：[Schema类型]

### Schema代码
\`\`\`json
[Schema JSON]
\`\`\`

### 预期效果
- Rich Result类型：[类型]
- 点击率预期提升：[百分比]

### 验证结果
- 语法检查：✅ 通过
- Rich Results：✅ 可用
```

---

## Related Skills

- [seo-audit](../seo-audit/SKILL.md) - SEO审计
- [ai-seo](../ai-seo/SKILL.md) - AI时代SEO