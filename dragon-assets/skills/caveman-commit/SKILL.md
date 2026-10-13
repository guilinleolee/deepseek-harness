---
license: UNKNOWN
name: caveman-commit
description: |
github_repo: JuliusBrussee/caveman
github_hash: 84cc3c14fa1e10182adaced856e003406ccd250d
last_updated: 2026-04-25
source_type: derived
version: 1.0.0
触发词: caveman commit, 极简提交, 压缩commit, terse commit。
来源: JuliusBrussee/caveman (13,252 ⭐), MIT License。
author: github/JuliusBrussee
adapted-by: Claude Code (天龙引擎 V8.90)
date: 2026-04-11
allowed-tools: 
triggers: ["caveman commit", "Caveman Commit — 超压缩提交规范"]
---

# Caveman Commit — 超压缩提交规范

## 描述

将 commit message 压缩为 caveman-speak 风格，主体 ≤50 字符，基于 Conventional Commits 规范。

## 格式

```
<type>(<scope>): <verb> <object>

# type: feat | fix | docs | style | refactor | test | chore | perf | ci | build
# scope: 模块/文件/功能 (可选)
# verb: add | remove | update | fix | refactor | improve | enable | disable
# object: 目标
```

## 规则

1. **主体 ≤50 字符**（含 type 和 scope）
2. **用 why 不用 what**：commit 说明为什么改，不说明改了什么
   ```
   # ✅ why
   feat(auth): enable token refresh for mobile clients

   # ❌ what
   feat(auth): added refresh_token field to auth response
   ```
3. **祈使语气**：commit message 是给未来自己看的命令
4. **正文仅在必要时添加**：body 仅在 why 不明显时使用
5. **Breaking Changes 必须有 body**

## 类型速查

| type | 含义 | 示例 |
|------|------|------|
| feat | 新功能 | `feat(api): add GET /users/:id/profile` |
| fix | Bug修复 | `fix(auth): null guard on token expiry` |
| docs | 文档 | `docs(readme): update install steps` |
| style | 格式 | `style(imports): alphabetical sort` |
| refactor | 重构 | `refactor(db): extract connection pool` |
| test | 测试 | `test(api): add happy path for /users` |
| chore | 构建/工具 | `chore(deps): upgrade express to 5.x` |
| perf | 性能 | `perf(query): add index on user_id` |

## 天龙引擎集成

### 08发布师标准

`caveman-commit` 作为 `08发布师` 的标准 commit 输出格式。

## 来源与许可

- 项目: [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman)
- Stars: 13,252 | License: MIT
- 天龙引擎 V8.90 集成
