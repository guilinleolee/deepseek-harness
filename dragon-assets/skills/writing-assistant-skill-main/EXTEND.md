# Writing Assistant Skill EXTEND.md

## 默认写作助手配置

---

## 自定义写作阶段 (Custom Writing Stage)

### ideation
- focus: idea_generation
- output: rough_concepts
- structure: minimal
- polish: none

### drafting
- focus: content_creation
- output: complete_draft
- structure: organized
- polish: basic

### editing
- focus: refinement
- output: polished_version
- structure: optimized
- polish: high

### publishing
- focus: formatting_distribution
- output: final_publication
- structure: platform_ready
- polish: publication_quality

---

## 自定义内容类型 (Custom Content Type)

### blog-post
- length: 800_2000_words
- tone: conversational_informative
- structure: introduction_body_conclusion
- seo: important

### technical-article
- length: 1500_3000_words
- tone: professional_authoritative
- structure: problem_solution_analysis
- seo: secondary

### marketing-copy
- length: 200_800_words
- tone: persuasive_engaging
- structure: hook_benefit_cta
- seo: critical

### social-post
- length: 50_300_words
- tone: casual_relatable
- structure: hook_value_hashtag
- seo: hashtag_optimized

---

## 自定义写作风格 (Custom Writing Style)

### ap-style
- guidelines: associated_press
- formality: journalistic
- abbreviation: spelled_out_first
- oxford_comma: no

### chicago-style
- guidelines: chicago_manual
- formality: academic_book
- abbreviation: allows_more
- oxford_comma: yes

### conversational
- guidelines: informal_blogging
- formality: casual
- abbreviation: frequent
- oxford_comma: flexible

### technical
- guidelines: industry_specific
- formality: professional
- abbreviation: domain_standard
- oxford_comma: discipline_specific

---

## 自定义SEO策略 (Custom SEO Strategy)

### no-seo
- keywords: not_considered
- structure: content_first
- meta: none
- optimization: none

### basic-seo
- keywords: primary_included
- structure: headings_optimized
- meta: basic_description
- optimization: on_page

### advanced-seo
- keywords: primary_secondary_lsi
- structure: full_schema_markup
- meta: comprehensive
- optimization: technical_plus_content

---

## 自定义编辑强度 (Custom Editing Intensity)

### light-edit
- focus: grammar_spelling
- changes: minimal
- voice: preserved
- turnaround: fast

### medium-edit
- focus: clarity_flow_structure
- changes: moderate
- voice: enhanced
- turnaround: standard

### heavy-edit
- focus: complete_reorganization
- changes: extensive
- voice: may_be_refined
- turnaround: extended

---

## 自定义协作模式 (Custom Collaboration Mode)

### solo-writing
- involvement: writer_only
- feedback: self_review
- revision: unlimited
- timeline: writer_controlled

### assisted-writing
- involvement: ai_assisted
- feedback: ai_suggestions
- revision: collaborative
- timeline: accelerated

### team-writing
- involvement: multiple_contributors
- feedback: peer_review
- revision: negotiated
- timeline: coordinated

---

## 自定义平台适配 (Custom Platform Adaptation)

### generic-content
- platform: none
- formatting: markdown
- constraints: none
- optimization: universal

### platform-specific
- platform: single_target
- formatting: platform_native
- constraints: platform_guidelines
- optimization: fully_optimized

### multi-platform
- platform: multiple_targets
- formatting: adaptive
- constraints: cross_platform_considerations
- optimization: per_platform_customization

---

## 配置优先级

```
CLI参数 > 项目级EXTEND.md > 用户级EXTEND.md > 默认配置
```

- **项目级**: `.claude/skills/writing-assistant-skill-main/EXTEND.md`
- **用户级**: `~/.claude/skills/writing-assistant-skill-main/EXTEND.md`
- **默认级**: `skills/writing-assistant-skill-main/EXTEND.md`

---

## 使用示例

### 快速博客
```markdown
## Quick Blog Post

### quick-blog
- stage: drafting
- type: blog-post
- style: conversational
- seo: basic-seo
- editing: light-edit
- collaboration: assisted-writing
- platform: generic-content
```

### 技术文章
```markdown
## Technical Article

### technical-article
- stage: editing
- type: technical-article
- style: technical
- seo: advanced-seo
- editing: medium-edit
- collaboration: assisted-writing
- platform: platform-specific
```

### 营销内容套件
```markdown
## Marketing Content Suite

### marketing-suite
- stage: publishing
- type: marketing-copy
- style: ap-style
- seo: advanced-seo
- editing: heavy-edit
- collaboration: team-writing
- platform: multi-platform
```
