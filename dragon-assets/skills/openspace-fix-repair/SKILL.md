---
license: UNKNOWN
triggers: ["openspace fix repair", "OpenSpace Fix Repair"]
---
# OpenSpace Fix Repair

## Overview

OpenSpace Fix Repair is an autonomous debugging and self-healing system integrated with OpenSpace Cloud's 165 self-evolving skills. It provides intelligent error detection, root cause analysis, and automatic fix application for天龙引擎 skills and workflows.

## Core Features

### 1. Autonomous Error Detection

- Real-time error monitoring with pattern recognition
- Classification of 7 error categories (API, dependency, permission, syntax, test, build, git)
- Severity assessment and risk evaluation
- Automatic error documentation

### 2. Self-Healing Capabilities

| Error Type | Auto-Fix Strategy |
|------------|-------------------|
| **API Errors** | Rate limit backoff, retry with exponential delay |
| **Dependency Errors** | Install missing packages, version resolution |
| **Permission Errors** | chmod/chown adjustments, sudo escalation |
| **Syntax Errors** | AST-based auto-correction |
| **Test Failures** | Intelligent test isolation, flaky test detection |
| **Build Errors** | Incremental build, cache clearing |
| **Git Errors** | Conflict resolution, branch management |

### 3. OpenSpace Integration

Connects with OpenSpace Cloud's skill ecosystem for:
- Community-driven fix patterns
- Skill-specific debugging knowledge
- Cross-skill error correlation
- Continuous improvement from community fixes

### 4. Intelligent Recovery Protocol

```
┌─────────────────────────────────────────────────────────────┐
│ Error Detection → Classification → Risk Assessment         │
│        ↓                                                    │
│ Fix Planning → Validation → Application → Verification    │
│        ↓                                                    │
│ Success? → Yes → Document → Update OpenSpace             │
│        ↓ No                                               │
│ Escalate → Retry (max 3) → Report to Community           │
└─────────────────────────────────────────────────────────────┘
```

## Usage

```bash
# Run with auto-fix enabled
openspace-fix --skill <skill-name> --auto-fix

# Dry-run mode (preview fixes without applying)
openspace-fix --skill <skill-name> --dry-run

# Interactive mode (approve each fix)
openspace-fix --skill <skill-name> --interactive

# Watch mode (continuous monitoring)
openspace-fix --skill <skill-name> --watch

# Import community fix patterns
openspace-fix --sync-patterns

# Report fix to community
openspace-fix --report-fix --fix-id <id>
```

## Error Classification System

### 7 Primary Categories

| Category | Sub-patterns | Auto-fixable |
|----------|-------------|--------------|
| **API Errors** | rate_limit, quota_exceeded, timeout, auth_failed | Yes |
| **Dependency Errors** | module_not_found, import_error, version_conflict | Yes |
| **Permission Errors** | eacces, eperm, permission_denied | Partial |
| **Syntax Errors** | syntax_error, unexpected_token, indentation_error | Yes |
| **Test Failures** | assertion_failed, test_failed, flaky_test | Yes |
| **Build Errors** | compilation_error, link_error, type_error | Partial |
| **Git Errors** | merge_conflict, not_a_repo, detached_head | Partial |

### Severity Levels

| Level | Trigger | Action |
|-------|---------|--------|
| **Critical** | Data loss risk, security breach | Immediate stop + alert |
| **High** | Core functionality broken | Auto-fix with backup |
| **Medium** | Non-critical feature impaired | Auto-fix + notify |
| **Low** | Cosmetic/UX issue | User approval required |
| **Warning** | Potential future issue | Document + monitor |

## Integration with 天龙Hooks

This skill integrates with天龙引擎's hook system:

```javascript
// hooks/nine-dragons-log-watcher.js integration
// Auto-trigger fix-repair on detected errors
{
  "trigger": "postToolUse",
  "skill": "openspace-fix-repair",
  "on_error": true,
  "auto_fix_threshold": "medium"  // auto-fix medium and below
}
```

## Token Efficiency

OpenSpace reports **4.2x performance improvement** through:
- Early error detection (before escalation)
- Smart retry with exponential backoff
- Pattern-based caching of known fixes
- Minimal fix application (only changed lines)

## File Structure

```
openspace-fix-repair/
├── SKILL.md                    # This file
├── scripts/
│   └── auto_fix.py             # Core auto-fix engine
└── patterns/
    └── fix_patterns.json       # Community fix patterns
```

## Fix Pattern Schema

```json
{
  "pattern_id": "py_import_error_001",
  "error_pattern": "ModuleNotFoundError: No module named '(\\w+)'",
  "error_category": "dependency",
  "fix_template": "pip install {module_name}",
  "validation": "python -c 'import {module_name}'",
  "success_rate": 0.95,
  "author": "community",
  "contributed_by": "open-space-cloud",
  "times_applied": 1234
}
```

## Examples

### Basic Error Fix

```bash
# Detect and fix an import error
$ openspace-fix --skill python-skill --auto-fix

[ERROR] Detected: ModuleNotFoundError: No module named 'requests'
[CLASS] dependency.import_error (confidence: 0.92)
[FIX]  → pip install requests
[VALIDATING] ...
[SUCCESS] Fix applied in 2.3s
[DOCUMENTED] Added to fix_patterns.json
```

### Community Pattern Sync

```bash
# Sync latest fix patterns from OpenSpace
$ openspace-fix --sync-patterns

[SYNC] Fetching 165 self-evolving skills patterns...
[SYNC] Downloaded 342 new fix patterns
[SYNC] Updated fix_patterns.json
[SYNC] Pattern success rates recalculated
```

### Dry-Run Preview

```bash
# Preview fixes without applying
$ openspace-fix --skill my-skill --dry-run

[ERROR] Detected: KeyError: 'user_id'
[CLASS] api.data_error (confidence: 0.88)
[FIX PREVIEW]
  File: scripts/api_client.py:142
  Current: data['user_id']
  Proposed: data.get('user_id', default=None)
[APPLY? skipped (dry-run)]
```

## 与天龙现有调试系统协同

| Feature | 天龙System | openspace-fix-repair |
|---------|-----------|---------------------|
| Error Detection | nine-dragons-log-watcher | OpenSpace patterns |
| Root Cause | Manual | Pattern matching |
| Fix Application | Manual | Autonomous |
| Learning | lessons.md | Community patterns |
| Recovery | Manual retry | Smart retry protocol |

## OpenSpace 165 Skills Integration

The 165 OpenSpace self-evolving skills provide:
- Domain-specific fix patterns
- Skill relationship mapping
- Cross-skill error correlation
- Community-validated solutions

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-04-02 | Initial release with 7 error categories |
