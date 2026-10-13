# Claude Code Skills

This directory contains project-specific skills that provide Claude with domain knowledge and best practices for this codebase.

## 本地 Skills 索引（推荐入口）

- [`SKILLS_使用指南.md`](./SKILLS_使用指南.md)

## Skills by Category

### 编程宗师 (Programming Masters)
| Skill | Description |
|-------|-------------|
| [investigator](./investigator/SKILL.md) | **/00调研师**：考古摸底，查清代码逻辑与技术坑点 |
| [architect](./architect/SKILL.md) | **/01架构师**：划定蓝图，原子化拆解任务计划 |
| [builder](./builder/SKILL.md) | **/02构建师**：施工交付，编写高质量生产级代码 |
| [validator](./validator/SKILL.md) | **/03验证师**：极端找茬，跑压力与全方位测试 |
| [security-reviewer](./security-reviewer/SKILL.md) | **/04安全师**：专项排雷，扫描安全漏洞 |
| [code-reviewer](./code-reviewer/SKILL.md) | **/05审查师**：终极审计，评审安全、性能与美感 |
| [scribe](./scribe/SKILL.md) | **/06记录师**：文明传承，自动维护高质量文档 |
| [publisher](./publisher/SKILL.md) | **/07发布师**：功德圆满，规范提交与 GitHub 发布 |

### Code Quality & Patterns
| Skill | Description |
|-------|-------------|
| [testing-patterns](./testing-patterns/SKILL.md) | Jest testing, factory functions, mocking strategies, TDD workflow |
| [systematic-debugging](./systematic-debugging/SKILL.md) | Four-phase debugging methodology, root cause analysis |

### React & UI
| Skill | Description |
|-------|-------------|
| [react-ui-patterns](./react-ui-patterns/SKILL.md) | React patterns, loading states, error handling, GraphQL hooks |
| [core-components](./core-components/SKILL.md) | Design system components, tokens, component library |
| [formik-patterns](./formik-patterns/SKILL.md) | Form handling, validation, submission patterns |

### Data & API
| Skill | Description |
|-------|-------------|
| [graphql-schema](./graphql-schema/SKILL.md) | GraphQL queries, mutations, code generation |

## Skill Combinations for Common Tasks

### Building a New Feature
1. **react-ui-patterns** - Loading/error/empty states
2. **graphql-schema** - Create queries/mutations
3. **core-components** - UI implementation
4. **testing-patterns** - Write tests (TDD)

### Building a Form
1. **formik-patterns** - Form structure and validation
2. **graphql-schema** - Mutation for submission
3. **react-ui-patterns** - Loading/error handling

### Debugging an Issue
1. **systematic-debugging** - Root cause analysis
2. **testing-patterns** - Write failing test first

## How Skills Work

Skills are automatically invoked when Claude recognizes relevant context. Each skill provides:

- **When to Use** - Trigger conditions
- **Core Patterns** - Best practices and examples
- **Anti-Patterns** - What to avoid
- **Integration** - How skills connect

## Adding New Skills

1. Create directory: `.claude/skills/skill-name/`
2. Add `SKILL.md` (case-sensitive) with YAML frontmatter:
   ```yaml
   ---
   # Required fields
   name: skill-name              # Lowercase, hyphens, max 64 chars
   description: What it does and when to use it. Include trigger keywords.  # Max 1024 chars

   # Optional fields
   allowed-tools: Read, Grep, Glob    # Restrict available tools
   model: claude-sonnet-4-20250514    # Specific model to use
   ---
   ```
3. Include standard sections: When to Use, Core Patterns, Anti-Patterns, Integration
4. Add to this README
5. Add triggers to `.claude/hooks/skill-rules.json`

**Important:** The `description` field is critical—Claude uses semantic matching on it to decide when to apply the skill. Include keywords users would naturally mention.

## Maintenance

- Update skills when patterns change
- Remove outdated information
- Add new patterns as they emerge
- Keep examples current with codebase
