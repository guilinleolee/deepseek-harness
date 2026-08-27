# skills/00-INDEX.md · 天龙引擎 SKILL 全量索引 V2.8

> **更新日期**：2026-08-22（SEO/GEO融合系统完成）
>
> **作用**：V8-restored 仓 175 个 skills 的归类索引（主仓 9 个 + skills-v2 11 个单独列）
>
> **来源**：[`dragon-engine-V8-restored/skills/`](../../../../projects/dragon-engine-V8-restored/skills/) + [`dragon-engine/skills/`](../skills/) + [`~/.claude/skills/`](../../../../skills/)

---

## 0. 全量数字（2026-07-27 实扫 + A1/A2 sync 已完成）

| 仓 | 一级 skills 数 | SKILL.md 数 | 角色 |
|---|---|---|---|
| **主仓** `dragon-engine/skills/` | **44** ⭐sync 后（9 + A2 +4 + A1 +25 + 阶段35 +3 + 本批 +2 + gpt-image）| ~126（含二级） | **26 阶段当前生产** · slim 同步版 |
| **V8-restored** `dragon-engine-V8-restored/skills/` | 175 | 3,786（含子目录） | **全量恢复版** · 2026-07-22 备份 |
| **`skills-v2/`** 主仓 | 11 | 11 | V2 升级版（gpt-image-2-* / voxcpm-*） |
| **`~/.claude/skills/`** | 17 | ~50 | 用户全局 V2/V3 顶层 skill |
| **合计去重** | **~213 一级** | **~3,830 SKILL.md** | |

⚠️ 主仓 → V8 仓增量 = **137 个 skills**（V8 仓 175 - 主仓 38 = 137）。这些仍是潜在 sync 候选（绝大多数是实验性 / 老版本，未纳入本次 A1/A2 范围）。

---

## 1. 主仓 38 个核心 skills（26 阶段生产部署 · A1+A2 sync 后）

### 1.1 25 阶段原 9 个
| Skill | 版本 | 用途 | 上游协议 |
|---|---|---|---|
| `async-task-pattern/` | V1.0 | 4 原语 + 5 adapter 异步任务统一 | 自研 |
| `blogger-fingerprint-registry/` | V3.0 | 10 维博主指纹库 | 自研 |
| `blogger-hologram-to-poster/` | V1.0 | 博主全息 → 多平台 PNG | 自研 |
| `blogger-poster/` ⭐NEW | V1.0 | 博主全息 → 多平台发布（整合版）| 自研 |
| `cinema-director-laoli/` | V1.0 | 老李风 8 套电影分镜 | 自研 |
| `generative-media-skills/` | V1.0 | 78 个 muapi SKILL.md（74 已镜像） | MIT ✅ |
| `guizang-social-card-skill/` | V2.0 | 28 版式 × 10 主题 PNG 商单 | AGPL ⚠️ |
| `nano-banana-brief/` | V1.0 | GPT-Image2 reasoning brief | MIT ✅ |
| `skill-updater/` | V1.1.3 | report-only GitHub 上游检查器 · 55 PASS | 自研 |
| `_archive/map-component-V1.0-DEPRECATED.md` | V1.0 🟡DEPRECATED | 模式地图组件（已并入 guizang V2.0）| AGPL ⚠️ |

### 1.2 A2 增量（4 个 · 阶段 26 财经底座）
| Skill | 版本 | 用途 | 上游协议 |
|---|---|---|---|
| `a-stock-data-bridge/` ⭐NEW | V1.0 | 43 端点+15 源 A 股数据 | Apache-2.0 |
| `global-stock-data-bridge/` ⭐NEW | V1.0 | 17 端点+5 源 港美欧日韩 | Apache-2.0 |
| `a-stock-data/` ⭐NEW | V3.4.0 | 上游 7,555⭐ simonlin1212 镜像 | Apache-2.0 |
| `00-INDEX.md` ⭐NEW | V2.5 | 本文件 · 175 skills 索引 | 自研 |

### 1.3 A1 增量（25 个 · anysearch + baoyu）
| Skill | 版本 | 用途 | 上游协议 |
|---|---|---|---|
| `anysearch/` ⭐NEW | V1.0 | 4 CLI 客户端 + runtime.conf 真源 | Apache-2.0 |
| `anysearch-academic/` ⭐NEW | V1.0 | 学术场景封装 | Apache-2.0 |
| `anysearch-business/` ⭐NEW | V1.0 | 商业场景封装 | Apache-2.0 |
| `anysearch-finance/` ⭐NEW | V1.0 | 金融场景封装（与 a-stock-data 互补）| Apache-2.0 |
| `baoyu-skills/` ⭐NEW | V1.0 | 22 件套父目录（占位）| MIT ✅ |
| `baoyu-{article-illustrator,comic,compress-image,cover-image}/` × 4 | V1.0+ | 图文/漫画/压缩/封面 | MIT ✅ |
| `baoyu-{danger-gemini-web,danger-x-to-markdown}/` × 2 | V1.0+ | 高危 web 抓取 | MIT ✅ |
| `baoyu-{diagram,electron-extract,format-markdown,image-gen}/` × 4 | V1.0+ | 图表/抽取/格式化/出图 | MIT ✅ |
| `baoyu-{infographic,markdown-to-html,post-to-wechat,post-to-weibo}/` × 4 | V1.0+ | 信息图/Html/发布 | MIT ✅ |
| `baoyu-{post-to-x,slide-deck,translate,url-to-markdown}/` × 4 | V1.0+ | X 发布/幻灯片/翻译/抓取 | MIT ✅ |
| `baoyu-{wechat-summary,xhs-images,youtube-transcript}/` × 3 | V1.0+ | 微信摘要/小红书图/YouTube 转写 | MIT ✅ |
| `baoyu-skills-integration/` | V1.0+ | 整合器 | MIT ✅ |

### 1.4 阶段 35 增量（3 个 · 蒸馏三件套 · 41.1k⭐ · MIT×2 + AGPL×1）
| Skill | 版本 | 用途 | 上游协议 |
|---|---|---|---|
| `nuwa-skill/` ⭐NEW | V1.0 | 蒸馏人·29.6k⭐·5 维人物 skill + test-prompts.json (darwin 兼容) | MIT ✅ |
| `cangjie-skill/` ⭐NEW | V1.0 | 蒸馏书·6.2k⭐·7 阶段 RIA-TV++ 元流水线 + 21+ packs + AGPL 三档商用 | AGPL ⚠️ |
| `darwin-skill/` ⭐NEW | V2.1 | skill 自动进化·5.3k⭐·9 维 rubric + hill climbing + Phase 0.5 neat-freak gate | MIT ✅ |

### 1.5 ⭐本批升级（联网去痕 2 件套 · 2026-08-05）
| Skill | 版本 | 用途 | 上游协议 |
|---|---|---|---|
| `web-access/` ⭐UPGRADE | **v2.5.3**（原 v2.4.1）| 给 Claude Code 完整联网：WebSearch / WebFetch / curl / Jina / CDP 五层调度 + 浏览器自动化 + 站点经验积累 + 本地书签/历史搜索（find-url.mjs）| MIT ✅ |
| `humanizer-zh/` ⭐NEW | V1.0 | 去除 AI 写作痕迹（24 种模式）· 中文版 · 基于 Wikipedia Signs of AI writing | MIT ✅ |

> **主仓 + skills-v2（11 V2 升级版）+ ~/.claude/skills（17）= 主仓实际命中生产 72+ skill**

### ⭐OPC融合新增（2026-08-17 · xiaobei × dragon-engine）

> 来源：xiaobei/TeamWiseFlow × dragon-engine融合
> License：OpenClaw开源 + MIT

| Skill/Agent | 版本 | 用途 | 上游协议 |
|---|---|---|---|
| `opc-content-calibrator/` | V1.0 | 7维内容打分+盲预测+复盘+rubric进化 | OpenClaw ✅ |
| `opc-lead-hunting/` | V1.0 | 潜客挖掘（策略A/B）+多平台联动 | OpenClaw ✅ |
| `opc-investor-pipeline/` | V1.0 | 投资人发掘→材料→触达→状态跟踪 | OpenClaw ✅ |
| `bd-record/` | V1.0 | BD记录（潜客追踪+触达历史+状态管理）| OpenClaw ✅ |
| `ir-record/` | V1.0 | IR记录（投资人信息+触达+状态追踪）| OpenClaw ✅ |
| `agents/opc-suite/` | V2.0 | OPC协调Agent（P0审批流+P1项目隔离+P2配置）| OpenClaw+MIT |

> **OPC能力**：内容校准 × 潜客挖掘 × 投资人关系 = 完整商业闭环
> **融合点**：博主全息克隆 + 三模态生成 + 9平台分发 + 28-10财经底座

### 1.6 ⭐本批新增（dbskill v2.18.15 · 14 件套 · 2026-08-06）
源：`github.com/dontbesilent2025/dbskill` · shallow clone 到 `dragon-engine/skills/dbskill/`；按需拷贝 14 个全新 sub-skill 到主仓。

| Skill | 版本 | 用途 | 上游协议 |
|---|---|---|---|
| `dbs-agent-migration/` ⭐NEW | v2.18.15 | Agent 迁移到 dbs 工作台 | BY-NC ⚠️ |
| `dbs-bridge/` ⭐NEW | v2.18.15 | bridge-skill.sh 跨平台 skill 桥接（含脚本） | BY-NC ⚠️ |
| `dbs-content-system/` ⭐NEW | v2.18.15 | 内容资产工程化脚手架（294K · 7 templates + scaffold/rules + 2 docs）| BY-NC ⚠️ |
| `dbs-decision/` ⭐NEW | v2.18.15 | 长期决策记录与回放 | BY-NC ⚠️ |
| `dbs-good-question/` ⭐NEW | v2.18.15 | 澄清概念、目标与问题 | BY-NC ⚠️ |
| `dbs-knowledge/` ⭐NEW | v2.18.15 | 文件夹知识库治理 + 导航 + 健康检查 | BY-NC ⚠️ |
| `dbs-resonate/` ⭐NEW | v2.18.15 | 文稿共鸣 / 逻辑 / 传播性检查 | BY-NC ⚠️ |
| `dbs-script-flow/` ⭐NEW | v2.18.15 | 短视频脚本节奏与钩子 | BY-NC ⚠️ |
| `dbs-skill-cleaner/` ⭐NEW | v2.18.15 | 本地 skill 风险审查（**带删除动作** · 使用前必读 SKILL.md） | BY-NC ⚠️ |
| `dbs-spread/` ⭐NEW | v2.18.15 | 内容传播性诊断 | BY-NC ⚠️ |
| `dbs-standard-answer/` ⭐NEW | v2.18.15 | 同构案例矩阵 + 条件性答案 | BY-NC ⚠️ |
| `dbs-update/` ⭐NEW | v2.18.15 | dbskill 系统更新入口 | BY-NC ⚠️ |
| `dbs-wechat-html/` ⭐NEW | v2.18.15 | 公众号 HTML 排版（templates/styles.md）| BY-NC ⚠️ |
| `dbs-xhs-title/` ⭐NEW | v2.18.15 | 小红书标题生成（739 行） | BY-NC ⚠️ |

> 主仓 dbskill sub-skill 总计：**30 个**（29 业务 + 1 统一入口 /dbs），其中 **14 个**本次新建、**16 个**仍为旧版（详见 §9 升级候选清单）。
> 上游健康检查 `tools/check-skill-routing-contract.py` ✅ PASS。

### 1.7 ⭐本批升级（dbskill v2.18.15 · 14 个旧 SKILL.md 覆盖 · 2026-08-06）
源：上一批 16 个同名旧 SKILL.md 中除主入口与 austrian 外，全部覆盖到上游 v2.18.15。旧版备份：`skills/.bak-upgrade-20260806-114920/`。

| Skill | 旧 → 新字节（Δ）| 用途变更 | 推荐度 |
|---|---|---|---|
| `dbs-diagnosis/` ⭐UPGRADE | 3,596 → 21,094（+17,498） | 商业模式诊断大扩充 | ⭐⭐⭐⭐⭐ |
| `dbs-slowisfast/` ⭐UPGRADE | 4,960 → 12,644（+7,684） | 慢就是快主题深化 | ⭐⭐⭐⭐⭐ |
| `dbs-action/` ⭐UPGRADE | 3,079 → 10,589（+7,510） | 执行力诊断 | ⭐⭐⭐⭐⭐ |
| `dbs-goal/` ⭐UPGRADE | 4,282 → 11,200（+6,918） | 目标清晰化 | ⭐⭐⭐⭐ |
| `dbs-learning/` ⭐UPGRADE | 9,641 → 15,626（+5,985） | 交互式学习 | ⭐⭐⭐⭐ |
| `dbs-hook/` ⭐UPGRADE | 4,770 → 10,569（+5,799） | 短视频开头优化 | ⭐⭐⭐⭐ |
| `dbs-ai-check/` ⭐UPGRADE | 6,821 → 12,455（+5,634） | AI 写作特征识别 | ⭐⭐⭐⭐ |
| `dbs-save/` ⭐UPGRADE | 6,081 → 11,430（+5,349） | 诊断存档 | ⭐⭐⭐⭐ |
| `dbs-benchmark/` ⭐UPGRADE | 4,412 → 9,375（+4,963） | 对标分析 | ⭐⭐⭐⭐ |
| `dbs-content/` ⭐UPGRADE | 5,850 → 10,006（+4,156） | 内容创作诊断 | ⭐⭐⭐⭐ |
| `dbs-report/` ⭐UPGRADE | 6,571 → 9,876（+3,305） | 诊断报告 | ⭐⭐⭐⭐ |
| `dbs-restore/` ⭐UPGRADE | 5,573 → 8,052（+2,479） | 接续诊断 | ⭐⭐⭐ |
| `dbs-chatroom/` ⭐UPGRADE | 7,904 → 9,308（+1,404） | 定向聊天室 | ⭐⭐⭐ |
| `dbs-deconstruct/` ⭐UPGRADE | 8,241 → 8,929（+688） | 概念拆解 | ⭐⭐⭐ |

> **未升级项（保留旧版）**：`dbs/` 主入口（路由表 `/dbskill` → `/dbs` 触发词改动）· `dbs-chatroom-austrian/`（行为变更：旧=奥地利学派追问工具；新=哈耶克×米塞斯×Claude 三人聊天室）。
> 增量合计 **+78,070 B**（约 +76 KB 知识密度）。升级后上游 `tools/check-skill-routing-contract.py` 复跑 ✅ PASS，4 件套全检（marketplace-scope / plugin-update-contract / release-versions）全过。

### 1.8 ⭐本批新增（mano-cua · 2026-08-18）
源：`github.com/Mininglamp-AI/mano-skill` · VLA 视觉语言动作模型驱动的桌面 GUI 自动化
License：MIT-0

| Skill | 版本 | 用途 | 上游协议 |
|---|---|---|---|
| `mano-cua/` ⭐NEW | V1.1.0 | 桌面 GUI 自动化：自然语言驱动 VLA 模型执行点击/输入/滚动/拖拽等视觉界面操作。支持本地离线模式（macOS Apple Silicon）和云端模式。| MIT-0 ✅ |

> **功能亮点**：混合视觉模型自动选择（Mano-P 轻量快速 + Claude 深度推理）、隐私优先本地模式、跨平台支持（macOS 稳定 / Windows / Linux Beta）

### 1.9 ⭐本批新增（65-02 个股档案分析师 · 2026-08-18）
源：`github.com/quantskills/skill-a-share-stock-dossier` · A股个股多维度档案 Agent Skill
License：GPL-3.0

| Skill/Agent | 版本 | 用途 | 上游协议 |
|---|---|---|---|
| `65-02-stock-dossier/` ⭐NEW | V1.0 | A股个股档案：资金流向/股东变化/估值分析/研报摘要/龙虎榜/融资融券/公告解读（10+维度）| GPL-3.0 ⚠️ |
| `agents/65-02-stock-dossier.md` ⭐NEW | V1.0 | 个股档案分析师岗位：多维度数据采集→指标计算→档案渲染→完整性校验 | GPL-3.0 ⚠️ |
| `pandadata-api/` ⭐NEW | V1.0 | Pandadata API skill：60+接口/资金流/研报/融资融券，支持 Claude Code/Codex、Cursor、OpenAI | GPL-3.0 ⚠️ |
| `pandadata-api/scripts/` | - | Runtime SDK + 兼容层 + 设置脚本 | GPL-3.0 ⚠️ |

> **功能亮点**：10+维度个股档案生成、数据溯源到接口级别、与 65-01 市场复盘分析师形成"个股-市场"双覆盖
> **协作关系**：28-10 财经数据底座（上游）→ 65-02 个股档案 → 65-01 市场复盘（下游）

### 1.10 ⭐本批新增（免费数据三件套 · 2026-08-18）
源：`D:\tongmuye` 项目提取 + baostock + akshare + mootdx
License：BSD-3-Clause + MIT

| Skill | 版本 | 用途 | 上游协议 |
|---|---|---|---|
| `baostock-api/` ⭐NEW | V1.0 | 免费A股数据：日线/财务/分红，零门槛无需注册，来源于东方财富 | BSD-3-Clause ✅ |
| `akshare-api/` ⭐NEW | V1.0 | 免费多市场：港股/美股/期货/外汇/基金/宏观，来源于同花顺/新浪 | MIT ✅ |
| `mootdx-api/` ⭐NEW | V1.0 | 免费实时：A股实时行情/分时/盘口，通达信数据源 | MIT ✅ |
| `free-stock-data/requirements.txt` ⭐NEW | - | 免费数据源统一依赖清单 | - |

> **功能亮点**：零门槛免费数据、A股+港股+美股+期货全覆盖、与 tongmuye 项目同源
> **协作关系**：baostock(历史) + mootdx(实时) + akshare(多市场) = 完整免费数据底座

### 1.10 ⭐本批新增（66-03 期货深度分析师 + pandadata-deepview · 2026-08-18）
源：`github.com/quantskills/skill-futures-deepview-analyst` · 期货 DeepView 专项分析
License：GPL-3.0

| Skill/Agent | 版本 | 用途 | 上游协议 |
|---|---|---|---|
| `pandadata-deepview/` ⭐NEW | V1.0 | Pandadata DeepView 期货分析 skill：38个接口（席位博弈/期限结构/仓单库存/跨期套利）| GPL-3.0 ⚠️ |
| `agents/66-03-futures-analyst.md` ⭐NEW | V1.0 | 期货深度分析师岗位：四种分析模式（席位博弈/结构研判/库存现货/全品种扫描）| GPL-3.0 ⚠️ |
| `commands/futures-analysis.md` ⭐NEW | V1.0 | 期货分析快捷命令：触发 66-03 Agent + pandadata-deepview SKILL | GPL-3.0 ⚠️ |

> **功能亮点**：填补天龙引擎期货分析空白、与 65-01 市场复盘形成股期双轨、严格的事实/推断分离约束
> **协作关系**：65-01 市场复盘（股债现货视角）→ 66-03 期货深度（期货席位结构视角）→ 64-02 算法交易员（执行）

### 1.11 ⭐本批新增（MCP集成中心 · 2026-08-19）
源：自研 · 基于 GitHub modelcontextprotocol 生态
License：MIT ✅

| Skill/Agent/Command | 版本 | 用途 | 协议 |
|---|---|---|---|
| `mcp-integration/` ⭐NEW | V1.0 | MCP集成中心：10个内置MCP服务+5个远程MCP客户端（地理编码/GEO分析/Schema生成/llms.txt） | MIT ✅ |
| `mcp-integration/scripts/mcp_client.py` ⭐NEW | - | 内置MCP客户端：连接池、按需实例化 | MIT ✅ |
| `mcp-integration/scripts/mcp_remote.py` ⭐NEW | - | 远程MCP客户端：DataForSEO/Firecrawl/Exa/Tavily/Brave | MIT ✅ |
| `mcp-integration/scripts/cli.py` ⭐NEW | - | MCP CLI命令行工具 | MIT ✅ |
| `mcp/` ⭐NEW | - | MCP服务器注册表：mcp-registry.json | MIT ✅ |
| `mcp/geo-mcp-server/` ⭐NEW | - | 地理MCP服务器配置 | MIT ✅ |
| `agents/40-01-mcp-orchestrator.md` ⭐NEW | V1.0 | MCP编排器Agent：智能路由MCP调用到最合适服务 | MIT ✅ |
| `commands/mcp.md` ⭐NEW | V1.0 | MCP命令入口：`/mcp` | MIT ✅ |

> **功能亮点**：按需调用MCP服务（无需预配置连接）、内置10个GEO/SEO服务、远程服务支持Firecrawl网页抓取/Exa语义搜索/Tavily AI搜索
> **协作关系**：seo-geo → mcp-integration → geo-content-generator（GEO数据流）/ 01调研师（竞品扫描）/ 04验证师（引用检查）

## 2. V8-restored 仓 175 个 skills 主题分类

### 2.1 🚀 AI/Agent 框架（~22 个）
```
agent-browser / agent-browser-skill        # 浏览器自动化
agent-federation                            # 多 agent 联邦
agent-harness-construction                 # agent 脚手架
agent-payment-x402                         # x402 支付协议
agent-reach + agent-reach-integration      # 联网协议（7.5k⭐）
agents-list / agent-teams-playbook         # agent 列表与协作
agentverse                                 # agent 生态
ai-csuite                                  # AI 决策层
ai-first-engineering                        # AI 优先工程
ai-regression-testing                      # AI 回归测试
ai-three-tier-fallback                     # 三层 fallback
airstrip-one-trigger                       # Airstrip One 触发器
```

### 2.2 📝 内容/写作（~15 个）
```
academic-paper / advertising-copy / article-page-generator
blog-page-generator / brainstorming
careers-page-generator / changelog-page-generator
chinese-copywriting-rules / claude-checkpoints
content-templates (子)/ about-page-generator
alternatives-page-generator / category-page-generator
copywriting 系列
creator-buddy                       # 公众号/小红书/视频全栈创作工具箱（2026-08-05 新增 · 源 SpaceZephyr/creator-buddy）
```

### 2.3 🎨 视觉/设计/AGPL（~10 个）
```
aetherviz-master / alphagbm / alphagbm-skills
app-ads / blogger-distill-{competitor-monitor,orchestration,verify-gate}
brand-{asset-protocol,guidelines,protection,visual-generator}
breadcrumb-generator / canvas-design / carousel
```

### 2.4 🎬 视频/多媒体（~9 个）
```
baoyu-{comic,infographic,slide-deck,youtube-transcript,image-gen}
character-design-prompts / cinematic 系列
cinema-director 系列 / drone-style-video / freeze-effect-video
ugc-video-factory / product-video-ad-maker / music-video
```

### 2.5 🌐 营销/分销/平台（~25 个）
```
aitoearn-{engage,mcp,monetize,publish}    # 一键发布四件套
app-ads / auto-redbook-skills              # 小红书自动化
bidding-document-generator                  # 投标文档
bilibili-operations / brand-protection
china-risk-matrix / china-traffic-tactics
china-viral-content-analyzer
claw-{auto-research,autoresearch-loop}
```

### 2.6 🔍 研究/分析（~10 个）
```
10-02-ai-researcher / academic-paper
analyst / any2pdf-pro
ai-news-radar-scout / analytics-tracking
backlink-analysis / baidu-index / backtest-framework
research 系列
```

### 2.7 🛠 工具/CLI/基础设施（~14 个）
```
adapter 系列 / analyzers
api-{auth-patterns,design}
architect / backend-patterns
benchmark / benchmark.sh / beads
beads-skill / booster / builder
bundle-manager
```

### 2.8 💻 开发/工程（~16 个）
```
aider-pair-programming / ai-regression-testing
ce-{agent-native-checker,knowledge-compound,review-style}
ceo-advisor / claude-api / claude-mem
claude-mem-skill / claude-to-im
claude-hooks-project
```

### 2.9 💰 金融/量化（~9 个）
```
a-stock-data + a-stock-data-bridge ⭐NEW（阶段 26）
anysearch-finance / backtest-framework
charlie-cfo-bootstrapped / claude-ceo-advisor
finance 系列
```

### 2.10 🧪 数据/隐私（~5 个）
```
17-08-data-privacy-compliance-skill
api-design / analytics-tracking
data-eng 系列
```

### 2.11 🤖 agent/角色（~25 个 — V8 独有）
```
45-01电商运营 / 35-02-social-media
35-06-博主蒸馏分析师
404-page-generator / about-page-generator
a-class / b-class / c-class             # 角色 ABC 分级
capa-officer / ceo-advisor / ceo-advisor
chinese-copyright-application
claude-mem / claude-mem-skill
card / card-dealing / carousel
case-simulator-cn / checkpoint-recovery
caveman-{commit,eval-harness,file-compress,review,terse}
china-viral-content-analyzer
claude-api / claude-to-im
```

### 2.12 🔐 合规/法务（~6 个）
```
china-risk-matrix / chinese-copyright-application / chinese-copywriting-rules
citation-verify / claude-mem-skill
compliance 系列
```

### 2.13 🌏 中文/出海（~6 个）
```
auto-redbook-skills / bilibili-operations / china-risk-matrix
china-traffic-tactics / china-viral-content-analyzer
chinese-copyright-application / chinese-copywriting-rules
```

### 2.14 📦 baoyu 21 件套（~21 个 · 已合并到主仓 baoyu 系列）
```
baoyu-{article-illustrator,comic,compress-image,cover-image}
baoyu-{danger-gemini-web,danger-x-to-markdown}
baoyu-{diagram,electron-extract,format-markdown,image-gen}
baoyu-{infographic,markdown-to-html,post-to-wechat,post-to-weibo}
baoyu-{post-to-x,skills-integration,slide-deck,translate,url-to-markdown}
baoyu-{wechat-summary,xhs-images,youtube-transcript}
```

### 2.15 🧰 浏览器/Playwright（~5 个）
```
browserbase-{integration,skill}
browser-harness-core / browser-profile-manager
browser-qa / browser-testing
browser-use-{agent,cloud,ecosystem,mcp,workflow}
```

### 2.16 🎁 其他（~20 个）
```
advertising-copy / affiliate-{marketing,page-generator}
aetherviz-master / airdrop 系列
algorithmic-art (+.md) / alphagbm
analytics-tracking / api-{auth-patterns,design}
app-ads / architect / article-page-generator
artifact-output-contract / artifacts-builder.md
atlassian-{admin,templates}
autogenesis / auto-{redbook-skills,research-claw,research-loop}
awesome-claude-skills-repo
```

---

## 3. 全局 ~/.claude/skills/ 17 个顶层 skill

```
agent-reach                  # 15 渠道联网（7.5k⭐ V1.5.0）
blogger-fingerprint-registry # 10 维博主指纹 V3.0
gpt-image                    # GPT Image 2 原版（wuyoscar 官方 · 162 提示词画廊）
gpt-image-2-api-integration  # OpenAI 图
gpt-image-2-bridge           # 图桥梁
gpt-image-2-gallery-explorer # 案例库
gpt-image-2-prompt-library   # 提示词库
gpt-image-2-style-library    # 风格库（21 模板·544 案例·24 风格）
gpt-image-2-voxcpm-bridge    # 图音桥
last30days                   # 30 天热点
lib-bingling-v2              # 教学库
multi-platform-publisher     # 9 平台分发
tmpril6rz4k                  # 临时测试
voxcpm-multi-speaker         # 多说话人
voxcpm-streaming             # 流式 TTS
voxcpm-tts-integration       # TTS 集成（31.7k⭐）
voxcpm-voice-distillery      # 博主声音指纹蒸馏
摸鱼绿公众号封面.png         # 测试素材
```

## 4. skills-v2/ 主仓 11 个 V2 升级版

| skill | 升级点 |
|---|---|
| `blogger-fingerprint-registry/` V3 → V2 | V3 同步到 V2 |
| `gpt-image-2-{api-integration,bridge,gallery-explorer,prompt-library,style-library,voxcpm-bridge}/` × 6 | V2 同步 |
| `multi-platform-publisher/` V2.0 | 9 平台 |
| `voxcpm-{multi-speaker,tts-integration,voice-distillery}/` × 3 | V2 同步 |

## 5. plugins/ 系统级 17 个（~/.claude/plugins/）

```
code-review / feature-dev / frontend-design / hookify
pr-review-toolkit / ralph-wiggum / security-guidance
commit-commands / learning-output-style / explanatory-output-style
plugin-dev / claude-hud / agent-sdk-dev / claude-opus-4-5-migration
+ repos/ marketplaces/ + installed_plugins.json（当前安装清单）
```

## 5.1 tikhub-plugin（2026-08-11 新增 · 自媒体工作台采集层）

> **来源**：`plugins/tikhub/`（GitHub TikHub/tikhub-plugin v1.1.0 · MIT）· 19 个 skills 复制到 `skills/_tikhub/`
> **用途**：社交媒体数据采集（用户需求采集 + 爆款挖掘），7 平台 MCP 已注册到 `~/.claude.json`（12 个 MCP）
> **前置**：需在 `~/.claude/settings.json` 的 env 配置 `TIKHUB_API_KEY`（注册 https://user.tikhub.io 获取）
> **关联**：[[秉凌自媒体工作台]] · TikHub采集层选型决策

| Skill | 用途 |
|------|------|
| `tikhub-onboarding` | 入口：获取 key / 路由 |
| `tikhub-mcp` / `tikhub-rest-api` / `tikhub-python-sdk` | 三种接入方式 |
| `social-listening` | ⭐ 用户需求采集（关键词→评论→情感→主题） |
| `comments-analysis` | ⭐ 评论分析（情感/主题/问题） |
| `trend-research` / `hashtag-research` | ⭐ 爆款/话题挖掘 |
| `creator-analytics` / `competitor-analysis` | 博主/竞品分析（爆款拆解） |
| `douyin` / `xiaohongshu` / `tiktok` / `instagram` / `youtube` / `twitter-threads` | 平台专项 |
| `social-media-downloader` / `bulk-data-export` | 下载 / 批量导出 |

## 5.2 demand-refiner（2026-08-11 新增 · 自媒体工作台需求层）

> **来源**：`skills/demand-refiner/`（秉凌自研 · v1.0.0）· 自媒体工作台核心
> **用途**：把采集到的用户评论/笔记 → LLM 痛点聚类 → 结构化《需求库》（高频痛点/高频问题/用户画像/选题建议）
> **输入**：TikHub social-listening 采集结果 或 手动整理的评论文本
> **配套脚本**：`scripts/prepare.py`（清洗去重 + 跨文档词频统计，纯标准库）
> **关联**：[[秉凌自媒体工作台]] · demand-refiner · 需求提炼

| 步骤 | 说明 |
|------|------|
| Step 1 | 准备数据（JSON 数组，含 text/source/platform） |
| Step 2 | 文本清洗（去广告/水军/表情/链接） |
| Step 3 | LLM 痛点聚类（痛点/问题/购买意向/正反馈/观望 5 分类） |
| Step 4 | 生成《需求库》Markdown（保存到 ~/viral-content-reports/demand-library/） |
| Step 5 | 反馈到内容生产（天龙 /viral） |

## 5.3 blogger-distiller（2026-08-11 更新为官方完整版 · 自媒体工作台爆款拆解层）

> **来源**：`skills/blogger-distiller/`（GitHub otter1101/blogger-distiller · **MIT 可商用**）· 博主蒸馏器
> **用途**：输入博主名 → 采集 TA 的笔记 → 三层蒸馏（认知层/策略层/内容层）→ 产出 HTML 蒸馏报告 + 创作 Skill
> **模式**：A 拆解对标博主（学 TA）/ B 诊断自己账号（看自己）
> **数据源**：TikHub API（需 `TIKHUB_API_TOKEN`，已复用现有 Key 配置）
> **入口**：`python run.py "<博主名>"`（串联 Phase 0 环境检查 → 0.5 交互 → 1 采集 → 2 分析 → 3 蒸馏）
> **更新记录**：2026-08-11 由脚本版替换为官方完整版（新增 run.py/install.py/check_env.py/LICENSE/assets/references）
> **关联**：[[爆款拆解层-blogger-distiller接入评估]] · 自媒体工作台

| 环节 | 说明 |
|------|------|
| Phase 0 | check_env.py 环境准备（Python/依赖/TikHub Token/Whisper） |
| Phase 0.5 | 交互确认（平台/模式/数量 30-50-80/口播） |
| Phase 1 | crawl_xhs / crawl_douyin 数据采集（TikHub API） |
| Phase 2 | analyze.py 统计分析（标题模式/CTA/藏赞比/发布频率） |
| Phase 3 | deep_analyze.py 生成 AI Prompt → 宿主 AI 完成 HTML 报告 + 创作 Skill |

> **注意**：原 `blogger-distiller.bak-20260811/` 为脚本版备份，确认新版可用后清理

## 5.4 content-review-dashboard（2026-08-11 新增 · 自媒体工作台数据复盘层）

> **来源**：`skills/content-review-dashboard/`（秉凌自研 · v1.0.0）· 自媒体工作台第⑤层
> **用途**：记录发布内容表现数据（阅读/点赞/评论/收藏/转发/涨粉）→ 生成数据复盘看板 → 识别爆款与低效内容 → 反哺选题
> **配套脚本**：`scripts/run_dashboard.py`（CSV 读写：add/list/stats 三个子命令）
> **数据**：`~/viral-content-reports/dashboard/posts.csv`
> **关联**：[[数据复盘看板-规划方案]] · 自媒体工作台

| 命令 | 说明 |
|------|------|
| `add` | 记录内容（平台/标题/类型/互动数据/涨粉/备注） |
| `list` | 查看内容列表（可按平台过滤） |
| `stats` | 汇总统计（KPI + 平台分布 + TOP3） |

> **Streamlit UI**：天龙 UI「📊 数据复盘」菜单（KPI 卡 + 趋势图 + 平台分布 + TOP5 + 低效内容 + 录入表单）

## 5.5 content-publisher（2026-08-11 新增 · 自媒体工作台发布层）

> **来源**：`skills/content-publisher/`（秉凌自研 · v1.0.0）· 自媒体工作台第④层
> **用途**：把一篇内容生成多平台适配发布包（标题/正文/标签/封面文案），配合 PostBot 浏览器扩展一键同步发布
> **配套**：`third-party/postbot-extension/`（PostBot v1.2.3 扩展已下载）+ `third-party/PostBot安装指南.md`
> **关联**：[[秉凌自媒体工作台]] · PostBot · 内容发布

| 平台 | 适配要点 |
|------|---------|
| 小红书 | 标题≤20字口语钩子 / 短句正文 + emoji / 话题标签 |
| 抖音 | 前3秒口播钩子 / 脚本结构 / 话题标签 |
| 公众号 | 标题≤25字 / 结构化长文 + 配图 |
| 知乎 / B站 | 问题式标题 / 深度回答 / 标签 |

> **Streamlit UI**：天龙 UI「🚀 内容发布」菜单（PostBot 引导 + 发布包生成）

## 6. 索引维护说明

- **本文件刷新原则**：每次新 skill 进入主仓或 V8 仓后更新一次（否则可读 `ls dragon-engine-V8-restored/skills/ | sort`）
- **同步方向**：主仓 ← V8 仓（V8 是备份源，主仓是生产裁剪版）
- **备份源地址**：`git@github.com:.../claude-config-backup.git @ v8-restored-20260722`（远程）+ `D:\知识库\天龙引擎\dragon-engine-backup-20260722\`（本地归档 1.12 GB）
- **生产部署顺序**：主仓 9 + skills-v2 11 + ~/.claude/skills 17 = **37 个高频调用的 skill**

## 7. 主题文件 31 个（memory/）

> 见 [MEMORY.md](memory/MEMORY.md) §关键文件路径段

```
agent-reach-integration     # V1.5.0
agpl-attribution-statements # AGPL 红线
aihot-integration           # 阶段 10 热点追踪
anysearch-integration       # 阶段 24 Apache-2.0
apache-attribution-statements # Apache-2.0 红线（⭐最严格）
atutun-xhs-cover-integration
baoyu-skills-integration
blogger-hologram-to-poster (-v2)
book-distiller-v908-12
cross-ai-replication-prompt
generative-media-skills-integration
github-to-skills-v11
gpt-image-2-integration
guizang-{social-card-integration,v2-pipeline}
html-anything-integration
huashu-{design-integration,vs-guizang-course-redirect}
hv-analysis-integration
ip-diagram-creator-integration
khazix-{integration,v2-integration}
laoli-collaboration-integration
map-component-merge-decision
mcp-infrastructure
mit-attribution-statements
neat-freak-integration
voxcpm-integration
xhs-visual-director-integration
a-stock-data-integration ⭐NEW（待新增·阶段 26）
```

合计 **31 个**主题文件（不含 MEMORY.md 自身），新增 a-stock-data-integration.md 后即为 **32 个**。

---

## 8. 一键复刻清单（给任意 AI 应用）

```
1. 读 BIBLE.md（V1.0·21 阶段对齐）· 6 KB
2. 读 memory/MEMORY.md（142 行索引·26 阶段）· 8.7 KB
3. 读 CLAUDE.md（V2.5·精准版）· 6 KB
4. 读 skills/00-INDEX.md（本文件）· 8 KB
总上下文注入 ~28.7 KB（< 30 KB 限制），立刻复刻 26 阶段 + ~3,800 SKILL.md + ~325 agents 调度能力
```

> **天龙视角**：本索引是天龙引擎对外的"全资产地图"，任何盘点（媒体宣传 / 投资人介绍 / Claude 复刻）都基于本文件 + BIBLE.md + MEMORY.md 三件套。

---

## 6. SEO/GEO 技能体系 (2026-08-22 新增)

> 来源：5个GitHub仓库 · MIT/Apache-2.0
> 总计：112 Skills + 28 Agents

### 6.1 ⭐geo-seo-claude (zubair-trabzada · GEO优先SEO)

| Skill | 功能 | 来源 |
|-------|------|------|
| `geo-seo-claude/geo-audit.md` | GEO+SEO完整审计（并行子agent） | MIT |
| `geo-seo-claude/geo-citability.md` | AI引用可评分（ChatGPT/Claude/Perplexity） | MIT |
| `geo-seo-claude/geo-content.md` | GEO内容质量评估 | MIT |
| `geo-seo-claude/geo-crawlers.md` | AI爬虫访问检查 | MIT |
| `geo-seo-claude/geo-llmstxt.md` | llms.txt合规检查 | MIT |
| `geo-seo-claude/geo-platform-optimizer.md` | 平台专项优化 | MIT |
| `geo-seo-claude/geo-schema.md` | Schema.org优化 | MIT |
| `geo-seo-claude/geo-technical.md` | 技术SEO分析 | MIT |
| `geo-seo-claude/geo-brand-mentions.md` | 品牌提及分析 | MIT |
| `geo-seo-claude/geo-compare.md` | 竞品GEO对比 | MIT |
| `geo-seo-claude/geo-proposal.md` | GEO提案生成 | MIT |
| `geo-seo-claude/geo-prospect.md` | 潜客GEO分析 | MIT |
| `geo-seo-claude/geo-report.md` | 报告生成 | MIT |
| `geo-seo-claude/geo-report-pdf.md` | PDF报告 | MIT |
| `geo-seo-claude/geo-update.md` | GEO更新追踪 | MIT |

**Agents**: geo-ai-visibility, geo-content, geo-platform-analysis, geo-schema, geo-technical

### 6.2 ⭐seo-skill (aevans-eng · 轻量级SEO)

| Skill | 功能 | 来源 |
|-------|------|------|
| `seo-skill/SKILL.md` | 静态站点9点审计（meta/OG/Twitter/JSON-LD） | MIT |

### 6.3 ⭐claude-seo (AgriciDaniel · 全功能SEO)

| Category | Skills | 来源 |
|----------|--------|------|
| **Orchestrator** | seo.md | MIT |
| **Audit** | seo-audit, seo-page, seo-competitor-pages | MIT |
| **Content** | seo-content, seo-content-brief, seo-cluster, seo-sxo | MIT |
| **Technical** | seo-technical, seo-sitemap | MIT |
| **Schema** | seo-schema | MIT |
| **GEO/AI** | seo-geo | MIT |
| **Local** | seo-local, seo-maps | MIT |
| **Commerce** | seo-ecommerce | MIT |
| **Tools** | seo-dataforseo, seo-backlinks, seo-google, seo-image-gen, seo-images, seo-drift, seo-flow, seo-hreflang, seo-plan, seo-programmatic | MIT |

**Agents**: seo-backlinks, seo-cluster, seo-content, seo-dataforseo, seo-drift, seo-ecommerce, seo-flow, seo-geo, seo-google, seo-image-gen, seo-local, seo-maps, seo-performance, seo-schema, seo-sitemap, seo-sxo, seo-technical, seo-visual

### 6.4 ⭐claude-blog (AgriciDaniel · 博客+SEO)

| Command | 功能 | 来源 |
|---------|------|------|
| /blog write | 博客写作（5门交付合同） | MIT |
| /blog seo-check | SEO检查 | MIT |
| /blog geo | GEO优化 | MIT |
| /blog analyze | 内容分析 | MIT |
| /blog rewrite | 重写 | MIT |
| /blog translate | 翻译 | MIT |
| /blog localize | 本地化 | MIT |
| /blog cluster | 主题聚类 | MIT |
| /blog strategy | 策略规划 | MIT |
| /blog audit | 博客审计 | MIT |
| /blog brief | 简报生成 | MIT |
| /blog persona | 人物画像 | MIT |
| /blog brand | 品牌内容 | MIT |
| /blog schema | Schema生成 | MIT |

**Skills**: blog.md (orchestrator) + 31 sub-skills
**Agents**: blog-researcher, blog-reviewer, blog-seo, blog-translator, blog-writer

### 6.5 ⭐localseoskills (garrettjsmith · 本地SEO专家)

| Category | Skills | 来源 |
|----------|--------|------|
| **Audit** | local-seo-audit | MIT |
| **GBP** | gbp-optimization, gbp-posts, gbp-suspension-recovery, gbp-api-automation | MIT |
| **Citations** | local-citations | MIT |
| **Keywords** | local-keyword-research | MIT |
| **Content** | local-content-strategy, local-content-briefs, local-landing-pages | MIT |
| **Maps** | geogrid-analysis, local-maps | MIT |
| **Reviews** | review-management | MIT |
| **Link Building** | local-link-building | MIT |
| **PPC** | local-ppc-ads, local-search-ads, lsa-ads | MIT |
| **Reporting** | local-reporting, client-deliverables | MIT |
| **Multi-location** | multi-location-seo, service-area-seo | MIT |
| **MCP Tools** | localseodata-tool, dataforseo-tool, brightlocal-tool, semrush-tool, ahrefs-tool, local-falcon-tool, serpapi-tool, screaming-frog-tool, google-search-console-tool, google-analytics-tool, whitespark-tool, lsa-spy-tool, bing-places, apple-business-connect | MIT |
| **Dispatch** | dispatch (智能路由) | MIT |
| **Brief** | brief (持久化简报) | MIT |

### 6.6 SEO/GEO 协作关系

```
用户需求
    ↓
┌─────────────────────────────────────────┐
│  geo-seo-claude (15 skills)            │ ← GEO优先 · AI搜索
│  claude-seo (25 skills)                │ ← 全功能SEO
│  localseoskills (39 skills)            │ ← 本地SEO
│  claude-blog (32 skills)               │ ← 博客+SEO
│  seo-skill (1 skill)                  │ ← 轻量静态站
└─────────────────────────────────────────┘
    ↓
/seo audit <url>  →  完整SEO审计
/geo citability   →  AI引用评分
/blog write       →  博客写作+SEO
/seo local        →  本地SEO
```

### 6.7 快速使用

| 命令 | 场景 |
|------|------|
| `/seo audit <url>` | 全站SEO审计 |
| `/seo geo <url>` | GEO优化分析 |
| `/geo citability <url>` | AI引用评分 |
| `/seo local` | 本地SEO优化 |
| `/blog write <topic>` | SEO博客写作 |
| `/seo setup` | 初始化Python环境 |

### 6.8 ⭐SEO/GEO融合系统 (2026-08-22)

> 整合5个仓库的112个Skills + 28个Agents，形成统一编排体系

| 组件 | 路径 | 说明 |
|------|------|------|
| **编排Agent** | `agents/40-seo-orchestrator.md` | 统一调度所有SEO/GEO技能 |
| **统一Skill** | `skills/seo-orchestrator.md` | 命令路由和技能库 |
| **统一命令** | `commands/seo.md` | `/seo` 入口 |
| **GEO命令** | `commands/geo.md` | `/geo` 快捷命令 |

**融合结构**:
```
用户: /seo <需求>
    ↓
commands/seo.md → agents/40-seo-orchestrator.md
    ↓
智能路由到:
├── geo-seo-claude (15 skills)
├── claude-seo (25 skills)
├── localseoskills (39 skills)
└── claude-blog (32 skills)
    ↓
整合报告
```

**统一命令入口**:
- `/seo audit <url>` — 全站审计
- `/seo geo <url>` — GEO优先
- `/seo local <business>` — 本地SEO
- `/seo blog <topic>` — 博客写作
- `/seo compare <a> vs <b>` — 竞品对比
- `/seo quick <url>` — 快速评分

---

## 7. ⭐ Matt Pocock Skills 中文版 (mattpocock-skills-zh · 2026-08-22)

> **来源**：`github.com/devcxl/mattpocock-skills-zh`（Matt Pocock Skills 中文翻译版）
> **License**：MIT
> **用途**：AI Coding 最佳实践流程体系，包含工程流程、代码质量、团队协作等完整技能库

### 7.1 mattpocock-engineering（工程技能 · 18 个）

| Skill | 版本 | 用途 | 触发词 |
|---|---|---|---|
| `ask-matt/` ⭐NEW | V1.0 | 技能路由器：告诉你该用哪个技能 | `/ask-matt` |
| `codebase-design/` ⭐NEW | V1.0 | 模块形态设计：接口/深度/接缝/适配器 | `/codebase-design` |
| `code-review/` ⭐NEW | V1.0 | 双轴代码审查：标准 + 规格 | `/code-review` |
| `diagnosing-bugs/` ⭐NEW | V1.0 | 难啃 bug 诊断：紧反馈循环 + 回归测试 | `/diagnosing-bugs` |
| `domain-modeling/` ⭐NEW | V1.0 | 领域建模：术语打磨 + ADR 记录 | `/domain-modeling` |
| `grill-with-docs/` ⭐NEW | V1.0 | 盘问打磨：带文档痕迹的追问流程 | `/grill-with-docs` |
| `implement/` ⭐NEW | V1.0 | 实现流程：TDD 红绿切片驱动 | `/implement` |
| `improve-codebase-architecture/` ⭐NEW | V1.0 | 架构改进：揭示深化机会 | `/improve-codebase-architecture` |
| `prototype/` ⭐NEW | V1.0 | 原型验证：一次性代码回答设计问题 | `/prototype` |
| `research/` ⭐NEW | V1.0 | 后台调研：委托阅读 + 引用文档 | `/research` |
| `resolving-merge-conflicts/` ⭐NEW | V1.0 | 合并冲突：意图追溯解决 | `/resolving-merge-conflicts` |
| `setup-matt-pocock-skills/` ⭐NEW | V1.0 | 初始化：配置 issue 跟踪器 | `/setup-matt-pocock-skills` |
| `tdd/` ⭐NEW | V1.0 | 测试驱动开发：Mock/测试策略 | `/tdd` |
| `to-spec/` ⭐NEW | V1.0 | Spec 生成：对话 → 规范文档 | `/to-spec` |
| `to-tickets/` ⭐NEW | V1.0 | Ticket 拆分：示踪子弹式 issue | `/to-tickets` |
| `triage/` ⭐NEW | V1.0 | Issue 分类：agent 就绪输出 | `/triage` |
| `wayfinder/` ⭐NEW | V1.0 | 路径导航：大型项目的决策地图 | `/wayfinder` |
| `wizard/` ⭐NEW | V1.0 | 人工在环：只有人才能做的步骤 | `/wizard` |

### 7.2 mattpocock-productivity（生产力技能 · 7 个）

| Skill | 版本 | 用途 | 触发词 |
|---|---|---|---|
| `grilling/` ⭐NEW | V1.0 | 盘问原语：轮次/前沿/决策分离 | `/grilling` |
| `grill-me/` ⭐NEW | V1.0 | 无状态盘问：打磨不在工作目录的计划 | `/grill-me` |
| `handoff/` ⭐NEW | V1.0 | 交接协议：新环境/目录/同事的桥接 | `/handoff` |
| `teach/` ⭐NEW | V1.0 | 跨会话学习：有状态的概念训练 | `/teach` |
| `to-questionnaire/` ⭐NEW | V1.0 | 问卷生成：从别人脑中提取信息 | `/to-questionnaire` |
| `wait-what/` ⭐NEW | V1.0 | 上下文矫正：重新解释缺失信息 | `/wait-what` |
| `writing-for-agents/` ⭐NEW | V1.0 | Agent 文档编写：skills/AGENTS.md 参考 | `/writing-for-agents` |

### 7.3 mattpocock-misc（杂项技能 · 4 个）

| Skill | 版本 | 用途 | 触发词 |
|---|---|---|---|
| `git-guardrails-claude-code/` ⭐NEW | V1.0 | Git 保护栏：防止误操作 | `/git-guardrails-claude-code` |
| `migrate-to-shoehorn/` ⭐NEW | V1.0 | 迁移工具：到 shoehorn 模式 | `/migrate-to-shoehorn` |
| `scaffold-exercises/` ⭐NEW | V1.0 | 练习脚手架：训练任务生成 | `/scaffold-exercises` |
| `setup-pre-commit/` ⭐NEW | V1.0 | Pre-commit 配置 | `/setup-pre-commit` |

### 7.4 mattpocock-in-progress（开发中 · 5 个）

| Skill | 版本 | 用途 | 状态 |
|---|---|---|---|
| `claude-handoff/` ⭐NEW | V1.0 | Agent 交接协议 | 🔨 开发中 |
| `loop-me/` ⭐NEW | V1.0 | 循环执行 | 🔨 开发中 |
| `setup-ts-deep-modules/` ⭐NEW | V1.0 | TypeScript 深度模块 | 🔨 开发中 |
| `writing-beats/` ⭐NEW | V1.0 | 写作节拍 | 🔨 开发中 |
| `writing-fragments/` ⭐NEW | V1.0 | 写作片段 | 🔨 开发中 |
| `writing-shape/` ⭐NEW | V1.0 | 写作形态 | 🔨 开发中 |

### 7.5 Matt Pocock 技能体系架构

```
主干流程：想法 → 交付
    │
    ├── /grill-with-docs  ──── 盘问打磨想法
    │         │
    │         ├── /handoff ↔ /prototype  ── 设计问题绕道
    │         │
    │         ├── /to-spec  ──────────── 生成规范
    │         │         │
    │         │         └── /to-tickets  ─ 拆分成 ticket
    │         │                    │
    │         │                    └── /implement  ─ 驱动 TDD 实现
    │         │                              │
    │         │                              └── /code-review  ─ 双轴审查
    │         │
    │         └── /codebase-design  ───────── 模块形态设计
    │
    ├── /triage  ──────────────────── Issue 分类（外来 bug/请求）
    │
    ├── /diagnosing-bugs  ─────────── 难啃 bug 诊断
    │
    └── /wayfinder  ───────────────── 庞大项目的决策地图

独立技能：
    ├── /grill-me  ─ 无状态盘问
    ├── /resolving-merge-conflicts  ─ 合并冲突
    ├── /research  ─ 后台调研
    ├── /wizard  ── 人工在环
    ├── /teach  ─── 跨会话学习
    └── /wait-what  ─ 上下文矫正
```
