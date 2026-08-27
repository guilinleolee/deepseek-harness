# Brainstorming EXTEND.md

## 默认头脑风暴配置

---

## 自定义会话类型 (Custom Session Type)

### rapid-fire
- duration: 5_10_min
- pace: fast
- quantity: many_ideas
- depth: surface

### deep-dive
- duration: 30_60_min
- pace: moderate
- quantity: fewer_ideas
- depth: thorough

### structured-session
- duration: 15_30_min
- pace: guided
- quantity: targeted
- depth: balanced

---

## 自定义创意生成 (Custom Idea Generation)

### free-association
- method: random_connections
- constraints: minimal
- direction: unguided
- creativity: high

### scamper
- method: systematic_transform
- constraints: technique_based
- direction: structured
- creativity: moderate

### reverse-thinking
- method: inversion
- constraints: opposite_view
- direction: counter_intuitive
- creativity: high

---

## 自定义提示技巧 (Custom Prompting Techniques)

### literal-prompts
- style: direct_questions
- ambiguity: low
- context: minimal
- interpretation: straightforward

### metaphor-prompts
- style: figurative_language
- ambiguity: medium
- context: rich
- interpretation: associative

### constraint-prompts
- style: boundary_setting
- ambiguity: low
- context: specific
- interpretation: focused

---

## 自定义筛选标准 (Custom Filtering Criteria)

### quantity-first
- metric: idea_count
- threshold: high
- evaluation: deferred
- filtering: minimal

### quality-first
- metric: idea_value
- threshold: selective
- evaluation: immediate
- filtering: strict

### novelty-first
- metric: uniqueness
- threshold: distinctive
- evaluation: comparative
- filtering: selective

---

## 自定义扩展模式 (Custom Expansion Mode)

### linear-expansion
- method: sequential_building
- branching: limited
- connection: direct
- scope: focused

### radial-expansion
- method: central_idea_outward
- branching: extensive
- connection: associative
- scope: broad

### network-expansion
- method: interconnected_nodes
- branching: unlimited
- connection: multidirectional
- scope: comprehensive

---

## 自定义参与者角色 (Custom Participant Roles)

### solo-brainstorm
- participants: single_user
- collaboration: none
- diversity: internal
- perspective: individual

### facilitated-session
- participants: user_guide
- collaboration: guided
- diversity: complementary
- perspective: enhanced

### group-brainstorm
- participants: multiple_agents
- collaboration: interactive
- diversity: multidisciplinary
- perspective: varied

---

## 自定义时间盒 (Custom Timeboxing)

### no-limit
- constraint: none
- flexibility: unlimited
- pressure: absent
- iteration: organic

### soft-limits
- constraint: suggested
- flexibility: extendable
- pressure: gentle
- iteration: checkpointed

### hard-limits
- constraint: strict
- flexibility: none
- pressure: intense
- iteration: timed_sessions

---

## 自定义环境设置 (Custom Environment)

### minimal-environment
- stimuli: blank_slate
- distraction: eliminated
- focus: internal
- resources: basic

### enriched-environment
- stimuli: curated_inspiration
- distraction: managed
- focus: enhanced
- resources: diverse

### immersive-environment
- stimuli: context_saturated
- distraction: filtered_relevant
- focus: domain_specific
- resources: comprehensive

---

## 自定义输出格式 (Custom Output Format)

### raw-list
- structure: flat_bullet_points
- organization: none
- detail: minimal
- exportability: simple

### categorized-list
- structure: grouped_by_theme
- organization: thematic
- detail: medium
- exportability: formatted

### mind-map
- structure: hierarchical_nodes
- organization: visual
- detail: variable
- exportability: specialized

### ranked-list
- structure: ordered_by_priority
- organization: scored
- detail: annotated
- exportability: structured

---

## 配置优先级

```
CLI参数 > 项目级EXTEND.md > 用户级EXTEND.md > 默认配置
```

- **项目级**: `.claude/skills/brainstorming/EXTEND.md`
- **用户级**: `~/.claude/skills/brainstorming/EXTEND.md`
- **默认级**: `skills/brainstorming/EXTEND.md`

---

## 使用示例

### 快速创意生成
```markdown
## Quick Ideation

### quick-ideation
- session: rapid-fire
- generation: free-association
- prompting: literal-prompts
- filtering: quantity-first
- expansion: linear-expansion
- roles: solo-brainstorm
- timeboxing: soft-limits
- environment: minimal-environment
- output: raw-list
```

### 深度结构化研讨
```markdown
## Deep Structured Session

### deep-structured
- session: deep-dive
- generation: scamper
- prompting: constraint-prompts
- filtering: quality-first
- expansion: network-expansion
- roles: facilitated-session
- timeboxing: hard-limits
- environment: enriched-environment
- output: categorized-list
```

### 创新团队工作坊
```markdown
## Innovation Workshop

### innovation-workshop
- session: structured-session
- generation: reverse-thinking
- prompting: metaphor-prompts
- filtering: novelty-first
- expansion: radial-expansion
- roles: group-brainstorm
- timeboxing: no-limit
- environment: immersive-environment
- output: mind-map
```
