---
name: skill-creator-v2 技能创建器V2
description: Use when creating new skills, editing existing skills, or needing interactive skill development guidance. Integrates official Anthropic skill creation patterns with TDD methodology for production-grade skills. Use when user says "create a skill", "build a skill", "skill creator", or asks about skill development best practices.
version: 2.0.0
author: Nine-Dragons Team
license: MIT
compatibility: Claude Code, Claude.ai, API
---

# Skill Creator V2 - Enhanced Skill Development Guide

## Overview

**Skill Creator V2 combines:**
- 📘 **Official Anthropic patterns** - Sequential workflows, MCP coordination, iterative refinement
- 🧪 **TDD methodology** - Test-driven documentation with RED-GREEN-REFACTOR cycle
- 🤖 **Interactive guidance** - Step-by-step skill creation with validation
- 📦 **Production-ready** - Automated testing, packaging, and distribution

**Core Philosophy**: Create skills that are **tested, validated, and production-ready** from day one.

---

## Three Paths Through This Guide

Choose your path based on your goal:

### 🎨 **Path 1: Standalone Skills** (Beginner → Advanced)
Focus on Fundamentals → Planning & Design → Testing & Iteration
- Best for: Domain expertise, workflows, documentation
- No MCP required
- Timeline: 15-30 minutes for first skill

### 🔌 **Path 2: MCP-Enhanced Skills** (Intermediate)
Focus on Skills + MCP → Patterns → Integration
- Best for: Enhancing existing MCP servers with workflow guidance
- Requires: Working MCP server
- Timeline: 30-60 minutes

### 🚀 **Path 3: Advanced Patterns** (Expert)
Focus on Multi-MCP coordination, domain-specific intelligence
- Best for: Complex workflows spanning multiple services
- Requires: Deep MCP knowledge
- Timeline: 1-2 hours

---

## Step 1: Understanding with Concrete Examples

### Interactive Discovery Process

Before creating ANY skill, answer these questions:

#### 🎯 **Use Case Definition**
```
Use Case: [One-line description]
Trigger: What does user say to activate this skill?
Steps:
  1. [First action]
  2. [Second action]
  ...
Result: [What outcome does user achieve?]
```

#### 🔍 **Domain Analysis**
- What specialized knowledge does this skill need?
- What tools are required (built-in or MCP)?
- What mistakes do users commonly make?
- What would make this skill **irreplaceable**?

#### 📂 **Skill Category Selection**

**Category 1: Document & Asset Creation**
- Use when: Creating consistent, high-quality output
- Examples: frontend-design, docx, pptx, xlsx
- Key techniques: Embedded style guides, templates, quality checklists

**Category 2: Workflow Automation**
- Use when: Multi-step processes with consistent methodology
- Examples: skill-creator, project-sprint-planning
- Key techniques: Step-by-step validation, templates, iterative loops

**Category 3: MCP Enhancement**
- Use when: Workflow guidance for MCP tool access
- Examples: sentry-code-review, notion-project-setup
- Key techniques: Multi-MCP coordination, domain expertise, error handling

---

## Step 2: Planning the Skill Structure

### 🏗️ **Anatomy of a Skill**

```
skill-name/
├── SKILL.md              # Required - Main instructions
├── scripts/              # Optional - Executable code
│   ├── init_skill.py     # Initialization
│   ├── validate.py       # Validation
│   └── package.py        # Packaging
├── references/           # Optional - Documentation
│   ├── api-guide.md
│   └── examples/
└── assets/               # Optional - Templates, fonts
    └── template.md
```

### 📊 **Progressive Disclosure Design**

Skills use a **three-level loading system**:

| Level | Content | Token Cost | When Loaded |
|-------|---------|------------|-------------|
| **1. Metadata** | name + description (YAML) | ~100 tokens | Always in context |
| **2. SKILL.md** | Full instructions | <5k words | When skill triggers |
| **3. Resources** | scripts, references, assets | Unlimited* | As needed |

**Key Principle**: Only load what you need, when you need it.

### 🎯 **Reusable Resource Planning**

Ask: "What will Claude need to reference repeatedly?"

#### **Scripts (`scripts/`) - When to Include**
✅ Include when:
- Same code rewritten repeatedly
- Deterministic reliability needed
- Token-intensive operations

❌ Don't include when:
- Simple one-off commands
- Already available in built-in tools

**Example**:
```bash
# ✅ Good: Rotate PDF (complex, repeated)
scripts/rotate_pdf.py

# ❌ Bad: List files (built-in)
scripts/ls.sh
```

#### **References (`references/`) - When to Include**
✅ Include when:
- API documentation (>100 lines)
- Database schemas
- Domain-specific knowledge
- Company policies/templates

❌ Don't include when:
- Can be summarized in <50 lines
- Core to the skill (keep in SKILL.md)

#### **Assets (`assets/`) - When to Include**
✅ Include when:
- Templates (HTML, React, PowerPoint)
- Brand assets (logos, fonts)
- Boilerplate code
- Sample documents

❌ Don't include when:
- Only for reference (use `references/`)

---

## Step 3: Writing Effective YAML Frontmatter

### ⚠️ **CRITICAL: Frontmatter Determines Skill Discovery**

The `description` field is **THE most important part** of your skill. Claude reads this to decide when to load your skill.

### 📝 **Description Field Formula**

```yaml
---
name: skill-name-in-kebab-case
description: [What it does] + [When to use it] + [Key capabilities] + [Trigger phrases]. Use when user asks to [specific tasks] or mentions [specific symptoms].
---
```

### ✅ **Good Examples**

```yaml
# Example 1: Specific and actionable
---
name: figma-design-docs
description: Analyzes Figma design files and generates developer handoff documentation. Use when user uploads .fig files, asks for "design specs", "component documentation", or "design-to-code handoff".
---
```

```yaml
# Example 2: Clear workflow guidance
---
name: linear-sprint-planning
description: Manages Linear project workflows including sprint planning, task creation, and status tracking. Use when user mentions "sprint", "Linear tasks", "project planning", or asks to "create tickets".
---
```

```yaml
# Example 3: Domain-specific with triggers
---
name: payment-compliance-check
description: Payment processing workflow with compliance checks for sanctions, jurisdiction, and risk assessment. Use when user says "process payment", "check compliance", or handles financial transactions.
---
```

### ❌ **Bad Examples**

```yaml
# Too vague
---
name: helper
description: Helps with projects.
---

# Missing triggers
---
name: document-builder
description: Creates sophisticated documentation systems.
---

# Too technical, no user triggers
---
name: entity-model
description: Implements the Project entity model with hierarchical relationships.
---
```

### 🚫 **Security Restrictions**

**Forbidden in frontmatter:**
- XML angle brackets (`< >`) - Security risk
- Skills named with "claude" or "anthropic" prefix - Reserved
- Code execution in YAML - Uses safe YAML parsing

**Allowed:**
- Any standard YAML types
- Custom metadata fields
- Long descriptions (up to 1024 characters)

### 📋 **Optional Frontmatter Fields**

```yaml
---
name: skill-name
description: [required description]
license: MIT                    # Optional: License for open-source
allowed-tools: "Bash(python:*) Bash(npm:*) WebFetch"  # Optional: Restrict tool access
metadata:                      # Optional: Custom fields
  author: Company Name
  version: 1.0.0
  mcp-server: server-name
  category: productivity
  tags: [project-management, automation]
  documentation: https://example.com/docs
  support: support@example.com
---
```

---

## Step 4: Writing SKILL.md Body

### 📐 **Recommended Structure**

```markdown
---
name: skill-name
description: [What + When + How]
---

# Skill Name

## Overview
What is this? Core principle in 1-2 sentences.

## When to Use
[Inline flowchart if decision non-obvious]

### Symptom-Based Triggers
- User says: [specific phrases]
- Context: [when this applies]
- File types: [.ext, .ext]

### When NOT to Use
- [Alternative approaches]
- [When skill would over-trigger]

## Core Pattern
[For techniques/patterns: Before/after comparison]

## Quick Reference
[Table or bullets for common operations]

## Implementation
### Step 1: [First Major Step]
Clear explanation + example.

### Step 2: [Second Major Step]
...

## Examples
### Example 1: [Common scenario]
User says: "[query]"
Actions:
1. [Action 1]
2. [Action 2]
Result: [Outcome]

## Troubleshooting
### Error: [Common error]
Cause: [Why it happens]
Solution: [How to fix]

## Common Mistakes
What goes wrong + how to avoid it.

## Real-World Impact (optional)
Concrete results/metrics.
```

### 🎯 **Writing Style Guidelines**

**CRITICAL: Write in imperative/infinitive form (verb-first)**

✅ **Good:**
```markdown
To accomplish X, do Y.
Before calling create_project, verify:
- Project name is non-empty
- At least one team member assigned
```

❌ **Bad:**
```markdown
You should do X.
If you need to do Y, make sure to...
```

### 🔍 **Claude Search Optimization (CSO)**

**Principle**: Future Claude needs to FIND your skill

#### **1. Keyword Coverage**
Use words Claude would search for:
- **Error messages**: "Hook timed out", "ENOTEMPTY", "race condition"
- **Symptoms**: "flaky", "hanging", "zombie", "pollution"
- **Synonyms**: "timeout/hang/freeze", "cleanup/teardown/afterEach"
- **Tools**: Actual commands, library names, file types

#### **2. Token Efficiency**

**Target word counts:**
- Frequently-loaded skills: <200 words total
- Other skills: <500 words (still be concise)

**Techniques:**

**Move details to tool help:**
```markdown
# ❌ BAD: Document all flags
search-conversations supports --text, --both, --after DATE

# ✅ GOOD: Reference --help
search-conversations supports multiple modes. Run --help for details.
```

**Use cross-references:**
```markdown
# ❌ BAD: Repeat workflow details
See other-skill for detailed workflow explanation...

# ✅ GOOD: Reference other skill
**REQUIRED:** Use [other-skill-name] for workflow.
```

---

## Step 5: MCP Enhancement Patterns (5 Patterns)

### 🎯 **Pattern 1: Sequential Workflow Orchestration**

**Use when**: Users need multi-step processes in specific order

**Template**:
```markdown
## Workflow: [Workflow Name]

### Step 1: [First Action]
Call MCP tool: `tool_name`
Parameters: param1, param2
Validation: [What to check before proceeding]

### Step 2: [Second Action]
Call MCP tool: `tool_name`
Wait for: [confirmation/condition]

### Step 3: [Third Action]
...
```

**Example**:
```markdown
## Workflow: Customer Onboarding

### Step 1: Create Account
Call MCP tool: `create_customer`
Parameters: name, email, company
Validation: Account ID returned

### Step 2: Setup Payment
Call MCP tool: `setup_payment_method`
Wait for: payment_method.verified == true

### Step 3: Create Subscription
Call MCP tool: `create_subscription`
Parameters: plan_id, customer_id (from Step 1)

### Step 4: Send Welcome Email
Call MCP tool: `send_email`
Template: welcome_email_template
```

---

### 🌐 **Pattern 2: Multi-MCP Coordination**

**Use when**: Workflows span multiple services

**Template**:
```markdown
## Phase [N]: [Phase Name] ([Service MCP])

### Actions
1. [Action 1]
2. [Action 2]
3. [Data passing to next phase]

### Validation Before Next Phase
- [Check 1]
- [Check 2]
```

**Example**:
```markdown
## Multi-Phase Design Handoff

### Phase 1: Design Export (Figma MCP)
1. Export design assets from Figma
2. Generate design specifications
3. Create asset manifest

**Validation**: All assets exported successfully

### Phase 2: Asset Storage (Drive MCP)
1. Create project folder in Drive
2. Upload all assets
3. Generate shareable links

**Validation**: All files uploaded, links accessible

### Phase 3: Task Creation (Linear MCP)
1. Create development tasks
2. Attach asset links to tasks
3. Assign to engineering team

**Validation**: Tasks created with valid attachments

### Phase 4: Notification (Slack MCP)
1. Post handoff summary to #engineering
2. Include asset links and task references
```

---

### 🔄 **Pattern 3: Iterative Refinement**

**Use when**: Output quality improves with iteration

**Template**:
```markdown
## Iterative [Process Name]

### Initial Draft
1. Fetch data via MCP
2. Generate first draft
3. Save to temporary file

### Quality Check
Run validation: `scripts/check.py`
Identify issues:
- [Issue type 1]
- [Issue type 2]

### Refinement Loop
1. Address each identified issue
2. Regenerate affected sections
3. Re-validate

**Stop when**: Quality threshold met (define criteria)

### Finalization
1. Apply final formatting
2. Generate summary
3. Save final version
```

---

### 🧠 **Pattern 4: Context-Aware Tool Selection**

**Use when**: Same outcome, different tools based on context

**Template**:
```markdown
## Smart [Action Name]

### Decision Tree
Check [context factor]:
- [Condition A]: Use [Tool/Service A]
- [Condition B]: Use [Tool/Service B]
- [Condition C]: Use [Tool/Service C]

### Execution
Based on decision:
- Call appropriate MCP tool
- Apply service-specific metadata
- Generate access link

### User Communication
Explain why that choice was made
```

**Example**:
```markdown
## Smart File Storage

### Decision Tree
Check file type and size:
- Large files (>10MB): Use cloud storage MCP
- Collaborative docs: Use Notion/Docs MCP
- Code files: Use GitHub MCP
- Temporary files: Use local storage

### Execution
Based on decision:
- Call selected MCP tool
- Apply service-specific metadata
- Generate access link

### User Communication
"Stored [filename] to [service] because [reason]. Access link: [url]"
```

---

### 🏢 **Pattern 5: Domain-Specific Intelligence**

**Use when**: Skill adds specialized knowledge beyond tool access

**Template**:
```markdown
## [Domain] Intelligence Layer

### Before Processing
1. Fetch data via MCP
2. Apply [domain] rules:
   - [Rule 1]
   - [Rule 2]
   - [Rule 3]
3. Document [domain] decision

### Processing
IF [domain] passed:
- Call processing MCP tool
- Apply domain-specific logic
- Process transaction

ELSE:
- Flag for review
- Create [domain] case

### Audit Trail
- Log all [domain] checks
- Record processing decisions
- Generate audit report
```

**Example**:
```markdown
## Financial Compliance Intelligence

### Before Processing (Compliance Check)
1. Fetch transaction details via MCP
2. Apply compliance rules:
   - Check sanctions lists
   - Verify jurisdiction allowances
   - Assess risk level
3. Document compliance decision

### Processing
IF compliance passed:
- Call payment processing MCP tool
- Apply appropriate fraud checks
- Process transaction

ELSE:
- Flag for review
- Create compliance case

### Audit Trail
- Log all compliance checks
- Record processing decisions
- Generate audit report
```

---

## Step 6: TDD Testing Methodology

### 🧪 **The Iron Law**

```
NO SKILL WITHOUT A FAILING TEST FIRST
```

**This applies to:**
- ✅ New skills
- ✅ Edits to existing skills
- ✅ "Simple additions"
- ✅ "Documentation updates"

**No exceptions:**
- Don't keep untested changes as "reference"
- Don't "adapt" while running tests
- Delete means delete

### 🔄 **RED-GREEN-REFACTOR Cycle**

#### **RED Phase: Write Failing Test (Baseline)**

Run pressure scenario **WITHOUT** the skill. Document:
- What choices did the agent make?
- What rationalizations did they use (verbatim)?
- Which pressures triggered violations?

**This is "watch the test fail"** - you must see natural behavior.

**Example Test Scenario:**
```bash
# Test: Create project without skill
# Expected: Agent forgets validation steps

Query: "Help me create a new project called 'Test Project'"

Baseline Behavior:
❌ Agent creates project immediately
❌ Skips team member assignment
❌ Doesn't check for duplicate names
❌ Ignores start date validation

Rationalizations documented:
- "User didn't specify details"
- "Can add team members later"
- "Start date is optional"
```

#### **GREEN Phase: Write Minimal Skill**

Write skill that addresses **those specific rationalizations only**.

**Example Skill Addition:**
```markdown
## CRITICAL: Project Creation Validation

Before creating ANY project, verify:
- [ ] Project name is non-empty
- [ ] At least one team member assigned
- [ ] Start date is not in the past
- [ ] No duplicate project names exist

**No exceptions:**
- Don't proceed with empty names
- Don't skip team assignment
- Don't ignore validation
```

**Re-test with skill:**
```bash
# Test: Create project WITH skill
# Expected: Agent follows all validation steps

Query: "Help me create a new project called 'Test Project'"

With Skill Behavior:
✅ Asks for team member assignment
✅ Checks for duplicate names
✅ Validates start date
✅ Only creates project after all checks pass
```

#### **REFACTOR Phase: Close Loopholes**

Agent found new rationalization? Add explicit counter. Re-test.

**Example Loophole:**
```
Agent: "I'll create the project with default values to save time"

Counter in skill:
```markdown
**No defaults shortcut:**
- Don't use default team members
- Don't auto-generate names
- Don't assume optional fields
```

### 📊 **Testing Different Skill Types**

#### **Discipline-Enforcing Skills** (TDD, security rules)

**Test with:**
- Academic questions: Do they understand the rules?
- Pressure scenarios: Do they comply under stress?
- Multiple pressures: time + sunk cost + exhaustion

**Success**: Agent follows rule under maximum pressure

#### **Technique Skills** (how-to guides)

**Test with:**
- Application scenarios: Can they apply the technique?
- Variation scenarios: Do they handle edge cases?
- Missing information: Do instructions have gaps?

**Success**: Agent successfully applies technique to new scenario

#### **Pattern Skills** (mental models)

**Test with:**
- Recognition: Do they recognize when pattern applies?
- Application: Can they use the mental model?
- Counter-examples: Do they know when NOT to apply?

**Success**: Agent correctly identifies when/how to apply pattern

#### **Reference Skills** (APIs, documentation)

**Test with:**
- Retrieval: Can they find the right information?
- Application: Can they use what they found?
- Gap testing: Are common use cases covered?

**Success**: Agent finds and correctly applies reference information

---

## Step 7: Validation and Packaging

### ✅ **Automated Validation**

Use `skill-validate` CLI tool (see companion script):

```bash
# Validate skill structure and frontmatter
skill-validate path/to/skill

# Run with detailed output
skill-validate path/to/skill --verbose

# Auto-fix common issues
skill-validate path/to/skill --fix
```

**Validation checks:**
- ✅ YAML frontmatter format
- ✅ Required fields present
- ✅ Skill naming conventions (kebab-case)
- ✅ Description quality (triggers, length)
- ✅ File organization
- ✅ Token efficiency (<5k words for SKILL.md)
- ✅ No security violations (XML tags, reserved names)

### 📦 **Automated Packaging**

Use `skill-package` CLI tool:

```bash
# Package skill with validation
skill-package path/to/skill

# Specify output directory
skill-package path/to/skill --output ./dist

# Package without validation (not recommended)
skill-package path/to/skill --skip-validation
```

**Packaging process:**
1. **Validate** skill automatically
2. **Create** zip file with proper structure
3. **Generate** manifest.json with metadata
4. **Report** token counts and optimization tips

---

## Step 8: Success Criteria

### 📈 **Quantitative Metrics**

- **Skill triggers on 90%+ of relevant queries**
  - Measure: Run 10-20 test queries
  - Track: Auto-load vs manual invocation rate

- **Completes workflow in minimal tool calls**
  - Measure: Compare with/without skill
  - Track: Tool call count and total tokens

- **0 failed API calls per workflow**
  - Measure: Monitor MCP server logs
  - Track: Retry rates and error codes

### 🎯 **Qualitative Metrics**

- **Users don't need to prompt about next steps**
  - Test: Note how often you need to redirect
  - Ask: Beta users for feedback

- **Workflows complete without user correction**
  - Test: Run same request 3-5 times
  - Compare: Structural consistency and quality

- **Consistent results across sessions**
  - Test: Can new user accomplish task on first try?
  - Verify: Minimal guidance needed

---

## Step 9: Distribution and Sharing

### 🌐 **Current Distribution Model**

**Individual users:**
1. Download skill folder
2. Zip the folder (if needed)
3. Upload to Claude.ai (Settings > Capabilities > Skills)
4. Or place in Claude Code skills directory

**Organization-level:**
- Admins deploy workspace-wide
- Automatic updates
- Centralized management

### 📦 **Recommended GitHub Structure**

```
your-skill-repo/
├── README.md              # For human visitors
├── LICENSE                # License file
├── your-skill-name/       # The actual skill
│   ├── SKILL.md
│   ├── scripts/
│   ├── references/
│   └── assets/
└── examples/              # Usage examples with screenshots
    ├── example1.md
    └── example2.png
```

### 📝 **README Template**

```markdown
# [Skill Name]

[One-line description]

## What It Does

[2-3 sentences explaining the skill's purpose]

## Installation

### Claude.ai
1. Download the [skill-name] folder
2. Upload to Claude.ai > Settings > Skills
3. Enable the skill

### Claude Code
1. Clone this repo
2. Copy to `~/.claude/skills/`
3. Restart Claude Code

## Quick Start

```
Ask Claude: "[example trigger phrase]"
```

## Features

- ✅ [Feature 1]
- ✅ [Feature 2]
- ✅ [Feature 3]

## Examples

### Example 1: [Use case]
**User says**: "[query]"
**Result**: [outcome]

### Example 2: [Use case]
**User says**: "[query]"
**Result**: [outcome]

## MCP Integration

If this skill enhances an MCP server:
- **MCP Server**: [server-name]
- **Installation**: [link to MCP docs]
- **Why use both**: [explanation]

## Contributing

[How to contribute]

## License

[License type]

## Support

- Issues: [GitHub issues link]
- Discussions: [GitHub discussions link]
```

---

## Troubleshooting

### ❌ **Skill Won't Upload**

**Error**: "Could not find SKILL.md in uploaded folder"
- **Cause**: File not named exactly SKILL.md
- **Fix**: Rename to SKILL.md (case-sensitive)
- **Verify**: `ls -la` should show SKILL.md

**Error**: "Invalid frontmatter"
- **Cause**: YAML formatting issue
- **Common mistakes**:
  ```yaml
  # Wrong - missing delimiters
  name: my-skill
  description: Does things

  # Wrong - unclosed quotes
  name: my-skill
  description: "Does things

  # Correct
  ---
  name: my-skill
  description: Does things
  ---
  ```

**Error**: "Invalid skill name"
- **Cause**: Name has spaces or capitals
  ```yaml
  # Wrong
  name: My Cool Skill

  # Correct
  name: my-cool-skill
  ```

### 🎯 **Skill Doesn't Trigger**

**Symptom**: Skill never loads automatically

**Fix checklist**:
- Is description too generic? ("Helps with projects" won't work)
- Does description include trigger phrases?
- Does it mention relevant file types?

**Debug approach**:
Ask Claude: "When would you use the [skill-name] skill?"
Claude will quote the description back. Adjust based on what's missing.

### 🚫 **Skill Triggers Too Often**

**Symptom**: Skill loads for unrelated queries

**Solutions**:

1. **Add negative triggers**
   ```yaml
   description: Advanced data analysis for CSV files. Use for statistical modeling, regression, clustering. Do NOT use for simple data exploration (use data-viz skill instead).
   ```

2. **Be more specific**
   ```yaml
   # Too broad
   description: Processes documents

   # More specific
   description: Processes PDF legal documents for contract review
   ```

3. **Clarify scope**
   ```yaml
   description: PayFlow payment processing for e-commerce. Use specifically for online payment workflows, not for general financial queries.
   ```

### 🔌 **MCP Connection Issues**

**Symptom**: Skill loads but MCP calls fail

**Checklist**:
1. Verify MCP server is connected
   - Claude.ai: Settings > Extensions > [Your Service]
   - Should show "Connected" status

2. Check authentication
   - API keys valid and not expired
   - Proper permissions/scopes granted
   - OAuth tokens refreshed

3. Test MCP independently
   - Ask Claude to call MCP directly (without skill)
   - "Use [Service] MCP to fetch my projects"
   - If this fails, issue is MCP not skill

4. Verify tool names
   - Skill references correct MCP tool names
   - Check MCP server documentation
   - Tool names are case-sensitive

### 📝 **Instructions Not Followed**

**Symptom**: Skill loads but Claude doesn't follow instructions

**Common causes**:

1. **Instructions too verbose**
   - Keep instructions concise
   - Use bullet points and numbered lists
   - Move detailed reference to separate files

2. **Instructions buried**
   - Put critical instructions at the top
   - Use ## Important or ## Critical headers
   - Repeat key points if needed

3. **Ambiguous language**
   ```markdown
   # Bad
   Make sure to validate things properly

   # Good
   CRITICAL: Before calling create_project, verify:
   - Project name is non-empty
   - At least one team member assigned
   - Start date is not in the past
   ```

4. **Model "laziness"**
   Add explicit encouragement:
   ```markdown
   ## Performance Notes
   - Take your time to do this thoroughly
   - Quality is more important than speed
   - Do not skip validation steps
   ```

### 📊 **Large Context Issues**

**Symptom**: Skill seems slow or responses degraded

**Causes**:
- Skill content too large
- Too many skills enabled simultaneously
- All content loaded instead of progressive disclosure

**Solutions**:

1. **Optimize SKILL.md size**
   - Move detailed docs to `references/`
   - Link to references instead of inline
   - Keep SKILL.md under 5,000 words

2. **Reduce enabled skills**
   - Evaluate if you have >20-50 skills enabled
   - Recommend selective enablement
   - Consider skill "packs" for related capabilities

---

## Quick Checklist

### Before You Start
- [ ] Identified 2-3 concrete use cases
- [ ] Tools identified (built-in or MCP)
- [ ] Reviewed this guide and example skills
- [ ] Planned folder structure

### During Development
- [ ] Folder named in kebab-case
- [ ] SKILL.md file exists (exact spelling)
- [ ] YAML frontmatter has `---` delimiters
- [ ] `name` field: kebab-case, no spaces, no capitals
- [ ] `description` includes WHAT and WHEN
- [ ] No XML tags (`< >`) anywhere
- [ ] Instructions are clear and actionable
- [ ] Error handling included
- [ ] Examples provided
- [ ] References clearly linked

### Before Upload
- [ ] Tested triggering on obvious tasks
- [ ] Tested triggering on paraphrased requests
- [ ] Verified doesn't trigger on unrelated topics
- [ ] Functional tests pass
- [ ] Tool integration works (if applicable)
- [ ] Compressed as .zip file

### After Upload
- [ ] Test in real conversations
- [ ] Monitor for under/over-triggering
- [ ] Collect user feedback
- [ ] Iterate on description and instructions
- [ ] Update version in metadata

---

## Companion Tools

This skill works with these CLI tools:

- **skill-validate** - Validate skill structure and frontmatter
- **skill-package** - Package skill for distribution
- **skill-test** - Run test scenarios against skills
- **skill-create** - Initialize new skill from template

See individual tool documentation for usage.

---

## Version History

- **v2.0.0** (2025-02-24)
  - Integrated official Anthropic patterns
  - Added MCP enhancement patterns (5 patterns)
  - Enhanced TDD methodology
  - Added automated validation/packaging
  - Comprehensive troubleshooting guide

- **v1.0.0** (2025-02-08)
  - Initial release
  - Basic skill creation guidance

---

**License**: MIT
**Author**: Nine-Dragons Team
**Compatibility**: Claude Code, Claude.ai, API
**Based on**: Anthropic's "The Complete Guide to Building Skills for Claude" + TDD methodology

---

## Further Reading

### Official Anthropic Resources
- [Skills Best Practices Guide](https://docs.anthropic.com/en/docs/build-with-claude/skills)
- [Skills Documentation](https://docs.anthropic.com/en/docs/build-with-claude/skills)
- [MCP Documentation](https://modelcontextprotocol.io/)
- [Skills API Reference](https://docs.anthropic.com/en/api/skills)

### Community Resources
- [anthropic/skills GitHub](https://github.com/anthropics/skills) - Official skill repository
- [Claude Developers Discord](https://discord.gg/anthropic) - Community support

### Internal Resources
- See `writing-skills` for TDD methodology
- See `skill-mcp-patterns` for detailed MCP patterns
- See `skill-testing-framework` for automated testing
