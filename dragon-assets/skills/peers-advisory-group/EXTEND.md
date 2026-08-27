# Peers Advisory Group EXTEND.md

## 默认私董会配置

---

## 自定义顾问配置 (Custom Advisor Config)

### buffet-advisor
- persona: warren_buffett
- philosophy: value_investing
- style: wisdom_parables
- focus: long_term_value
- tone: patient_mentor

### gates-advisor
- persona: bill_gates
- philosophy: systematic_thinking
- style: analytical_questions
- focus: scalable_solutions
- tone: intellectual_curiosity

### musk-advisor
- persona: elon_musk
- philosophy: first_principles
- style: direct_challenge
- focus: breakthrough_innovation
- tone: ambitious_visionary

### jobs-advisor
- persona: steve_jobs
- philosophy: design_excellence
- style: demanding_feedback
- focus: product_perfection
- tone: passionate_visionary

---

## 自定义会议阶段 (Custom Meeting Stages)

### two-stage-process
- stages: [problem_definition, advisor_feedback]
- duration: focused
- interaction: sequential
- documentation: summary_only

### four-stage-process
- stages: [introduction, problem_deep_dive, advisor_qa, action_commitment]
- duration: extended
- interaction: iterative
- documentation: detailed_notes

### full-process
- stages: [preparation, problem_present, individual_advisory, peer_discussion, synthesis, commitment]
- duration: comprehensive
- interaction: collaborative
- documentation: full_transcript

---

## 自定义问题类型 (Custom Problem Types)

### strategic-problem
- category: strategy
- complexity: high
- time_horizon: long_term
- scope: organizational
- advisors: all_four

### operational-problem
- category: operations
- complexity: medium
- time_horizon: medium_term
- scope: departmental
- advisors: gates_buffett

### innovation-problem
- category: innovation
- complexity: very_high
- time_horizon: future
- scope: disruptive
- advisors: musk_jobs

### leadership-problem
- category: leadership
- complexity: high
- time_horizon: immediate
- scope: personal
- advisors: all_four

---

## 自定义反馈风格 (Custom Feedback Style)

### gentle-guidance
- tone: supportive
- questioning: socratic
- directness: low
- examples: stories
- priority: psychological_safety

### constructive-challenge
- tone: professional
- questioning: probing
- directness: medium
- examples: cases
- priority: insight_generation

### brutal-truth
- tone: direct
- questioning: sharp
- directness: high
- examples: counter_examples
- priority: breakthrough_thinking

---

## 自定义记录方式 (Custom Documentation)

### minimal-notes
- format: bullet_points
- detail: key_insights_only
- audio: none
- video: none
- sharing: summary_email

### standard-notes
- format: structured_summary
- detail: main_points_discussed
- audio: audio_recording
- video: none
- sharing: full_document

### comprehensive-record
- format: full_transcript_synthesized
- detail: word_for_word_plus_synthesis
- audio: professional_recording
- video: video_recording
- sharing: multimedia_package

---

## 自定义跟进机制 (Custom Follow-up Mechanism)

### no-followup
- scheduled: false
- checkins: none
- accountability: self
- progress: not_tracked

### email-followup
- scheduled: weekly
- checkins: automated_email
- accountability: self_reported
- progress: spreadsheet

### coaching-followup
- scheduled: bi_weekly
- checkins: live_session
- accountability: facilitated
- progress: dashboard

---

## 自定义参与者角色 (Custom Participant Roles)

### presenter-only
- roles: [problem_presenter]
- size: 1_person
- interaction: receives_feedback
- preparation: required

### peer-group
- roles: [problem_presenter, peer_participants]
- size: 3_5_people
- interaction: collaborative
- preparation: all_required

### full-advisory
- roles: [problem_presenter, peer_participants, expert_advisors]
- size: 5_8_people
- interaction: multi_dimensional
- preparation: intensive

---

## 自定义会议环境 (Custom Meeting Environment)

### virtual-meeting
- format: video_conference
- duration: 90_minutes
- tools: [zoom, miro, docs]
- atmosphere: focused_professional

### hybrid-meeting
- format: mixed_presence
- duration: 3_hours
- tools: [physical_space, digital_tools]
- atmosphere: immersive_collaborative

### in-person-meeting
- format: face_to_face
- duration: 1_day
- tools: [whiteboards, flipcharts, analog]
- atmosphere: intensive_retreat

---

## 配置优先级

```
CLI参数 > 项目级EXTEND.md > 用户级EXTEND.md > 默认配置
```

- **项目级**: `.claude/skills/peers-advisory-group/EXTEND.md`
- **用户级**: `~/.claude/skills/peers-advisory-group/EXTEND.md`
- **默认级**: `skills/peers-advisory-group/EXTEND.md`

---

## 使用示例

### 快速问题咨询
```markdown
## Quick Consultation

### quick-consultation
- advisors: all_four
- stages: two-stage-process
- problem: strategic-problem
- feedback: constructive-challenge
- documentation: minimal-notes
- followup: no-followup
- participants: presenter-only
- environment: virtual-meeting
```

### 深度战略研讨
```markdown
## Deep Strategy Session

### deep-strategy
- advisors: buffet_gates
- stages: full-process
- problem: strategic-problem
- feedback: constructive-challenge
- documentation: comprehensive-record
- followup: coaching-followup
- participants: peer-group
- environment: in-person-meeting
```

### 创新突破会
```markdown
## Innovation Breakthrough

### innovation-session
- advisors: musk_jobs
- stages: four-stage-process
- problem: innovation-problem
- feedback: brutal-truth
- documentation: standard-notes
- followup: email-followup
- participants: full-advisory
- environment: hybrid-meeting
```
