# Writing Plans EXTEND.md

## 默认写作计划配置

---

## 自定义计划粒度

### high-level-plan
- detail: major_milestones_only
- breakdown: limited
- timeline: rough_estimates
- flexibility: high

### detailed-plan
- detail: individual_tasks
- breakdown: comprehensive
- timeline: specific_deadlines
- flexibility: low

---

## 自定义阶段定义

### minimal-phases
- phases: [outline, draft, edit]
- transitions: simple
- gates: informal

### comprehensive-phases
- phases: [ideation, research, outline, draft, revise, edit, proofread, format, publish, promote]
- transitions: formal
- gates: approval_required

---

## 自定义协作模式

### solo-writer
- participants: single_author
- communication: none
- consensus: author_decision

### editorial-process
- participants: writers_editors_reviewers
- communication: formal_workflow
- consensus: approval_hierarchy

---

## 配置优先级
CLI参数 > 项目级EXTEND.md > 用户级EXTEND.md > 默认配置

---

## 使用示例

### 快速文章
- granularity: high-level-plan
- phases: minimal-phases
- collaboration: solo-writer

### 企业出版
- granularity: detailed-plan
- phases: comprehensive-phases
- collaboration: editorial-process
