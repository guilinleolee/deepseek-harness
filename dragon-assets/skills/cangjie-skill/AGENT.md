# AGENT.md · cangjie-skill × 天龙引擎

> **协议**：Agent 工作约定（与上游 cangjie-skill 平级扩展，但**不修改** upstream 任何字节）
> **AGPL 红线**：本文件是文档层扩展，不修改 LICENSE / README.md / methodology/ / extractors/ / templates/ 任何上游字节。

---

## 1. 何时使用本 skill

由 [SKILL.md `description`](SKILL.md) 的 trigger 词触发，主要场景：

| 触发词 | 路径 |
|---|---|
| 「蒸馏 XX」「把 XX 书做成 skill」「拆 XX」| Stage 0 → Stage 1 → Stage 1.5 → ... |
| 「把这个 B 站 / 播客 / 课程蒸馏成 skill」| 同上（先 video-downloader 取转写文本）|
| "distill this book into skills: <path>" | 英文直接路径 |

---

## 2. 7 阶段 RIA-TV++ 流水线（与上游一致）

```
阶段 0: Adler 整书理解           → BOOK_OVERVIEW.md
阶段 1: 5 个 agent 并行提取     → 候选方法论单元池
阶段 1.5: 三重验证筛选          → 通过的单元（用户轻确认 ★）
阶段 2: RIA++ 构造 skill        → 每个 skill 的 SKILL.md
阶段 3: Zettelkasten 链接       → INDEX.md + GLOSSARY.md
阶段 4: 压力测试（darwin 兼容）  → test-prompts.json + 回炉淘汰
阶段 5: 交付                    → DIGEST.md 精华长文 + 安装到 skills 目录
```

详见 [`methodology/00-overview.md`](methodology/00-overview.md)。

---

## 3. 天龙引擎协同约定

### 3.1 与 darwin-skill 衔接（关键契合点）

cangjie 阶段 4 产出的 `test-prompts.json` 严格 darwin 兼容（`darwin_compatible: true` + 7 字段 schema）：

```
cangjie Stage 2 (RIA++) →  生成 skills/<book>/<skill>/SKILL.md
cangjie Stage 4 (压力测试) → 生成 test-prompts.json (darwin 兼容)
                                          ↓
                              darwin Phase 1 (基线评估)
                              darwin Phase 2 (hill climbing)
                              darwin Phase 3 (result-card.html)
```

### 3.2 与 book-distiller V9.12 互导

| 协同方向 | 协议 |
|---|---|
| cangjie Stage 0 → book-distiller | 把 cangjie BOOK_OVERVIEW.md 喂给 book-distiller 4 层自检作 L1 完整性预筛 |
| book-distiller DIGEST → cangjie Stage 5 | 把 book-distiller DIGEST.md 当作 cangjie 输入文本 |
| 双向语料共享 | cangjie 蒸馏产物的 GLOSSARY.md 可被 book-distiller 引用 |

### 3.3 与 nuwa-skill 互不重叠

- **nuwa** = 蒸馏**人**（思维框架 / 表达 DNA）→ 1 个 `<person>-perspective/SKILL.md`
- **cangjie** = 蒸馏**书**（方法论 / 框架 / 原则）→ N 个 `<skill-slug>/SKILL.md`
- 产物不冲突，但产物的 `test-prompts.json` schema 一致，darwin 可同时消费

---

## 4. 阶段 1 并行 5 提取器（天龙调用约定）

| sub-agent | 提取对象 | prompt |
|---|---|---|
| framework-extractor | 决策框架 / 思维模型 | `extractors/framework-extractor.md` |
| principle-extractor | 原则 / 清单 / 规则 | `extractors/principle-extractor.md` |
| case-extractor | 作者在书中亲自用过的实例 | `extractors/case-extractor.md` |
| counter-example-extractor | 书中警告的失败模式 | `extractors/counter-example-extractor.md` |
| glossary-extractor | 关键概念词典 | `extractors/glossary-extractor.md` |

天龙 Agent 工具调用：5 个 sub-agent 一次性发起（不串行）。

---

## 5. 蒸馏档位（成本控制）

| 档位 | 调研规模 | 成本 | 触发条件 |
|---|---|---|---|
| 快速 | 1 个 adler + 5 agent 各跑 1 轮 | ≈ 标准 1/3 | 冷门 / 试效果 |
| 标准（默认）| 完整 7 阶段 + 三重验证 | 中等 | 默认 |
| 深度 | 7 阶段 + 多轮 darwin 评估 | 最高 | 打算开源发布 |

**永远先试点 1 本** —— 除非用户明确说"批量"。

---

## 6. 失败兜底

| 失败模式 | 兜底 |
|---|---|
| 阶段 0 文本缺失 | 立即停下来问用户要 PDF/EPUB/字幕 |
| 5 agent 并行不可用 | 退化为串行执行（产出格式不变）|
| 阶段 1.5 候选通过率 < 25% | 检查 source 文本质量 + 提示用户补充语料 |
| 阶段 4 test-prompts 全不过 | 回炉重做阶段 2（不做"表面修补"）|

---

## 7. 不在天龙范围内的约束

- **不**在没有文本的情况下"凭记忆"蒸馏（宁可停下来问用户）
- **不**上传 cangjie 完整模板到 H5 / 博客 / 公众号文章内的可访问 HTML 位置（**AGPL § 13 触发**）
- **不**把 cangjie 蒸馏方法论当知识付费课程售卖（**AGPL § 5 + L107 + L171 三重禁止**）
- **不**整包闭源转售（除非 fork + AGPL 同协议）
- **不**用 cangjie 输出训练竞品模型或复刻类似产品

---

## 8. 后续协同点（天龙 36-38 候选）

- **36**：cangjie 蒸馏产物落双路径（`~/.claude/skills/` + `dragon-engine/skills/<book>-skill/`）
- **37**：darwin 进化结果自动同步给 neat-freak V1.1 做 Apache/MIT/AGPL 三协议红线复核
- **38**：与 book-distiller V9.12 的 post_distill_vet 联动 → cangjie 蒸馏产物二次过 vet