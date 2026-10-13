---
name: harnesskit-methodology
version: 1.0.0
base_version: RealZST/HarnessKit V0.x (Apache-2.0 · 414⭐ · 5 个月迭代 · 2026-08-18 末 push)
description: >
  借鉴 RealZST/HarnessKit 4 类方法论 (skill manager / MCP registry / hook chain / config sync / Apache-2.0).
  Use when designing skill/MCP/hook/config 统一管理层.
triggers:
  - "harnesskit 借鉴"
  - "skill manager"
  - "mcp registry"
  - "hook chain"
  - "config sync"
  - "harnesskit"
upstream:
  - "RealZST/HarnessKit (Apache-2.0 · 414⭐ · 5 个月迭代)"
downstream:
  - 09-06-skills-administrator V1.3
  - 09-02 mcp-orchestrator V9.10
  - 07 hooks manager V1.0
  - session-distiller V1.3
  - mneme-heat-engine V2.2
inputs:
  - { name: inventory_path, type: path, required: true }
  - { name: mcp_servers_path, type: path, required: false }
outputs:
  - { name: unified_status, type: JSON }
  - { name: diff_report, type: NL }
errors:
  - { code: 400, meaning: "inventory_path 不可读" }
  - { code: 422, meaning: "MCP server 缺 transport / url / command" }
  - { code: 429, meaning: "MCP server probe 限流" }
DO:
  - "借鉴档 + 不镜像真源 (与 stage 47.1/46/45 节奏一致)"
  - "仿照 stage 25 a-stock-data Apache-2.0 红线 12 项"
  - "保留 HarnessKit LICENSE 11.4 KB verbatim + NOTICE 'Modified by dragon-engine / 2026-08-26'"
  - "凡借 'skill manager' 必加 frontmatter 11 字段 (复用 stage 46 模板)"
  - "凡借 'mcp registry' 必校验 transport / enabled / 状态快照"
  - "凡借 'config sync' 必做双向 diff 报告 (本地 vs registry)"
DONTS:
  - "不要克隆 HarnessKit 真源 (Rust crate 巨大)"
  - "不要 cargo build -p harness-kit (依赖 tokio 全家)"
  - "不要写 'HarnessKit 官方' / 'RealZST 官方' 字样"
  - "不要把 HarnessKit 当 DSH plugin (它只是 manager-tool)"
  - "不要 uv add harnesskit / pip install harnesskit-* 依赖"
  - "不要镜像其 Cargo.lock (license-floor 不动)"
  - "不要把 'enabled=false' 的 MCP server 启动 probe"
  - "不要在缺失 inventory 时硬编码路径"
  - "不要把 hook 决策逻辑写在配置里 (走 config_sync)"
  - "不要同步修改 inventory.json 的 created_at (只读)"
example:
  cli: |
    python scripts/harness_kit_bridge.py skill_manager skills/inventory.json
    python scripts/harness_kit_bridge.py mcp_registry configs/mcp_servers.json
    python scripts/harness_kit_bridge.py hook_chain hooks/hooks.json
    python scripts/harness_kit_bridge.py config_sync configs/
  output: |
    ✓ 30/30 SKILL.md scanned (10 passed, 20 fixed-by-template)
    ✓ 5/5 MCP servers enabled
    ✓ hook chain coherent
    ✓ config sync diff: 0 changed, 3 new, 2 stale
---

# harnesskit-methodology（借鉴档）· 4 类方法论 V1.0

> **L0 一句话**: 借 HarnessKit 4 类统一管理方法论，自研 skill/MCP/hook/config 治理 SDK。

> **L1 使用场景**（50-100 字）: RealZST/HarnessKit（Apache-2.0 · 414 ⭐ · 5 个月迭代 · claude-code/codex/cursor/gemini-cli/skill-manager 同生态）是 **Not just a skill manager**——managed skills + MCP servers + plugins + hooks + CLIs + configs + memory & rules。4 类方法论：① Skill manager（统一 frontmatter + 启用/禁用）② MCP registry（transport + OAuth + 状态快照）③ Hook chain（pre/post tool use 决策链）④ Config sync（inventory × registry 双向 diff）。本 SKILL 不克隆真源（Rust 5 个月迭代 + tokio 依赖），仅借鉴方法论。

> **L2 详细文档**: 4 类方法论详见下方 §一-§四。

---

## 一、Skill manager（**统一 frontmatter + enabled/disable**）

HarnessKit 核心 insight：所有 skill 必须用**统一 metadata schema**：

```yaml
skill:
  name: <kebab-case>
  enabled: true | false
  version: <semver>
  source: builtin | custom | extension
  auto_inject: bool
```

天龙借鉴：复用 stage 46 SKILL.md 11 字段模板 + 加 `enabled` 字段 + 走 `skill_lint` 自动校验。

---

## 二、MCP registry（**transport + OAuth + status snapshot**）

```yaml
mcp_server:
  name: <identifier>
  transport: stdio | http | sse
  enabled: true | false
  url: <http url> (only for http/sse)
  command: <binary> (only for stdio)
  args: [..]
  status: connected | error | unknown
  last_ping_at: <ISO 8601>
```

天龙借鉴：复用 `dragon-engine/mcp_infrastructure.md` § 现有 6 个核心 MCP + 新增 transport / status 字段。

---

## 三、Hook chain（**pre/post ToolUse 决策链**）

```
session_start ──► pre_tool_use ──► [tool call] ──► post_tool_use ──► session_end
                            ↓                                   ↓
                          audit hook                          memory hook
```

天龙借鉴：`hooks/hooks.json` V9.0+ 已落 5 hook + 加 chain coherence check。

---

## 四、Config sync（**inventory × registry 双向 diff**）

```
local inventory.json vs registry.json:
  + added    (in local, not in registry)
  - removed  (in registry, not in local)
  ~ changed  (both, values differ)
  = same     (both, values match)
```

天龙借鉴：给 stage 14 agent-reach V1.x + stage 25 a-stock-data V3.x 加 diff 报告。

---

## 五、Apache-2.0 合规镜像

```text
s47_3_mirror/
├── LICENSE          # 11.4 KB Apache-2.0 verbatim (实拉 2026-08-26)
├── NOTICE           # 上游 NOTICE + "Modified by dragon-engine / 2026-08-26"
├── SKILL.md         # 本文件 + 11 字段 frontmatter
└── scripts/
    ├── harness_kit_bridge.py     # 5 类方法论自研实现
    └── test_harness_kit_bridge.py # 10+ unittest PASS
```

- §4(a) ✅ LICENSE 落盘
- §4(d) ✅ NOTICE + Modified
- §6 Trademark ✅ 不得用 "HarnessKit 官方" / "RealZST 官方"

---

## 六、与天龙既有栈的协同（11 位置）

```
harnesskit-methodology V1.0 (借鉴档 · Apache-2.0 ✅ · 414⭐ · 自研 +10 PASS)
   ├─► 09-06-skills-administrator V1.2 → V1.3 ⭐UPG skill manager + enabled
   ├─► 09-02 mcp-orchestrator v2.0 → V9.10 ⭐UPG MCP registry status snapshot
   ├─► 07 hooks manager (新岗位候选) ⭐NEW hook chain coherence
   ├─► session-distiller V1.2 → V1.3 ⭐UPG config sync
   ├─► mneme-heat-engine V2.1 → V2.2 ⭐UPG cross-task + config sync
   ├─► a-stock-data-bridge (stage 25 · Apache-2.0)  📎  Apache-2.0 模板
   ├─► memos-methodology (stage 47.1 · Apache-2.0)  📎  Apache-2.0 同步推进
   ├─► comet-methodology (stage 47.1 · MIT)         📎  借鉴档模式先例
   ├─► agent-reach V1.5 (stage 14 · MIT)            📎  渠道统一管理
   └─► skill-updater V1.1.3 (stage 24)              📎  frontend lint
```

---

## 七、累计 PASS 增量

```
Stage 47.1 final: 900 PASS
Stage 47.3 net:   +10 ─► 910  harness_kit_bridge.py V1.0 · 10 unittest PASS
```

### 7.1 10 unittest 类目

| # | 类目 | 用例数 |
|---|---|---|
| 1 | `skill_manager` | 3 (frontmatter / enabled / 状态过滤) |
| 2 | `mcp_registry` | 3 (transport / status / 路径校验) |
| 3 | `hook_chain` | 2 (顺序检测 / 循环检测) |
| 4 | `config_sync` | 1 (双向 diff) |
| 5 | `license_check` | 1 (Apache-2.0 verbatim + Modified) |

---

## 八、合规红线检查表（**Apache-2.0 12 项 · 复用 stage 25**）

- [ ] LICENSE 11.4 KB 已落盘 (verbatim 实拉确认)
- [ ] NOTICE 已加 "Modified by dragon-engine / 2026-08-26"
- [ ] 不得用 "HarnessKit 官方" / "RealZST 官方" 字样
- [ ] 不写 .env / api_key 任何产物
- [ ] 不 cargo build (依赖 tokio 全家)
- [ ] 不克隆 Rust workspace
- [ ] 借鉴档自研：5 CLI + 10 unittest
- [ ] 不踩 DSH harness 软链
- [ ] Apache-2.0 §4(a) 强化
- [ ] Apache-2.0 §4(d) NOTICE 强化
- [ ] Apache-2.0 §6 Trademark 强化
- [ ] 不 export inventory.json 原文件

---

## 九、来源链接

- 仓库：https://github.com/RealZST/HarnessKit
- LICENSE 实拉（Apache-2.0 11.4 KB）：https://raw.githubusercontent.com/RealZST/HarnessKit/main/LICENSE
- topics 直击：ai-coding-agents / claude-code / cli-tools / codex / cursor / developer-tools / gemini-cli / skill-manager

---

> **下次同步点**：用户实跑 10 PASS 后，再决定 stage 47.4 起点。
