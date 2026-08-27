# dragon-assets/ · 天龙引擎资产同步镜像

> **本目录是天龙引擎（dragon-engine V2.5）的资产镜像**——纯数据层，不是 Cordis plugin。
> 同步日期：2026-08-27 · 同步源：`C:\Users\li\.claude\projects\dragon-engine\` · 镜像版本：V2.5

## 0. 是什么

把天龙引擎的 **1157 个 SKILL.md / agent / command / hook / script / memory / ip-profile / index** 全量镜像到此目录，供 DSH（DeepSeek Harness）按需检索、调用、桥接。

| 维度 | 数据 |
|---|---|
| 资产数 | **1,224**（SKILLS 784 + AGENTS 187 + HOOKS 90 + COMMANDS 156 + PLUGINS 7）|
| 总文件 | ~21,225 |
| 总大小 | ~289 MB |
| 同步策略 | 镜像 + 清理（git/pycache/node_modules 已剔除）|
| 同步率 | **99.36%**（与天龙主仓文件计数对齐）|

## 1. 目录结构

```
dragon-assets/
├── README.md                          ← 本文件
├── LICENSE-ATTRIBUTION.md             ← 三档 License 致谢模板（MIT/AGPL/Apache）
├── .gitignore
│
├── skills/                            ← 天龙 skills/（843 个一级目录 · ~20,000 文件 · 290 MB）
│   ├── async-task-pattern/            （示例：4 原语异步接口）
│   ├── cinema-director-laoli/          （老李风电影分镜）
│   ├── nano-banana-brief/             （GPT-Image2 推理 brief）
│   ├── guizang-social-card-skill/     ⚠️ AGPL-3.0
│   ├── cangjie-skill/                 ⚠️ AGPL-3.0
│   ├── nuwa-skill/                    MIT ✅
│   ├── darwin-skill/                  MIT ✅
│   ├── a-stock-data-bridge/           Apache-2.0
│   ├── ... 843 个一级目录
│   └── _archive/  _template/  _templates/  _tikhub/
│
├── agents/                            ← 天龙 agents/（182 .md · 角色定义）
│   ├── 00-99 编号体系：00-analyst / 01-investigator / 02-architect / 03-builder /
│   │   04-validator / 05-security-reviewer / 06-code-reviewer / 07-scribe / 08-publisher
│   ├── 35-06-blogger-distiller.md     （博主蒸馏分析师 V1.4 12 维全息）
│   ├── 28-10-finance-data-base.md     （财经数据底座师）
│   └── .gitnexus/  shibazi/  zcf/
│
├── commands/                          ← 天龙 commands/（139 .md + 12 .sh · slash 命令）
│   ├── 00调研师.md  01架构师.md  ...（核心九部 CJK 文件名保留）
│   ├── INDEX.md                       （132 命令分类索引）
│   └── deepdive/  dragon-cli/  nine-dragons/  pm/  zcf/
│
├── memory/                            ← 天龙 memory/（120+ .md · 主题文件）
│   ├── MEMORY.md                      （142 行主索引）
│   ├── stage-25-announce.md ~ stage-50-announce.md
│   ├── a-stock-data-integration.md / agent-reach-integration.md / ...
│   ├── agpl-attribution-statements.md ⚠️
│   ├── mit-attribution-statements.md
│   ├── apache-attribution-statements.md
│   └── critical/  obsidian-mirror/
│
├── runtime/                           ← 天龙 hooks/ + scripts/ + plugins/
│   ├── hooks/                         （121 文件 · 9 个事件阶段）
│   │   ├── preToolUse/  postToolUse/  session-start/  session-end/
│   │   ├── userPromptSubmit/  utility/  on-demand/  bridge/  gitnexus/
│   ├── scripts/                       （51 文件 · 配置/审批/资源/账户管理）
│   │   ├── dragon-config.js / dragon.js
│   │   ├── resource-manager.js / account-manager.js
│   │   ├── build-index.py / gen-status-md.py
│   └── plugins/                       （289 文件 · 配置/工作流/trajectory-debug）
│
├── ip-profiles/                       ← 天龙 ip-profiles/（35 文件 · 3 人 IP 授权）
│   ├── laoli_bro_2026/                （老李 IP · 365 天授权至 2027-07-03）
│   ├── outdoor_lily/
│   └── tech_vc_bro/
│
├── index/                             ← 天龙自动生成索引（**1,224 资产**）
│   ├── INDEX_MASTER.json
│   ├── INDEX_README.md
│   ├── SKILLS.jsonl                   （784 行）
│   ├── AGENTS.jsonl                   （187 行）
│   ├── HOOKS.jsonl                    （90 行）
│   ├── COMMANDS.jsonl                 （156 行）
│   └── PLUGINS.jsonl                  （7 行）
│
├── docs/                              ← 天龙 docs/（9 文件 · 工作流图谱）
├── prompts/                           ← 天龙 prompts/（7 文件 · system prompt）
├── tests/                             ← 天龙 tests/（25 文件 · smoke/conformance）
├── market/                            ← 天龙 market/（15 文件 · 市场复盘产物）
├── output/                            ← 天龙 output/（6 文件 · 历史产物归档）
└── top-level/                         ← 天龙顶层入口文档
    ├── README.md                      （GitHub 仓库 README）
    ├── BIBLE.md                       （天龙引擎名片 · 给 AI 看的自我介绍）
    ├── CLAUDE.md                      （Claude 自动加载 · ≤6KB）
    ├── MEMORY.md                      （memory/ 主索引副本）
    ├── MAINTENANCE.md / REFERENCE_INDEX.md / STATUS.md / VERSION / package.json
```

## 2. 怎么用

### 2.1 只读检索（推荐）

直接读 `index/*.jsonl`，按需 `grep <id>` 后下钻到具体文件：

```bash
# 看天龙有哪些 skill
cat dragon-assets/index/SKILLS.jsonl | head -20

# 找博主相关的 skill
grep -i 'blogger\|holo' dragon-assets/index/SKILLS.jsonl

# 看某个 skill 的详细内容
cat dragon-assets/skills/async-task-pattern/SKILL.md
```

### 2.2 通过 DSH 治理包调用（Phase 2/3 后可用）

```ts
// 通过 packages/dragon-bridge/ 调用
import { dragonBridge } from '@deepseek-ai/dsh-experimental-dragon-bridge'

// 列所有 skill
const skills = await dragonBridge.list({ kind: 'skill' })

// 按 ID 查
const skill = await dragonBridge.get('async-task-pattern')

// 读 L0/L1 切片（命中后再读 L2）
const l0 = await dragonBridge.read('async-task-pattern', 'L0')
```

### 2.3 重新生成索引

```bash
python dragon-assets/runtime/scripts/build-index.py --include-library
```

## 3. License 治理（必读）

天龙资产遵循**三档 License**（详见 `LICENSE-ATTRIBUTION.md`）：

| License | 资产示例 | 治理策略 |
|---------|---------|---------|
| **MIT ✅** | async-task-pattern / nano-banana-brief / nuwa-skill / darwin-skill | 零红线 + 致谢上游 |
| **Apache-2.0 ✅** | a-stock-data-bridge / agent-reach / html-anything-bridge | NOTICE + Modified by 段 |
| **AGPL-3.0 ⚠️** | guizang-social-card-skill / cangjie-skill | **仅 PNG / 文档商单，禁止 SaaS 化** |
| **NOASSERTION ❌** | （天龙里几乎没有）| NO-GO 拒收 |

**核心红线**：
- ❌ 把 AGPL 资产（如 guizang）部署为 SaaS / 网络服务
- ❌ 删除上游 LICENSE 全文 + 致谢声明
- ❌ 把 muapi 生成结果标成"博主本人手绘"
- ❌ 在无 IP 授权时输出博主风格内容（必查 `ip-profiles/<id>/ip_consent.txt`）

## 4. 同步策略（增量更新怎么做）

```bash
# 重新同步（robocopy 镜像模式）
robocopy "C:\Users\li\.claude\projects\dragon-engine\skills" \
         "D:\deepseek-harness\dragon-assets\skills" \
         * /MIR /R:0 /W:0 /NP /NDL /NFL

# 同步后清理
powershell -File D:\deepseek-harness\scripts\dragon-cleanup.ps1

# 重建索引
python dragon-assets\runtime\scripts\build-index.py
```

详见 `DRAGON_SYNC_PLAN.md` 与即将落地的 `DRAGON_INTEGRATION.md`。

## 5. 与 DSH 主仓的关系

```
D:\deepseek-harness\
├── packages/                          ← DSH Cordis 包（强类型、强约束）
│   ├── skill/                         ← 原生 skill 能力
│   ├── skill-index/                   ⭐ Phase 2A 新建
│   ├── agent-roster/                  ⭐ Phase 2B 新建
│   ├── license-policy/                ⭐ Phase 2C 新建
│   ├── dragon-bridge/                 ⭐ Phase 3A 新建（@deepseek-ai/dsh-experimental-*）
│   └── ...
│
├── dragon-assets/                     ← 本目录 · 纯数据层
│   └── (天龙 21225 文件)
│
├── DRAGON_SYNC_PLAN.md                ← 同步计划
└── DRAGON_INTEGRATION.md              ⭐ Phase 3C 将写
```

**核心约束**：DSH 主仓的 release 包**不依赖** `dragon-assets/`。`dragon-bridge`（experimental）是唯一允许调用本目录的入口。

## 6. 不做的事

- ❌ 不在 `dragon-assets/` 跑 git commit（让上游 DSH 主仓使用者自行决定）
- ❌ 不修改天龙任何文件（只读 + 镜像 + 清理）
- ❌ 不引入天龙 `index/` 之外的二进制（图片/PDF 仅同步 metadata）
- ❌ 不重写天龙 skill 为 Cordis plugin（5-10x 工作量，留给 Phase 4+）
- ❌ 不引入 AGPL 资产到 DSH release 包

## 7. 版本

- **天龙镜像版本**: V2.5（2026-08-04 快照）
- **DSH 镜像日期**: 2026-08-27
- **同步源**: `C:\Users\li\.claude\projects\dragon-engine\`
- **维护者**: li
- **配套文档**: `DRAGON_SYNC_PLAN.md` · `LICENSE-ATTRIBUTION.md`
