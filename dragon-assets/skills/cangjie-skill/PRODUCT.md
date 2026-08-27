# PRODUCT.md · cangjie-skill × 天龙引擎产品定位

> **与上游 cangjie-skill 平级扩展，但**不修改** upstream 任何字节**
> **AGPL 红线**：本文件是文档层扩展

---

## 1. 一句话定位

**cangjie 是天龙引擎「书 / 长视频 / 播客」的元蒸馏器**——把任意长内容蒸馏成一组可调用 skill 群（含 test-prompts.json 供 darwin 自动进化）。

---

## 2. 与天龙既有 9 类核心 skill 的边界

| 维度 | cangjie-skill | 既有对照 | 边界 |
|---|---|---|---|
| 蒸馏对象 | 书 / 长视频 / 播客 / 课程 | book-distiller V9.12（仅书）| cangjie 范围更广 |
| 流水线 | 7 阶段 RIA-TV++ + 5 agent 并行 | book-distiller 单线程 + 4 层自检 | cangjie 自动化程度更高 |
| 产物类型 | 一组可调用 skill 群 + DIGEST | DIGEST 长文 + 概念卡 + 知识图谱 | 互补 |
| 评估 | 三重验证（V1 跨域 / V2 预测力 / V3 独特性）+ 阶段 4 压力测试 | post_distill_vet | 互补 |
| 进化 | test-prompts.json → darwin | book-distiller 无进化 | cangjie 可进化 |
| License | AGPL-3.0 ⚠️ | MIT ✅（自研）| 严格合规要求 |

---

## 3. 关键决策树

```
用户说「蒸馏 XX」或「拆 XX 书」或 "distill this book"
    │
    ├─ XX 是书 / 长视频 / 播客？ → 是 → cangjie-skill
    │
    ├─ XX 是已上传的 PDF / EPUB 知识资产？ → 是 → book-distiller V9.12
    │
    ├─ XX 是「人 / 思维模式」？ → 是 → nuwa-skill
    │
    └─ XX 是「优化现有 skill」？ → 是 → darwin-skill
```

---

## 4. 7 阶段 RIA-TV++ 流水线（核心方法论）

| 阶段 | 名称 | 产出 |
|---|---|---|
| 0 | Adler 整书理解 | BOOK_OVERVIEW.md（结构 / 解释 / 批判 / 应用）|
| 1 | 5 agent 并行提取 | candidates/{framework, principle, case, counter-example, glossary}.md |
| 1.5 | 三重验证筛选 | verified.md（V1 跨域 / V2 预测力 / V3 独特性）+ rejected/ |
| 2 | RIA++ 构造 skill | <skill-slug>/SKILL.md（R / I / A1 / A2 / E / B 六段）|
| 3 | Zettelkasten 链接 | INDEX.md（含引用图 mermaid）+ GLOSSARY.md |
| 4 | 压力测试（darwin 兼容）| test-prompts.json + test-results.md |
| 5 | 交付 | DIGEST.md + 安装到 skills 目录 |

---

## 5. Stage 35 协同架构

```
              ┌─────────────────────────────────────────┐
              │   video-downloader / kangarooking-skill │  ← 字幕 / 转写文本
              └────────────────────┬────────────────────┘
                                   ↓
       ┌─────────────────────────────────────────────────┐
       │            cangjie-skill (AGPL)                │  ← 7 阶段 RIA-TV++
       │            Stage 0 → Stage 5                    │
       │            test-prompts.json → darwin          │
       └────────────────┬────────────────────────────────┘
                        │
                        ↓
       ┌─────────────────────────────────────────────────┐
       │            darwin-skill (MIT)                  │  ← 9 维 rubric
       │            Phase 0.5 neat-freak gate            │
       │            Phase 1-2 hill climbing              │
       └────────────────┬────────────────────────────────┘
                        │
                        ↓
       ┌─────────────────────────────────────────────────┐
       │            nuwa-skill (MIT)                    │  ← 蒸馏人（姊妹）
       │            5 维人物 skill                       │
       │            test-prompts.json → darwin          │
       └─────────────────────────────────────────────────┘
                                     ↑
       ┌─────────────────────────────────────────────────┐
       │      book-distiller V9.12 (自研 MIT)          │  ← 互导协议
       │      cangjie Stage 0 ↔ book-distiller 4 层    │
       └─────────────────────────────────────────────────┘
```

---

## 6. AGPL 红线（必须遵守）

| 红线 | 后果 |
|---|---|
| 上传 cangjie 完整模板到 H5 / 博客 | 🔴 协议违规 |
| 把 cangjie 蒸馏方法论当知识付费课程售卖 | 🔴 AGPL § 5 + L107 + L171 三重禁止 |
| 整包闭源转售（除非 fork + AGPL 同协议）| 🔴 派生必开源 |
| 用 cangjie 输出训练竞品模型 | 🔴 禁止 |
| 删除 LICENSE verbatim "AGPL v3" 段 | 🔴 禁止 |
| 改 upstream methodology/extractors/templates 字节 | 🔴 派生代码必须公开 |

详见 `COMMERCIAL_LICENSING.md`（本目录）+ `memory/agpl-attribution-statements.md §六`。

---

## 7. 核心数字

| 维度 | 数字 |
|---|---|
| 7 阶段流水线 | 0 / 1 / 1.5 / 2 / 3 / 4 / 5 |
| 5 agent 并行提取器 | framework / principle / case / counter-example / glossary |
| 三重验证通过率 | 通常 25-50% |
| 产物 SKILL.md 六段 | R / I / A1 / A2 / E / B |
| test-prompts.json 必含 | 3 should_trigger + 2 should_not_trigger + 1 edge_case（≥1 跨 skill 混淆诱饵）|
| 已产 skill packs | 21+（buffett-letters · poor-charlies-almanack · mao-selected-works · huangdi-neijing 等）|

---

## 8. 后续协同（阶段 36-38 候选）

- **36**：cangjie 蒸馏产物落双路径
- **37**：darwin 进化结果自动同步给 neat-freak V1.1
- **38**：与 book-distiller V9.12 的 post_distill_vet 联动 → cangjie 蒸馏产物二次过 vet