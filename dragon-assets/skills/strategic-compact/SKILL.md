---
license: UNKNOWN
name: strategic-compact
version: 1.0.0
description: |
  建议在逻辑间隔进行手动上下文压缩，以在任务阶段保持上下文，而不是依赖任意的自动压缩。
author: 天龙引擎团队
created: 2026-02-26
category: ai

triggers:
  - "用户提到「strategic-compact 策略压缩」时"
---

# Strategic Compact Skill

Suggests manual `/compact` at strategic points in your workflow rather than relying on arbitrary auto-compaction.

## Why Strategic Compaction?

Auto-compaction triggers at arbitrary points:
- Often mid-task, losing important context
- No awareness of logical task boundaries
- Can interrupt complex multi-step operations

Strategic compaction at logical boundaries:
- **After exploration, before execution** - Compact research context, keep implementation plan
- **After completing a milestone** - Fresh start for next phase
- **Before major context shifts** - Clear exploration context before different task

## How It Works

The `suggest-compact.sh` script runs on PreToolUse (Edit/Write) and:

1. **Tracks tool calls** - Counts tool invocations in session
2. **Threshold detection** - Suggests at configurable threshold (default: 50 calls)
3. **Periodic reminders** - Reminds every 25 calls after threshold

## Hook Setup

Add to your `~/.claude/settings.json`:

```json
{
  "hooks": {
    "PreToolUse": [{
      "matcher": "tool == \"Edit\" || tool == \"Write\"",
      "hooks": [{
        "type": "command",
        "command": "~/.claude/skills/strategic-compact/suggest-compact.sh"
      }]
    }]
  }
}
```

## Configuration

Environment variables:
- `COMPACT_THRESHOLD` - Tool calls before first suggestion (default: 50)

## Best Practices

1. **Compact after planning** - Once plan is finalized, compact to start fresh
2. **Compact after debugging** - Clear error-resolution context before continuing
3. **Architectural Drift Detection** - If `update-codemaps` shows >30% change, it's highly recommended to compact as the structural context has shifted significantly.
4. **Don't compact mid-implementation** - Preserve context for related changes
5. **Read the suggestion** - The hook tells you *when*, you decide *if*

## Related

- [The Longform Guide](https://x.com/affaanmustafa/status/2014040193557471352) - Token optimization section
- Memory persistence hooks - For state that survives compaction

#### Evolution Pattern (Maintenance)

To preserve custom improvements when a core skill is upgraded, avoid editing `SKILL.md` directly for individual modifications. Instead:

1. Create or update an `evolution.json` file in the skill's root directory.
2. Store modification suggestions, custom rules, or evolved logic there.
3. This ensures that your custom "evolutions" are preserved even if the base `SKILL.md` is replaced during an upgrade.
