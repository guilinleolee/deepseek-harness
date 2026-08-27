# 结构化数据模板

> 提升AI理解效率的Schema标记方案

## 🎯 核心目标

通过结构化数据标记：
1. 提升AI理解效率 +50%
2. 增加被引用概率
3. 提高实体识别准确率
4. 优化内容呈现形式

## 📋 必选Schema类型

### 1. Article（文章）

```json
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "文章标题",
  "description": "文章摘要，100-160字",
  "author": {
    "@type": "Person",
    "name": "作者姓名",
    "url": "作者主页URL"
  },
  "publisher": {
    "@type": "Organization",
    "name": "发布组织",
    "logo": {
      "@type": "ImageObject",
      "url": "Logo URL"
    }
  },
  "datePublished": "2026-03-03",
  "dateModified": "2026-03-03",
  "mainEntityOfPage": {
    "@type": "WebPage",
    "@id": "文章URL"
  },
  "image": "封面图URL",
  "articleSection": "分类",
  "wordCount": 1500,
  "inLanguage": "zh-CN"
}
```

### 2. Organization（组织）

```json
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "组织名称",
  "description": "组织简介",
  "url": "官网URL",
  "logo": {
    "@type": "ImageObject",
    "url": "Logo URL"
  },
  "sameAs": [
    "社交媒体链接1",
    "社交媒体链接2"
  ],
  "contactPoint": {
    "@type": "ContactPoint",
    "contactType": "customer service",
    "email": "contact@example.com"
  }
}
```

### 3. BreadcrumbList（面包屑）

```json
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    {
      "@type": "ListItem",
      "position": 1,
      "name": "首页",
      "item": "https://example.com"
    },
    {
      "@type": "ListItem",
      "position": 2,
      "name": "分类",
      "item": "https://example.com/category"
    },
    {
      "@type": "ListItem",
      "position": 3,
      "name": "文章标题",
      "item": "https://example.com/article"
    }
  ]
}
```

## 📋 推荐Schema类型

### 4. FAQPage（问答）

```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "问题1",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "答案1，建议100-300字"
      }
    },
    {
      "@type": "Question",
      "name": "问题2",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "答案2"
      }
    }
  ]
}
```

### 5. Person（作者）

```json
{
  "@context": "https://schema.org",
  "@type": "Person",
  "name": "作者姓名",
  "description": "作者简介",
  "url": "作者主页",
  "image": "作者头像URL",
  "jobTitle": "职位",
  "worksFor": {
    "@type": "Organization",
    "name": "所属组织"
  },
  "sameAs": [
    "LinkedIn主页",
    "Twitter主页"
  ],
  "knowsAbout": ["专业领域1", "专业领域2"]
}
```

### 6. WebSite（网站）

```json
{
  "@context": "https://schema.org",
  "@type": "WebSite",
  "name": "网站名称",
  "url": "网站URL",
  "description": "网站简介",
  "publisher": {
    "@type": "Organization",
    "name": "组织名称"
  },
  "potentialAction": {
    "@type": "SearchAction",
    "target": "https://example.com/search?q={search_term_string}",
    "query-input": "required name=search_term_string"
  }
}
```

## 📋 可选Schema类型

### 7. VideoObject（视频）

```json
{
  "@context": "https://schema.org",
  "@type": "VideoObject",
  "name": "视频标题",
  "description": "视频描述",
  "thumbnailUrl": "缩略图URL",
  "uploadDate": "2026-03-03",
  "duration": "PT5M30S",
  "contentUrl": "视频文件URL",
  "embedUrl": "嵌入URL"
}
```

### 8. HowTo（教程）

```json
{
  "@context": "https://schema.org",
  "@type": "HowTo",
  "name": "教程标题",
  "description": "教程描述",
  "step": [
    {
      "@type": "HowToStep",
      "name": "步骤1",
      "text": "详细说明",
      "image": "步骤图片URL"
    },
    {
      "@type": "HowToStep",
      "name": "步骤2",
      "text": "详细说明"
    }
  ],
  "totalTime": "PT30M",
  "estimatedCost": {
    "@type": "MonetaryAmount",
    "currency": "CNY",
    "value": "0"
  }
}
```

## 🔧 集成方式

### 方式1：JSON-LD（推荐）

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Article",
  ...
}
</script>
```

### 方式2：Microdata

```html
<div itemscope itemtype="https://schema.org/Article">
  <h1 itemprop="headline">文章标题</h1>
  <span itemprop="author" itemscope itemtype="https://schema.org/Person">
    <span itemprop="name">作者姓名</span>
  </span>
</div>
```

## 📊 质量检查

### 检查清单

- [ ] 所有必选Schema已添加
- [ ] JSON-LD格式正确
- [ ] 无语法错误
- [ ] URL有效
- [ ] 日期格式正确（ISO 8601）
- [ ] 图片URL有效
- [ ] 作者信息完整

### 验证工具

```bash
# Google结构化数据测试工具
https://search.google.com/test/rich-results

# Schema.org验证器
https://validator.schema.org/
```

## 💡 优化建议

### 建议1：优先级排序

```
P0（必选）：Article + Organization + BreadcrumbList
P1（推荐）：FAQPage + Person + WebSite
P2（可选）：VideoObject + HowTo + ImageObject
```

### 建议2：覆盖率目标

```
首页：100%（Organization + WebSite + SearchAction）
文章页：100%（Article + BreadcrumbList + Person）
产品页：100%（Product + Organization + BreadcrumbList）
FAQ页：100%（FAQPage）
```

### 建议3：定期更新

```
月度检查：
- Schema.org更新
- 新增Schema类型
- 验证工具更新
- 竞品Schema分析
```

## 🚫 常见错误

### 错误1：Schema缺失

```markdown
❌ 错误：页面无任何结构化数据
✅ 正确：至少添加Article + Organization
```

### 错误2：格式错误

```json
❌ 错误：
{
  "@type": "Article"
  "headline": "标题"  // 缺少逗号
}

✅ 正确：
{
  "@type": "Article",
  "headline": "标题"
}
```

### 错误3：信息不完整

```json
❌ 错误：
{
  "@type": "Article",
  "headline": "标题"
  // 缺少author、datePublished等必填字段
}

✅ 正确：
{
  "@type": "Article",
  "headline": "标题",
  "author": {...},
  "datePublished": "2026-03-03",
  ...
}
```

## 🔗 相关资源

- `prompts/entity-optimization.md` - 实体优化
- `tools/schema-generator.js` - Schema生成工具
- `references/schema-templates.md` - Schema模板库

---

**版本**: 1.0.0
**最后更新**: 2026-03-03