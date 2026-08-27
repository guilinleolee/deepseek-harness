---
name: stage-473-harnesskit-integration
description: stage 47.3 · RealZST/HarnessKit 借鉴档 V1.0 — Apache-2.0 ✅ · 414⭐ · 5 个月迭代 · 4 类方法论 + 10 unittest PASS
metadata:
  node_type: memory
  originSessionId: stage-473-harnesskit-20260826
  modified: 2026-08-26T16:00:00.000Z
heat: 0.7
last_ref_date: 2026-08-26
mneme_schema: v12.0
---

# stage 47.3 · RealZST/HarnessKit 借鉴档 V1.0

> **TL;DR**：上游 [RealZST/HarnessKit](https://github.com/RealZST/HarnessKit)（**Apache-2.0 ✅ · 414⭐ · 5 个月迭代 · 2026-08-18 末 push** · topics：ai-coding-agents / claude-code / codex / cursor / developer-tools / gemini-cli / skill-manager）按 stage 47 盘点边界 GO 结论 + stage 47.1/46 借鉴档模式一次性集成。本阶段交付：**11 字段 SKILL.md V1.0** + **4 类方法论自研实现** `harness_kit_bridge.py`（skill_manager / mcp_registry / hook_chain / config_sync / license_check 5 个子命令）+ **LICENSE verbatim 11,358 B** + **NOTICE 含 "Modified by dragon-engine / 2026-08-26"** + **10 unitest PASS**。累计 PASS **900 → 910**（+10 net）。

---

## 一、实拉元数据（2026-08-26 · GitHub REST API）

| 字段 | 值 |
|---|---|
| **仓库** | `RealZST/HarnessKit` |
| **协议** | **Apache-2.0 ✅** （LICENSE 11,358 B verbatim + SPDX 确认） |
| **Stars / Forks** | 414 / 35 |
| **language** | **Rust** |
| **创建** | **2026-03-27**（5 个月迭代 · 中等成熟度） |
| **末 push** | **2026-08-18**（8 天前） |
| **archived** | false |
| **topics** | `ai-coding-agents / claude-code / cli-tools / codex / cursor / developer-tools / gemini-cli / skill-manager` |
| **生态匹配** | ⭐⭐⭐⭐⭐ — `claude-code / codex / cursor / gemini-cli / skill-manager` 与天龙 DSL 完全同生态 |

> **边界 GO 关键**：HarnessKit 是 **Not just a skill manager**，是 **managed skills + MCP servers + plugins + hooks + CLIs + configs + memory & rules** 的统一管理层。与天龙 stage 14 agent-reach / stage 47.1 memos / stage 21 async-task-pattern 等适配。

---

## 二、4 类借鉴清单

| # | 上游 HarnessKit 设计 | 天龙自研落地 |
|---|---|---|
| ① | **Skill manager** (统一 frontmatter + enabled/disabled) | `skill_manager` 子命令: SKILL_KEYS_REQUIRED = {name, version, enabled} + semver 校验 |
| ② | **MCP registry** (transport + OAuth + status) | `mcp_registry` 子命令: MCP_TRANSPORT = {stdio, http, sse} + 强制 url 或 command |
| ③ | **Hook chain** (pre/post ToolUse) | `hook_chain` 子命令: HOOK_EVENTS (8 类) + DFS 循环检测 |
| ④ | **Config sync** (inventory × registry diff) | `config_sync` 子命令: added/removed/changed/same 四向 diff |

---

## 三、不做真源镜像的撞墙报告（D2 · 借鉴档模式）

| 选项 | 撞墙根因 | 选用 |
|---|---|---|
| git clone + cargo check | Rust workspace + tokio 全家 · 本机无 Cargo dep 安装 | ❌ 不选 |
| cargo new harnesskit-rs | 与天龙 Python 主仓不兼容 | ❌ 不选 |
| **借鉴档 + 自研 Python** | 零依赖（仅 Python 3 + PyYAML）+ 与 stage 47.1/46 节奏一致 | ✅ 选用 |

---

## 四、Apache-2.0 红线 12 项

- [x] LICENSE 11.4 KB（实拉 11,358 B）verbatim 落盘
- [x] NOTICE 加 "Modified by dragon-engine / 2026-08-26"
- [x] 不得用 "HarnessKit 官方" / "RealZST 官方" 字样（已在 SKILL.md DONTS 第 3 条）
- [x] 不写 .env / .netrc 任何产物
- [x] 不 cargo build（依赖 tokio 全家，已在 SKILL.md DONTS 第 2 条）
- [x] 不克隆 Rust workspace（已在 SKILL.md DONTS 第 1 条）
- [x] 借鉴档自研：5 CLI + 10 unittest
- [x] Apache-2.0 §4(a) 强化（LICENSE 落盘）
- [x] Apache-2.0 §4(d) NOTICE 强化
- [x] Apache-2.0 §6 Trademark 强化
- [x] 不踩 DSH harness 软链
- [x] 不 export inventory.json 原文件

---

## 五、5 CLI 子命令实测

```bash
$ python scripts/harness_kit_bridge.py skill_manager tests/fixtures/sample_inventory.json
[OK] 3/3 skills validated; 2 enabled
---EXIT: 0---

$ python scripts/harness_kit_bridge.py skill_manager tests/fixtures/bad_inventory.json
[FAIL] skills[0]: missing required keys ['version']
[FAIL] skills[1]: version 'invalid-version' not semver
--- 2 errors · EXIT: 1 ---

$ python scripts/harness_kit_bridge.py mcp_registry tests/fixtures/sample_mcp.yaml
[OK] 3/3 MCP servers validated; 2 enabled
---EXIT: 0---

$ python scripts/harness_kit_bridge.py hook_chain tests/fixtures/sample_hooks.json
[OK] 3 hooks validated, no cycle detected
---EXIT: 0---

$ python scripts/harness_kit_bridge.py hook_chain tests/fixtures/bad_hooks_cycle.json
[FAIL] hook chain has cycle (DFS detected)
---EXIT: 1 ---

$ python scripts/harness_kit_bridge.py config_sync \
    --local tests/fixtures/config_local.json \
    --registry tests/fixtures/config_registry.json
[OK] config_sync diff:
  + added:    1
  - removed:  1
  ~ changed:  1
  = same:     1
  added details: ['new-skill-x']
  removed details: ['old-skill-y']
  changed details: ['khazix-writer']
---EXIT: 0---

$ python scripts/harness_kit_bridge.py license_check skills/harnesskit-methodology/SKILL.md
  [OK] LICENSE contains Apache License
  [OK] LICENSE contains Version 2.0
  [OK] LICENSE contains 'Licensed under the Apache License, Version 2.0'
  [OK] NOTICE contains 'Modified by dragon-engine / 2026-08-26'
---EXIT: 0---
```

---

## 六、10 unittest PASS（实测 · 2026-08-26）

```
TestHarnessKitSkillManager:                3 用例
  test_01_good_inventory_validates        PASSED  # 3/3 skills, 2 enabled
  test_02_bad_inventory_fails             PASSED  # missing/invalid version
  test_03_v_prefix_accepted               PASSED  # V1.0 等老式 semver

TestHarnessKitMcpRegistry:                 3 用例
  test_04_good_mcp_validates              PASSED  # 3/3 servers
  test_05_bad_transport_fails              PASSED  # stdio requires command
  test_06_http_requires_url               PASSED  # http requires url

TestHarnessKitHookChain:                  2 用例
  test_07_good_chain_no_cycle             PASSED  # 3 hooks, no cycle
  test_08_cycle_detected                  PASSED  # DFS detect cycle

TestHarnessKitConfigSync:                 1 用例
  test_09_diff_added_removed_changed      PASSED  # 4 种状态各 1

TestHarnessKitLicense:                     1 用例
  test_10_apache_20_verbatim_and_modified PASSED  # LICENSE + NOTICE byte-equal

                                              ── 10/10 PASS ✓
```

---

## 七、与天龙既有栈协同（11 位置）

```
harnesskit-methodology V1.0 (借鉴档 · Apache-2.0 ✅ · 414⭐ · 自研 +10 PASS)
   ├─► 09-06-skills-administrator V1.2 → V1.3 ⭐UPG skill manager + enabled
   ├─► 09-02 mcp-orchestrator V9.08 → V9.10 ⭐UPG MCP registry status
   ├─► 07 hooks manager (新岗位候选) ⭐NEW hook chain coherence
   ├─► session-distiller V1.2 → V1.3 ⭐UPG config sync
   ├─► mneme-heat-engine V2.1 → V2.2 ⭐UPG cross-task + config sync
   ├─► a-stock-data-bridge (stage 25 · Apache-2.0)  📎  Apache-2.0 模板
   ├─► memos-methodology (stage 47.1 · Apache-2.0)  📎  Apache-2.0 同步
   ├─► comet-methodology (stage 47.1 · MIT)         📎  借鉴档模式先例
   ├─► agent-reach V1.5 (stage 14 · MIT)            📎  渠道统一管理
   └─► skill-updater V1.1.3 (stage 24)              📎  frontend lint
```

---

## 八、未决项与下一步

1. **stage 47.2 ECC Day 1-7 持续监控**（每 24h 跑 `python scripts/ecc_watcher.py snapshot`）
2. **5 个 ⭐UPG 候选 agent** 留指针（可在 stage 48 一并升级）
3. **stage 48 候选盘点** 30 天后再启动

---

## 九、来源链接

- 仓库主页：https://github.com/RealZST/HarnessKit
- LICENSE 实拉（11,358 B Apache-2.0 verbatim）：https://raw.githubusercontent.com/RealZST/HarnessKit/main/LICENSE
- topics 直击：ai-coding-agents / claude-code / cli-tools / codex / cursor / developer-tools / gemini-cli / skill-manager

---

> **下次同步点**：用户实跑 10 PASS 后决定 stage 47.4 起点 + stage 47.2 ECC Day 1 snapshot。
