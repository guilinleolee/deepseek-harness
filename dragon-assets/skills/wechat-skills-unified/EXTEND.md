# WeChat Skills Unified EXTEND.md

## 默认微信技能配置

---

## 自定义发布流程

### auto-publish
- flow: write_review_publish
- platforms: [公众号, 知乎, 掘金]
- timing: scheduled
- tracking: analytics_enabled

### manual-review
- flow: write_draft_review
- platforms: manual_selection
- timing: manual_publish
- tracking: manual_check

### batch-publish
- flow: bulk_articles
- platforms: multi_platform
- timing: optimal_times
- tracking: aggregated_stats

---

## 自定义内容适配

### wechat-official
- format: wechat_xml
- styling: custom_css
- features: [call_to_action, sharing]
- length: 2000_3000_chars

### zhihu-adapter
- format: markdown_html
- styling: zhihu_theme
- features: [images, references, math]
- length: comprehensive

### juejin-technical
- format: markdown
- styling: code_highlighting
- features: [code_blocks, diagrams]
- length: technical_depth

---

## 自定义SEO优化

### basic-seo
- keywords: 3_5_tags
- description: auto_generated
- structure: h1_h2_h3
- images: alt_tags

### advanced-seo
- keywords: semantic_analysis
- description: a_b_testing
- structure: schema_markup
- images: lazy_loading_webp

### local-seo
- keywords: location_based
- description: regional_focus
- structure: local_schema
- images: local_context

---

## 配置优先级

CLI参数 > 项目级EXTEND.md > 用户级EXTEND.md > 默认配置

---

## 使用示例

### 自动发布流程
- config: auto-publish
- platforms: [公众号, 知乎]
- seo: advanced-seo

### 批量内容分发
- config: batch-publish
- platforms: [公众号, 知乎, 掘金]
- seo: basic-seo

### 单平台手动发布
- config: manual-review
- platform: 公众号
- seo: local-seo
