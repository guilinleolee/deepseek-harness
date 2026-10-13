# HANDOFF.md · cangjie-skill × 天龙引擎

> **协议**：跨阶段交付文档（与上游 cangjie-skill 平级扩展，但**不修改** upstream 任何字节）
> **AGPL 红线**：本文件是文档层扩展，不修改 LICENSE / README.md / methodology/ / extractors/ / templates/ 任何上游字节。

---

## 1. 输入与输出契约

### 1.1 输入

| 维度 | 必填 | 默认 |
|---|---|---|
| 内容文本来源（PDF / EPUB / TXT / 字幕 / 转写稿）| ✅ | — |
| 内容元信息（书名 + 作者 + 出版年 / 视频标题 + UP 主 + 时间）| ✅ | — |
| 是否首次试点 | | 是（永远先试点 1 本）|
| 蒸馏档位（快速 / 标准 / 深度）| | 标准 |

### 1.2 输出结构（与上游一致）

```
books/<book-slug>/
├── PIPELINE_STATE.md          # 流水线状态: 当前阶段 + 各 skill 进度（断点续跑用）
├── BOOK_OVERVIEW.md           # 阶段 0 产出: 主旨/骨架/术语/批判
├── verified.md                # 阶段 1.5 产出: 通过三重验证的单元 + 判定理由
├── INDEX.md                   # 阶段 3 产出: skill 总览 + 引用图
├── GLOSSARY.md                # 阶段 3 产出: 全书共享术语词典
├── DIGEST.md                  # 阶段 5 产出: 面向读者的精华长文
├── candidates/                # 阶段 1 产出: 原始候选池（审计用）
├── rejected/                  # 阶段 1.5 淘汰的单元 + 原因（审计用）
└── <skill-slug-N>/
    ├── SKILL.md
    ├── test-prompts.json      # darwin 兼容格式
    └── test-results.md        # 阶段 4 测试通过率 + 失败分析
```

---

## 2. 与天龙既有资产的衔接

### 2.1 落盘路径

| 用途 | 路径 |
|---|---|
| 公开发布（任何人都能用）| `~/.claude/skills/<book-slug>/<skill-slug>/SKILL.md` |
| 博主全息（与 laoli_bro_2026 协同）| `~/.claude/ip-profiles/laoli_bro_2026/skills/<book-slug>-<skill-slug>/` |
| 主题研究（与 28-04 内容策划协同）| `dragon-engine/skills/<book-slug>/<skill-slug>/` |

### 2.2 与 darwin 衔接契约束化

```json
{
  "skill": "<book-slug>-<skill-slug>",
  "version": "0.1.0",
  "source_book": "<BOOK_TITLE> — <AUTHOR>",
  "darwin_compatible": true,
  "test_cases": [
    {"id": "should-trigger-01", "type": "should_trigger", "prompt": "...", "expected_behavior": "...", "notes": "..."},
    {"id": "should-not-trigger-01", "type": "should_not_trigger", "prompt": "..."},
    {"id": "edge-01", "type": "edge_case", "prompt": "..."}
  ],
  "minimum_pass_rate": 0.8,
  "notes": "至少 3 条 should_trigger + 2 条 should_not_trigger + 1 条 edge_case..."
}
```

darwin 直接消费，无需 schema 转换。

### 2.3 与 book-distiller 互导

- cangjie Stage 0 BOOK_OVERVIEW.md → book-distiller 4 层自检作 L1 完整性预筛
- book-distiller DIGEST.md → cangjie Stage 1 5 agent 并行提取的源文本

---

## 3. 质量门神（天龙额外约束）

| 校验项 | 阈值 | 失败动作 |
|---|---|---|
| 三重验证通过率 | 通常 25-50% | 阻断（候选不够质量）|
| R/I/A1/A2/E/B 六段完整 | 全部 | 阻断 |
| 原文引用长度 | ≤150 字/段（英文 ≤100 词/段）| 警告 |
| test-prompts.json 含诱饵 | ≥1 should_not_trigger | 阻断 |
| 跨 skill 混淆诱饵 | ≥1（应触发同书另一个 skill）| 阻断 |
| **天龙额外** | | |
| MIT 致谢段（5 模板）| 完整 | 警告 |
| AGPL 商用边界（COMMERCIAL_LICENSING.md）| 引用 | 阻断 |
| AGPL 红线 8 项 | 全部通过 | 阻断 |

详见 `tests/test_cangjie_installation.py` 27 项检查。

---

## 4. 跨阶段交付 Link

| 上游 | 输出物 | 下游 |
|---|---|---|
| 视频/播客转写 | 字幕 / 转写文本 | cangjie Stage 0 |
| cangjie Stage 4 | `<book>/<skill>/test-prompts.json` | darwin Phase 1 评估 |
| cangjie Stage 5 | DIGEST.md | book-distiller V9.12 二次加工 |
| darwin 进化结果 | `<skill>.SKILL.md`（改善版）| 反哺天龙 skill 库 |

---

## 5. 失败兜底

| 失败模式 | 兜底 |
|---|---|
| 内容文本缺失 | 立即停下来问用户 |
| 阶段 1 并行不可用 | 退化为串行（产出格式不变）|
| 候选通过率 < 25% | 检查源文本质量 + 提示用户补充语料 |
| test-prompts 全不过 | 回炉重做阶段 2 |
| AGPL 红线 8 项不过 | 阻断 + 报警 |

---

## 6. 累计 PASS 校验（天龙阶段 35-B）

- 27 项 cangjie 安装自检 = **27/27 PASS**
- 详见 `tests/test_cangjie_installation.py`