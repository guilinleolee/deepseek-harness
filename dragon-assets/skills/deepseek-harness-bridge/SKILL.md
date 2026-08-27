---
name: deepseek-harness-bridge
description: |
  借鉴 deepseek-ai/deepseek-harness V0.x（MIT · Copyright (c) 2026 DeepSeek · 196,376⭐ · DSH 官方主仓 · "Everything is a Plugin"）的 5 类核心设计 + 自研 V1.0。
  借鉴清单：① DSH 官方主仓架构（6 个 workspace 子目录）② "Everything is a Plugin" 5 原则 ③ cordis.patch.yml 协议 ④ @deepseek-ai/* 7 个 peer dependencies ⑤ 6 个 example plugin 借鉴模板（天龙 stage 41-49 已集成生态）。
  Stage 50.1 借鉴档 · 3 重 blocker（108.9 MB 巨型 + native/landlock-run + vendor + 自定义 scripts）。
metadata:
  version: "1.0.0"
  date: "2026-08-26"
  license: MIT
  author: 天龙引擎 · Stage 50.1
  upstream_borrowing:
    - deepseek-ai/deepseek-harness (MIT · 196,376⭐ · 2026)
  integration_stage: 50.1
  integration_mode: "借鉴档（3 重 blocker：巨型 + native/landlock-run + vendor + 自定义 scripts）"
  triggers:
    - "deepseek-harness"
    - "DSH 官方主仓"
    - "Everything is a Plugin"
    - "@deepseek-ai peer"
    - "cordis patch"
    - "DSH 主仓架构"
---

# deepseek-harness-bridge · V1.0（借鉴档 · 轻量）

> **TL;DR**：借鉴 [deepseek-ai/deepseek-harness](https://github.com/deepseek-ai/deepseek-harness)（**MIT ✅** · **DSH 官方主仓 · 196,376⭐** · "Everything is a Plugin"）的 **5 类核心设计** + **天龙自研 V1.0**。**天龙首次触碰 DSH 官方主仓**。**11/11 unittest PASS**（拆 6 大类）。

---

## L0: 一句话描述 (≤15字)

DSH 官方主仓借鉴。

---

## L1: 使用场景

当用户需要：
- 设计 DSH 插件 manifest（id/name/version/description/vendor 5 字段必填）
- 写 cordis.patch.yml 挂载插件到 DSH bundle
- 检查 package.json 的 7 个 @deepseek-ai/* peer dependencies
- 借鉴 DSH 官方 monorepo workspace 模板
- 用 6 个 example plugin 借鉴模板（天龙 stage 41-49 已集成生态）

---

## L2: 5 类借鉴

### 2.1 DSH 官方主仓架构（6 workspace）
```python
DSH_OFFICIAL_WORKSPACES = [
    "vendor/*",                    # @deepseek-ai/* 主仓包
    "packages/*/*",                # host / client / mcp 等
    "native/landlock-run",         # Linux sandbox
    "native/landlock-run/packages/*",
    "apps/*",                      # 终端应用
    "website",
]
```

### 2.2 "Everything is a Plugin" 5 原则
```python
EVERYTHING_IS_A_PLUGIN_PRINCIPLES = [
    "每个工具都是 Plugin（cordis + DSH bundle 标准）",
    "Plugin 通过 manifest 声明 metadata",
    "Plugin 与 host 解耦（通过 cordis Service interface）",
    "Plugin 失败不影响 host（graceful degradation）",
    "Plugin 可热插拔（runtime load/unload）",
]
```

### 2.3 cordis.patch.yml 协议
- `parse_cordis_patch(yaml)` 解析 + `validate_cordis_patch(patch)` 校验

### 2.4 @deepseek-ai/* 7 个 peer dependencies 校验
```python
DEEPSEEK_AI_PEERS = [
    "@deepseek-ai/cordis",
    "@deepseek-ai/dsh-cmdline",
    "@deepseek-ai/dsh-invariants",
    "@deepseek-ai/dsh-llm",
    "@deepseek-ai/dsh-llm-retry",
    "@deepseek-ai/dsh-session",
    "@deepseek-ai/dsh-web-frontend",
]
```

### 2.5 6 个 example plugin 借鉴模板（天龙 stage 41-49 已集成）
| id | 借鉴源 | stage |
|---|---|---|
| tui-bridge | ccch1mneyyy/dsh-TUI | 48 |
| peak-gate | f20880479-lab/dsh-peak-gate | 46 |
| balance-meter | Ghost011118/dsh-balance-meter | 45.1 |
| univer-office | dream-num/dsh-univer-office | 47 |
| agent-teams | NanmiCoder/dsh-agent-teams | 43 |
| eval-bridge | hccccc01333/dsh-eval | 45 |

---

## L3: 安装（不镜像真源 → 仅 bridge）

```bash
# 1. 装本 skill（天龙自有，已落 dragon-engine/skills/deepseek-harness-bridge/）
# 2. 验证 11 unittest PASS
python -m unittest tests/test_deepseek_harness_bridge.py -v
```

---

## L4: 触发词（10 类）

```
deepseek-harness, DSH 官方主仓, Everything is a Plugin, cordis patch
@deepseek-ai peer, monorepo workspace, DSH bundle
```

---

## L5: 下游协同

| 下游 | 协同 |
|---|---|
| **stage 47 dsh-univer-office-bridge** | Apache 借鉴档模式参考 |
| **stage 48 dsh-tui-bridge** | 6 example plugin 模板之一 |
| **stage 49.1 dsh-desktop-bridge** | 借鉴档模式参考 |
| **stage 49.2 memsearch-bridge** | 借鉴档模式参考 |
| **stage 49.4 open-design-bridge** | Apache 重量档借鉴档 |
| **40-01 mcp-orchestrator** | DSH plugin 路由基础 |
| **所有 stage 41-49 已集成生态** | 6 个 example plugin 直接借鉴 |

---

## L6: DON'T 护栏（5 条）

- ❌ **不要**镜像 deepseek-harness 真源（108.9 MB 巨型 · 3 重 blocker）
- ❌ **不要**实跑 native/landlock-run（Windows 跑不了）
- ❌ **不要**修改 vendor/* 子仓（DSH 主仓 sync 模式）
- ❌ **不要**省 cordis patch 中 `borrowed: true` 标注
- ❌ **不要**让 monorepo 写出 .yarnrc.yml 之外的多 packageManager 方案（避免与上游冲突）

---

## L7: 验证矩阵

| # | 必检项 | 期望 | 状态 |
|---|---|---|---|
| 1 | cordis patch 解析（patch: + - insert:）| 5 entries | ✅ |
| 2 | cordis patch 校验（id 必填）| 错误捕获 | ✅ |
| 3 | @deepseek-ai/* peer 检查（7 个）| matched/missing | ✅ |
| 4 | workspace 模板（6 个）| vendor/* + apps/* | ✅ |
| 5 | 5 原则完整 | 全列 | ✅ |
| 6 | 6 example plugin 映射 stage 41-49 | 全对 | ✅ |
| 7 | 11/11 unittest PASS | 6 大类 | ✅ |

---

## L8: 参考链接

- **借鉴源**：https://github.com/deepseek-ai/deepseek-harness · MIT
- **LICENSE verbatim**：https://raw.githubusercontent.com/deepseek-ai/deepseek-harness/master/LICENSE（1,065 B / 21 行 / "Copyright (c) 2026 DeepSeek" / MIT）
- **上游 homepage**：https://deepseek.com/harness
- **DSH 协议治理基线**：[`docs/dsh-ecosystem-license-policy.md`](../../../docs/dsh-ecosystem-license-policy.md)
- **Stage 50 盘点**：[`memory/stage-50-candidates-evaluation.md`](../../../memory/stage-50-candidates-evaluation.md)
- **Stage 50.1 主题文件**：[`memory/stage-501-deepseek-harness.md`](../../../memory/stage-501-deepseek-harness.md)
