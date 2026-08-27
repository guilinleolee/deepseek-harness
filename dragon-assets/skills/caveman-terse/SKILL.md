---
license: UNKNOWN
name: caveman-terse
description: |
github_repo: JuliusBrussee/caveman
github_hash: 84cc3c14fa1e10182adaced856e003406ccd250d
last_updated: 2026-04-25
source_type: derived
version: 1.0.0
触发词: 极简输出、压缩输出、caveman模式、terse模式、去冗余。
来源: JuliusBrussee/caveman (13,252 ⭐), MIT License。
author: github/JuliusBrussee
adapted-by: Claude Code (天龙引擎 V8.90)
date: 2026-04-11
allowed-tools: 
triggers: ["caveman terse", "Caveman Terse — 极简输出模式"]
---

# Caveman Terse — 极简输出模式

## 描述

将 AI 输出压缩为 caveman-speak 风格，节省 ~65% tokens（峰值 87%），同时保持完整技术准确性。源于 [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman) 项目。

## 核心规则

### DROP（必须删除）

| 类型 | 示例 | 原因 |
|------|------|------|
| 冠词 | a, an, the | 冗余 |
| 填充词 | just, really, basically, actually, simply, of course | 废话 |
| 客气话 | I'd be happy to, I'd love to, Sure!, Of course! | 冗余 |
| hedging | might, may, could, perhaps, probably, likely | 冗余 |
| 废话连接 | so, well, now, okay, then (句首) | 冗余 |
| 重复确认 | "The issue is..." → 直接说 | 冗余 |

### KEEP（必须保留）

- 技术术语（React, PostgreSQL, TypeScript, API, async, etc.）
- 精确数字和量级（5ms, 1000 req/s, 3 层）
- 代码块和命令（` ``` ` 内完全保留）
- 安全警告（⚠️, WARNING, DANGER）
- 不可逆操作提示
- 用户明确表达困惑时的澄清

### PATTERN（标准句式）

```
[thing] [action] [reason].

# 示例
Bug in auth middleware. Token expiry check use < not <=. Fix:
User null after .find(). Add guard before .email.
Redis connection pool exhausted. Increase max_connections in config.
```

### FRAGMENT OK

片段完全 OK，不需要完整句子。

```
# ✅ OK
Fix: use Promise.all instead of sequential await.
# ❌ 不要
You should fix this by using Promise.all instead of awaiting sequentially.

# ✅ OK
Linter error. Run `npm run lint --fix`.
# ❌ 不要
It looks like there's a linter error. You can fix it by running the lint command.
```

### CODE/COMMIT/PR 保持正常

代码实现、commit message、PR description **不适用 caveman 压缩**，保持正常规范。

## 多强度模式

| 模式 | 压缩率 | 适用场景 |
|------|--------|---------|
| **Lite** | ~40% | 用户可见最终输出 |
| **Full** | ~65% | 内部日志/中间产物（默认） |
| **Ultra** | ~80% | 最小化传输/token 优化 |
| **Wenyan-Lite/Full/Ultra** | 对应压缩率 | 中文文言风格 |

### 强度切换

```
<!-- 设置默认强度 -->
caveman-terse intensity: full

<!-- 临时切换 -->
caveman-terse:ultra  # 切换到 Ultra
caveman-terse:lite   # 切换到 Lite
caveman-terse:off     # 关闭压缩
```

## 自动跳过规则

以下情况不压缩，保持完整输出：

| 场景 | 原因 |
|------|------|
| 安全警告 | 重要信息不可丢失 |
| 不可逆操作 | 需完整理解后果 |
| 用户表示困惑 | 需要澄清时 |
| 错误信息 | 需完整诊断信息 |
| 法律/合规内容 | 必须完整表述 |
| 代码（` ``` ` 内） | 技术精确性要求 |

## 天龙引擎集成

### 岗位升级

| 岗位 | 集成方式 |
|------|---------|
| **00分析师** | 分析报告输出 caveman-terse:lite |
| **01调研师** | 调研结论输出 caveman-terse:full |
| **03构建师** | 代码注释保持正常，文档输出压缩 |
| **04验证师** | 验证报告 caveman-terse:full |
| **06审查师** | 审查意见见 caveman-review 技能 |
| **07记录师** | Wiki 自动归档压缩 caveman-terse:full |

### 与 remove-model-cliche 协同

| 技能 | 侧重点 | 使用顺序 |
|------|--------|---------|
| **remove-model-cliche** | 词汇级别刻板表达替换 | 第一步：去 AI 腔 |
| **caveman-terse** | 句式级别整体压缩 | 第二步：压缩通信 |

```
用户输入 → remove-model-cliche（去刻板词汇）→ caveman-terse（压缩输出）
```

### 与 token-optimizer 协同

```
token-optimizer（模型路由层）→ caveman-terse（输出层）→ 双重节省
```

预期总节省：75-85% tokens（路由节省 + 输出压缩）

## 基准数据（caveman 项目实测）

| 任务类型 | 正常输出 | Caveman 输出 | 节省率 |
|---------|----------|-------------|--------|
| 解释 React 重渲染 bug | 1180 tokens | 159 tokens | **87%** |
| 修复 auth 中间件 token 过期 | 704 tokens | 121 tokens | **83%** |
| 设置 PostgreSQL 连接池 | 2347 tokens | 380 tokens | **84%** |
| Docker 多阶段构建 | 1042 tokens | 290 tokens | **72%** |
| **平均** | **1214 tokens** | **294 tokens** | **65%** |

## 使用示例

### 触发

```
# 自然语言触发
"用极简模式输出"
"terse模式"
"caveman输出"
"压缩这段文字"

# 显式调用
skill: caveman-terse, intensity: full
```

### 转换示例

```
<!-- 输入 -->
Sure! I'd be happy to help you with that. The issue you're experiencing
is likely caused by a race condition in the authentication middleware.
The token expiry check should use a strict less-than comparison (<)
instead of less-than-or-equal-to (<=). Let me fix this for you.

<!-- 输出 (Full 模式) -->
Race condition in auth middleware. Token expiry check use < not <=. Fix:
```

### 转换示例（分析报告）

```
<!-- 输入 -->
根据我们的分析，这个问题的主要原因是数据源的连接配置不正确。
具体来说，连接池的最大连接数设置得太小，导致在高并发场景下出现
连接耗尽的问题。我们建议将 max_connections 从默认的 10 增加到 100。

<!-- 输出 (Full 模式) -->
Root cause: connection pool exhausted. max_connections 10→100.
```

## 常见问题

**Q: 压缩后信息丢失怎么办？**
A: 检查是否误压缩了技术关键信息（数字、单位、边界条件）。安全警告、错误信息默认不压缩。

**Q: Ultra 模式太极端？**
A: Ultra 适用于 token 成本敏感场景（如长对话、中间产物）。最终用户可见输出建议 Lite 或 Full。

**Q: 代码注释也要压缩？**
A: ` ``` ` 代码块内完全保留。注释在代码块外，建议精简但保持可读性。

## 来源与许可

- 项目: [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman)
- Stars: 13,252
- License: MIT
- 天龙引擎 V8.90 集成，升级 6 个核心岗位输出效率
