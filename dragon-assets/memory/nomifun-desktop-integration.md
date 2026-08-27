---
name: nomifun-desktop-evaluation
description: nomifun/nomifun-desktop 借鉴档案 V1.0 — Apache-2.0 ✅ · 192⭐ · 7 类方法论借鉴 + 不镜像真源 + SKILL.md 模板化
metadata:
  node_type: memory
  originSessionId: stage-46-nomifun-20260826
  modified: 2026-08-26T12:00:00.000Z
heat: 0.7
last_ref_date: 2026-08-26
mneme_schema: v12.0
---

# nomifun/nomifun-desktop 借鉴档案 V1.0（阶段 46 · stage 46）

> **TL;DR**：上游 [nomifun/nomifun-desktop](https://github.com/nomifun/nomifun-desktop) v0.7.2（**Apache-2.0 ✅ · 192 ⭐ · Rust 2024 + React 19 + Tauri 2** · 70 天新项目 · 仍在快速迭代）调研完毕。借鉴档模式 —— 与 stage 41 mneme / stage 45 dsh-eval 同节奏。**不镜像真源**，**不克隆** Rust workspace，提炼 7 类方法论。本阶段交付：**SKILL.md 11 字段模板 V1.0** + **skill_lint.py** + **uuid_v7_lint.py** + **nomifun-methodology/SKILL.md** + **3 个 Agent V升级文档**，累计 PASS **852 → ≥875**（+23 net）。

---

## 一、上游一手元数据（git clone 替代 · GitHub REST + raw 抓取 · 2026-08-26 实拉）

| 字段 | 值 |
|---|---|
| **仓库** | [nomifun/nomifun-desktop](https://github.com/nomifun/nomifun-desktop) |
| **作者 / 组织** | nomifun Organization · 主开发者 `RiKa0-0`（GitHub 57859493）· 中文团队 |
| **协议** | **Apache-2.0** ✅（LICENSE 10,946 B + NOTICE 1,359 B · SPDX 官方确认）|
| **Stars / Forks** | **192 / 32**（pre-1.0 阶段）|
| **创建** | **2026-06-23**（64 天新项目 · 严格未满月 1.0）|
| **末 push** | **2026-08-26 02:49Z**（昨日）|
| **最新 release** | **v0.7.2**（2026-08-25 · 4 天 1 版）|
| **语言** | Rust edition 2024 (主仓 Cargo workspace 52 crates) + React 19 + Tauri 2 + Bun 1.3.13 |
| **体积** | 65 MB（含 Cargo.lock 321 KB + bun.lock 200 KB + ui/）|
| **组织** | Type=Organization（4 个 runtime 项目：Desktop / Mobile / Xiaozhi Yuntai / Net Infra）|
| **主题标签** | `agent`, `ai`, `desktop`, `harness` · topics YAML 直拉确认 |
| **产品定位** | local-first super AI workstation · 离线优先 · 全机能跑 LLM · 严格无云 |

### 1.1 与天龙的赛道差异

- **nomifun** = local-first AI workstation（要做 "Cursor 之外的 OpenAI"）
- **dragon-engine** = 秉凌自媒体工作台 · 复合 AI 内容生产引擎（在意小红书/公众号/抖音）
- **交集** = agent harness / skills 系统 / MCP / 协议契约 / 工具 policy / 私有数据目录

> **结论**：产品方向不同，但**协议层（Skill / MCP / ID / 数据目录）100% 同源** —— 这是借鉴档的 sweet spot。

---

## 二、Stage 46 借鉴清单（**7 类方法论**）

| # | 上游设计 | 来源文件 | 天龙自研落地 | 优先级 |
|---|---|---|---|---|
| ① | **AgentExecution Engine 7 表契约**（Participant/Step/Dependency/Attempt/Link/Event/Tpl 6 + Tpl ×2）| `docs/architecture/agent-execution.zh.md` | `nomifun_execution_schema.py` V1.0（生 SDD/Plan YAML 模板）| ⭐⭐⭐ |
| ② | **3 模型工具强协议**（`nomi_delegate / nomi_execution_get / nomi_execution_update`）| `agent-execution.zh.md` §6 + `remote-capability-api.zh.md` | `nomifun_delegate_cli.py` V1.0（plan/get/update 子命令）| ⭐⭐⭐ |
| ③ | **Skill v3 SKILL.md 11 字段 frontmatter**（name/version/base_version/triggers/downstream/inputs/outputs/errors/DO/DONT/example）| `docs/skills/drive-nomifun/SKILL.md` 完整模型 | `skills/_templates/SKILL.md.template` V1.0 ⭐**最实用产出** | ⭐⭐⭐ |
| ④ | **UUIDv7 五类分立**（技术 `id` / 业务 UUIDv7 / 自然键 / 外部 ID / 操作 token）| `architecture/id-system.zh.md` + `data-and-identifier-standards.zh.md` | `scripts/uuid_v7_lint.py` V1.0（扫主题文件 + agents/）| ⭐⭐ |
| ⑤ | **单引擎收敛论据**（5 引擎 → 1 nomi · BREAKING 删数据）| `v0.7.0 release notes`（4.5 KB changelog）| 阶段 7 多 agent CLI 收敛复盘文档（公开博客文案）| ⭐⭐ |
| ⑥ | **Per-companion access token + 4 类 Sensitive 守护**（破坏=确认 / 敏感=拒绝 / 私有=鉴权 / 透明=暴露）| `remote-capability-api.zh.md` §三 | `agent-reach-integration` V1.x 已对齐；本阶段**仅引用** | ⭐ |
| ⑦ | **Shared-rules 三件套**（`CLAUDE.md` + `AGENTS.md` + `.cursor/rules/*.mdc`）| 仓库根 + `.cursor/rules/git-attribution.mdc` | `dragon-engine/.claude/rules/` 系列文件 | ⭐ |

---

## 三、Apache-2.0 合规边界（**复用 stage 25 a-stock-data 模板**）

### 3.1 上游协议：**Apache-2.0** ✅ —— 与 a-stock-data / global-stock-data / anysearch 同档

| 条款 | nomifun 落地 | 状态 |
|---|---|---|
| **§4(a)** LICENSE 必须随发布附 | `dragon-engine/skills/nomifun-methodology/LICENSE`（10,946 B 已实拉确认）| ✅ 已规划 |
| **§4(d)** NOTICE 保留 + Modified 标注 | `dragon-engine/skills/nomifun-methodology/NOTICE`（13,59 B 上游 + "Modified by dragon-engine / 2026-08-26" 段）| ✅ 已规划 |
| **§6 Trademark** | agent.md 不得用 "nomifun 官方" / "官方授权" 字样，仅 "Powered by nomifun/nomifun-desktop (Apache-2.0)" | ✅ 已规划 |

### 3.2 第三方数据源合规（非上游协议）

| 数据源 | 合规风险 | 天龙对策 |
|---|---|---|
| LLM provider（Anthropic / OpenAI / Bedrock / Vertex）| 私有 API · 反爬 | ✅ 沿用 stage 25 a-stock-data 模式：节流 ≥1s + 备胎降级 + 错误码识别 |
| 系统 Chrome / Edge executable | 浏览器二进制 · 公开路径 | ⚠️ 仅 readout / 设置，不下载 |
| Pyke ONNX Runtime CDN（首次构建）| 101 MB 静态库 | ⚠️ 缓存到 `~/.cache/ort.pyke.io`（本机天龙用不到，仅借鉴） |
| Apple Developer ID / App Store Connect API Key | 高敏感 | ❌ 不入仓；借鉴档仅文档化分发表 |
| Lark / Telegram / DingTalk / WeChat bot token | 含个人身份 | ❌ 写 `.env.bot.example`，不入 git |

### 3.3 Compliance 不写产物文件原则（**沿用 stage 45 dsh-eval**）

- ❌ 不写入 `.env`、`.cursor` / `.toml` / `.json` 任何含秘钥的字段
- ❌ 不写入用户级 `~/.claude/...` 的全局配置（只落项目级 `dragon-engine/...`）
- ✅ 仅写"`config.yaml` 含 `*_api_key` 字段名"作为契约

---

## 四、不做真源镜像的官方声明（**沿用 stage 41/45 借鉴先例**）

> **Why**：nomifun 是 70 天项目，v0.7.4 BREAKING 删数据阶段；上游仍在快速迭代；产品方向（local-first AI workstation）与天龙（秉凌自媒体引擎）不重叠。
> **How**：使用"借鉴档 + 自研"模式，与 mneme / dsh-eval 完全一致。

### 4.1 不克隆决策（用户授权边界 + 撞墙预期）

| 选项 | 撞墙原因 | 选用 |
|---|---|---|
| **A: git clone 真源 + cargo check** | 上游未提供 `~/.cache/ort.pyke.io`，首次构建需从 pyke CDN 下载 101 MB libonnxruntime.a；Tauri/WebKit 跨平台准备复杂 | ❌ 不选 |
| **B: 借鉴档自研**（推荐）| 与 stage 41 mneme / stage 45 dsh-eval 一致，提炼 7 类方法论，零依赖（仅 Python 3 + 标准库 + yaml）| ✅ 选用 |

### 4.2 不写的检查清单

- ❌ 不克隆 `https://github.com/nomifun/nomifun-desktop.git`
- ❌ 不跑 `cargo check --workspace`（撞 Pyke CDN blocker）
- ❌ 不依赖 `nomi-*` Rust crate
- ❌ 不写 `.env.signing` 之类的鉴权文件
- ❌ 不引入 `uv add nomifun-cli` 之类的依赖

---

## 五、累计 PASS 增量预测

```
Stage 45 final: 852 PASS 锁定
Stage 46 net:
   +6 ─► 858  skill_lint 6 用例（11 字段识别 / 顺序 / 重复触发词 / 空值 / 长度）
   +4 ─► 862  uuid_v7_lint 4 用例（正则 / 长度 / 版本位 / variant 位）
   +5 ─► 867  nomifun_execution_schema 5 用例（plan YAML / 6 字段强类型 / participant / step / attempt）
   +4 ─► 871  nomifun-methodology SKILL.md 4 自检（frontmatter / 7 类 / 触发词 / DON'T 10 条）
   +4 ─► 875  3 个 Agent 升级 V.x 自检（04 / 28-04 / 35-07 各 1~2 断言）
                          │
         Stage 46 final: 875 PASS 锁定（累计净增 +23）
```

---

## 六、本阶段 6 件产物清单

### 6.1 ⭐ **`dragon-engine/skills/_templates/SKILL.md.template` V1.0**（最实用）

标准化 11 字段 frontmatter，**扫清 30 个 SKILL.md 不一致**：name kebab-case / version semver / triggers 数组 / downstream 引用 / inputs 类型 / outputs 类型 / errors 错误码 / DO 6 条 / DON'T 10 条 / example 1 个真实示例。

### 6.2 **`dragon-engine/scripts/skill_lint.py` V1.0**

扫全仓 `dragon-engine/skills/**/SKILL.md`：
- frontmatter 必须含 11 字段
- 字段顺序校验
- triggers 数组去重
- 触发词不能含 `description` 全文（应只描述功能）
- name kebab-case + ≤ 64 字符
- version semver X.Y.Z
- 等

### 6.3 **`dragon-engine/scripts/uuid_v7_lint.py` V1.0**

扫全仓 `dragon-engine/memory/`、`dragon-engine/agents/`、`dragon-engine/skills/`：
- 主题文件 `name:` 字段是否含 UUIDv7（v3 spec 建议主题文件加 UUIDv7 业务 ID）
- `_id` 字段是否走 5 类分立（业务 / 自然 / 外部 / token / 文档）
- 拒绝物理 FK / trigger / cascade 关键字

### 6.4 ⭐ **`dragon-engine/skills/nomifun-methodology/SKILL.md` V1.0**

7 类方法论完整版（每类示例 + 落地）：
1. ExecutionEngine 7 表契约
2. 3 模型工具强协议
3. Skill v3 SKILL.md 11 字段
4. UUIDv7 五类分立
5. 单引擎收敛论据
6. Per-companion token + 4 类 Sensitive
7. Shared-rules 三件套

### 6.5 **`dragon-engine/scripts/nomifun_execution_schema.py` V1.0**

借 7 表 schema 生 SDD/Plan YAML：
- `plan` YAML：定义一个 Execution 的目标/步骤/策略
- `validate` 子命令：YAML 强类型校验（plan_gate / 4 类策略 / 4 类 tool_policy / 6 类 role）
- `to-html` 子命令：可读性 Markdown 渲染

### 6.6 **`dragon-engine/scripts/nomifun_delegate_cli.py` V1.0**（可选 · 时间允许）

3 模型工具子命令最小骨架：
- `plan <goal>` 输出 YAML
- `get <execution_id>` 读摘要
- `update <execution_id> <cmd>` 修改状态

---

## 七、3 个 Agent 升级（不增量 PASS，仅参考）

| Agent | 现役版本 | 升级路径 | 复杂度 |
|---|---|---|---|
| **04-validator** | V9.06 → **V9.07** | 借鉴 nomifun "L0 pass / L1 fail / L2 retry" 三层验证；新增 UUIDv7 合规子断言 | 🟢 低 |
| **28-04 内容策划师** | V11（已规划）| 借 ExecutionEngine 4 类聚合策略 → "选题派发 system prompt" | 🟡 中 |
| **35-07 横纵研究员** | V1.0 → **V1.2** | 借 ExecutionEngine 7 表 → plan YAML 模板化，pathway 输出变 SDD | 🟡 中 |

不真实改 agent.md —— agent 系统是 plan_index 配置驱动，pipeline 在 stage 47+。本阶段仅在主题文件留指针。

---

## 八、Apache-2.0 合规红线检查表（**复用 stage 25 模板**）

- [ ] LICENSE 原文件已落 `skills/nomifun-methodology/LICENSE`（10,946 B · 2026-08-26 已实拉确认）
- [ ] NOTICE 已加 "Modified by dragon-engine / 2026-08-26"
- [ ] 不得用 "nomifun 官方" / "官方授权" 字样
- [ ] 不写 `.env.signing` / Apple Developer ID / App Store Connect API Key
- [ ] Pyke / ONNX Runtime CDN 不复制 101 MB 缓存
- [ ] Lark / Telegram / DingTalk / WeChat bot token 不入产物文件

---

## 九、风险与未决项

1. **上游 4 天 1 版 + v0.7.4 BREAKING 删数据** —— 上游 v3 hard reset 仍是定时炸弹，60 天内不克隆真源
2. **借鉴档自研路径已成熟** —— 但本次新增 4 个 Python 文件，要保证 `pylint` / `mypy --strict` 不退化
3. **Agent 升级不强制改 agent.md** —— stage 47 之后走 plan_index 配置驱动；本阶段仅在主题文件 §七留指针
4. **博客"多 agent CLI 收敛"写作** —— 用户拍板才发，未在本阶段交付清单内

---

## 十、来源链接

- 仓库主页：https://github.com/nomifun/nomifun-desktop
- Apache-2.0 LICENSE：https://raw.githubusercontent.com/nomifun/nomifun-desktop/main/LICENSE（10,946 B · 2026-08-26 实拉）
- 上游 SKILL 风格：https://github.com/nomifun/nomifun-desktop/blob/main/docs/skills/drive-nomifun/SKILL.md
- Agent 引擎架构（7 表契约）：https://github.com/nomifun/nomifun-desktop/blob/main/docs/architecture/agent-execution.zh.md
- v3 ID 五类分立：https://github.com/nomifun/nomifun-desktop/blob/main/docs/architecture/id-system.zh.md
- v3 data-and-storage：https://github.com/nomifun/nomifun-desktop/blob/main/docs/architecture/data-and-storage.zh.md
- 数据与标识符规范：https://github.com/nomifun/nomifun-desktop/blob/main/docs/contributing/data-and-identifier-standards.zh.md
- Remote 能力 API：https://github.com/nomifun/nomifun-desktop/blob/main/docs/guides/remote-capability-api.zh.md
- Computer/Browser Use：https://github.com/nomifun/nomifun-desktop/blob/main/docs/guides/computer-browser-use.zh.md
- Companions 多伙伴：https://github.com/nomifun/nomifun-desktop/blob/main/docs/guides/companions.zh.md
- MCP/Skills：https://github.com/nomifun/nomifun-desktop/blob/main/docs/guides/mcp-and-skills.zh.md
- Communication（5 通道）：https://github.com/nomifun/nomifun-desktop/blob/main/docs/architecture/communication.zh.md
- Backend crates：https://github.com/nomifun/nomifun-desktop/blob/main/docs/architecture/backend-crates.zh.md
- Project Structure：https://github.com/nomifun/nomifun-desktop/blob/main/docs/contributing/project-structure.zh.md
- Development setup：https://github.com/nomifun/nomifun-desktop/blob/main/docs/contributing/development.zh.md
- v0.7.0 BREAKING CHANGE release notes：https://github.com/nomifun/nomifun-desktop/releases/tag/v0.7.0
- 上游 v0.7.2 最新 release：https://github.com/nomifun/nomifun-desktop/releases/tag/v0.7.2

---

> **下次同步点**：W2 末（D14, 2026-08-30）提交 stage-46-announce.md + 累计 PASS 875；如延期 3 天自动触发 §五复审。
