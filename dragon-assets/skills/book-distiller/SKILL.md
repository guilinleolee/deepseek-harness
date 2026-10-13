---
name: book-distiller
description: 天龙自研书籍蒸馏器 V9.12 — 4 层自检 + 多语言 + 知识图谱 + post_distill_vet 联动 · 与 cangjie-skill(AGPL-3.0)互导非依赖
version: 9.12
base_version: 9.08
category: meta-pipeline
department: 元流水线-知识工业化部
license: 天龙自有(非开源协议)
upstream:
  name: 天龙自研 (book-distiller V9.08-V9.12)
  version: V9.12
  url: (内部)
  license: 天龙自有
  stars: N/A
modified: 2026-08-04
modified_by: 天龙引擎 dragon-engine
integration_stage: 38
cangjie_compatible: true
cangjie_link_mode: 互导(非依赖) · cangjie 蒸馏产物可被 V9.12 4 层自检验证
triggers:
  - "蒸馏一本书"
  - "把书蒸馏为 skill"
  - "book distillation"
  - "章节摘要 + 概念卡"
  - "4 层自检"
  - "post_distill_vet"
  - "book-distiller V9.12"
---

# book-distiller · 天龙书籍蒸馏器 V9.12

> **TL;DR**:天龙自研书籍蒸馏器 V9.12,把一本书 / 一份长文档蒸馏为可复用的结构化资产(章节摘要 + 核心概念卡 + 案例库 + 知识图谱),**4 层自检**确保蒸馏质量。**与 cangjie-skill(AGPL-3.0 mirror-only)互导非依赖**——cangjie 的 7 阶段 RIA-TV++ 蒸馏产物可被 V9.12 4 层自检验证,反之亦然。

---

## L0: 一句话(≤15 字)

**天龙自研书籍蒸馏器 V9.12**

## L1: 使用场景

用户需要把一本书 / 一份长内容(报告 / 长文 / 课程转写 / 视频转录稿)蒸馏为可复用资产时使用:

1. **章节摘要** —— 全书骨架 + 段落摘要
2. **核心概念卡** —— 关键概念 + 解释 + 边界
3. **案例库** —— 自动识别"案例 / 故事 / 对话"段落
4. **知识图谱** —— 实体 + 关系抽取(多语言)
5. **4 层自检** —— L1 完整 / L2 一致 / L3 知识密度 / L4 复用价值
6. **post_distill_vet 联动** —— 蒸馏产物写入 skills/ 时自动跑 vet

## L2: 详细文档

### 版本演进

| 版本 | 关键变更 |
|------|---------|
| V9.08 | 基础蒸馏流程(章节 → 摘要 → 概念卡)|
| V9.09 | + 案例库(自动识别"案例 / 故事 / 对话"段落)|
| V9.10 | + 知识图谱(实体关系抽取)|
| V9.11 | + 多语言支持(中 / 英 / 日)|
| **V9.12** | **+ 蒸馏质量自检(4 层)+ 与 post_distill_vet 联动** |

### V9.12 核心升级:4 层自检

| 层级 | 检查内容 | 实现 |
|------|---------|------|
| **L1 完整性** | 章节是否 100% 覆盖(无遗漏 / 无重复) | 章节匹配 + 段落哈希去重 |
| **L2 一致性** | 摘要与原文章节主旨是否一致(无曲解) | 关键词重叠 + LLM 验证(可选)|
| **L3 知识密度** | 概念卡 / 案例库是否包含可操作知识 | 概念密度阈值 + 案例完整性 |
| **L4 复用价值** | 蒸馏产物是否能被天龙其他 skill 直接消费 | frontmatter 校验 + trigger 关键词命中 |

### post_distill_vet 联动

- book-distiller 蒸馏产物进入天龙资产前,必须通过 post_distill_vet
- 触发:蒸馏产物写入 `~/.claude/skills/` 或 `agents/` 时自动跑 vet
- 误报走 vet_whitelist V9.13 多语言白名单(尚未实现)

### 输入输出

**输入**(任意一种):
- cangjie 蒸馏产物目录(`BOOK_OVERVIEW.md` + `verified.md` + 12 × `SKILL.md` + `DIGEST.md`)
- 一份长文本 / 章节摘要 / 课程转写

**输出**(`--out-dir` 指定):
- `report_L1_completeness.md` —— 章节覆盖报告
- `report_L2_consistency.md` —— 主旨一致性报告
- `report_L3_density.md` —— 知识密度报告
- `report_L4_reuse.md` —— 复用价值报告
- `summary.json` —— 4 层 PASS/FAIL 总览

## L3: 与 cangjie-skill 协同(38 阶段互导)

### 互导(非依赖)

| 维度 | cangjie-skill | book-distiller V9.12 |
|------|--------------|---------------------|
| 来源 | kangarooking 上游 AGPL-3.0 | 天龙自研 V9.08-V9.12 |
| 阶段 | 7 阶段 RIA-TV++ 元流水线 | 章节→摘要→概念卡→案例→图谱→自检 |
| License | AGPL-3.0 ⚠️ mirror-only | 天龙自有 |
| 互导方向 | cangjie 输出 → V9.12 自检 | V9.12 输出 → cangjie stage-1 输入 |

### 实跑链路(38 阶段)

```
cangjie/local-tests/cangjie-test-book-minimal/
└── (模拟蒸馏产物)──┐
                    ├──→ book-distiller V9.12 4 层自检 ──→ summary.json
V9.12/local-tests/  │
└── (天龙蒸馏样本)──┘
```

## Attribution

天龙自研,无上游协议。

**协同上游**:[kangarooking/cangjie-skill](https://github.com/kangarooking/cangjie-skill)(AGPL-3.0)—— 互导非依赖,各自独立运行。

## 版本信息

- **Version**: 9.12
- **Base**: V9.08
- **Upgrade Date**: 2026-08-04
- **License**: 天龙自有
- **Integration Stage**: 38
- **累计 PASS**: 见 tests/test_installation.py(预计 18-22 PASS)