# Internal Communications EXTEND.md

## 默认内部沟通配置

---

## 自定义沟通类型 (Custom Communication Type)

### announcement
- purpose: one_way_broadcast
- audience: broad_organization
- urgency: varies
- feedback: limited

### collaboration
- purpose: two_way_dialogue
- audience: specific_teams
- urgency: responsive
- feedback: encouraged

### documentation
- purpose: reference_material
- audience: future_readers
- urgency: low
- feedback: revisions_accepted

---

## 自定义语气风格 (Custom Tone Style)

### formal-comm
- style: professional_structured
- contractions: avoided
- jargon: technical_appropriate
- emojis: minimal

### casual-comm
- style: conversational
- contractions: natural
- jargon: explained
- emojis: occasional

### urgent-comm
- style: direct_actionable
- contractions: minimal
- jargon: avoided
- emojis: none

---

## 自定义格式规范 (Custom Format Standards)

### plain-text
- structure: unformatted
- emphasis: caps_only
- links: full_urls
- formatting: none

### markdown-light
- structure: headers_bullets
- emphasis: bold_italic
- links: markdown_links
- formatting: minimal

### markdown-rich
- structure: full_hierarchy
- emphasis: extensive
- links: embedded_references
- formatting: tables_code_blocks

---

## 自定义受众定位 (Custom Audience Targeting)

### company-wide
- scope: all_employees
- specificity: universal_language
- context: minimal
- assumptions: none

### department-specific
- scope: single_department
- specificity: domain_knowledge
- context: familiar
- assumptions: shared_background

### project-team
- scope: project_members
- specificity: technical_details
- context: deep
- assumptions: full_project_knowledge

---

## 自定义分发策略 (Custom Distribution Strategy)

### email-only
- channels: email_distribution
- frequency: as_needed
- archiving: inbox_only
- searchability: limited

### slack-first
- channels: slack_primary
- frequency: real_time
- archiving: slack_search
- searchability: good

### hybrid-distribution
- channels: email_slack_docs
- frequency: tiered_approach
- archiving: multiple_locations
- searchability: excellent

---

## 自定义长度控制 (Custom Length Control)

### executive-summary
- length: one_screen_or_less
- detail: high_level_only
- depth: overview
- reading_time: under_2_min

### standard-length
- length: 2_5_screens
- detail: balanced
- depth: moderate
- reading_time: 5_10_min

### comprehensive
- length: as_needed
- detail: full
- depth: complete
- reading_time: varies_significantly

---

## 自定义行动号召 (Custom Call to Action)

### informational-only
- cta: none
- response: not_expected
- deadline: none
- next_steps: informational

### optional-response
- cta: feedback_invited
- response: voluntary
- deadline: suggested
- next_steps: optional

### required-action
- cta: specific_action
- response: mandatory
- deadline: firm
- next_steps: clearly_defined

---

## 配置优先级

```
CLI参数 > 项目级EXTEND.md > 用户级EXTEND.md > 默认配置
```

- **项目级**: `.claude/skills/internal-comms/EXTEND.md`
- **用户级**: `~/.claude/skills/internal-comms/EXTEND.md`
- **默认级**: `skills/internal-comms/EXTEND.md`

---

## 使用示例

### 公司公告
```markdown
## Company Announcement

### company-announcement
- type: announcement
- tone: formal-comm
- format: markdown-light
- audience: company-wide
- distribution: email-only
- length: executive-summary
- cta: informational-only
```

### 团队协作
```markdown
## Team Collaboration

### team-collaboration
- type: collaboration
- tone: casual-comm
- format: markdown-rich
- audience: project-team
- distribution: slack-first
- length: standard-length
- cta: optional-response
```

### 项目文档
```markdown
## Project Documentation

### project-documentation
- type: documentation
- tone: formal-comm
- format: markdown-rich
- audience: project-team
- distribution: hybrid-distribution
- length: comprehensive
- cta: informational-only
```
