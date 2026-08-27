# CLAUDE.md · 天龙引擎 dragon-engine V2.5

> **用途**：Claude Code / Claude Desktop 启动天龙引擎时自动加载（≤ 6KB · 加载即就绪）
>
> **更新日期**：2026-07-27（深度扫盘修订）
>
> **配套文件**：[BIBLE.md](BIBLE.md) · [MEMORY.md](memory/MEMORY.md) · [skills/00-INDEX.md](skills/00-INDEX.md)

---

## 0. 一句话

我是 **天龙引擎 dragon-engine V2.5** —— **26 阶段集成** + **~3,800 SKILL.md** + **~325 agents** + **~160 commands** + **3 IP 授权 + ≥611 PASS** + **~107k ⭐ 上游资产**。

## 1. 真·全量家底（2026-07-27 实扫 + A1/A2 sync 已完成 · 2026-08-05 index 系统接管）

| 维度 | 数字 | 位置 |
|---|---|---|
| **集成阶段** | **26** + **35** + **26.1 子阶段** | MEMORY.md §1 |
| **主仓索引（自动 · 2026-08-05 实测）** | **1,157 资产** | `index/{SKILLS,AGENTS,HOOKS,COMMANDS,PLUGINS}.jsonl` |
| └ skills（--include-library） | 759 | 5 jsonl 之 SKILLS.jsonl |
| └ agents | 174 | AGENTS.jsonl |
| └ hooks | 82 | HOOKS.jsonl |
| └ commands | 126 | COMMANDS.jsonl（**含 8 个 GBK 错码**）|
| └ plugins | 16 | PLUGINS.jsonl |
| **SKILL.md 总数** | ~3,830 | 主仓 ~120 + V8-restored 3,786 |
| **agents 总数** | ~325 | 主仓 5（35-06×4 + 28-10）+ V8-restored 321（含历史版本） |
| **commands** | ~160 | V8-restored 全仓 |
| **skills 一级目录** | ~213 | 主仓 38（sync 后）+ V8-restored 175 |
| **plugins（系统级）** | 17 | `~/.claude/plugins/` |
| **templates/** | 22+ | CoT/Few-Shot/RAG/ReAct 等 |
| **hooks/** | 70+ | dragon-commander V8 系列 |
| **IP 授权** | 3 人 | laoli_bro_2026 / outdoor_lily / tech_vc_bro |
| **累计验证 PASS** | ≥812 | 25 阶段 605 + 26 阶段 +2 + 35 阶段 49 + nuwa/cangjie/darwin 锁 |
| **GitHub ⭐ 上游** | ~107k | a-stock-data 7,555 + global-stock-data 1,199 + anysearch 4,446 + xhs-visual-director 1,065 + nuwa 29.6k + cangjie 6.2k + darwin 5.3k |

## 2. 双仓真相（必知·踩坑高发区）

| 仓 | 路径 | 角色 |
|---|---|---|
| **主仓**（生产中） | `C:\Users\li\.claude\projects\c--Users-li--claude\dragon-engine\` | 26 阶段当前生产 · **38 skills/（A1+A2 sync 后）+ 5 agents/** |
| **V8 仓**（2026-07-22 全量备份） | `C:\Users\li\.claude\projects\dragon-engine-V8-restored\` | 175 skills/ + **321 agents/** + 158 commands/ + BIBLE.md 11.7 KB |

⚠️ **常见误判**：只看主仓会得到"9 skills / 4 agents"——这是 95% 漏算。**任何"天龙引擎有多少"的盘点必须双仓合并**。

## 3. 触发词典（自然语言路由）

### 3.1 听到这些就出图/视频/音频
> "出图" "配图" "短片" "短视频" "分镜" "配音" "海报" "封面" "UGC" "seedance" "nano-banana brief"
> → `skills/generative-media-skills/library/*`（74 个 SKILL.md）+ `skills/async-task-pattern/adapters/muapi.sh`（首选）或主仓 `nano-banana-brief/` `cinema-director-laoli/`

### 3.2 听到这些走博主全息 / 老李风
> "博主全息" "博主克隆" "老李风" "khazix 风" "分镜脚本" "社媒文案"
> → `agents/35-06-blogger-distiller-v14-style.md`（指纹）→ `skills/cinema-director-laoli/scripts/generate.sh`（老李分镜）→ `skills/guizang-social-card-skill/pipeline/blogger-poster.mjs --blogger <id>`
> ⚠️ **必查** `~/.claude/ip-profiles/<id>/ip_consent.txt` 在有效期内

### 3.3 听到这些走 9 平台分发
> "9 平台分发" "工业化生产" "一键发布" "小红书/公众号/视频号/抖音/YouTube/TikTok/X/LinkedIn/微博"
> → `~/.claude/skills/multi-platform-publisher/scripts/publisher.py`
> → 或 V8 仓 `skills/multi-platform-publisher/` 11 个 SKILL.md

### 3.4 听到这些走合规/版权
> "AGPL 合规" "MIT 合规" "Apache-2.0 合规" "版权声明" "致谢" "LICENSE" "红线"
> → AGPL：仅交付 PNG / 方法论总结商单（guizang / cangjie）
> → MIT：自动附加 `memory/mit-attribution-statements.md`（含 §十二 nuwa + darwin 致谢）
> → Apache-2.0：自动附加 `memory/apache-attribution-statements.md`

### 3.5 听到这些走财经数据底座
> "股票数据" "A 股" "港股" "美股" "a-stock" "global-stock" "财经底座" "60-01 CIO" "64 量化"
> → `skills/a-stock-data-bridge/` + `skills/global-stock-data-bridge/`（Apache-2.0 NOTICE）
> → `agents/28-10-finance-data-base.md` ⭐NEW

### 3.6 听到这些走三件套（蒸馏 + 进化）
> "蒸馏 XX" "造 XX 的 skill" "女娲" "nuwa"
> → `skills/nuwa-skill/`（蒸馏人·29.6k⭐·MIT ✅）

> "拆 XX" "蒸馏这本书" "把 XX 书做成 skill" "cangjie"
> → `skills/cangjie-skill/`（蒸馏书·6.2k⭐·7 阶段 RIA-TV++·AGPL ⚠️）

> "优化 skill" "skill 评分" "达尔文" "darwin" "skill 怎么样"
> → `skills/darwin-skill/`（skill 自动进化·5.3k⭐·9 维 rubric + hill climbing·MIT ✅）
> ⚠️ **必跑** Phase 0.5 neat-freak V1.1 红线 gate（`l3-specs/darwin-neat-freak-bridge.md`）

### 3.7 听到这些就直接拒绝
> "把 guizang / cangjie 部署成 SaaS" "把 muapi 生成说成原创手绘" "在无 IP 授权时输出博主风格" "把 cangjie 7 阶段 / 21 packs 作为知识付费课程售卖"
> → 拒绝并解释合规边界（见 [BIBLE.md §5](BIBLE.md)）

## 4. 调用协议 · 跑实操前必做 3 件套

1. **读 spec**：`BIBLE.md` + `memory/MEMORY.md` + 本文件 `CLAUDE.md`
2. **同步主根**：把 `c--Users-li--claude/dragon-engine` 拉到 working tree
3. **smoke test**：跑 `tests/smoke.sh` 至少 1 轮，期望 PASS ≥ 611

### 跑实操中必做
- **AGPL 资产**：读 `memory/agpl-attribution-statements.md` 加版权声明（不能漏）
- **MIT 资产**：读 `memory/mit-attribution-statements.md` 致谢上游
- **Apache-2.0 资产**：读 `memory/apache-attribution-statements.md` 致谢上游
- **老李风 IP 检查**：`~/.claude/ip-profiles/laoli_bro_2026/ip_consent.txt` 必须在 expires_at > now

### 跑实操后必做
- 复盘 GitHub muapi/ai-clipping/seedance-2/rednote-cover 等上游，新 L3 spec 触达 → mirror 进天龙
- 测 `guizang V2.0` 端到端：67 秒 7 PNG + publisher.db ≥ 14 行 success
- 跑 `skill-updater scan.sh` 看 skill 现状（V1.1.3 · 已知 9 个天龙集成版自动走 AUTO_HINTS）

## 4.5 三层索引检索协议（自动生成 · 必走）

用 **hot → warm → cold** 三层模型取代了"靠人脑翻 README"：

| 层 | 资源 | 大小 | 何时读 |
|---|---|---|---|
| **Hot** | `CLAUDE.md` §3 触发词路由表（本文件） | ≤6 KB | 每次 prompt 自动加载 |
| **Warm** | `index/{SKILLS,AGENTS,HOOKS,COMMANDS,PLUGINS}.jsonl` | 5 个 · 共 ~485 KB | 命中触发词后，按 `kind` 加载对应 jsonl，再 `grep` 路由 |
| **Cold** | 原始资产文件（SKILL.md / *.md / *.sh / *.json） | 按需 · 单文件 | 路由命中 `id` 后精确加载 |

> ⚠️ **1,097 资产不可进上下文**——必须走索引。**禁止直接 `cat skills/<x>/SKILL.md` 来盘点资产**。
>
> - 自检：`python tests/test_index.py`（4 类断言 · 全绿才算索引健康）
> - 重生成：`python scripts/build-index.py [--kind skill|agent|hook|command|plugin]`
> - 状态看板：`python scripts/gen-status-md.py` → `STATUS.md`（3 节：资产 / 质量 / CJK 误码）
> - CJK 误码修复 runbook：`python scripts/check-cjk-filenames.py --emit-runbook docs/cjk-rename-runbook.md`
> - 入口：`index/INDEX_MASTER.json` + `index/INDEX_README.md` + `STATUS.md`
>
> 路由示例（伪）：
> ```
> 用户说「a股投研」→ hot §3.5 命中 → warm 加载 SKILLS.jsonl
>   → grep '"a股"' → 命中 a-stock-data-bridge / a-stock-data
>   → cold 读 skills/a-stock-data-bridge/SKILL.md
> ```

## 5. 关键路径速查

```
主仓：  C:\Users\li\.claude\projects\c--Users-li--claude\dragon-engine\
V8 仓： C:\Users\li\.claude\projects\dragon-engine-V8-restored\（全量·2026-07-22）
归档： D:\知识库\天龙引擎\dragon-engine-backup-20260722\（1.12 GB · 56k 文件）
商业： gitee.com/guilinleolee/tianlong-engine-commercial-materials @ main
远程： gitee.com/guilinleolee/claude-config-backup @ v8-restored-20260722

BIBLE.md           主仓 / V8 仓根目录 · 11.7 KB · 21 阶段对齐 + V2.5 增补
MEMORY.md          主仓 memory/ · ≤140 行索引 · 26 阶段清单
memory/主题文件    主仓 memory/ · 31 个 integration + 合规声明
agents/            主仓（4 个 35-06 最新版） + V8 仓（321 个历史）
skills/            主仓（9 个一级） + V8 仓（175 个一级）
skills-v2/         主仓 11 个 V2 升级版
prompts/           主仓 · README + local-replicate.md + local-upgrade.md
ip-profiles/       ~/.claude/ip-profiles/ · 3 个 IP 授权
index/             ⭐NEW 5 个 jsonl + INDEX_MASTER.json + INDEX_README.md（自动生成，详见 §4.5）
```

## 6. 边界 · 版权红线（5 类不可踩）

| ❌ 错 | ✅ 对 |
|--------|--------|
| 把 guizang 当 SaaS 部署（AGPL 网络服务） | 仅交付 PNG 商单（AGPL § 13 例外） |
| 删 guizang / SamurAIGPT / a-stock-data 版权声明 | 保留 LICENSE 全文 + 致谢上游 |
| 把 muapi 生成结果标成「博主本人手绘」 | 「多模态生成」 ≠ 「原创手绘」 |
| 用 emoji / "beautiful" / "cinematic 8k" 空泛词 | 用具体描述（"牛皮纸咖啡馆 + 50mm 镜头"） |
| 不跑 smoke test 就 merge 新 skill | 必跑 `tests/smoke.sh` 至少 1 轮 |

## 7. 下一阶段候选

| 优先级 | 任务 | 资产 |
|--------|------|------|
| 🟡 P1 | sync V8→主仓（安全版：仅主仓 missing 的 skills/agents/commands，最小变化）| `sync-dragon-to-codex.{bat,ps1}` |
| 🟡 P1 | 完成 28-10 财经数据底座师端到端冒烟 | `28-10-finance-data-base.md` + a-stock/global-stock bridge |
| 🟢 P2 | 老李 / outdoor_lily / tech_vc_bro 三博主 IP 授权批量到 2027 | `~/.claude/ip-profiles/` |
| 🔵 P3 | skill-updater V1.2 加 → checks-against-INTEGRATED_SKILLS 自动 A/B | `skill-updater/` |
| 🔵 P3 | publisher V2.0 OpenAPI 真实发布（替换 mock） | `multi-platform-publisher` |

## 8. 版本信息

- **Version**: 2.5
- **Author**: 天龙引擎集成 + li
- **License**: MIT（本文档）+ 各 skill 自带 license
- **Source**: 天龙引擎主根 + V8-restored 全量仓
- **Last Updated**: 2026-07-27（深度扫盘修订）
- **配套文档**: [BIBLE.md](BIBLE.md) · [MEMORY.md](memory/MEMORY.md) · [skills/00-INDEX.md](skills/00-INDEX.md)

---

> **天龙视角 · 入口索引**：本文档是给 Claude 自动加载的"天龙引擎使用说明"。任何 Claude 应用启动后读这份 + BIBLE.md + MEMORY.md，就能立刻复刻 26 阶段能力。触发协议见 §3，调用 3 件套见 §4。

## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

Rules:
- For codebase questions, first run `graphify query "<question>"` when graphify-out/graph.json exists. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).
