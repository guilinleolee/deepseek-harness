---
name: cangjie-skill-integration
description: kangarooking/cangjie-skill (6.2k⭐ AGPL-3.0) 天龙集成主题文件 · 阶段 35 · 蒸馏书 · 29/29 PASS
metadata:
  type: integration
  originSessionId: stage-35-nuwa-darwin-cangjie
  modified: 2026-08-04T12:34:02.456Z
heat: 0.7
last_ref_date: 2026-08-24
mneme_schema: v12.0
---


# cangjie-skill × 天龙引擎 · 阶段 35-B 集成主题文件

> **上游**：[kangarooking/cangjie-skill](https://github.com/kangarooking/cangjie-skill) · 6,209 ⭐ / 802 forks
> **License**：AGPL-3.0 ⚠️（34.5 KB / 659 行 verbatim）
> **集成阶段**：天龙 35 · 周 2
> **累计 PASS**：29/29（test_cangjie_installation.py）
> **镜像路径**：`dragon-engine/skills/cangjie-skill/`
> **作者**：kangarooking（袋鼠帝，独立开发者）
> **三件套**：与 nuwa (MIT) + darwin (MIT) 构成 alchaincyf 同作者的姊妹三件套（注：cangjie 作者是 kangarooking，独立）

---

## 1. 实跑元数据

| 维度 | 值 |
|---|---|
| GitHub URL | https://github.com/kangarooking/cangjie-skill |
| Stars / Forks | 6,209 / 802 |
| License SPDX | AGPL-3.0 |
| 上游 LICENSE size | 34,523 B（verifies "GNU AFFERO GENERAL PUBLIC LICENSE" + "Version 3"）|
| 主语言 | Python（脚本 + Markdown 方法论）|
| 镜像文件数 | 41（LICENSE + 3 README + SKILL.md + AGENT/HANDOFF/PRODUCT/COMMERCIAL_LICENSING.md + 8 methodology + 5 extractors + 5 templates + 1 script + 6 assets + .github + GITHUB_REPO.md）|

---

## 2. 镜像拓扑

```
dragon-engine/skills/cangjie-skill/
├── LICENSE                                              ← AGPL-3.0 verbatim（不可删）
├── SKILL.md                                             ← 加天龙 frontmatter（license: AGPL-3.0 + upstream）
├── README.md / README.en.md / README.ja.md              ← 上游 verbatim（多语言）
├── AGENT.md / HANDOFF.md / PRODUCT.md                   ← 天龙扩展（不修改 upstream 任何字节）
├── COMMERCIAL_LICENSING.md                              ← AGPL 强制（参考 guizang 三档 + 5 场景风险矩阵）
├── GITHUB_REPO.md                                       ← 上游 verbatim
├── methodology/                                         ← upstream 字节级镜像（8 文件）
│   ├── 00-overview.md                                   ← RIA-TV++ 概览
│   ├── 01-stage0-adler.md                               ← Adler 整书理解
│   ├── 02-stage1-parallel-extract.md                    ← 5 agent 并行提取
│   ├── 03-stage1.5-triple-verify.md                     ← 三重验证 V1/V2/V3
│   ├── 04-stage2-ria-plus.md                            ← RIA++ 构造
│   ├── 05-stage3-zettelkasten.md                        → 链接
│   ├── 06-stage4-pressure-test.md                       → darwin 兼容压力测试
│   └── 07-stage5-deliver.md                             → DIGEST.md 交付
├── extractors/                                          ← upstream 字节级镜像（5 文件）
│   ├── case-extractor.md
│   ├── counter-example-extractor.md
│   ├── framework-extractor.md
│   ├── glossary-extractor.md
│   └── principle-extractor.md
├── templates/                                           ← upstream 字节级镜像（5 文件）
│   ├── BOOK_OVERVIEW.md.template
│   ├── DIGEST.md.template
│   ├── INDEX.md.template
│   ├── SKILL.md.template                                → R/I/A1/A2/E/B 六段
│   └── test-prompts.json.template                       → darwin_compatible: true + 7 字段 schema
├── scripts/  (generate_star_history.py)
├── assets/  (star-history.svg + wechat-personal-qr.jpg + wecom-cangjie-group-qr.png + kangarooking-gzh.png + star-history-logo.png.b64 + xkcd.woff.b64 + star-history-assets-LICENSE.txt)
├── .github/  (workflows/update-star-history.yml)
├── scripts/cangjie_check.py                             ← 天龙 check (8 项 AGPL 红线 + 2 项补充)
├── tests/test_cangjie_installation.py                   ← 29 项 pytest PASS
└── .gitignore
```

**关键约束**：**AGPL 不允许 l3-specs/ 子包装**（与 MIT 不同），所有天龙本地增强只走 AGENT.md / HANDOFF.md / PRODUCT.md / COMMERCIAL_LICENSING.md 文档层。

---

## 3. 能力矩阵（7 阶段 RIA-TV++ · 蒸馏书）

| 阶段 | 名称 | 产出 | 关键质量门神 |
|---|---|---|---|
| 0 | Adler 整书理解 | BOOK_OVERVIEW.md | 结构 / 解释 / 批判 / 应用 四步 |
| 1 | 5 agent 并行提取 | candidates/{framework, principle, case, counter-example, glossary}.md | 5 个独立 agent |
| 1.5 | 三重验证筛选 | verified.md + rejected/ | V1 跨域 / V2 预测力 / V3 独特性（通常 25-50% 通过率）|
| 2 | RIA++ 构造 skill | `<skill-slug>/SKILL.md` | R/I/A1/A2/E/B 六段 |
| 3 | Zettelkasten 链接 | INDEX.md + GLOSSARY.md | 引用图 mermaid |
| 4 | 压力测试（darwin 兼容）| test-prompts.json + test-results.md | 3 should_trigger + 2 should_not_trigger（含跨 skill 混淆）+ 1 edge |
| 5 | 交付 | DIGEST.md + 安装到 skills 目录 | 用户安装位置确认 |

---

## 4. 实施边界（AGPL 红线 · 必须遵守 · 8 项）

| 红线 | 约束 |
|---|---|
| **R1 LICENSE verbatim** | 不可删上游 34.5 KB AGPL-3.0 全文 |
| **R2 mirror 字节级保护** | upstream methodology/extractors/templates 字节级镜像，不可 modification |
| **R3 COMMERCIAL_LICENSING.md** | 必须含 3 档商用合作（深度内置 / 上架与露出 / 收益分成）|
| **R4 README.md 署名** | 末尾 AGPL 署名段（GNU AGPL v3 / AGPL-3.0 / AGPL_v3）|
| **R5 test-prompts darwin 兼容** | 模板含 `darwin_compatible: true` 字段（cangjie→darwin 衔接关键）|
| **R6 5 场景风险矩阵** | C1-C5 必须存在（COMMERCIAL_LICENSING.md 或 PRODUCT.md）|
| **R7 不上传完整模板** | 文档层有禁止表述（"上传 + 禁止 / 🔴"）|
| **R8 不卖方法论** | 7 阶段 / 21 packs / 三重验证不可作为知识付费课程 |

**附加红线**：
- **不可子包装** — AGPL 禁止 `l3-specs/` 子目录（与 MIT 不同）
- **派生代码必须公开** — 改 upstream 任何字节 → 派生作品同样 AGPL-3.0 开源
- **SaaS 网络服务触发** — 部署成 SaaS 必须公开服务端修改源码（AGPL § 13）

详见 `dragon-engine/skills/cangjie-skill/COMMERCIAL_LICENSING.md`

---

## 5. 与天龙既有 26 阶段的协同矩阵

| 维度 | 协同对象 | 协议 |
|---|---|---|
| **darwin 衔接** | darwin-skill (MIT) | cangjie Stage 4 → test-prompts.json → darwin Phase 1 |
| **nuwa 三件套** | nuwa-skill (MIT) | 同 schema 7 字段，darwin 可同时消费 |
| **book-distiller V9.12 互导** | book-distiller V9.12 | cangjie Stage 0 ↔ book-distiller 4 层自检 |
| **AGPL 合规护栏** | neat-freak V1.1 | 自动巡检 AGPL 红线 |
| **已产 skill packs** | 21+ | buffett-letters / poor-charlies-almanack / mao-selected-works / huangdi-neijing / duan-yongping / viral-copywriting / first-principles 等 |

---

## 6. 累计 PASS 增量（阶段 35-B 锁定）

| 测试族 | 状态 |
|---|---|
| A. mirror 完整性（5 项）| ✅ PASS |
| B. AGPL 红线 8 项（R1-R8）| ✅ PASS |
| C. SKILL.md / 文件结构（6 项）| ✅ PASS |
| D. mirror 字节级保护（5 项）| ✅ PASS |
| E. darwin 兼容 test-prompts.json 模板（3 项）| ✅ PASS |
| F. check 脚本与端到端（2 项）| ✅ PASS |
| **累计** | **29/29 PASS** ✅ |

总累计 = 783（35-C 之后）+ 29 = **812 PASS**（天龙 35-B 锁定）

---

## 7. cangjie→darwin 自动进化协议

cangjie Stage 4 输出的 `test-prompts.json` 严格 darwin 兼容（`darwin_compatible: true` + 7 字段 schema），是三件套"咬合"的关键：

```
cangjie Stage 2 (RIA++) →  生成 <book-slug>/<skill-slug>/SKILL.md
cangjie Stage 4 (压力测试) → 生成 test-prompts.json (darwin 兼容)
                                          ↓
                              darwin Phase 0.5 (neat-freak gate)
                                          ↓
                              darwin Phase 1 (9 维 rubric + 3 judge)
                                          ↓
                              darwin Phase 2 (hill climbing + paired)
                                          ↓
                              darwin Phase 3 (result-card.html)
```

详细字段映射：
- `skill` → darwin 优化目标
- `version` → darwin baseline version
- `source_book` → darwin audit 来源
- `darwin_compatible: true` → schema 标记
- `test_cases[]` → darwin Phase 1 实测用例
- `minimum_pass_rate: 0.8` → darwin keep/revert 阈值
- `notes` → darwin 评估补充信息

详见 `dragon-engine/skills/cangjie-skill/AGENT.md § 3.1`

---

## 8. cangjie ↔ book-distiller V9.12 互导协议

| 协同方向 | 协议 |
|---|---|
| cangjie Stage 0 → book-distiller | cangjie BOOK_OVERVIEW.md → book-distiller L1 完整性预筛 |
| book-distiller DIGEST → cangjie Stage 1 | DIGEST.md → cangjie 5 agent 并行提取源文本 |
| 双向语料共享 | cangjie GLOSSARY.md → book-distiller 引用 |

---

## 9. 风险与未决项

| 风险 | 缓解 |
|---|---|
| AGPL 红线误触（上传 methodology 完整模板到 H5）| (a) `agpl-attribution-statements.md §六` 加显式红线段 (b) `cangjie_check.py` 强校验 (c) 与 guizang 5 场景风险矩阵对照 |
| cangjie 模板冲突（与 book-distiller V9.12 认知重叠）| (a) `cangjie-skill-integration.md` §8 互导协议明示 (b) CLAUDE.md §3.7 触发词典分场景 |
| 蒸馏档位成本高 | 默认标准档 + 3 档（快速 / 标准 / 深度）可选 |
| 上游版本断更 | (a) 镜像后 `rm -rf .git` 防 subtree 漂移 (b) `skill-updater scan.sh` 报告 stale 检测 |
| 5 agent 并行不可用 | 退化为串行执行（产出格式不变）|

---

## 10. 来源链接

- 上游仓库：https://github.com/kangarooking/cangjie-skill
- 上游 LICENSE：https://github.com/kangarooking/cangjie-skill/blob/main/LICENSE
- 上游 SKILL.md：https://github.com/kangarooking/cangjie-skill/blob/main/SKILL.md
- AGPL-3.0 全文：https://www.gnu.org/licenses/agpl-3.0.html
- 本地镜像：`dragon-engine/skills/cangjie-skill/`
- 主题文件：`memory/cangjie-skill-integration.md`（本文件）
- AGPL 致谢模板：`memory/agpl-attribution-statements.md §六`
- AGPL 商用边界：`dragon-engine/skills/cangjie-skill/COMMERCIAL_LICENSING.md`
- 累计 PASS：`dragon-engine/skills/cangjie-skill/tests/test_cangjie_installation.py`

---

## 11. 实施计划（天龙阶段 35-B · 已完成）

| 任务 | 状态 |
|---|---|
| mkdir + tarball 镜像 | ✅ 2026-08-04 |
| SKILL.md frontmatter | ✅ |
| AGENT.md / HANDOFF.md / PRODUCT.md | ✅ |
| COMMERCIAL_LICENSING.md（参考 guizang 三档）| ✅ |
| scripts/cangjie_check.py（8 项 AGPL 红线）| ✅ |
| tests/test_cangjie_installation.py (29/29) | ✅ |
| memory/cangjie-skill-integration.md（本文件）| ✅ 2026-08-04 |
| agpl-attribution §六 致谢模板 | ✅ 2026-08-04 |

---

## 12. 协同矩阵

| cangjie 调用 | 触发 |
|---|---|
| `darwin-skill` | test-prompts.json 自动消费 → 进化 |
| `nuwa-skill` | 同生态姊妹（schema 对齐）|
| `book-distiller V9.12` | 互导协议（cangjie Stage 0 ↔ book-distiller 4 层）|
| `neat-freak V1.1` | AGPL 红线巡检 |
| `agent-reach V1.5.0` | 网络搜索（替换原始网络）|

| 天龙其他 skill 调用 cangjie | 触发 |
|---|---|
| `35-02 / 35-06 博主全息` | 「蒸馏这本书」|
| `28-04 内容策划师` | 「拆《XX》」|
| `book-distiller V9.12` | cangjie Stage 0 4 层预筛 |
| `darwin-skill` | cangjie 产物自动进化 |