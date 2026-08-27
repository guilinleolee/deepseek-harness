# 天龙引擎 dragon-engine V2.5

> **26 阶段集成 · 819 PASS · ~107k ⭐ 上游资产 · MIT ✅ 零红线 + AGPL ⚠️ 红线双轨 · 三模态闭环 + 视频 + 9 平台分发**

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![License: AGPL-3.0](https://img.shields.io/badge/license-AGPL--3.0-orange.svg)](https://www.gnu.org/licenses/agpl-3.0.html)
[![Skills](https://img.shields.io/badge/skills-73%20SKILL.md%20%2B%204%20new-green.svg)](./skills)
[![Tests](https://img.shields.io/badge/tests-602%20PASS-brightgreen.svg)](./skills/async-task-pattern/tests/smoke.sh)

## 这是什么？

天龙引擎是一个**多模态内容生产引擎**——博主全息克隆 + 多模态工业化生成 + 9 平台分发 + 金融数据底座 + 自进化记忆。本仓是天龙引擎 **V2.5（2026-07-27）** 的真主树，包含：

- ✅ **4 个新 skill**（cinema-director-laoli / nano-banana-brief / async-task-pattern / generative-media-skills）
- ✅ **73 个 muapi 多模态 SKILL.md 镜像**（generative-media-skills/library/）
- ✅ **guizang V2.0 端到端 pipeline**（博主全息 → 小红书 6 页 carousel + 公众号封面 PNG）
- ✅ **MIT ✅ + AGPL-3.0 ⚠️ 双轨合规**（详见 [合规模板](skills/generative-media-skills/LICENSE)）

## 快速上手（5 分钟）

```bash
# 1. 克隆
git clone https://github.com/guilinleolee/dragon-engine.git
cd dragon-engine

# 2. 看 README（BIBLE.md 是详细 spec，本 README 是入口）
cat README.md

# 3. 跑 smoke test
bash skills/async-task-pattern/tests/smoke.sh
# 预期：20/20 PASS
```

## 资产地图

```
skills/
├── async-task-pattern/         # 4 原语（submit/poll/upload/download）+ 5 adapter
├── cinema-director-laoli/      # 8 套老李风电影分镜
├── nano-banana-brief/          # GPT-Image2 4 维推理 brief
├── generative-media-skills/    # 73 个 muapi 多模态 SKILL.md + tags.json
│   ├── library/{motion(28),visual(32),social(7),edit(2),workflow(1),_core(3)}
│   ├── LICENSE                 # 真上游 MIT（1 KB）
│   └── scripts/mirror-upstream.sh
├── blogger-fingerprint-registry/  # 博主指纹 DB 升级 util
├── blogger-hologram-to-poster/   # V1.0 桥接路径
├── guizang-social-card-skill/    # AGPL-3.0 · V2.0 pipeline（小红书 + 公众号）
├── _archive/                   # DEPRECATED 历史资产
├── memory/                     # 30 个主题文件（integration / 合规）+ MEMORY.md 主索引
├── agents/                     # 4 个 35-06 博主蒸馏分析师（V1.0/V1.1/V1.3/V1.4 · 56 KB）
└── skills-v2/                  # 11 个根级 V2/V3 skill（gpt-image-2-* 6 + voxcpm-* 3 + multi-platform-publisher + blogger-fingerprint-registry · 1.5 MB · ⚠️ 不含 .db）
```

## 21 阶段能力矩阵

| # | 能力 | 关键资产 |
|---|------|---------|
| 1 | **三模态闭环** | gpt-image-2 + VoxCPM2 + khazix/laoli-writer |
| 2 | **博主全息克隆** | 12 维指纹（V1.4）|
| 3 | **老李风** | laoli-writer + cinema-director-laoli + 35-02/35-05/35-06 |
| 4 | **多模态生成（200+ 模型）** | generative-media-skills + 73 SKILL.md |
| 5 | **异步任务统一接口** | async-task-pattern（20/20 PASS）|
| 6 | **AGPL 视觉专精** | guizang V2.0（67s 7 PNG + publisher 14 行）|
| 7-21 | **... 详见 [BIBLE.md 详细 spec]** | |

## 调用协议 · 如何用？

### 自然语言 trigger（36 个）

中文 28 + 英文 8。完整列表见 [BIBLE.md §4.1](./BIBLE.md)（本 README 不重复）。

### 一段 prompt 启动

```
你是天龙引擎。先读 README.md + BIBLE.md + skills/ 目录。
当用户说 X：① 出图/视频/音频 → 调 skills/async-task-pattern/adapters/muapi.sh
② 小红书图文 → 调 skills/guizang-social-card-skill/pipeline/blogger-poster.mjs --blogger <id>
③ 老李风短视频 → 调 skills/cinema-director-laoli + agents/35-05 V11
④ AGPL 自动加版权声明；⑤ MIT 致谢。
```

### 一键博主出图（老李实跑 67s 7 PNG）

```bash
cd skills/guizang-social-card-skill
node pipeline/blogger-poster.mjs --blogger laoli_bro_2026
# 预期：67s 后 5 张小红书 carousel + 2 张公众号封面 + publisher.db 14 行 success
```

## 协同矩阵（核心 4 个 skill）

```
cinema-director-laoli V1.0 (老李 8 套分镜)
        ↓ 喂分镜 JSON
35-05 V11 (老李风 + cinema + async-task 12 步)
        ↓ 调 muapi 200+ 模型
async-task-pattern V1.0 (4 原语 + 5 adapter · 20/20 PASS)
        ↓ 异步执行
generative-media-skills V1.0 (73 SKILL.md · MIT ✅)
        ↓ 9 平台分发
multi-platform-publisher V1.0
```

## 🗂 资产索引（自动生成 · 推荐阅读入口）

1,157 个资产（5 类）已自动索引为 `index/` 下 5 个 jsonl + INDEX_MASTER.json + INDEX_README.md。**先查索引再读原文**，避免 LLM 上下文过载：

| 文件 | 资产数 | 用途 |
|---|---|---|
| [`index/SKILLS.jsonl`](./index/SKILLS.jsonl) | 759 | 全部 skill（含 muapi library 递归） |
| [`index/AGENTS.jsonl`](./index/AGENTS.jsonl) | 174 | agent 角色定义 |
| [`index/HOOKS.jsonl`](./index/HOOKS.jsonl) | 82 | 钩子脚本 |
| [`index/COMMANDS.jsonl`](./index/COMMANDS.jsonl) | 126 | 命令 |
| [`index/PLUGINS.jsonl`](./index/PLUGINS.jsonl) | 16 | plugin |

```bash
# 重新生成（自动抓取 SKILL.md frontmatter + LICENSE/NOTICE + git log）
python scripts/build-index.py --include-library

# 健康检查 · 4 类断言
python tests/test_index.py

# 状态看板（3 节：资产 / 质量 / CJK 误码）
python scripts/gen-status-md.py        # -> STATUS.md

# CJK 误码文件 runbook（手 git mv 用）
python scripts/check-cjk-filenames.py --emit-runbook docs/cjk-rename-runbook.md
```

工具目录：[docs/tools/catalog.md](./docs/tools/catalog.md) · 详情见
[CLAUDE.md §4.5](./CLAUDE.md#45-三层索引检索协议自动生成-必走) 三层索引协议（Hot → Warm → Cold）。

## ⚙️ 核心脚本（P0/P1/P2）

> **2026-08-17 新增** · 本地优先配置 + 项目隔离 + 审批工作流

### P2: 统一配置入口

```bash
# 配置管理器
node scripts/dragon-config.js get active_project          # 获取当前项目
node scripts/dragon-config.js list-projects             # 列出所有项目
node scripts/dragon-config.js path drafts               # 获取路径
node scripts/dragon-config.js init --force             # 初始化
```

### P1: 项目隔离增强

```bash
# 资源包管理器
node scripts/resource-manager.js init --blogger <id>   # 初始化资源包
node scripts/resource-manager.js list --blogger <id>    # 列出资源包

# 账户管理器
node scripts/account-manager.js init --blogger <id>   # 初始化账户
node scripts/account-manager.js add --blogger <id> --platform xiaohongshu
node scripts/account-manager.js list --blogger <id>    # 列出账户
```

### P0: 审批工作流

```bash
# 审批 CLI
node scripts/dragon.js init                            # 初始化工作流
node scripts/dragon.js list                           # 列出草稿
node scripts/dragon.js review <draft_id>              # 预览/进入审核
node scripts/dragon.js approve <draft_id>             # 批准发布
node scripts/dragon.js reject <draft_id> --reason "..." # 拒绝
node scripts/dragon.js status <draft_id>              # 查看状态
```

### npm 快捷脚本

```bash
npm run config    # dragon-config.js
npm run resource  # resource-manager.js
npm run account   # account-manager.js
npm run dragon   # dragon.js
```

## 🔀 工作流可视化 ⭐NEW

> **[docs/workflow/README.md](docs/workflow/README.md)** · 5 大核心 pipeline 的 Mermaid 流程图

| Pipeline | 入口 | 验证 |
|----------|------|------|
| 博主全息出图 | `blogger-poster.mjs` | 67s 7 PNG ✅ |
| 老李风分镜 | `cinema-director-laoli` | 6/6 PASS ✅ |
| 异步任务接口 | `async-task-pattern/` | 19/19 PASS ✅ |
| 财经数据底座 | `em_base.py` | 茅台 24 rows ✅ |
| 三模态闭环 | BIBLE.md §3 | 351 爆款矩阵 ✅ |

## 合规

| 上游 | License | 用法 |
|------|---------|------|
| SamurAIGPT/Generative-Media-Skills | **MIT ✅** | 73 SKILL.md 镜像 + 200+ 模型路由 |
| op7418/guizang-social-card-skill | **AGPL-3.0 ⚠️** | 仅 PNG 商单交付，禁止 SaaS |
| OpenBMB/VoxCPM | Apache-2.0 | TTS 推理 |
| freestylefly/awesome-gpt-image-2 | 7.7k ⭐ | 视觉 prompt 库 |
| alchaincyf/huashu-design | 21.5k ⭐ | 设计底座 |

**AGPL-3.0 红线**：guizang 资产仅交付 PNG / 输出图片，禁止作为 SaaS / 网络服务分发。

## 累计验证 · 602 PASS

| 来源 | PASS |
|------|------|
| async-task-pattern smoke | 20/20 |
| Layer 3 e2e（nano-banana-brief + cinema-director-laoli）| 12/12 |
| guizang V2.0 端到端 | 7 PNG + 14 publisher success |
| 蒸馏三件套（nuwa + cangjie + darwin）· 阶段 35 | 49/49 |
| 金融底座三件套（a-stock + global + trading-agents）· 阶段 25 | 84/84 |
| mneme-heat-engine（借鉴 dsh-mneme）· 阶段 41 | 12/12 |
| 历史 1-20 阶段 | 571/571 |
| **合计** | **819** |

## 版本演进

| 版本 | 日期 | 关键 |
|------|------|------|
| V1.0 | 2026-06-17 | P0-P3 集成 · 8 个新 skill |
| V2.0 | 2026-07-20 | 阶段 21 + cinema/nano-banana/async-task/generative-media 4 新 + 73 镜像 + 35-06 V1.4 12 维 |
| **V2.5** | 2026-07-27 | 阶段 22-43 · 26 阶段集成 · 蒸馏三件套 · 金融底座 · mneme 自进化 · 1,224 资产 |

## 文档

- **[BIBLE.md](./BIBLE.md)** · 11.7 KB · 天龙引擎名片（给 AI 看的自我介绍）
- **[MEMORY.md](./memory/MEMORY.md)** · 142 行主索引
- **[generative-media-skills-integration.md](./memory/generative-media-skills-integration.md)** · 9 KB · 阶段 21 整合文档
- **[mit-attribution-statements.md](./memory/mit-attribution-statements.md)** · 10 KB · MIT 致谢模板
- **[agpl-attribution-statements.md](./memory/agpl-attribution-statements.md)** · 5 KB · AGPL 致谢模板
- 全部 30 个主题文件（integration / 合规）见 [memory/](./memory/)

## Agent（35-06 博主蒸馏分析师链路）

| 版本 | 文件 | 行数 | 关键 |
|------|------|------|------|
| V1.0 | [35-06-blogger-distiller-v10.md](./agents/35-06-blogger-distiller-v10.md) | ~150 | 6 维视觉指纹基线 |
| V1.1 | [35-06-blogger-distiller-v11-voxcpm.md](./agents/35-06-blogger-distiller-v11-voxcpm.md) | ~350 | 7 维全息（+ VoxCPM2 声音指纹）|
| V1.3 | [35-06-blogger-distiller-v13-ugc.md](./agents/35-06-blogger-distiller-v13-ugc.md) | ~170 | 10 维全息（+ UGC 视频化 3 子维）|
| **V1.4** | [35-06-blogger-distiller-v14-style.md](./agents/35-06-blogger-distiller-v14-style.md) | ~210 | **12 维全息**（+ 视频风格 + 文案风格 · Style Library 子集 8+8）|

## 根级 V2/V3 skill（skills-v2/ · 11 个）

| License | Skill | 用途 |
|---------|-------|------|
| MIT | gpt-image-2-api-integration | gpt-image-2 API 集成 |
| MIT | gpt-image-2-bridge | gpt-image-2 桥接 |
| MIT | gpt-image-2-gallery-explorer | 544 案例 gallery 探索 |
| MIT | gpt-image-2-prompt-library | 21 模板 prompt 库 |
| MIT | gpt-image-2-style-library | 21 风格库 |
| MIT | gpt-image-2-voxcpm-bridge | 图音一致性打分桥 |
| Apache-2.0 + MIT | voxcpm-multi-speaker | 多说话人 |
| Apache-2.0 + MIT | voxcpm-tts-integration | TTS 集成 |
| Apache-2.0 + MIT | voxcpm-voice-distillery | 声音指纹蒸馏 |
| 自研 | multi-platform-publisher | 9 平台一键发布 |
| 自研 | blogger-fingerprint-registry | 博主指纹 DB（不含 .db） |

⚠️ **本仓不包含 SQLite 数据库**（博主指纹 DB + 发布任务 DB · 个人 IP 数据）—— 必须本地持有

## 下一批

- 🔴 MUAPI_API_KEY 拿到后激活 73 个 SKILL.md
- 🟡 批量博主一键出图（registry → V2.0 → publisher）
- 🟢 35-05 V12（接入 muapi Seedance 真推理）

---

🤖 Generated with [Claude Code](https://claude.com/claude-code)
Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>

> **天龙视角 · 入口索引**：本 README 是 GitHub 仓库的入口。详细 spec 见 [BIBLE.md](./BIBLE.md)。调用协议见上 §调用协议。一段 prompt 启动见 §一段 prompt 启动。
2026-07-23 13:23:45 — test commit for hook

2026-07-23 13:27:25 — test commit for hook

test-token-fix-639204215790269668
