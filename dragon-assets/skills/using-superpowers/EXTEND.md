# Using Superpowers EXTEND.md

## 默认超能力配置

---

## 自定义能力等级

### novice
- experience: learning_basics
- guidance: detailed_instructions_needed
- autonomy: low
- discovery: explicit_directions

### practitioner
- experience: competent_execution
- guidance: occasional_hints
- autonomy: moderate
- discovery: some_exploration

### expert
- experience: mastery_level
- guidance: minimal_none
- autonomy: high
- discovery: self_directed

---

## 自定义学习模式

### tutorial-mode
- style: step_by_step_guidance
- pacing: controlled
- examples: extensive
- exploration: limited

### guided-discovery
- style: hints_and_suggestions
- pacing: self_paced
- examples: selective
- exploration: encouraged

### exploratory-mode
- style: open_ended_problem_solving
- pacing: free_form
- examples: on_demand
- exploration: full_autonomy

---

## 自定义反馈循环

### instant-feedback
- timing: immediate_validation
- detail: specific_corrections
- suggestions: direct_fixes
- learning: rapid_iteration

### reflective-feedback
- timing: delayed_summaries
- detail: pattern_based_insights
- suggestions: guiding_questions
- learning: deeper_understanding

### minimal-feedback
- timing: on_error_only
- detail: error_messages
- suggestions: none
- learning: trial_and_error

---

## 自定义上下文提供

### minimal-context
- detail: task_description_only
- examples: none
- rationale: not_provided
- transfer: limited

### rich-context
- detail: comprehensive_background
- examples: extensive
- rationale: fully_explained
- transfer: high_transferability

### adaptive-context
- detail: adjusts_to_user_level
- examples: situationally_relevant
- rationale: progressive_disclosure
- transfer: optimized

---

## 自定义错误处理

### protective-mode
- intervention: prevent_mistakes
- recovery: guided_correction
- learning: from_prevention
- confidence: building

### resilient-mode
- intervention: allow_mistakes
- recovery: explain_then_fix
- learning: from_repair
- confidence: testing

### challenge-mode
- intervention: minimal_support
- recovery: self_directed
- learning: from_struggle
- confidence: proving

---

## 自定义协作风格

### assistant-mode
- role: supportive_helper
- initiative: responsive
- creativity: follows_lead
- ownership: shared

### partner-mode
- role: active_collaborator
- initiative: proactive_suggestions
- creativity: contributes_ideas
- ownership: joint

### mentor-mode
- role: guiding_teacher
- initiative: instructive
- creativity: models_thinking
- ownership: develops_your_skills

---

## 配置优先级

CLI参数 > 项目级EXTEND.md > 用户级EXTEND.md > 默认配置

---

## 使用示例

### 初学者引导
- level: novice
- learning: tutorial-mode
- feedback: instant-feedback
- context: rich-context
- errors: protective-mode
- collaboration: mentor-mode

### 日常开发
- level: practitioner
- learning: guided-discovery
- feedback: reflective-feedback
- context: adaptive-context
- errors: resilient-mode
- collaboration: partner-mode

### 专家模式
- level: expert
- learning: exploratory-mode
- feedback: minimal-feedback
- context: minimal-context
- errors: challenge-mode
- collaboration: assistant-mode
