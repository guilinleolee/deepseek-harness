---
type: lesson
title: "[log-watcher] dependency: Cannot find module"
tags: [dragon-engine, log-watcher, critical, dependency, auto-extracted]
created: 2026-08-07
updated: 2026-08-07
source: log-watcher
confidence: 0.95
agent: log-watcher
heat: 0.7
last_ref_date: 2026-08-24
mneme_schema: v12.0
---


# [log-watcher] dependency: Cannot find module

**严重级**: P0-严重 (critical)
**类型**: dependency
**模式**: /cannot find module/i
**触发**: Cannot find module
**可恢复**: 否

**错误上下文**:
```
Error: Cannot find module 'B2-test-dep'
Require stack
```

**建议**:

🔧 依赖错误 - 需要手动干预

建议操作：
1. 运行 npm install 或 yarn install
2. 检查 package.json 是否存在
3. 检查node_modules是否完整
4. 必要时删除 node_modules 和 package-lock.json 后重新安装

命令：npm install
      

**来源 Hook**: nine-dragons-log-watcher
**节流窗口**: 5 分钟

