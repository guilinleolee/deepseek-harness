---
license: UNKNOWN
name: agents-list
version: 1.0.0
description: |
  agents
author: 天龙引擎团队
created: 2026-02-26
category: development

triggers:
  - "用户提到「agents-list」时"
---

# agents

查看天龙引擎所有可用代理列表

## Usage

```
/agents [部门]
```

## Examples

```
/agents
/agents 核心九部
/agents 技术中心
```

## What it does

显示所有已注册的代理，按部门分组，包括：
- 代理ID和名称
- 所属部门
- 核心能力

## Output

```
╔══════════════════════════════════════════════════════════╗
║          🐉 天龙引擎指挥官李依依（一一）                      ║
╠══════════════════════════════════════════════════════════╣
║  📋 可用代理列表                                           ║
║    总数：14                                                ║
║                                                           ║
║  🏢️  核心九部                                              ║
║    1. 00分析师 - 需求分析,问题解构,可行性评估...              ║
║    2. 01调研师 - 考古摸底,代码考古,依赖分析...                ║
║    ...
╚══════════════════════════════════════════════════════════╝
```

## Related commands

- `/agent-info <id>` - 查看代理详细信息
- `/command` - 智能推荐代理
- `/status` - 查看系统状态
