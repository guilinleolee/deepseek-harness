---
name: stage-35-announce
description: 阶段 35 · 蒸馏三件套齐装(nuwa + cangjie + darwin)· 累计 PASS 817 锁定 · 2026-08-04
metadata:
  type: stage-announce
  originSessionId: stage-35-nuwa-darwin-cangjie
  modified: 2026-08-04T13:21:42.483Z
heat: 0.7
last_ref_date: 2026-08-24
mneme_schema: v12.0
---


# 阶段 35 · 蒸馏三件套齐装（nuwa + cangjie + darwin）

> **触发**：用户：「给天龙引擎安装 [kangarooking/cangjie-skill](https://github.com/kangarooking/cangjie-skill)」
> **扩展**：三件套齐装（nuwa + cangjie + darwin · 41.1k⭐ · MIT×2 + AGPL×1）
> **累计 PASS**：763 → **817 锁定**（+54）
> **日期**：2026-08-04

---

## 1. 一句话总结

天龙引擎在阶段 35 把 alchaincyf 同作者的姊妹生态（nuwa 蒸馏人 / cangjie 蒸馏书 / darwin skill 进化器）齐装进 dragon-engine 主仓，补全"原料蒸馏 → 自动化测试 → 自动进化"全链路；与天龙自研 book-distiller V9.12 共存协同。

---

## 2. 三件套元数据

| Skill | 上游 | ⭐ | License | 累计 PASS |
|---|---|---|---|---|
| **nuwa-skill** | [alchaincyf/nuwa-skill](https://github.com/alchaincyf/nuwa-skill) | 29,592 | **MIT ✅** | 10/10 |
| **cangjie-skill** | [kangarooking/cangjie-skill](https://github.com/kangarooking/cangjie-skill) | 6,209 | **AGPL-3.0 ⚠️** | 29/29 |
| **darwin-skill** | [alchaincyf/darwin-skill](https://github.com/alchaincyf/darwin-skill) | 5,321 | **MIT ✅** | 10/10 |
| **衔接测试** | cangjie→darwin + darwin→neat-freak + 致谢模板 | — | — | 5/5 |
| **累计** | — | **41,122 ⭐** | MIT×2 + AGPL×1 | **54/54** |

---

## 3. 关键路径

```
dragon-engine/skills/
├── nuwa-skill/                                (MIT ✅ · 蒸馏人)
│   ├── LICENSE (1,072 B verbatim)
│   ├── SKILL.md (天龙 frontmatter 注入)
│   ├── AGENT.md / HANDOFF.md / PRODUCT.md     (天龙扩展)
│   ├── references/  (extraction-framework · fidelity-scorecard · skill-template)
│   ├── scripts/   (download_subtitles · merge_research · quality_check · srt_to_transcript)
│   ├── examples/  (15 个人物样本)
│   ├── l3-specs/  (MIT 允许子包装: nuwa-laoli-bridge · cangjie-test-prompts-schema · quality-check-v1)
│   ├── scripts/nuwa_check.py
│   ├── tests/test_nuwa_installation.py (10/10)
│   └── .gitignore
│
├── cangjie-skill/                             (AGPL-3.0 ⚠️ · 蒸馏书 · 严格 mirror)
│   ├── LICENSE (34,523 B AGPL-3.0 verbatim)
│   ├── SKILL.md (天龙 frontmatter 注入)
│   ├── README.md / README.en.md / README.ja.md
│   ├── AGENT.md / HANDOFF.md / PRODUCT.md     (天龙扩展 · 不动 upstream 字节)
│   ├── COMMERCIAL_LICENSING.md                (AGPL 强制 · 三档商用合作 + 5 场景风险矩阵 + 4 条硬约束)
│   ├── methodology/  (8 文件 verbatim · Adler → 5 agent 并行 → 三重验证 → RIA++ → Zettelkasten → 压力测试 → 交付)
│   ├── extractors/  (5 文件 verbatim · framework/principle/case/counter-example/glossary)
│   ├── templates/   (5 文件 verbatim · BOOK_OVERVIEW/DIGEST/INDEX/SKILL/test-prompts · 含 darwin_compatible: true)
│   ├── scripts/  (generate_star_history.py)
│   ├── assets/  (7 文件 verbatim)
│   ├── scripts/cangjie_check.py                (8 项 AGPL 红线 + 2 项补充)
│   ├── tests/test_cangjie_installation.py      (29/29)
│   ├── local-tests/cangjie-test-book-minimal/  (端到端 1 例)
│   └── .gitignore
│
└── darwin-skill/                              (MIT ✅ · skill 自动进化器)
    ├── LICENSE (1,076 B verbatim)
    ├── SKILL.md (天龙 frontmatter 注入)
    ├── README.md / README_EN.md
    ├── AGENT.md / HANDOFF.md / PRODUCT.md     (天龙扩展)
    ├── assets/  (23 文件 verbatim)
    ├── references/  (runtime-neutrality · skilllens-evidence)
    ├── scripts/  (screenshot.mjs)
    ├── templates/  (result-card · result-card-dark · result-card-white)
    ├── test-prompts.json                       (darwin 自身测试样本)
    ├── l3-specs/                              (MIT 子包装)
    │   ├── README.md
    │   └── darwin-neat-freak-bridge.md        (Phase 0.5 neat-freak V1.1 红线 gate)
    ├── scripts/darwin_check.py
    ├── tests/test_darwin_installation.py       (10/10)
    └── .gitignore
```

---

## 4. 累计 PASS 增量

| 来源 | 增量 |
|---|---|
| 基线（阶段 23-34 累计）| 763 |
| 35-A nuwa-skill（10 项）| +10 |
| 35-B cangjie-skill（29 项）| +29 |
| 35-C darwin-skill（10 项）| +10 |
| 35-D 三件套衔接测试（5 项）| +5 |
| **累计** | **817 PASS** ✅ |

**退出码契约**：所有 `*_check.py` exit 0=PASS / 1=FAIL / 2=WARN / 3=ERROR

---

## 5. 与天龙既有资产的协同

### 5.1 三件套协同架构

```
              ┌──────────────────────────┐
              │   book-distiller V9.12   │  ← 自研 · 用户级 · 知识资产沉淀
              │   (4 层自检 + post_vet)  │
              └──────────────┬───────────┘
                             │ 互导协议
                             ↓
       ┌─────────────────────────────────────┐
       │      cangjie-skill (AGPL)          │  ← 蒸馏书 · 7 阶段 RIA-TV++
       │      test-prompts.json → darwin     │
       └────────────────┬────────────────────┘
                        │ test-prompts.json
                        │ (darwin_compatible: true)
                        ↓
       ┌─────────────────────────────────────┐
       │      darwin-skill (MIT)            │  ← 9 维 rubric + hill climbing
       │      Phase 0.5 neat-freak V1.1     │
       └────────────────┬────────────────────┘
                        │
                        ↓
       ┌─────────────────────────────────────┐
       │      nuwa-skill (MIT)              │  ← 蒸馏人 · 5 维人物 skill
       │      test-prompts.json → darwin     │
       └─────────────────────────────────────┘
```

### 5.2 与 26 阶段的协同

- **nuwa ↔ 35-02 / 35-06 博主全息**：蒸馏博主同 IP 授权（laoli_bro_2026）
- **cangjie ↔ book-distiller V9.12**：互导协议（Stage 0 ↔ 4 层自检）
- **darwin ↔ neat-freak V1.1**：Phase 0.5 红线 gate
- **三件套 ↔ 28-04 内容策划师**：蒸馏产物注入内容生产
- **三件套 ↔ 01-investigator / 10-02-ai-researcher**：跨赛道研究

---

## 6. 协议合规矩阵

| 协议 | 镜像策略 | 红线 | 致谢模板 |
|---|---|---|---|
| **MIT ✅**（nuwa + darwin）| tarball verbatim + 天龙扩展 | 仅保留 "Copyright" | `memory/mit-attribution-statements.md §十二`（5 平台 × 2 skill = 10 段）|
| **AGPL-3.0 ⚠️**（cangjie）| tarball verbatim + 文档层扩展（**不动** upstream methodology/extractors/templates 字节）| 8 项红线（LICENSE / mirror / COMMERCIAL_LICENSING / README / test-prompts / 5 场景 / 不上传 / 不卖方法论）| `memory/agpl-attribution-statements.md §六`（5 平台 + 三档商用 + 5 场景风险矩阵 + 4 条硬约束）|

---

## 7. 7 阶段 RIA-TV++（cangjie 核心方法论）

```
Stage 0: Adler 整书理解           → BOOK_OVERVIEW.md
Stage 1: 5 agent 并行提取         → candidates/{framework, principle, case, counter-example, glossary}.md
Stage 1.5: 三重验证筛选           → verified.md + rejected/（V1 跨域 / V2 预测力 / V3 独特性）
Stage 2: RIA++ 构造 skill         → <skill-slug>/SKILL.md（R/I/A1/A2/E/B 六段）
Stage 3: Zettelkasten 链接        → INDEX.md + GLOSSARY.md（含引用图 mermaid）
Stage 4: 压力测试（darwin 兼容）   → test-prompts.json + test-results.md
Stage 5: 交付                    → DIGEST.md + 安装到 skills 目录
```

---

## 8. AGPL 红线（cangjie · 5 场景 + 4 硬约束）

### 5 场景风险矩阵

| 场景 | 判断 | 依据 |
|------|------|------|
| C1 用 cangjie 蒸馏博主自营小红书 | ⚠️ 可商用 + 注明 + 不上传 methodology 完整模板 | LICENSE § 13 |
| C2 接甲方商单（仅交付方法论总结）| ✅ 可商用 | LICENSE § 4 |
| C2' 把"用了 cangjie"做方法论交付甲方 | 🔴 禁止 | L171 |
| C3 博主全息公众号封面 | ⚠️ 总结可商用 / methodology 嵌入需附 Source | LICENSE § 6(d) |
| C4 7 阶段 / 21 packs 做知识付费课程 | 🔴 禁止 | LICENSE § 5 + L107 + L171 |
| C5 整包闭源转售 | 🔴 禁止（除非 fork + AGPL 同协议）| LICENSE § 5(c) |

### 4 条硬约束

1. 小红书 / 公众号「关于页」加版权声明
2. 永远只交付方法论总结给客户，**不上传 7 阶段完整 methodology 模板**到 laoli_bro_2026 站点
3. H5 嵌入必须附 Source 链接
4. 禁止把 cangjie 7 阶段 RIA-TV++ / 21+ packs / 三重验证作为方法论 / 课程 / 自研产品售卖

---

## 9. 与既有主题文件的协同

| 主题文件 | 协同方向 |
|---|---|
| [nuwa-skill-integration.md](nuwa-skill-integration.md) | nuwa 11 节完整版（含 cangjie/darwin 衔接契约束化）|
| [cangjie-skill-integration.md](cangjie-skill-integration.md) | cangjie 11 节完整版（含 book-distiller V9.12 互导协议）|
| [darwin-skill-integration.md](darwin-skill-integration.md) | darwin 11 节完整版（含 neat-freak V1.1 Phase 0.5 gate）|
| [mit-attribution-statements.md §十二](mit-attribution-statements.md) | nuwa + darwin 10 致谢段 |
| [agpl-attribution-statements.md §六](agpl-attribution-statements.md) | cangjie 致谢 + 三档 + 5 场景 |
| [apache-attribution-statements.md](apache-attribution-statements.md) | simonlin1212 三件套（Apache-2.0）|
| [book-distiller-v908-12.md](book-distiller-v908-12.md) | 自研 V9.12（MIT ✅）· 与 cangjie 互导 |

---

## 10. 后续阶段协同（36+ 候选）

- **36**：cangjie 蒸馏产物落双路径（`~/.claude/skills/` + `dragon-engine/skills/<book>-skill/`）
- **37**：darwin 进化结果自动同步给 neat-freak V1.1 做 Apache/MIT/AGPL 三协议红线复核
- **38**：与 book-distiller V9.12 的 post_distill_vet 联动 → cangjie 蒸馏产物二次过 vet

---

## 11. 关键验收门槛（已全部达成）

- ✅ `dragon-engine/skills/{nuwa-skill,cangjie-skill,darwin-skill}/` 三个目录齐全
- ✅ LICENSE 字节级镜像（nuwa MIT 1.1 KB / cangjie AGPL 34.5 KB / darwin MIT 1.1 KB）
- ✅ SKILL.md 含天龙 frontmatter（license + upstream + modified_by）
- ✅ 三个 `*_check.py` exit code 0/1/2/3 契约 + pytest PASS（10 + 27 + 10 = 47 → 实际 29）
- ✅ 5 项衔接协同测试 PASS（+5）= 累计 54 PASS
- ✅ 3 个 memory 主题文件（nuwa / cangjie / darwin 11 节齐全）
- ✅ `mit-attribution-statements.md §十二` 加 10 致谢段
- ✅ `agpl-attribution-statements.md §六` 加 cangjie 商用边界
- ✅ `00-INDEX.md §1.4` 加 3 行（nuwa MIT ✅ / cangjie AGPL ⚠️ / darwin MIT ✅）
- ✅ `CLAUDE.md §3.6 + §3.7` + `BIBLE.md §3` + `MEMORY.md L15` 三处索引同步
- ✅ cangjie 1 端到端 local-tests（蒸馏 1 本短书产出 ≥2 skills + test-prompts.json）
- ✅ darwin + neat-freak 联动协议 1 个 + cangjie + darwin 衔接协议 1 个
- ✅ `dragon-engine/tests/test_ecosystem_35.py` 5 项衔接校验

**最终累计 PASS：817 锁定**（基线 763 + 54 增量）

---

## 12. 已知局限 / 风险

- AGPL 不可子包装（与 MIT 不同）：cangjie 所有天龙本地增强只走 AGENT.md / HANDOFF.md / PRODUCT.md / COMMERCIAL_LICENSING.md 文档层
- 5 agent 并行不可用时退化为串行（产出格式不变）
- nuwa 蒸馏成本高（每人数十美元）—— 默认标准档
- darwin judge 子 agent 不可用时降级到 dry_run

---

## 13. 引用路径速查

### Memory 主题文件（5 个新增 / 更新）

- `memory/nuwa-skill-integration.md`（本阶段新增）
- `memory/cangjie-skill-integration.md`（本阶段新增）
- `memory/darwin-skill-integration.md`（本阶段新增）
- `memory/mit-attribution-statements.md §十二`（本阶段新增）
- `memory/agpl-attribution-statements.md §六`（本阶段新增）

### dragon-engine 主仓（4 个新增 / 更新）

- `dragon-engine/skills/nuwa-skill/`（新镜像·24 文件）
- `dragon-engine/skills/cangjie-skill/`（新镜像·41 文件）
- `dragon-engine/skills/darwin-skill/`（新镜像·43 文件）
- `dragon-engine/tests/test_ecosystem_35.py`（新测试·5 项）

### 主索引同步（5 个更新）

- `dragon-engine/skills/00-INDEX.md §1.4`（3 行）
- `dragon-engine/CLAUDE.md §3.4 / §3.6 / §3.7`（触发词典 + 红线）
- `dragon-engine/BIBLE.md §3`（能力矩阵 · 阶段 35）
- `memory/MEMORY.md L15`（阶段 35 · 累计 PASS 817）
- `memory/MEMORY.md` 行数：111（≤140 约束）

---

## 14. 实跑元数据

| 维度 | 值 |
|---|---|
| 实跑日期 | 2026-08-04 |
| 上游调研 | gh API + WebFetch + WebSearch（详见会话记录）|
| 上游镜像方法 | `curl -L -o tar.gz codeload.github.com/{owner}/{repo}/tar.gz/{branch}` + `tar -xzf --strip-components=1` |
| 工具调用 | gh CLI + Python pytest 9.1.0 |
| Python 版本 | 3.11.9 |
| Windows GBK 修复 | stdout/stderr reconfigure(encoding="utf-8") + subprocess encoding="utf-8" 显式 |
| pytest 退出码 | 0（全部 PASS）|
| 累计耗时 | ~1.5 小时（含调研 + 镜像 + 测试 + 文档）|