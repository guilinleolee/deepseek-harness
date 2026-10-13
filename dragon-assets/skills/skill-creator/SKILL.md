---
name: skill-creator
version: 1.0.0
description: |
  Use when creating new skills or updating existing ones to extend Claude's capabilities with specialized knowledge, workflows, or tool integrations.
author: 天龙引擎团队
created: 2026-02-26
category: testing

triggers:
  - "用户提到「skill-creator 技能创建器」时"
---

# Skill Creator

This skill provides guidance for creating effective skills.

## About Skills

Skills are modular, self-contained packages that extend Claude's capabilities by providing
specialized knowledge, workflows, and tools. Think of them as "onboarding guides" for specific
domains or tasks—they transform Claude from a general-purpose agent into a specialized agent
equipped with procedural knowledge that no model can fully possess.

### What Skills Provide

1. Specialized workflows - Multi-step procedures for specific domains
2. Tool integrations - Instructions for working with specific file formats or APIs
3. Domain expertise - Company-specific knowledge, schemas, business logic
4. Bundled resources - Scripts, references, and assets for complex and repetitive tasks

## Core Principles

### Concise is Key

The context window is a public good. Skills share the context window with everything else Claude needs: system prompt, conversation history, other Skills' metadata, and the actual user request.

**Default assumption: Claude is already very smart.** Only add context Claude doesn't already have. Challenge each piece of information: "Does Claude really need this explanation?" and "Does this paragraph justify its token cost?"

Prefer concise examples over verbose explanations.

### Set Appropriate Degrees of Freedom

Match the level of specificity to the task's fragility and variability:

**High freedom (text-based instructions)**: Use when multiple approaches are valid, decisions depend on context, or heuristics guide the approach.

**Medium freedom (pseudocode or scripts with parameters)**: Use when a preferred pattern exists, some variation is acceptable, or configuration affects behavior.

**Low freedom (specific scripts, few parameters)**: Use when operations are fragile and error-prone, consistency is critical, or a specific sequence must be followed.

Think of Claude as exploring a path: a narrow bridge with cliffs needs specific guardrails (low freedom), while an open field allows many routes (high freedom).

### Anatomy of a Skill

Every skill consists of a required SKILL.md file and optional bundled resources:

```
skill-name/
├── SKILL.md (required)
│   ├── YAML frontmatter metadata (required)
│   │   ├── name: (required)
│   │   └── description: (required)
│   └── Markdown instructions (required)
└── Bundled Resources (optional)
    ├── scripts/          - Executable code (Python/Bash/etc.)
    ├── references/       - Documentation intended to be loaded into context as needed
    └── assets/           - Files used in output (templates, icons, fonts, etc.)
```

#### SKILL.md (required)

Every SKILL.md consists of:

- **Frontmatter** (YAML): Contains `name` and `description` fields. These are the only fields that Claude reads to determine when the skill gets used, thus it is very important to be clear and comprehensive in describing what the skill is, and when it should be used.
- **Body** (Markdown): Instructions and guidance for using the skill. Only loaded AFTER the skill triggers (if at all).

#### Bundled Resources (optional)

##### Scripts (`scripts/`)

Executable code (Python/Bash/etc.) for tasks that require deterministic reliability or are repeatedly rewritten.

- **When to include**: When the same code is being rewritten repeatedly or deterministic reliability is needed
- **Example**: `scripts/rotate_pdf.py` for PDF rotation tasks
- **Benefits**: Token efficient, deterministic, may be executed without loading into context
- **Note**: Scripts may still need to be read by Claude for patching or environment-specific adjustments

##### References (`references/`)

Documentation and reference material intended to be loaded as needed into context to inform Claude's process and thinking.

- **When to include**: For documentation that Claude should reference while working
- **Examples**: `references/finance.md` for financial schemas, `references/mnda.md` for company NDA template, `references/policies.md` for company policies, `references/api_docs.md` for API specifications
- **Use cases**: Database schemas, API documentation, domain knowledge, company policies, detailed workflow guides
- **Benefits**: Keeps SKILL.md lean, loaded only when Claude determines it's needed
- **Best practice**: If files are large (>10k words), include grep search patterns in SKILL.md
- **Avoid duplication**: Information should live in either SKILL.md or references files, not both. Prefer references files for detailed information unless it's truly core to the skill—this keeps SKILL.md lean while making information discoverable without hogging the context window. Keep only essential procedural instructions and workflow guidance in SKILL.md; move detailed reference material, schemas, and examples to references files.

##### Assets (`assets/`)

Files not intended to be loaded into context, but rather used within the output Claude produces.

- **When to include**: When the skill needs files that will be used in the final output
- **Examples**: `assets/logo.png` for brand assets, `assets/slides.pptx` for PowerPoint templates, `assets/frontend-template/` for HTML/React boilerplate, `assets/font.ttf` for typography
- **Use cases**: Templates, images, icons, boilerplate code, fonts, sample documents that get copied or modified
- **Benefits**: Separates output resources from documentation, enables Claude to use files without loading them into context

#### What to Not Include in a Skill

A skill should only contain essential files that directly support its functionality. Do NOT create extraneous documentation or auxiliary files, including:

- README.md
- INSTALLATION_GUIDE.md
- QUICK_REFERENCE.md
- CHANGELOG.md
- etc.

The skill should only contain the information needed for an AI agent to do the job at hand. It should not contain auxilary context about the process that went into creating it, setup and testing procedures, user-facing documentation, etc. Creating additional documentation files just adds clutter and confusion.

### Progressive Disclosure Design Principle

Skills use a three-level loading system to manage context efficiently:

1. **Metadata (name + description)** - Always in context (~100 words)
2. **SKILL.md body** - When skill triggers (<5k words)
3. **Bundled resources** - As needed by Claude (Unlimited because scripts can be executed without reading into context window)

#### Progressive Disclosure Patterns

Keep SKILL.md body to the essentials and under 500 lines to minimize context bloat. Split content into separate files when approaching this limit. When splitting out content into other files, it is very important to reference them from SKILL.md and describe clearly when to read them, to ensure the reader of the skill knows they exist and when to use them.

**Key principle:** When a skill supports multiple variations, frameworks, or options, keep only the core workflow and selection guidance in SKILL.md. Move variant-specific details (patterns, examples, configuration) into separate reference files.

**Pattern 1: High-level guide with references**

```markdown
# PDF Processing

## Quick start

Extract text with pdfplumber:
[code example]

## Advanced features

- **Form filling**: See [FORMS.md](FORMS.md) for complete guide
- **API reference**: See [REFERENCE.md](REFERENCE.md) for all methods
- **Examples**: See [EXAMPLES.md](EXAMPLES.md) for common patterns
```

Claude loads FORMS.md, REFERENCE.md, or EXAMPLES.md only when needed.

**Pattern 2: Domain-specific organization**

For Skills with multiple domains, organize content by domain to avoid loading irrelevant context:

```
bigquery-skill/
├── SKILL.md (overview and navigation)
└── reference/
    ├── finance.md (revenue, billing metrics)
    ├── sales.md (opportunities, pipeline)
    ├── product.md (API usage, features)
    └── marketing.md (campaigns, attribution)
```

When a user asks about sales metrics, Claude only reads sales.md.

Similarly, for skills supporting multiple frameworks or variants, organize by variant:

```
cloud-deploy/
├── SKILL.md (workflow + provider selection)
└── references/
    ├── aws.md (AWS deployment patterns)
    ├── gcp.md (GCP deployment patterns)
    └── azure.md (Azure deployment patterns)
```

When the user chooses AWS, Claude only reads aws.md.

**Pattern 3: Conditional details**

Show basic content, link to advanced content:

```markdown
# DOCX Processing

## Creating documents

Use docx-js for new documents. See [DOCX-JS.md](DOCX-JS.md).

## Editing documents

For simple edits, modify the XML directly.

**For tracked changes**: See [REDLINING.md](REDLINING.md)
**For OOXML details**: See [OOXML.md](OOXML.md)
```

Claude reads REDLINING.md or OOXML.md only when the user needs those features.

**Important guidelines:**

- **Avoid deeply nested references** - Keep references one level deep from SKILL.md. All reference files should link directly from SKILL.md.
- **Structure longer reference files** - For files longer than 100 lines, include a table of contents at the top so Claude can see the full scope when previewing.

## Skill Creation Workflow (RED-GREEN-REFACTOR)

技能创建本质上是针对 AI 行为的**防御性工程**。严禁在没有观察到“基准失败”的情况下编写技能。

### Phase 1: RED - 压力测试与基准建立
1. **定义场景**：设计 3+ 个具有压力的测试用例（如：时间紧迫、成本压力、权威压制）。
2. **观察失败 (Baseline)**：在没有新技能的情况下运行场景，记录 AI 的具体违规行为、逻辑漏洞以及**找的借口 (Rationalizations)**。
3. **识别红旗**：总结出哪些词汇或行为是失败的预兆（如：“总之”、“我认为没必要再检查”）。

### Phase 2: GREEN - 编写最小可行技能
1. **针对性开发**：编写仅够解决 Phase 1 中所观察到的漏洞的技能内容。
2. **触发器优化 (CSO)**：编写以 `Use when...` 开头的描述，确保技能在正确的时间被加载。
3. **验证通过**：携带新技能再次运行测试用例，确保 AI 现在能严格遵守指令。

### Phase 3: REFACTOR - 闭环审计与加固
1. **堵死漏洞**：针对 AI 可能产生的新借口，添加显式的禁止条款。
2. **重构效能**：压缩冗余文字，将详细参考资料移至 `references/`，确保 `SKILL.md` 极其精炼。
3. **添加防御组件**：引入“合理化对照表”和“红旗警告”清单。

---

## Defensive Documentation (防御性文档设计)

为了防止 AI 在执行时“偷懒”或“绕过”复杂步骤，必须在技能中内置防御逻辑。

### 1. Rationalization Table (合理化陷阱表)
列出 AI 常见的“心理暗示”及其对应的真实规则。
| 借口 (Rationalization) | 事实 (Reality) |
| --- | --- |
| “我已经手动检查过了” | 自动化验证不可替代，手动检查必有疏漏。 |
| “这次任务很简单，跳过流程” | 简单的任务是错误的温床，流程是底线。 |

### 2. Red Flags (红旗警告)
明确列出一旦出现必须立即停止并重新开始的征兆。
- ❌ **语义模糊**：使用“尽可能”、“大概”等词汇。
- ❌ **跳过步骤**：以“为了效率”为名省略审计环。

---

## CSO & Token Efficiency (搜索优化与效能)

### 1. Description: 触发条件优先
**铁律：描述必须描述“何时使用”，严禁总结“工作流程”。**
- ❌ **错误**：Use for code review - analyzes code and suggests fixes. (AI 会根据这段总结直接做简略分析，而跳过技能正文)
- ✅ **正确**：Use when code is completed and ready for PR, before merging into main.

### 2. 字数目标 (Word Count Targets)
- **入门/核心工作流**：< 150 字。
- **频繁加载的技能**：< 200 字。
- **普通技能**：< 500 字。
- **详细 API/文档**：必须移至 `references/`，在主技能中使用链接引用。

---

## Standard Creation Steps

1. **Understand** with concrete examples.
2. **Plan** reusable contents (scripts, references, assets).
3. **Initialize** (run `init_skill.py`).
4. **Edit** (implement RED-GREEN-REFACTOR cycle).
5. **Package** (run `package_skill.py`).
6. **Iterate** based on real usage.


## User-Learned Best Practices & Constraints

> **Auto-Generated Section**: This section is maintained by `skill-evolution-manager`. Do not edit manually.

### User Preferences
- 命名规范：在 Frontmatter 的 name 字段中，务必在英文名后紧跟中文名（例如：name: humanizer 去AI味）。
- 元数据要求：创建或更新 SKILL 时，Frontmatter 必须包含 'github_url'（追踪来源）和 'github_hash'（追踪具体版本/提交）。
- 描述翻译：在 Frontmatter 的 description 字段中，必须将英文描述翻译成中文，确保中英双语描述（英文在前，中文在后，或根据描述长度合理排列）。

### Known Fixes & Workarounds
- 进化性修改：对于技能的后续修改，不要直接编辑 SKILL.md。应在技能根目录创建/更新 evolution.json 文件，以确保存储的改进建议在核心技能升级时得以保留。

### Custom Instruction Injection

在创建新技能时，始终遵循 Progressive Disclosure（渐进式披露）原则，保持 SKILL.md 精简。