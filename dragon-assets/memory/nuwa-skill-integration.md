---
name: nuwa-skill-integration
description: alchaincyf/nuwa-skill (29.6k⭐ MIT) 天龙集成主题文件 · 阶段 35 · 蒸馏人 · 10/10 PASS
metadata:
  type: integration
  originSessionId: stage-35-nuwa-darwin-cangjie
  modified: 2026-08-04T11:28:43.729Z
heat: 0.7
last_ref_date: 2026-08-24
mneme_schema: v12.0
---


# nuwa-skill × 天龙引擎 · 阶段 35-A 集成主题文件

> **上游**：[alchaincyf/nuwa-skill](https://github.com/alchaincyf/nuwa-skill) · 29,592 ⭐ / 4,137 forks
> **License**：MIT ✅ © 2026 Huashu (花叔)
> **集成阶段**：天龙 35 · 周 1-A
> **累计 PASS**：10/10（test_nuwa_installation.py）
> **镜像路径**：`dragon-engine/skills/nuwa-skill/`
> **作者**：alchaincyf（同 darwin 作者）

---

## 1. 实跑元数据

| 维度 | 值 |
|---|---|
| GitHub URL | https://github.com/alchaincyf/nuwa-skill |
| Stars / Forks | 29,592 / 4,137 |
| License SPDX | MIT |
| 上游 LICENSE size | 1,072 B（verifies "MIT License" + "Copyright" + "Permission is hereby granted"）|
| 创建日期 | 2026-04（早期）|
| 最近 push | 2026-07-29 |
| 主语言 | Python |
| 镜像文件数 | 24（LICENSE + 5 README + SKILL.md + AGENT.md + HANDOFF.md + PRODUCT.md + 4 scripts + 3 references + 15 examples + l3-specs + .gitignore）|

---

## 2. 镜像拓扑

```
dragon-engine/skills/nuwa-skill/
├── LICENSE                                    ← 上游 verbatim（不可删 ©）
├── SKILL.md                                   ← 加天龙 frontmatter (license: MIT + upstream: {...})
├── README.md / README_EN.md / README_ES.md / README_JA.md / README_KO.md  ← 上游 verbatim
├── AGENT.md / HANDOFF.md / PRODUCT.md         ← 天龙扩展（不修改上游任何字节）
├── assets/                                    ← 上游镜像
├── examples/  (15 个人物样本: karpathy/musk/feynman/ilya/mrbeast/munger/naval/pg/jobs/yuchen/taleb/trump/x-mastery/zhangxuefeng/yiming)
├── references/  (extraction-framework.md · fidelity-scorecard.md · skill-template.md)  ← 上游 verbatim
├── scripts/  (download_subtitles.sh · merge_research.py · quality_check.py · srt_to_transcript.py)
├── promo/                                     ← 上游镜像
├── .github/                                   ← 上游镜像
├── l3-specs/                                  ← MIT 子包装增强（天龙本地）
│   └── README.md  (nuwa-laoli-bridge / cangjie-test-prompts-schema / quality-check-v1)
├── scripts/nuwa_check.py                      ← 天龙 check 脚本 (exit code 0/1/2/3 契约)
├── tests/test_nuwa_installation.py            ← 10 项 pytest PASS
├── .gitignore                                 ← 天龙扩展
└── wechat-qrcode.jpg / 6-agents-parallel.png / advisory-board.png / cover-distill-minds.png / x-thread-en.md  ← 上游 verbatim
```

---

## 3. 能力矩阵（5 维 · 蒸馏人）

| 维度 | 内容 |
|---|---|
| **心智模型** | 3-7 个核心心智模型（每个有「仅 X 会这么说」字样）|
| **决策启发式** | 1-2 步可执行决策框架（带 A2 触发场景）|
| **表达 DNA** | 句式 / 词汇 / 语气 / 节奏 / 口头禅（≥3 特征）|
| **反模式** | 「绝对不做什么」清单 |
| **诚实边界** | ≥3 条「做不到什么」声明 |

nuwa 蒸馏的产物是 1 个 `<person>-perspective/SKILL.md` + `test-prompts.json`（darwin 兼容）。

---

## 4. 实施边界（MIT 红线 · 必须遵守）

| 维度 | 约束 |
|---|---|
| **LICENSE 完整性** | 不可删上游 "MIT License" + "Copyright (c) 2026 Huashu (花叔)" |
| **致谢强度** | 5 平台模板（小红书 / 公众号 / H5 / 视频号 / 微博）+ 8 致谢段（详见 mit-attribution §十二）|
| **不得抹去上游作者** | 不能把 nuwa 5 维说成"博主原创蒸馏法"|
| **可子包装** | MIT 允许 — `l3-specs/` 子目录可写天龙本地增强（无需公开修改源码）|
| **可修改源码** | MIT 允许 — 派生作品自由，保留版权声明即可 |
| **可商业使用** | MIT 允许 — 无附加条件 |
| **SaaS 网络服务** | MIT 允许 — 无传染 |

---

## 5. 与天龙既有 26 阶段的协同矩阵

| 维度 | 协同对象 | 协议 |
|---|---|---|
| IP 蒸馏 | `~/.claude/ip-profiles/laoli_bro_2026/` | 35-02 / 35-06 博主全息 |
| 通用思维模型 | khazix-writer V1.1 + laoli-writer V1.0 | 风格 / 文风 |
| 与 cangjie + darwin 三件套 | 同生态 alchaincyf 三件套 | cangjie (AGPL) + darwin (MIT) |
| 内容策划 | 28-04 内容策划师 | 把蒸馏产物注入内容生产 |
| 财经数据 | a-stock-data-bridge / global-stock-data-bridge | 投资思维模型 |

---

## 6. 累计 PASS 增量（阶段 35-A 锁定）

| 测试项 | 状态 |
|---|---|
| T1 LICENSE verbatim | ✅ PASS |
| T2 SKILL.md frontmatter | ✅ PASS |
| T3 天龙扩展三件套 | ✅ PASS |
| T4 upstream scripts | ✅ PASS |
| T5 upstream references | ✅ PASS |
| T6 upstream examples | ✅ PASS |
| T7 l3-specs/ 子目录 | ✅ PASS |
| T8 nuwa_check.py exit 0 | ✅ PASS |
| T9 mit-attribution section | ✅ PASS |
| T10 no mirror modification | ✅ PASS |
| **累计** | **10/10 PASS** ✅ |

总累计 = 763（基线）+ 10 = **773 PASS**（天龙 35-A 锁定）

---

## 7. 风险与未决项

| 风险 | 缓解 |
|---|---|
| nuwa 蒸馏成本高（每人数十美元）| 默认标准档 + 3 档（快速 / 标准 / 深度）可选 |
| 上游 README 多语言（5 份）| 镜像保留全部 + 中文 README 优先 |
| 蒸馏产物可能与既有 skill 重复 | nuwa 输出 <person>-perspective 命名空间 |
| IP 授权过期 | 自动降级为公开人物模式 |

---

## 8. 来源链接

- 上游仓库：https://github.com/alchaincyf/nuwa-skill
- 上游 LICENSE：https://github.com/alchaincyf/nuwa-skill/blob/main/LICENSE
- 上游 SKILL.md：https://github.com/alchaincyf/nuwa-skill/blob/main/SKILL.md
- 本地镜像：`dragon-engine/skills/nuwa-skill/`
- 主题文件：`memory/nuwa-skill-integration.md`（本文件）
- 致谢模板：`memory/mit-attribution-statements.md §十二`
- 累计 PASS：`dragon-engine/skills/nuwa-skill/tests/test_nuwa_installation.py`

---

## 9. 实施计划（天龙阶段 35-A · 已完成）

| 任务 | 状态 |
|---|---|
| mkdir + tarball 镜像 | ✅ 2026-08-04 |
| SKILL.md frontmatter | ✅ |
| AGENT.md / HANDOFF.md / PRODUCT.md | ✅ |
| l3-specs/ 子包装 | ✅ |
| scripts/nuwa_check.py | ✅ |
| tests/test_nuwa_installation.py (10/10) | ✅ |
| memory/nuwa-skill-integration.md（本文件）| ✅ 2026-08-04 |
| mit-attribution §十二 | ✅ 2026-08-04 |

---

## 10. 协同矩阵（与天龙既有 skill 互相引用）

| nuwa 调用 | 触发 |
|---|---|
| `~/.claude/ip-profiles/laoli_bro_2026/ip_consent.txt` | 35-02 / 35-06 协同 |
| `agent-reach V1.5.0` | 网络搜索（替代网络） |
| `darwin-skill` | test-prompts.json 自动消费 → 进化 |
| `cangjie-skill` | 同生态姊妹（AGPL）|

| 天龙其他 skill 调用 nuwa | 触发 |
|---|---|
| `35-02 / 35-06 博主全息` | 「蒸馏 XX 思维方式」|
| `28-04 内容策划师` | 「用芒格视角写文案」|
| `khazix-writer V1.1` | 「芒格的逆向思维」|