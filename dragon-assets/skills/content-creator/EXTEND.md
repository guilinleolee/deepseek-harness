# Content Creator EXTEND.md

## 默认内容配置

---

## 自定义品牌声音 (Custom Brand Voice)

### professional-corporate
- tone: formal
- voice: authoritative
- personality: professional
- language: standard
- emojis: minimal
- slang: none
- humor: conservative

### friendly-casual
- tone: conversational
- voice: approachable
- personality: friendly
- language: simple
- emojis: moderate
- slang: light
- humor: encouraged

### bold-edgy
- tone: provocative
- voice: confident
- personality: daring
- language: expressive
- emojis: liberal
- slang: contextual
- humor: dark

---

## 自定义SEO配置 (Custom SEO Configuration)

### my-seo-settings
- target_keywords: []
- secondary_keywords: []
- long_tail_keywords: []
- keyword_density: 1.5%
- meta_description_length: 160
- title_length: 60
- readability_score: Grade 8
- internal_links: 3-5
- external_links: 2-3

---

## 自定义内容类型 (Custom Content Types)

### blog-post
- structure: introduction-body-conclusion
- word_count: 1000-1500
- headings: h2-h4
- paragraphs: 3-5 sentences
- bullet_points: included
- call_to_action: bottom
- author_bio: included

### social-media
- structure: hook-value-cta
- character_limit: 280
- hashtags: 3-5
- mentions: 1-2
- emojis: 2-4
- links: 1
- media: suggested

### email-newsletter
- structure: teaser-content-promo
- subject_line: 40-char
- preview_text: 100-char
- paragraphs: short
- images: included
- links: trackable
- p.s.: included

### product-description
- structure: problem-solution-proof
- word_count: 300-500
- benefits: bullet-list
- features: detailed
- testimonials: included
- urgency: created
- guarantee: mentioned

---

## 自定义写作风格 (Custom Writing Styles)

### ap-style
- grammar: AP-standards
- punctuation: minimal-oxford
- capitalization: standard
- abbreviation: spelled-out-first
- numbers: digits-for-10+
- dates: month-day-year

### chicago-style
- grammar: Chicago-standards
- punctuation: oxford-comma
- capitalization: headline-style
- abbreviation: permitted
- numbers: spelled-out-to-100
- dates: month-day-year

### academic-style
- grammar: formal
- punctuation: strict
- capitalization: sentence-case
- abbreviation: defined-first
- numbers: written-out
- citations: required
- references: bibliography

---

## 自定义内容结构 (Custom Content Structure)

### pillar-page
- h1: main-topic
- h2: sections
- h3: subsections
- h4: details
- toc: included
- faq: included
- related_content: sidebar
- comments: enabled

### comparison-article
- introduction: brief
- comparison_table: included
- pros_cons: listed
- verdict: clear
- recommendation: specific
- affiliate_links: disclosed

### how-to-guide
- overview: summary
- prerequisites: listed
- steps: numbered
- warnings: highlighted
- tips: boxed
- troubleshooting: included
- conclusion: encouraging

---

## 自定义CTA配置 (Custom CTA Configuration)

### my-ctas
- primary: "立即开始"
- secondary: "了解更多"
- tertiary: "免费试用"
- urgency: "限时优惠"
- personalization: address-user
- placement: strategic
- variation: a/b-tested

---

## 自定义内容日历 (Custom Content Calendar)

### weekly-schedule
- monday: blog-post
- tuesday: social-media
- wednesday: video-script
- thursday: email-newsletter
- friday: case-study
- saturday: social-roundup
- sunday: planning

### content-pipeline
- idea: backlog
- research: in-progress
- drafting: review
- editing: final-approval
- publishing: scheduled
- promoting: active

---

## 自定义分析指标 (Custom Analytics Metrics)

### engagement-metrics
- views: tracked
- reads: calculated
- shares: counted
- comments: moderated
- time_on_page: measured
- bounce_rate: monitored
- conversion_rate: optimized

### seo-metrics
- ranking: tracked
- impressions: counted
- ctr: calculated
- backlinks: monitored
- domain_authority: checked
- page_speed: tested

---

## 加载优先级

```
CLI参数 > 项目级EXTEND.md > 用户级EXTEND.md > 默认配置
```

- **项目级**: `.claude/skills/content-creator/EXTEND.md`
- **用户级**: `~/.claude/skills/content-creator/EXTEND.md`
- **默认级**: `skills/content-creator/EXTEND.md`

---

## 使用示例

### 定义品牌声音
```markdown
## Brand Voice

### startup-voice
- tone: friendly-confident
- personality: innovative-approachable
- language: simple-clear
- humor: light-witty
- examples: tech-analogies
```

### 自定义SEO策略
```markdown
## SEO Strategy

### local-seo
- keywords: location-based
- google-my-business: optimized
- reviews: actively-managed
- local-content: prioritized
```

### 内容模板
```markdown
## Content Templates

### listicle
- title_number: odd
- items: 7-15
- images: per-item
- descriptions: brief
- conclusion: summary
```
