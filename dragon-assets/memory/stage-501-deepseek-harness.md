# Stage 50.1 · deepseek-harness-bridge V1.0 · 主题文件

> **阶段**：天龙引擎 · **stage 50.1**（**借鉴档 · 轻量 · MIT · DSH 官方主仓**）
> **日期**：2026-08-26
> **集成度**：⭐ 战略级 — **天龙首次触碰 DSH 官方主仓**（196,376⭐）
> **入口文件**：[`skills/deepseek-harness-bridge/SKILL.md`](../skills/deepseek-harness-bridge/SKILL.md)

---

## 一、TL;DR

> 借鉴 [deepseek-ai/deepseek-harness](https://github.com/deepseek-ai/deepseek-harness) V0.x（**MIT ✅** · "Copyright (c) 2026 DeepSeek" · **196,376⭐ / 22,270 🍴 · DSH 生态最大** · 108.9 MB · "Everything is a Plugin"）的 **5 类核心设计** + **天龙自研 V1.0**。遇到 **3 重 blocker**（108.9 MB 巨型 + native/landlock-run Linux-only + vendor + 自定义 scripts），借鉴档是唯一可行路径。累计 PASS **893 → 898**（+5 net · 11/11 自研 unittest 拆 6 大类）。

---

## 二、触发源（一手）

| 字段 | 值 |
|---|---|
| **上游仓库** | https://github.com/deepseek-ai/deepseek-harness |
| **作者** | **deepseek-ai**（GitHub 148330874 · **DeepSeek 官方 Organization**）|
| **协议** | **MIT ✅**（LICENSE 1,065 B verbatim · "Copyright (c) 2026 DeepSeek" · SPDX `MIT`）|
| **★ / 🍴** | **196,376⭐ / 22,270 🍴**（**DSH 生态最大**）|
| **size** | 108.9 MB · 巨型 |
| **language** | TypeScript（86 个子包）|
| **topics** | ai-agents / cordis / dsh / dsh-plugin |
| **default_branch** | `master` |
| **创建** | 2026-08-13T11:56:32Z（13 天前）|
| **末 push** | 2026-08-21T12:35:08Z |
| **homepage** | https://deepseek.com/harness |
| **npm name** | `@deepseek-ai/dsh-root@0.1.1-rc.2`（root workspace）|
| **engines** | node ^22.19.0 || >=24.0.0 |
| **packageManager** | pnpm@11.7.0 |
| **workspaces** | `vendor/*` `packages/*/*` `native/landlock-run` `apps/*` `website` |
| **核心哲学** | "Everything is a Plugin" |
| **意义** | **天龙首次触碰 DSH 官方主仓** · 借鉴价值最高 |

---

## 三、D3 工程实证 · ⚠️ 撞墙（3 重 blocker）

| # | Blocker | 应对 |
|---|---|---|
| 1 | **108.9 MB 巨型** | 借鉴档不实跑 `pnpm install` |
| 2 | **native/landlock-run**（Linux 内核 sandbox）| 借鉴档不在 Windows 跑 |
| 3 | **vendor + 自定义 scripts**（scripts/*.ts 用 tsx 跑）| 借鉴档用 Python 自研 |

---

## 四、5 类借鉴（DSH 官方主仓 → deepseek-harness-bridge V1.0）

### 4.1 DSH 官方主仓架构（6 workspace）

```python
DSH_OFFICIAL_WORKSPACES = [
    "vendor/*",                    # @deepseek-ai/* 主仓包（peer 依赖）
    "packages/*/*",                # host / client / mcp 等
    "native/landlock-run",         # Linux 内核 sandbox（Windows 不可用）
    "native/landlock-run/packages/*",
    "apps/*",                      # 终端应用（CLI / TUI / IDE）
    "website",                     # 官方文档站
]
```

### 4.2 "Everything is a Plugin" 5 原则

```python
EVERYTHING_IS_A_PLUGIN_PRINCIPLES = [
    "每个工具都是 Plugin（cordis + DSH bundle 标准）",
    "Plugin 通过 manifest 声明 metadata（id/name/version/entry）",
    "Plugin 与 host 解耦（通过 cordis Service interface）",
    "Plugin 失败不影响 host（graceful degradation）",
    "Plugin 可热插拔（runtime load/unload）",
]
```

### 4.3 cordis.patch.yml 协议（借鉴 stage 47/48）

```python
def parse_cordis_patch(yaml_text: str) -> CordisPatch:
    if "patch:" not in yaml_text:
        raise ValueError("missing 'patch:' key in cordis.patch.yml")
    # 提取 - insert: 块
```

### 4.4 @deepseek-ai/* 7 个 peer dependencies 校验

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

### 4.5 6 个 example plugin 借鉴模板（天龙 stage 41-49 已集成生态）

| id | 借鉴源 | stage |
|---|---|---|
| **tui-bridge** | ccch1mneyyy/dsh-TUI | 48 |
| **peak-gate** | f20880479-lab/dsh-peak-gate | 46 |
| **balance-meter** | Ghost011118/dsh-balance-meter | 45.1 |
| **univer-office** | dream-num/dsh-univer-office | 47 |
| **agent-teams** | NanmiCoder/dsh-agent-teams | 43 |
| **eval-bridge** | hccccc01333/dsh-eval | 45 |

---

## 五、11/11 自研 unittest PASS 拆 6 大类

```
✓ TestCordisPatch       (3)  # parse / missing / validate
✓ TestPeers             (2)  # matched / missing
✓ TestWorkspaces        (2)  # default / to_dict
✓ TestPrinciples       (2)  # count / not_empty
✓ TestExamplePlugins    (1)  # six_plugins
✓ TestEndToEnd          (1)  # workflow
                          11/11 ✓ 0.001s
```

---

## 六、5 CLI 自研工具（deepseek_harness_bridge.py）

```bash
$ deepseek_harness_bridge.py parse-patch --yaml "patch: ..."
$ deepseek_harness_bridge.py check-peers --package-json '{...}'
$ deepseek_harness_bridge.py list-workspaces    # → 6 个 workspace glob
$ deepseek_harness_bridge.py check-principles   # → 5 原则
$ deepseek_harness_bridge.py example-plugins    # → 6 个 example 借鉴模板
```

---

## 七、累计 PASS 锁定

```
893 (Stage 50 累计)
   +5 ─► 898   deepseek_harness_bridge.py 11/11 自研 unittest PASS
                  (上游 100+ vitest 计入上游库不双计)
                          │
                          ─► 898 locked
```

---

## 八、跳转入口

- **真源 SKILL.md**：[`skills/deepseek-harness-bridge/SKILL.md`](../skills/deepseek-harness-bridge/SKILL.md)
- **DSH 协议治理基线**：[`docs/dsh-ecosystem-license-policy.md`](../docs/dsh-ecosystem-license-policy.md)
- **Stage 50 盘点**：[`memory/stage-50-candidates-evaluation.md`](stage-50-candidates-evaluation.md)

---

> **下次同步点**：用户在 DSH 真机克隆 deepseek-harness 后跑 `pnpm install` + `pnpm test`，验证 6 个 example plugin 协同。
