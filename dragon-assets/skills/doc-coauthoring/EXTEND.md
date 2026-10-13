# Doc Coauthoring EXTEND.md

## 默认文档协作配置

---

## 自定义协作模式 (Custom Collaboration Modes)

### single-author
- authors: 1
- review: self
- approval: automatic
- merge: automatic

### peer-review
- authors: 2-4
- review: peer_required
- approval: majority
- merge: after_approval

### collaborative-editing
- authors: 2+
- review: continuous
- approval: consensus
- merge: continuous

### formal-review
- authors: 2+
- review: staged
- approval: all_required
- merge: after_all_approvals

---

## 自定义文档结构 (Custom Document Structure)

### linear-document
- structure: linear
- sections: sequential
- collaboration: sequential_access
- locking: paragraph_level

### modular-document
- structure: modular
- sections: independent
- collaboration: parallel
- locking: section_level

### layered-document
- structure: layered
- sections: [content, style, structure]
- collaboration: role_based
- locking: layer_level

---

## 自定义角色分配 (Custom Role Assignment)

### lead-author
- role: lead_author
- responsibilities: [outline, content, final_review]
- permissions: [read, write, approve]
- priority: primary

### co-author
- role: co_author
- responsibilities: [content_sections, reviews]
- permissions: [read, write, suggest]
- priority: secondary

### reviewer
- role: reviewer
- responsibilities: [feedback, suggestions, approval]
- permissions: [read, comment, approve]
- priority: tertiary

### editor
- role: editor
- responsibilities: [style, grammar, consistency]
- permissions: [read, comment, edit]
- priority: secondary

---

## 自定义工作流阶段 (Custom Workflow Stages)

### planning
- stage: planning
- activities: [outline, research, structure]
- participants: all_authors
- duration: defined
- deliverable: approved_outline

### drafting
- stage: drafting
- activities: [writing, research, citations]
- participants: authors
- duration: flexible
- deliverable: complete_draft

### reviewing
- stage: reviewing
- activities: [peer_review, feedback, revisions]
- participants: all_participants
- duration: defined
- deliverable: reviewed_draft

### finalizing
- stage: finalizing
- activities: [editing, formatting, publishing]
- participants: lead_author + editor
- duration: defined
- deliverable: final_document

---

## 自定义反馈机制 (Custom Feedback Mechanism)

### inline-comments
- method: inline
- format: markdown
- resolution: discussion
- tracking: per_comment
- notification: immediate

### pull-request-review
- method: pr_review
- format: github_pr
- resolution: commit_based
- tracking: per_pr
- notification: batched

### tracked-changes
- method: tracked_changes
- format: suggestion_mode
- resolution: accept/reject
- tracking: per_change
- notification: optional

### meeting-feedback
- method: synchronous
- format: discussion
- resolution: meeting_notes
- tracking: per_meeting
- notification: scheduled

---

## 自定义版本控制 (Custom Version Control)

### main-branch
- branch: main
- protection: restricted
- commits: direct
- reviews: not_required

### feature-branch
- branch: feature/*
- protection: restricted
- commits: direct
- reviews: pr_required

### draft-branch
- branch: draft/*
- protection: open
- commits: direct
- reviews: optional

---

## 自定义冲突解决 (Custom Conflict Resolution)

### manual-resolution
- strategy: manual
- detection: git_conflict_markers
- resolution: authors_resolve
- locking: pessimistic

### automatic-resolution
- strategy: automatic
- detection: inline_conflicts
- resolution: last_write_wins
- locking: optimistic

### mediated-resolution
- strategy: mediated
- detection: any_conflict
- resolution: third_party
- locking: pessimistic

---

## 自定义质量检查 (Custom Quality Checks)

### basic-checks
- checks: [spelling, grammar, formatting]
- automation: partial
- blocking: none
- severity: suggestions

### standard-checks
- checks: [spelling, grammar, formatting, consistency, links]
- automation: automated
- blocking: critical_only
- severity: mixed

### comprehensive-checks
- checks: [spelling, grammar, formatting, consistency, links, citations, plagiarism, accessibility]
- automation: automated
- blocking: critical_and_high
- severity: strict

---

## 自定义文档标准 (Custom Documentation Standards)

### style-guide
- standard: custom
- sections: defined
- formatting: strict
- enforcement: manual

### template-based
- standard: template
- sections: predefined
- formatting: enforced
- enforcement: automated

### iso-based
- standard: iso_iec
- sections: iso_compliant
- formatting: formal
- enforcement: validated

---

## 自定义访问控制 (Custom Access Control)

### open-access
- visibility: public
- editing: all_contributors
- commenting: all_users
- approval: none

### restricted-access
- visibility: team
- editing: authors_only
- commenting: team
- approval: authors

### confidential-access
- visibility: authors_only
- editing: authors_only
- commenting: authors_only
- approval: all_authors

---

## 自定义通知设置 (Custom Notification Settings)

### immediate-notifications
- triggers: all_changes
- method: instant
- digest: none
- frequency: real_time

### batch-notifications
- triggers: milestones
- method: email
- digest: hourly
- frequency: periodic

### summary-notifications
- triggers: completion
- method: digest
- digest: daily
- frequency: scheduled

---

## 自定义归档策略 (Custom Archive Strategy)

### no-archive
- archiving: none
- retention: indefinite
- cleanup: manual

### time-based-archive
- archiving: after_completion
- retention: 1_year
- cleanup: automatic

### event-based-archive
- archiving: after_publishing
- retention: project_lifetime
- cleanup: on_project_close

---

## 配置优先级

```
CLI参数 > 项目级EXTEND.md > 用户级EXTEND.md > 默认配置
```

- **项目级**: `.claude/skills/doc-coauthoring/EXTEND.md`
- **用户级**: `~/.claude/skills/doc-coauthoring/EXTEND.md`
- **默认级**: `skills/doc-coauthoring/EXTEND.md`

---

## 使用示例

### 快速协作
```markdown
## Quick Collaboration

### quick-collab
- mode: peer-review
- structure: linear-document
- roles: [lead-author, reviewer]
- workflow: [drafting, finalizing]
- feedback: inline-comments
- version_control: main-branch
- conflicts: manual-resolution
- quality: basic-checks
- standards: style-guide
- access: open-access
- notifications: immediate-notifications
- archive: no-archive
```

### 专业协作
```markdown
## Professional Collaboration

### professional-collab
- mode: formal-review
- structure: modular-document
- roles: [lead-author, co-author, reviewer, editor]
- workflow: [planning, drafting, reviewing, finalizing]
- feedback: pull-request-review + tracked-changes
- version_control: feature-branch
- conflicts: mediated-resolution
- quality: comprehensive-checks
- standards: template-based
- access: restricted-access
- notifications: batch-notifications
- archive: time-based-archive
```

### 企业级协作
```markdown
## Enterprise Collaboration

### enterprise-collab
- mode: collaborative-editing
- structure: layered-document
- roles: all_roles
- workflow: all_stages
- feedback: all_feedback_mechanisms
- version_control: draft-branch + feature-branch
- conflicts: automatic-resolution
- quality: comprehensive-checks + validation
- standards: iso-based
- access: confidential-access
- notifications: summary-notifications
- archive: event-based-archive
```
