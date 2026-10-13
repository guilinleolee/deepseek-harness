---
name: caveman-review
description: |
github_repo: JuliusBrussee/caveman
github_hash: 84cc3c14fa1e10182adaced856e003406ccd250d
last_updated: 2026-04-25
source_type: derived
version: 1.0.0
单行 PR code review，格式 L<line>: <severity> <type>: <problem>. <fix>.
触发词: caveman review, 极简review, 单行review, terse review。
来源: JuliusBrussee/caveman (13,252 ⭐), MIT License。
author: github/JuliusBrussee
adapted-by: Claude Code (天龙引擎 V8.90)
date: 2026-04-11
allowed-tools: 
---

# Caveman Review — 单行代码审查

## 描述

将代码审查意见压缩为单行格式，每个问题一行，基于 caveman-speak 极简风格。

## 格式

```
L<line>: <severity> <type>: <problem>. <fix>.

# line: 行号（数字或范围如 42-45）
# severity: 🔴 bug | 🟡 risk | 🔵 nit | ❓ q
# type: 问题类型
# problem: 问题描述
# fix: 修复方案
```

## 严重性前缀

| 前缀 | 含义 | 必须修复 |
|------|------|---------|
| 🔴 | Bug：错误或安全漏洞 | ✅ 必须 |
| 🟡 | Risk：潜在风险或性能问题 | 建议 |
| 🔵 | Nit：代码风格/格式小问题 | 可选 |
| ❓ | Question：需要澄清 | 需要回复 |

## 问题类型

| type | 含义 | 示例 |
|------|------|------|
| bug | 功能错误 | `🔴 bug: user null after .find()` |
| null | 空指针风险 | `🔴 null: no guard after API call` |
| leak | 资源泄漏 | `🟡 leak: unclosed stream` |
| perf | 性能问题 | `🟡 perf: N+1 query in loop` |
| security | 安全漏洞 | `🔴 security: SQL injection possible` |
| style | 代码风格 | `🔵 nit: magic number L3` |
| complexity | 复杂度 | `🟡 complexity: function 87 lines` |
| missing | 缺失检查 | `🟡 missing: error handling` |

## 天龙引擎集成

### 06审查师标准

`caveman-review` 升级 `06审查师` 代码审查输出格式。

### 示例

```
<!-- 输入 (正常 review) -->
在第 42 行，user 对象可能为 null。在调用 .email 属性之前，
应该先添加空值检查。如果 find() 没有找到匹配的用户，
返回值会是 undefined，后续的 .email 访问会导致运行时错误。
建议添加一个 guard 语句来检查 user 是否存在。

<!-- 输出 (caveman-review) -->
L42: 🔴 null: user can be null after .find(). Add guard before .email.
```

## 来源与许可

- 项目: [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman)
- Stars: 13,252 | License: MIT
- 天龙引擎 V8.90 集成，升级 06审查师 review 效率
