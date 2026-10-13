# PRODUCT.md · nuwa-skill × 天龙引擎产品定位

> **与上游 nuwa-skill 平级扩展，但**不修改** upstream 任何字节**
> **目的**：理清 nuwa 在天龙生态中的位置，避免与既有 26 阶段 100+ skill 冲突

---

## 1. 一句话定位

**nuwa 是天龙引擎「人 / 思维模式」的蒸馏器**——把任何人的思维方式蒸馏成可执行的人物 skill（vs book-distiller 蒸馏书 / cangjie 蒸馏书做 skill 群）。

---

## 2. 与天龙既有 9 类核心 skill 的边界

| 维度 | nuwa-skill | 既有对照 | 边界 |
|---|---|---|---|
| 蒸馏对象 | 人 / 思维模式 | book-distiller 蒸馏书 / cangjie 蒸馏书 | 互不重叠 |
| 产物类型 | 1 个 `<person>-perspective/SKILL.md` | book-distiller 产 DIGEST + 概念卡 | nuwa 单点深入，book-distiller 广度 |
| 输入 | 文本 / 有声 / 视频 | 文本 | nuwa 也支持音视频（scripts/srt_to_transcript.py）|
| 评估 | quality_check.py (5 维) | post_distill_vet (4 层) | 互补：nuwa 5 维 + vet 4 层 |
| 落地 | 人物 skill | 知识资产 | 互补 |
| 进化 | test-prompts.json → darwin | book-distiller 无进化 | 互补：nuwa 可进化 |

---

## 3. 关键决策树

```
用户说「蒸馏 XX」
    │
    ├─ XX 是人 / 思维模式？→ 是 → nuwa-skill
    │
    ├─ XX 是书 / 长视频 / 播客？→ 是 → cangjie-skill
    │
    ├─ XX 是知识资产 / 已上传的 PDF？→ 是 → book-distiller V9.12
    │
    └─ XX 是「优化现有 skill」？→ 是 → darwin-skill
```

---

## 4. Stage 35 阶段协同架构

```
              ┌──────────────────────────┐
              │   book-distiller V9.12   │  ← 自研 · 用户级 · 知识资产沉淀
              │   (4 层自检 + post_vet)  │
              └──────────────┬───────────┘
                             │
                             ↓
       ┌─────────────────────────────────────┐
       │      cangjie-skill (AGPL)          │  ← 蒸馏书 · 产可调用 skill 群
       │      RIA-TV++ 7 阶段                │
       │      test-prompts.json → darwin     │
       └────────────────┬────────────────────┘
                        │
                        ↓
       ┌─────────────────────────────────────┐
       │      darwin-skill (MIT)            │  ← 任意 skill 进化器
       │      9 维 rubric + hill climbing   │
       │      配合 neat-freak V1.1 红线护栏  │
       └────────────────┬────────────────────┘
                        │
                        ↓
       ┌─────────────────────────────────────┐
       │      nuwa-skill (MIT)  本阶段扩   │  ← 蒸馏人 · 产思维模式 skill
       │      5 维人物 skill                 │
       │      test-prompts.json → darwin     │
       └─────────────────────────────────────┘
```

天龙调用约定：**nuwa 产出 → darwin 评估 → 改进 → 保留或回滚 → 反哺 35-02 / 35-06 博主全息**

---

## 5. 三个核心数字

| 维度 | 数字 |
|---|---|
| nuwa 默认档位 | 标准（6 维度）|
| nuwa 典型成本 | 中等（单一人物，全自动）|
| test-prompts.json schema | 7 字段对齐 darwin |

---

## 6. 后续协同（阶段 36-38 候选）

- **36**：nuwa 蒸馏产物落双路径 + 龙引擎主题文件
- **37**：darwin 进化结果自动同步给 neat-freak V1.1
- **38**：与 book-distiller V9.12 的 post_distill_vet 联动
