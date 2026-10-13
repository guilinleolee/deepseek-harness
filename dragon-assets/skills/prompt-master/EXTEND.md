# Prompt Master EXTEND.md

## 默认提词师配置

---

## 自定义提示词结构 (Custom Prompt Structure)

### simple-structure
- components: [task, context]
- hierarchy: flat
- sections: minimal
- organization: linear

### structured-structure
- components: [role, task, context, constraints, output_format]
- hierarchy: two_level
- sections: clearly_delimited
- organization: logical_flow

### advanced-structure
- components: [role, task, context, constraints, examples, output_format, evaluation_criteria]
- hierarchy: multi_level
- sections: comprehensive
- organization: modular

---

## 自定义角色定义 (Custom Role Definition)

### generic-role
- specificity: general_assistant
- expertise: broad
- personality: neutral
- perspective: omniscient

### expert-role
- specificity: domain_expert
- expertise: specialized
- personality: professional
- perspective: disciplinary

### persona-role
- specificity: character_based
- expertise: contextual
- personality: distinct
- perspective: immersive

---

## 自定义任务描述 (Custom Task Description)

### vague-task
- clarity: open_ended
- specificity: low
- scope: flexible
- interpretation: broad

### specific-task
- clarity: well_defined
- specificity: high
- scope: bounded
- interpretation: narrow

### atomic-task
- clarity: precise_action
- specificity: exact
- scope: single_step
- interpretation: unambiguous

---

## 自定义上下文提供 (Custom Context Provision)

### minimal-context
- detail: essential_only
- background: omitted
- assumptions: stated
- examples: none

### standard-context
- detail: relevant_information
- background: summarized
- assumptions: explicit
- examples: selective

### comprehensive-context
- detail: extensive
- background: detailed
- assumptions: comprehensive
- examples: extensive

---

## 自定义约束设置 (Custom Constraints Setup)

### loose-constraints
- rules: minimal_guidelines
- restrictions: few
- boundaries: flexible
- enforcement: soft

### moderate-constraints
- rules: clear_guidelines
- restrictions: reasonable
- boundaries: defined
- enforcement: moderate

### strict-constraints
- rules: extensive_rules
- restrictions: many
- boundaries: rigid
- enforcement: strict

---

## 自定义输出格式 (Custom Output Format)

### free-format
- structure: unstructured
- medium: natural_language
- template: none
- validation: informal

### semi-structured-format
- structure: partially_defined
- medium: markdown
- template: suggested
- validation: manual

### structured-format
- structure: fully_specified
- medium: json_xml_schema
- template: required
- validation: automated

---

## 自定义示例使用 (Custom Example Usage)

### no-examples
- quantity: none
- variety: na
- placement: na
- purpose: na

### few-examples
- quantity: 1_3
- variety: limited
- placement: before_output
- purpose: illustration

### many-examples
- quantity: extensive
- variety: diverse
- placement: integrated
- purpose: comprehensive_guide

---

## 自定义迭代优化 (Custom Iterative Refinement)

### single-shot
- iterations: 1
- feedback: none
- refinement: none
- quality: initial_attempt

### few-shot
- iterations: 2_3
- feedback: incorporated
- refinement: incremental
- quality: improved

### chain-of-thought
- iterations: unlimited_until_satisfied
- feedback: continuous
- refinement: recursive
- quality: optimized

---

## 配置优先级

```
CLI参数 > 项目级EXTEND.md > 用户级EXTEND.md > 默认配置
```

- **项目级**: `.claude/skills/prompt-master/EXTEND.md`
- **用户级**: `~/.claude/skills/prompt-master/EXTEND.md`
- **默认级**: `skills/prompt-master/EXTEND.md`

---

## 使用示例

### 快速提示
```markdown
## Quick Prompt

### quick-prompt
- structure: simple-structure
- role: generic-role
- task: vague-task
- context: minimal-context
- constraints: loose-constraints
- output: free-format
- examples: no-examples
- iteration: single-shot
```

### 标准提示
```markdown
## Standard Prompt

### standard-prompt
- structure: structured-structure
- role: expert-role
- task: specific-task
- context: standard-context
- constraints: moderate-constraints
- output: semi-structured-format
- examples: few-examples
- iteration: few-shot
```

### 精通提示
```markdown
## Master Prompt

### master-prompt
- structure: advanced-structure
- role: persona-role
- task: atomic-task
- context: comprehensive-context
- constraints: strict-constraints
- output: structured-format
- examples: many-examples
- iteration: chain-of-thought
```
