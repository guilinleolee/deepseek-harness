---
license: UNKNOWN
name: github-to-skills-github
version: 1.0.0
description: |
  用于将 GitHub 仓库转换为专业 AI 技能的自动化工厂。当用户提供 GitHub URL 并希望对其进行“打包”、“封装”或从中“创建技能”时使用此技能。它会自动获取仓库详情、最新的提交哈希，并生成带有增强元数据的标准化技能结构，适用于生命周期管理。
author: 天龙引擎团队
created: 2026-02-26
category: automation

triggers:
  - "用户提到「github-to-skills GitHub技能转换器」时"
---

# GitHub to Skills Factory

This skill automates the conversion of GitHub repositories into fully functional AI skills.

## Core Functionality

1. **Analysis**: Fetches repository metadata (Description, README, Latest Commit Hash).
2. **Scaffolding**: Creates a standardized skill directory structure.
3. **Metadata Injection**: Generates `SKILL.md` with extended frontmatter (tracking source, version, hash) for future automated management.
4. **Wrapper Generation**: Creates a `scripts/wrapper.py` (or similar) to interface with the tool.

## Usage

**Trigger**: `/GitHub-to-skills <github_url>` or "Package this repo into a skill: <url>"

### Required Metadata Schema

Every skill created by this factory MUST include the following extended YAML frontmatter in its `SKILL.md`. This is critical for the `skill-manager` to function later.

```yaml
---
name: <kebab-case-repo-name>
description: <concise-description-for-agent-triggering>
# EXTENDED METADATA (MANDATORY)
github_url: <original-repo-url>
github_hash: <latest-commit-hash-at-time-of-creation>
version: <tag-or-0.1.0>
created_at: <ISO-8601-date>
entry_point: scripts/wrapper.py # or main script
dependencies: # List main dependencies if known, e.g., ["yt-dlp", "ffmpeg"]
---
```

## Workflow

1. **Fetch Info**: The agent first runs `scripts/fetch_github_info.py` to get the raw data from the repo.
2. **Plan**: The agent analyzes the README to understand how to invoke the tool (CLI args, Python API, etc.).
3. **Generate**: The agent uses the `skill-creator` patterns to write the `SKILL.md` and wrapper scripts, ensuring the **extended metadata** is present.
4. **Verify**: Checks if the commit hash was correctly captured.

## Resources

- `scripts/fetch_github_info.py`: Utility to scrape/API fetch repo details (README, Hash, Tags).
- `scripts/create_github_skill.py`: Orchestrator to scaffold the folder and write the initial files.

## Best Practices for Generated Skills

- **Isolation**: The generated skill should install its own dependencies (e.g., in a venv or via `uv`/`pip`) if possible, or clearly state them.
- **Progressive Disclosure**: Do not dump the entire repo into the skill. Only include the necessary wrapper code and reference the original repo for deep dives.
- **Idempotency**: The `github_hash` field allows the future `skill-manager` to check `if remote_hash != local_hash` to trigger updates.


## User-Learned Best Practices & Constraints

> **Auto-Generated Section**: This section is maintained by `skill-evolution-manager`. Do not edit manually.

### User Preferences
- 优先使用 uv 或 pip 自动处理依赖关系
- 生成的技能应保持目录结构简洁，只包含核心封装逻辑

### Known Fixes & Workarounds
- 处理非标准 README.md 文件名（如 readme.md）的兼容性

### Custom Instruction Injection

在包装 GitHub 仓库时，始终检查 README 以确定最合适的入口点。