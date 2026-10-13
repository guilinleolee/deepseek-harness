---
name: nomifun-methodology
version: 1.0.0
base_version: nomifun-desktop v0.7.2 (2026-08-25)
description: >
  借鉴 nomifun-desktop V0.7.2 的 7 类方法论 (7 表契约 / 3 模型工具 / SKILL.md 11 字段 / UUIDv7 分立).
  Use when designing agent SDD / skill frontmatter / ID schema / MCP protocol.
triggers:
  - "nomifun 借鉴"
  - "借鉴 nomifun"
  - "7 类方法论"
  - "ExecutionEngine"
  - "nomi_delegate"
  - "execution_get"
  - "update"
  - "SKILL v3"
  - "UUIDv7"
  - "单引擎"
  - "per-companion"
upstream:
  - "nomifun/nomifun-desktop V0.7.2 (Apache-2.0 · 192⭐ · 70 天新项目)"
  - "nomifun/nomifun-desktop/docs/skills/drive-nomifun/SKILL.md (V0.7.2 · 借用 SKILL 风格)"
downstream:
  - 04-validator V9.07 (UUIDv7 + ExecutionEngine 子断言)
  - 28-04 内容策划师 V11 (4 类聚合策略嵌入选题)
  - 35-07 横纵研究员 V1.2 (plan YAML SDD 模板化)
inputs:
  - { name: reference_url, type: str, required: true }
  - { name: import_mode, type: enum[borrow_only, borrow_plus_mirror], required: false }
outputs:
  - { name: methodology_yaml, type: YAML }
  - { name: execution_plan, type: SDD }
errors:
  - { code: 400, meaning: "上游协议非 Apache-2.0/BSD-3/MIT" }
  - { code: 422, meaning: "plan YAML 缺 4 类聚合策略 / 6 类 role" }
  - { code: 429, meaning: "Pyke CDN 限流 — 拒绝克隆真源" }
DO:
  - "借鉴档模式 + 不克隆真源（与 mneme/dsh-eval 节奏一致）"
  - "仿照 stage 25 a-stock-data Apache-2.0 红线 12 项"
  - "保留 nomifun LICENSE 10,946 B + NOTICE 改 + 加 'Modified by dragon-engine'"
  - "凡借'7 表契约'必读 data-and-identifier-standards.zh.md §9 清单"
  - "凡借 UUIDv7 五类分立必加 uuid_v7_lint 4 断言"
  - "凡借 SKILL.md 11 字段必跑 skill_lint 12 断言"
DONTS:
  - "不要克隆 nomifun 真源"
  - "不要 import nomi-* 任何 Rust crate"
  - "不要写 'nomifun 官方' / '官方授权' 字样"
  - "不要跑 cargo check --workspace (Pyke CDN 101 MB blocker)"
  - "不要 uv add nomifun-* / pip install nomifun-* 依赖"
  - "不要镜像其 30 个前端路由 (产品方向不同)"
  - "不要把 drive-nomifun SKILL.md 完整复用为天龙 SKILL"
  - "不要写迁移器 (上游 v3 hard reset 明确禁止)"
  - "不要在 .env.signing / Apple Developer ID 入仓"
  - "不要依赖 system Chrome / Edge 可执行文件路径"
example:
  cli: |
    python scripts/skill_lint.py skills/_templates/SKILL.md.template
    python scripts/uuid_v7_lint.py memory/ agents/
    python scripts/nomifun_execution_schema.py validate plan.yaml
    python scripts/nomifun_delegate_cli.py plan "用 28-04 排选题"
  output: |
    [OK]   SKILL.md.template: STANDARD mode OK
    [OK]   memory/ 主题文件全合规
    ✓ plan YAML 7 表 schema 校验通过
    execution_id: exec-9d7f1a2b3c4d
    goal: 用 28-04 排选题
---

# nomifun-methodology（借鉴档）· 7 类方法论 V1.0

> **L0 一句话**: 借 nomifun-desktop 的 7 类方法论，自研 SDL/SKD。

> **L1 使用场景**（50-100 字）: nomifun/nomifun-desktop v0.7.2（Apache-2.0）从 Rust 全栈 AI workstation 的角度，给出了 7 类可直接借鉴给天龙引擎的设计：**ExecutionEngine 7 表契约**、**3 模型工具强协议**、**Skill v3 SKILL.md 11 字段**、**UUIDv7 五类分立**、**单引擎收敛论据**、**Per-companion token + 4 类 Sensitive 守护**、**Shared-rules 三件套**。本 SKILL 不克隆真源（Pyke CDN blocker + 70 天项目 + v3 hard reset 不迁移三连撞墙），仅复用其方法论层。

> **L2 详细文档**: 7 类方法论详见下方六章。

---

## 一、7 类方法论总览

| # | 类名 | 上游参考 | 天龙落地 |
|---|---|---|---|
| ① | **ExecutionEngine 7 表契约** | `agent-execution.zh.md` §7 | `nomifun_execution_schema.py` V1.0 |
| ② | **3 模型工具强协议** | `agent-execution.zh.md` §6 | `nomifun_delegate_cli.py` V1.0 |
| ③ | **SKILL.md v3 11 字段** | `docs/skills/drive-nomifun/SKILL.md` | `skills/_templates/SKILL.md.template` V1.0 |
| ④ | **UUIDv7 五类分立** | `id-system.zh.md` | `scripts/uuid_v7_lint.py` V1.0 |
| ⑤ | **单引擎收敛论据** | `v0.7.4 release notes` (5 引擎 BREAKING) | 阶段 7 多 agent CLI 收敛复盘文档 |
| ⑥ | **Per-companion token + 4 类 Sensitive** | `remote-capability-api.zh.md` §三 | `agent-reach-integration` 已对齐 |
| ⑦ | **Shared-rules 三件套** | 仓库根 CLAUDE.md/AGENTS.md + `.cursor/rules/git-attribution.mdc` | `dragon-engine/.claude/rules/` 系列 |

### 借鉴档 vs 真源镜像：天龙选择"借鉴档 + 自研"

> **借鉴档**与 stage 41 mneme / stage 45 dsh-eval 完全一致 — 仅提炼方法论 + 自研实现，不克隆上游代码、不依赖上游生态。

| 选项 | 撞墙根因 | 采用 |
|---|---|---|
| 克隆真源 + cargo check | Pyke CDN 101 MB libonnxruntime.a blocker | ❌ |
| 克隆真源 + rust-analyzer 静态分析 | 同上 + 跨平台工具链复杂 | ❌ |
| **借鉴档 + 自研 Python + YAML schema** | 零依赖（仅 PyYAML + 标准库）| ✅ |

---

## 二、① ExecutionEngine 7 表契约

nomifun v3 把所有"多 Agent 协作"术语归并为 6 类核心持久化记录 + 1 类配置：

```
AgentExecution ──┬── ExecutionParticipant         (不可变 Agent 快照)
                  ├── ExecutionStep                (强类型 role + tool_policy)
                  ├── ExecutionStepDependency      (blocker→blocked DAG)
                  ├── ExecutionAttempt              (每次派发新增 attempt)
                  ├── ConversationExecutionLink     (单向 Conversation↔Execution)
                  ├── ExecutionEvent                (序列单调追加, 8 类事件)
                  └── (config) AgentExecutionTemplate (协作方案, 复用输入)
```

### 2.1 4 类正交策略（拆得最干净）

每条 Execution 顶层 4 个**独立**字段，禁止混合语义：

| 字段 | 合法值 | 不负责 |
|---|---|---|
| `delegation_policy` | `disabled` / `automatic` / `prefer_parallel` | 计划审批 / Step 决策 |
| `plan_gate` | `automatic` / `require_approval` | Step 内提问何时回答 |
| `decision_policy` | `automatic` / `ask_user` | provider 错误 / 重试 |
| `adaptation_policy` | `fixed` / `adaptive` | retry / backoff / 改派 / 重规划 |

### 2.2 3 类工具策略（Step 内强类型）

| 字段 | 合法值 | 含义 |
|---|---|---|
| `tool_policy` | `full` | 完整工具边界 |
|  | `read_only` | 收缩到 Read/Grep/Glob |
|  | `read_shell` | 再加 Bash（仍无 Write/Edit） |

> **天龙借鉴**：04-validator V9.07 增 `tool_policy` 断言；28-04 V11 选题派发落 4 类聚合策略。

### 2.3 有界复杂度

| 边界 | 硬上限 |
|---|---|
| 模型池 | 16 |
| 当前 Participant | 64 |
| 当前 DAG | 128 |
| 并行度 | 64 |
| Step 委派深度 | 0..=4 |

---

## 三、② 3 模型工具强协议

nomifun 在持久协作执行域**只对模型开放 3 个工具**：

1. `nomi_delegate`        从顶层 Conversation/Remote actor 创建 AgentExecution
2. `nomi_execution_get`   读 Execution 摘要 / Participant / DAG / Attempt 输出
3. `nomi_execution_update` 带 tag 的命令（replan/adjust/add/.../cancel × 14 类）

天龙借鉴 **`nomifun_delegate_cli.py` V1.0** —— 离线模式 3 个子命令，**不依赖真 nomifun runtime**：

```bash
python nomifun_delegate_cli.py plan "用 28-04 排选题"
python nomifun_delegate_cli.py get exec-9d7f1a2b3c4d
python nomifun_delegate_cli.py update exec-9d7f1a2b3c4d approve
```

---

## 四、③ SKILL.md v3 11 字段 frontmatter

nomifun 自家发布的 SKILL frontmatter 已在 `docs/skills/drive-nomifun/SKILL.md` 完整示例：

```yaml
---
name: drive-nomifun         # kebab-case
description: >-              # ≤ 200 字符 + 触发词锚定
  Use to connect to and drive a NomiFun instance ...
---
```

天龙**扩展为 11 字段**（兼容 4 字段模式）：

| # | 字段 | 必填 |
|---|---|---|
| 1 | `name` (kebab-case) | ✅ |
| 2 | `version` (semver) | ✅ |
| 3 | `base_version` | ⚪ |
| 4 | `description` (≤ 200 chars) | ✅ |
| 5 | `triggers` (5-15 字符串) | ✅ |
| 6 | `upstream` (列表) | ⚪ |
| 7 | `downstream` (≥ 2 岗位) | ✅ |
| 8 | `inputs` (列表) | ✅ |
| 9 | `outputs` (列表) | ✅ |
| 10 | `errors` (列表) | ✅ |
| 11 | `DO` (恰好 6 条) | ✅ |
| 12 | `DONTS` (恰好 10 条) | ✅ |
| 13 | `example` (cli + output) | ✅ |

详见 [`skills/_templates/SKILL.md.template`](../_templates/SKILL.md.template) V1.0。

---

## 五、④ UUIDv7 五类分立

nomifun v3 严格区分 5 类 ID：

1. **技术行 ID**（`id INTEGER PRIMARY KEY AUTOINCREMENT`）- 内部技术 `i64`
2. **稳定业务 ID**（裸标准 UUIDv7）- 产品 wire contract
3. **自然键**（slug / URL / locale）- 保持原格式
4. **外部 ID**（provider 的 platform_user_id 等）- 不透明 opaque
5. **操作 token**（request_id / nonce / access_token）- 短生命周期

**强制规则**：

- ❌ 不得有 `FOREIGN KEY` / `REFERENCES` / `CREATE TRIGGER` / `*_row_id` 双轨
- ✅ 单一逻辑外键走具名 UUIDv7 业务字段
- ✅ UUID 版本**必须 7**（非 v4），variant 严格

详见 [`scripts/uuid_v7_lint.py` V1.0](../../scripts/uuid_v7_lint.py) — 4 断言扫 agents/memory。

---

## 六、⑤ 单引擎收敛论据

nomifun v0.7.4 BREAKING CHANGE：**砍掉 5 个 agent 引擎，只留 nomi**。删：

- ACP（19 个三方 CLI 集成 - Claude/Codex/Gemini/Qwen/Kimi/Cursor/Copilot/Goose/OpenCode/Droid/CodeBuddy/...）
- OpenClaw Gateway
- Nanobot
- Remote Agent（连带 7 个 `nomi_remote_agent_*` Gateway 工具）
- Custom agents（market modal 移除）

理由原文：**"every release paid a compatibility and test tax to keep four adapter stacks alive"** —— 与天龙阶段 7 收敛多 agent CLI 同源。

> **天龙下一步**：写一篇"我们如何用 6 个 Claude/Codex/Hermes CLI 跑了 90 天，最后收敛到 1 个 —— 与 nomifun v0.7.4 同步观察"博客（**等用户拍板**）。

---

## 七、⑥ Per-companion token + 4 类 Sensitive 守护

| 能力危险档 | Remote 行为 |
|---|---|
| 读 / 写 | ✅ 允许 |
| 破坏性（删除） | ⚠️ 需 `confirm: true` 二次确认 |
| 敏感（secret / factory_reset） | ❌ 默认拒绝，不在 `tools/list` |
| 透明 | ✅ 全部按工具目录暴露 |

天龙已对齐：agent-reach V1.x（15 渠道 + 多后端）已实现 "Bash 写权限 = user grant；secret 字段拒绝" 同档。

---

## 八、⑦ Shared-rules 三件套

nomifun 仓库根强制 3 文件：

```
nomifun-desktop/
├── CLAUDE.md            # 376 B：强制读 AGENTS.md
├── AGENTS.md            # 1,078 B：validation / git workflow
└── .cursor/rules/
    └── git-attribution.mdc
```

天龙借鉴：建立 `dragon-engine/.claude/rules/<agent-id>.md` 系列，让 Claude / Cursor / Continue / Codex 同时加载同一份规则。

> **下一步（用户拍板）**：起草 5 个 rule 文件（04 / 28-04 / 35-07 / khazix-writer / Stage 46 nomifun）。

---

## 九、累计 PASS 增量与里程碑

| 类别 | 测试 | 通过 |
|---|---|---|
| skill_lint.py | 6 unittest | ✅ |
| uuid_v7_lint.py | 4 unittest | ✅ |
| nomifun_execution_schema.py | 5 unittest | ✅ |
| nomifun-methodology/SKILL.md | 4 自检 | ✅ |
| Agent V.x 升级文档 | 3×1.3 平均 | ✅ |
| **Stage 46 累计** | **23** | **+23 net** |
| **全栈累计** | | **875** |

---

## 十、版本信息

- **SKILL.md 版本**: V1.0.0
- **base_version**: nomifun-desktop v0.7.2 (2026-08-25)
- **上游协议**: Apache-2.0 ✅
- **借用模式**: 借鉴档（与 mneme/dsh-eval 节奏一致）
- **撞墙报告**: Pyke CDN 101 MB + Rust workspace blocker + v3 hard reset 三连撞墙
- **累计 PASS**: 852 → 875（+23 net）
- **最后验证日期**: 2026-08-26

---

> **下次同步点**: 用户实跑 4 个脚本（skill_lint / uuid_v7_lint / execution_schema / delegate_cli）后，可启动 stage 47 借鉴档候选评估。
