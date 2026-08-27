---
license: UNKNOWN
name: systematic-debugging
version: 2.0.0
description: |
系统化调试方法论 V2.0 - 整合 GSD-2 debug-like-expert + omnidebug-autopilot

包含六阶段调试流程、自动堆栈检测、决策门控机制。支持全栈、全语言、全框架。

核心理念：先理解问题，再动手修复。每阶段结束触发Decision Gate。

触发词：调试、debug、排查问题、fix bug、find root cause
author: 天龙引擎团队 (整合 GSD-2 + omnidebug)
created: 2026-02-26
updated: 2026-03-25
category: development

triggers:
  - "用户说「帮我调试」时"
  - "遇到错误需要排查时"
  - "测试失败需要分析时"
  - "debug this"
  - "fix this bug"
  - "why is this failing"
  - "find root cause"

integrates:
  - omnidebug-autopilot
  - decision-gate
---

# Systematic Debugging V2.0

> 整合自：GSD-2 debug-like-expert + omnidebug-autopilot + 天龙引擎原有方法论

## Core Principle

**NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST.**

Never apply symptom-focused patches that mask underlying problems. Understand WHY something fails before attempting to fix it.

## Decision Gate Integration ⭐ V2.0

每个阶段完成后触发Decision Gate，确保用户对调试流程有控制权：

| 阶段 | 完成后门控 | 用户选择 |
|------|-----------|---------|
| Triage | 分析完成门 | 继续修复/创建文档/深入探索/第二意见 |
| Root Cause | 分析完成门 | 立即修复/进一步验证/获取架构师意见 |
| Fix Strategy | 多路径选择门 | 选择修复方案 |
| Verification | 发布确认门 | 确认完成/运行额外测试 |

## The Six-Phase Framework ⭐ V2.0 (扩展自四阶段)

### Phase 1: Root Cause Investigation

Before touching any code:

1. **Read error messages thoroughly** - Every word matters
2. **Reproduce the issue consistently** - If you can't reproduce it, you can't verify a fix
3. **Examine recent changes** - What changed before this started failing?
4. **Gather diagnostic evidence** - Logs, stack traces, state dumps
5. **Trace data flow** - Follow the call chain to find where bad values originate

**Root Cause Tracing Technique:**
```
1. Observe the symptom - Where does the error manifest?
2. Find immediate cause - Which code directly produces the error?
3. Ask "What called this?" - Map the call chain upward
4. Keep tracing up - Follow invalid data backward through the stack
5. Find original trigger - Where did the problem actually start?
```

**Key principle:** Never fix problems solely where errors appear—always trace to the original trigger.

**⭐ V2.0 Evidence Collection (from omnidebug):**
```
Collect only relevant artifacts:
- Console and application logs
- Test output with stack traces
- Network failures and status codes
- Runtime metrics (latency, memory, CPU) when performance related
- Config/env differences between working and failing contexts
- Browser artifacts: Devtools console, HAR files, screenshots
```

**⭐ V2.0 Root Cause Chain:**
```
1. Symptom statement
2. Immediate fault location
3. Underlying mechanism
4. Trigger condition
5. Why safeguards missed it
```

### Phase 2: Pattern Analysis

1. **Locate working examples** - Find similar code that works correctly
2. **Compare implementations completely** - Don't just skim
3. **Identify differences** - What's different between working and broken?
4. **Understand dependencies** - What does this code depend on?

### Phase 3: Hypothesis and Testing

Apply the scientific method:

1. **Formulate ONE clear hypothesis** - "The error occurs because X"
2. **Design minimal test** - Change ONE variable at a time
3. **Predict the outcome** - What should happen if hypothesis is correct?
4. **Run the test** - Execute and observe
5. **Verify results** - Did it behave as predicted?
6. **Iterate or proceed** - Refine hypothesis if wrong, implement if right

### Phase 4: Implementation

1. **Create failing test case** - Captures the bug behavior
2. **Implement single fix** - Address root cause, not symptoms
3. **Verify test passes** - Confirms fix works
4. **Run full test suite** - Ensure no regressions
5. **If fix fails, STOP** - Re-evaluate hypothesis

**Critical rule:** If THREE or more fixes fail consecutively, STOP. This signals architectural problems requiring discussion, not more patches.

## Red Flags - Process Violations

Stop immediately if you catch yourself thinking:

- "Quick fix for now, investigate later"
- "One more fix attempt" (after multiple failures)
- "This should work" (without understanding why)
- "Let me just try..." (without hypothesis)
- "It works on my machine" (without investigating difference)

## Warning Signs of Deeper Problems

**Consecutive fixes revealing new problems in different areas** indicates architectural issues:

- Stop patching
- Document what you've found
- Discuss with team before proceeding
- Consider if the design needs rethinking

## Common Debugging Scenarios

### Test Failures

```
1. Read the FULL error message and stack trace
2. Identify which assertion failed and why
3. Check test setup - is the test environment correct?
4. Check test data - are mocks/fixtures correct?
5. Trace to the source of unexpected value
```

### Runtime Errors

```
1. Capture the full stack trace
2. Identify the line that throws
3. Check what values are undefined/null
4. Trace backward to find where bad value originated
5. Add validation at the source
```

### "It worked before"

```
1. Use git bisect to find the breaking commit
2. Compare the change with previous working version
3. Identify what assumption changed
4. Fix at the source of the assumption violation
```

### Intermittent Failures

```
1. Look for race conditions
2. Check for shared mutable state
3. Examine async operation ordering
4. Look for timing dependencies
5. Add deterministic waits or proper synchronization
```

## Debugging Checklist

Before claiming a bug is fixed:

- [ ] Root cause identified and documented
- [ ] Hypothesis formed and tested
- [ ] Fix addresses root cause, not symptoms
- [ ] Failing test created that reproduces bug
- [ ] Test now passes with fix
- [ ] Full test suite passes
- [ ] No "quick fix" rationalization used
- [ ] Fix is minimal and focused

## Success Metrics

Systematic debugging achieves ~95% first-time fix rate vs ~40% with ad-hoc approaches.

Signs you're doing it right:
- Fixes don't create new bugs
- You can explain WHY the bug occurred
- Similar bugs don't recur
- Code is better after the fix, not just "working"

## Integration with Other Skills

- **testing-patterns**: Create test that reproduces the bug before fixing

#### Evolution Pattern (Maintenance)

To preserve custom improvements when a core skill is upgraded, avoid editing `SKILL.md` directly for individual modifications. Instead:

1. Create or update an `evolution.json` file in the skill's root directory.
2. Store modification suggestions, custom rules, or evolved logic there.
3. This ensures that your custom "evolutions" are preserved even if the base `SKILL.md` is replaced during an upgrade.
